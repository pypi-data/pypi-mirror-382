#!/usr/bin/env python3
# =============================================================================
"""Balena Vars

Author:
    Juan Pablo Castillo - juan.castillo@kiwibot.com
"""
# =============================================================================

import balena
import os
import uuid
import datetime
import logging
from fleet_control.utils.utils import *
from fleet_control.utils.python_utils import format_time, load_json, confirm_schedule, COLORS
from fleet_control.resources.classes import create_target, Device, Application

logger = logging.getLogger(__name__)


def delete_variables(
    target_device: balena.types.models.TypeDevice,
    variables: dict[str, dict],
    service: int = 0,
    exclude: set | None = None,
) -> None:
    """Update device variables with source variables."""
    device_id = target_device["id"]
    device_name = target_device.get("device_name", "Unknown")
    env_vars = variables.get("env_vars")
    service = next(iter(variables.get("service_vars", {}).keys()), 0)
    service_vars = variables.get("service_vars", {}).get(service)

    if exclude is None:
        exclude = set()
    exclude.add("BOT_ID")

    # Update environment variables
    if env_vars:
        for var_name in env_vars:
            if var_name in exclude:
                continue
            balena_sdk.models.device.env_var.remove(device_id, var_name)
            logger.info(f"Variable {var_name} deleted for device {device_name}")

    # Update service variables
    if service_vars:
        for var_name in service_vars:
            if var_name in exclude:
                continue
            balena_sdk.models.device.service_var.remove(target_device["uuid"], service, var_name)
            logger.info(f"Service variable {var_name} deleted for device {device_name}")


def update_variables(
    target: balena.types.models.TypeDevice | balena.types.models.TypeApplication | Device | Application,
    source_vars: dict[str, dict],
    target_vars: dict[str, dict] | None = None,
    target_custom_vars: dict[str, dict] | None = None,
    exclude: set | None = None,
    delete_custom: bool = False,
    turn_off_nodes: bool = False,
    dry_run_mode: bool = False,
    force: bool = False,
) -> None:
    """Update device or application variables with source variables.

    Args:
        target: Either a device or application object, or a Device/Application instance
        source_env_vars: Dictionary of environment variables to set
        source_service_vars: Dictionary of service variables to set
        exclude: List of variable names to exclude from updates
        delete_custom: Whether to delete custom variables
        turn_off_nodes: Whether to turn off nodes not present in source
        force: Don't check if the variable is already set
    """
    if dry_run_mode:
        logger.info("\033[33mDry run mode enabled, no changes will be done\033[0m")

    # Create target object if a raw balena typedDict was passed
    if not isinstance(target, (Device, Application)):
        target = create_target(target)

    custom_env_vars, custom_service_vars = {}, {}
    source_env_vars: dict[str, str] = source_vars["env_vars"]
    service = next(iter(source_vars["service_vars"].keys()), 0)
    source_service_vars: dict[str, str] = source_vars["service_vars"][service]

    # Get existing variables
    if not force:
        exclude_set = set(exclude or []).union({"BOT_ID", "UAVCAN_SCREEN_INITIAL_ANIMATION"})
        temp = target.get_variables() if not target_vars else target_vars
        existing_env_vars = temp.get("env_vars")
        service = next(iter(temp["service_vars"].keys()), 0)
        existing_service_vars = temp.get("service_vars", {}).get(service)  # type: ignore
    else:
        exclude_set = set()
        existing_env_vars = {}
        existing_service_vars = {}
        if isinstance(target, Device):
            service = get_service_id(target.belongs_to__application["__id"], "main")  # type: ignore
        elif isinstance(target, Application):
            service = get_service_id(target.id, "main")  # type: ignore

    if delete_custom:
        temp_custom = target.get_variables(custom=True) if not target_custom_vars else target_custom_vars
        custom_env_vars, custom_service_vars = temp_custom["env_vars"], temp_custom["service_vars"][service]  # type: ignore

    def update_variable(var_name, value, existing_vars, is_service_var=False):
        if existing_vars.get(var_name) != value and var_name not in exclude_set:
            if is_service_var and service:
                target.set_service_var(service, var_name, value) if not dry_run_mode else None  # type: ignore
            else:
                target.set_env_var(var_name, value) if not dry_run_mode else None
            logger.info(f"{var_name} set to {value} for {target.get_identifier()}")
        existing_vars.pop(var_name, None)

    # Turn off nodes not present in source when cloning
    if turn_off_nodes:

        def turn_off_node(existing_vars, source_vars, is_service_var=False):
            for var_name in list(existing_vars):
                if var_name.startswith("NODE") and var_name not in exclude_set and source_vars.get(var_name) is None:
                    if existing_vars.get(var_name) != "0":
                        if is_service_var and service:
                            target.set_service_var(service, var_name, "0") if not dry_run_mode else None  # type: ignore
                        else:
                            target.set_env_var(var_name, "0") if not dry_run_mode else None
                        logger.info(f"{var_name} set to 0 for {target.get_identifier()}")
                    existing_vars.pop(var_name)

        turn_off_node(existing_env_vars, source_env_vars)
        turn_off_node(existing_service_vars, source_service_vars, True)

    # Update environment variables
    for var_name, value in source_env_vars.items():
        update_variable(var_name, value, existing_env_vars)

    # Update service variables
    for var_name, value in source_service_vars.items():
        update_variable(var_name, value, existing_service_vars, True)

    # Remove remaining custom variables (only for clone)
    if delete_custom:

        def remove_custom_variable(existing_vars, custom_vars, source_vars, is_service_var=False):
            for var_name in list(existing_vars):
                if (
                    var_name not in exclude_set
                    and var_name in custom_vars
                    and source_vars.get(var_name) != custom_vars.get(var_name)
                ):
                    if is_service_var and service:
                        target.remove_service_var(service, var_name) if not dry_run_mode else None  # type: ignore
                    else:
                        target.remove_env_var(var_name) if not dry_run_mode else None
                    logger.info(f"{var_name} removed for {target.get_identifier()}")
                    existing_vars.pop(var_name)

        remove_custom_variable(existing_env_vars, custom_env_vars, source_env_vars)
        remove_custom_variable(existing_service_vars, custom_service_vars, source_service_vars, True)


def change(variables: dict | str, targets: set, force: bool = False):
    """Change or create specified variable(s) to TARGET(s).

    Args:
        variables (dict | str): Separated by spaces in the form "var1=value1=service1 var2=value2=service2"
        targets (set): One or more target bots (format: 4X000) and/or fleets

    Raises:
        ValueError: If variables are not in the correct format
    """

    if not targets:
        logger.error("At least one target must be specified")
        return
    if isinstance(variables, str):
        env_vars, service_vars = {}, {}
        for var in variables.split(" "):
            if not VARIABLES_REGEX.match(var):
                raise ValueError("Variable must be in the format 'variable1=value=service' or 'variable1=value'")
            variable = var.split("=")

            if len(variable) <= 2 or variable[2] == "*":
                env_vars.update({variable[0]: variable[1]})
            else:
                service_vars.update({variable[0]: variable[1]})
        variables = {"env_vars": env_vars, "service_vars": {"main": service_vars}}
    elif isinstance(variables, dict):
        pass
    else:
        logger.error("Check 'variables' object class")
        return

    for target_id in targets:
        if BOT_ID_REGEX.match(target_id):
            target = get_device_by_id(target_id)
        else:
            target = get_fleet(target_id)

        if target:
            logger.info(f"Updating: {target_id}")
            update_variables(target, variables, force=force)
            logger.info(f"Successfully updated: {target_id}")


def clone(source: str, targets: set, exclude: str | None = None):
    """Clone configuration from SOURCE to TARGET(s).

    Args:
        source (str): Either a device ID (format: 4X000) or a fleet name.
        targets (set): One or more target device IDs (format: 4X000) or fleets.
        exclude (str | None, optional): Variables to exclude, must be in the format "var1 var2". Defaults to None.

    Raises:
        ValueError: If device is not found
        ValueError: If fleet is not found
    """
    if not targets:
        logger.error("At least one target device must be specified")
        return

    exclude_vars = set()
    if exclude is not None:
        for variable2exclude in exclude.split(" "):
            exclude_vars.add(variable2exclude)

    # Check if source is a device ID (4X000) or fleet
    if BOT_ID_REGEX.match(source):
        # Source is a device
        source_device = get_device_by_id(source)
        if not source_device:
            raise ValueError(f"Source device {source} not found")
        source_vars = get_device_variables(source_device)
    else:
        # Source is a fleet
        source_fleet = get_fleet(source)
        if not source_fleet:
            raise ValueError(f"Source fleet {source} not found")
        source_vars = get_fleet_variables(source_fleet)

    for target_id in targets:
        if not BOT_ID_REGEX.match(target_id):
            logger.info(f"{COLORS['WARNING']}Fleet {target_id} selected as target!{COLORS['RESET']}")
            target = get_fleet(target_id)
        else:
            target = get_device_by_id(target_id)
        if target:
            logger.info(f"Updating: {target_id}")
            update_variables(
                target,
                source_vars,
                exclude=exclude_vars,
                delete_custom=True,
                turn_off_nodes=True,
            )
            logger.info(f"Successfully updated: {target_id}")


def purge(targets: set, exclude: str | None = None):
    """Purge all custom variables in TARGET device(s).

    Args:
        targets (set): One or more target device IDs (format: 4X000).
        exclude (str | None, optional): Variables to exclude, must be in the format "var1 var2". Defaults to None.
    """
    exclude_vars = set()
    if exclude is not None:
        for variable2exclude in exclude.split(" "):
            exclude_vars.add(variable2exclude)

    for target_id in targets:
        if not BOT_ID_REGEX.match(target_id):
            logger.info(f"Skipping invalid target ID format: {target_id}")
            continue
        target_device = get_device_by_id(target_id)
        if target_device:
            logger.info(f"Purging device: {target_id}")
            variables = get_device_variables(target_device, custom_only=True)
            delete_variables(target_device, variables, exclude=exclude_vars)
            logger.info(f"Successfully purged device: {target_id}")


def get(
    targets: set[str] | set[balena.types.models.TypeDevice] | balena.types.models.TypeApplication,
    variable_name: str = "",
    custom: bool = False,
    all_vars: bool = False,
) -> dict[str, dict[str, str | int]]:  # type: ignore
    """Fetch variable value for a device or fleet.

    Args:
        targets (set[str] | set[balena.types.models.TypeDevice] | balena.types.models.TypeApplication): One or more target device IDs (format: 4X000) and/or fleets.
        variable_name (str, optional): Variable name. Defaults to "".
        custom (bool, optional): Return all custom vars. Defaults to False.
        all_vars (bool, optional): Return all device + fleet vars. Defaults to False.

    Returns:
        dict[str, dict[str, str | int]]: Dictionary with variables or value of variable
    """
    variables = {}
    for target in targets:
        target_device = None
        target_fleet = None
        if isinstance(target, str):
            target_name = target
            if BOT_ID_REGEX.match(target_name):
                target_device = get_device_by_id(target_name)
            else:
                target_fleet = get_fleet(target_name)
        elif target.get("device_name"):
            target_name = target["device_name"].removeprefix("kiwibot")
            target_device = target
        elif target.get("app_name"):
            target_fleet = target
        else:
            logger.info(f"Skipping invalid target format: {target}")
            continue
        variables[target_name] = {"env_vars": {}, "service_vars": {"main": {}}}

        if target_device:
            logger.info(f"Getting vars for {target_name}")
            device_id = target_device["id"]  # type: ignore
            app_id = int(target_device["belongs_to__application"]["__id"])  # type: ignore

            if all_vars or custom:
                variables[target_name] = get_device_variables(target_device, custom_only=custom)
            else:
                app_id = int(target_device["belongs_to__application"]["__id"])  # type: ignore
                service = get_service_id(target_device, "main")
                # Get env-var values variables
                value = balena_sdk.models.device.env_var.get(device_id, variable_name)
                if value is None:
                    value = balena_sdk.models.application.env_var.get(app_id, variable_name)

                if value is not None:
                    variables[target_name]["env_vars"] = {variable_name: value}

                # Get service variables value
                value = balena_sdk.models.device.service_var.get(device_id, service, variable_name)

                if value is None:
                    value = balena_sdk.models.service.var.get(service, variable_name)

                if value is not None:
                    variables[target_name]["service_vars"] = {service: {variable_name: value}}
        elif target_fleet:
            logger.info(f"Getting vars for {target_name}")
            fleet_id = target_fleet["id"]
            _vars = get_fleet_variables(fleet_id)
            env_vars = _vars.get("env_vars", {})
            service_vars = _vars.get("service_vars", {}).get("main", {})

            if all_vars:
                variables[target_name] = _vars
            elif custom:
                variables[target_name] = get_custom_set_vars_fleet(target_fleet)
            else:
                if variable_name in env_vars:
                    variables[target_name]["env_vars"] = {variable_name: env_vars[variable_name]}
                if variable_name in service_vars:
                    variables[target_name]["service_vars"]["main"] = {variable_name: service_vars[variable_name]}

    return variables


def delete(variables: dict | str, targets: set):
    """Delete the overwritten value for the specified variable(s) on the TARGET device(s).

    Args:
        variables (dict | str): Separated by spaces in the form "var1=value1=service1 var2=value2=service2"
        targets (set): One or more target device IDs (format: 4X000)

    Raises:
        ValueError: If variables are not in the correct format
    """
    if not targets:
        logger.error("At least one target device must be specified")
        return
    if isinstance(variables, str):
        env_vars, service_vars = {}, {}
        for var in variables.split(" "):
            if not VARIABLES_REGEX.match(var):
                raise ValueError("Variable must be in the format 'variable1=value=service'")
            variable = var.split("=")

            if len(variable) <= 2 or variable[2] == "*":
                env_vars.update({variable[0]: variable[1]})
            else:
                service_vars.update({variable[0]: variable[1]})
        variables = {"env_vars": env_vars, "service_vars": {"main": service_vars}}
    elif isinstance(variables, dict):
        pass
    else:
        logger.error("Check 'variables' object class")
        return

    for target_id in targets:
        if not BOT_ID_REGEX.match(target_id):
            logger.info(f"Skipping invalid target ID format: {target_id}")
            continue

        target_device = get_device_by_id(target_id)
        if target_device:
            # Get service id and rebuild the dict using the id instead of "main"
            service = get_service_id(target_device, "main")
            variables["service_vars"][service] = variables["service_vars"].pop("main")

            logger.info(f"Updating device: {target_id}")
            delete_variables(target_device, variables)
            logger.info(f"Successfully updated device: {target_id}")
            variables["service_vars"]["main"] = variables["service_vars"].pop(service)


def move(fleet: str, targets: set, keep_vars: bool, keep_service_vars: bool, clone: bool, semver: str | None = None):
    """Move target(s) from its fleet to specified FLEET.

    Args:
        fleet (str): Chosen fleet's name (i.e: Test4_x).
        targets (set): One or more target device IDs (format: 4X000).
        keep_vars (bool): keep custom device vars
        keep_service_vars (bool): keep custom device and service vars
        clone (bool): keep custom and previous fleet vars
        semver (str | None, optional): pin to specific release (format: 1.3.11+rev87). Defaults to None.
    """
    if not targets:
        logger.error("At least one target device must be specified")
        return

    if BOT_ID_REGEX.match(fleet):
        logger.error(f"Error moving {', '.join(targets)} to {fleet}")
        return

    fleet_id = get_fleet(fleet)["id"]
    release = find_release(fleet_id, semver)

    for target_id in targets:
        if not BOT_ID_REGEX.match(target_id):
            logger.info(f"Skipping invalid target ID format: {target_id}")
            continue

        target_device = get_device_by_id(target_id)
        if not target_device:
            logger.info(f"No target with ID found: {target_id}")
            continue

        logger.info(f"Moving device: {target_id}")
        variables = {"env_vars": {}, "service_vars": {"main": {}}}
        if clone:
            variables = get(set([target_id]), all_vars=True)
        elif keep_service_vars:
            variables = get(set([target_id]), custom=True)

        balena_sdk.models.device.move(target_device["id"], fleet_id)
        logger.info(f"Successfully moved device {target_id} to {fleet}")

        pin_to_release(target_device, release)

        if keep_service_vars or clone:
            if clone:
                update_variables(target_device, variables, turn_off_nodes=True)
            else:
                variables["env_vars"].update({})
                update_variables(target_device, variables)
        elif not keep_vars:
            purge(set(target_id))


def schedule_change(message_data: dict, date: str, date_format: str, tz: str) -> None:
    """POST request with variables to change in some targets to a Google Pub/Sub topic at a specified time.

    Args:
        message_data (dict): File with the targets and variables to change.
        date (str): The date string to convert (e.g., '2024-11-25 15:30:00')
        date_format (str): The format of the date string
        tz (str): The timezone for the schedule date

    """
    task_id = uuid.uuid1()
    message_data["task_id"] = str(task_id)
    date_object = format_time(date, date_format, tz)

    row = [
        str(task_id),
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        date_object.strftime("%Y-%m-%d %H:%M:%S GMT%Z"),
        "",
        False,
        ", ".join([target for target in message_data["targets"]]),
        ", ".join([f"{variable}={value}" for variable, value in message_data["variables"]["env_vars"].items()])  # type: ignore
        + ", ".join(
            [
                f"{variable}={value}"
                for variable, value in message_data["variables"]["service_vars"]["main"].items()  # type: ignore
            ]
        ),
    ]
    schedule_base(date_object, tz, message_data, "vars-change", "VarChangeLog", row)


def schedule_update(message_data: dict, date: str, date_format: str, tz: str) -> None:
    """POST request with targets to pin to a specific release.

    Args:
        message_data (dict): File with the targets and selected release. See readme for more details.
        date (str): The date string to convert (e.g., '2024-11-25 15:30:00')
        date_format (str): The format of the date string
        tz (str): The timezone for the schedule date
    """

    # Process input data (from JSON file or command-line arguments)
    task_id = uuid.uuid1()
    message_data["task_id"] = str(task_id)
    date_object = format_time(date, date_format, tz)

    row = [
        str(task_id),
        datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
        date_object.strftime("%Y-%m-%d %H:%M:%S GMT%Z"),
        "",
        False,
        message_data["fleet"],
        message_data["release"],
        ", ".join([target for target in message_data["targets"]]),
    ]
    schedule_base(date_object, tz, message_data, "pin-to-release", "BotPinReleaseLog", row)


def schedule_base(date_object, tz, message_data, pubsub_topic, worksheet_name, row: list[str]):
    """Base function to schedule a task in Google Cloud Tasks and log it in Google Sheets."""
    if (
        PROJECT_ID is None
        or LOCATION_ID is None
        or QUEUE_ID is None
        or (SERVICE_ACCOUNT is None and SERVICE_ACCOUNT_EMAIL is None)
    ):
        logger.error(
            "Missing one of the required environment variables: PROJECT_ID, LOCATION_ID, QUEUE_ID, SERVICE_ACCOUNT, or SERVICE_ACCOUNT_EMAIL"
        )
        raise EnvironmentError("Please set these variables in your environment or .env file.")
    if SERVICE_ACCOUNT is not None:
        service_account = load_json(SERVICE_ACCOUNT)
        service_account_client_email = service_account.get("client_email")
    else:
        service_account_client_email = SERVICE_ACCOUNT_EMAIL

    row.insert(1, AUTHOR)
    pubsub_message = format_pubsub_message(message_data)
    confirmation = confirm_schedule(message_data, date_object, tz)

    if confirmation.lower() in ["no", "n"]:
        logger.warning("Operation Aborted")
    elif confirmation.lower() in ["yes", "y"]:
        # Create the Cloud Task
        create_http_task(
            project=PROJECT_ID,
            location=LOCATION_ID,
            queue=QUEUE_ID,
            url=f"https://pubsub.googleapis.com/v1/projects/{PROJECT_ID}/topics/{pubsub_topic}:publish",
            json_payload=pubsub_message,
            scheduled_datetime=date_object,
            task_id=message_data["task_id"],
            service_account_client_email=service_account_client_email,
        )
        logger.info("Task created successfully")

        # Add record to Google Sheets
        try:
            sheet = open_sheet(SERVICE_ACCOUNT, SPREADSHEET_NAME, worksheet_name)
            response = sheet.append_row(row)
        except gspread.exceptions.APIError as e:
            logger.warning(f"Error adding record to {SPREADSHEET_NAME}, task was still created, check credentials")
            logger.warning(f"Error {e.args[0].get('code')}: {e.args[0].get('message')}")
        except Exception as e:
            logger.warning(f"Unexpected error adding record to {SPREADSHEET_NAME}, task was still created")
            logger.warning(f"Error: {e}")


def initialize(device: str | balena.types.models.TypeDevice, fleet: str):
    """Initialize TARGET with previous device tags, remove old device, delete default config variables, and move to specified FLEET.

    Args:
        device (str): Target device ID (format: 4X000).
        fleet (str): Chosen fleet's name (i.e: Test4_x).
    """
    fleet_id = get_fleet(fleet)["id"]
    bots = balena_sdk.models.device.get_all_by_application(fleet_id)
    sorted_bots = sorted(bots, key=lambda d: d["created_at"], reverse=True)
    new_bot = sorted_bots[0]
    del bots, sorted_bots

    if isinstance(device, dict):
        bot_to_delete = device
    else:
        bot_to_delete = get_device_by_id(device)

    if bot_to_delete:
        bot_to_delete_uuid, new_bot_uuid = bot_to_delete.get("uuid"), new_bot.get("uuid")

        # Clone tags
        tags = balena_sdk.models.device.tags.get_all_by_device(bot_to_delete_uuid)
        tags = {tag["tag_key"]: tag["value"] for tag in tags}
        for key, value in tags.items():
            balena_sdk.models.device.tags.set(new_bot_uuid, key, value)

        # Delete old device
        balena_sdk.models.device.remove(bot_to_delete_uuid)
        balena_sdk.models.device.rename(new_bot.get("uuid"), bot_to_delete.get("device_name"))

        # Set bot_id var
        balena_sdk.models.device.env_var.set(
            new_bot_uuid, "BOT_ID", bot_to_delete.get("device_name").replace("kiwibot", "")
        )

        # Delete default config variables
        config_vars = balena_sdk.models.device.config_var.get_all_by_device(new_bot_uuid)
        config_vars = {config_var["name"]: config_var["value"] for config_var in config_vars}
        for name in config_vars:
            balena_sdk.models.device.config_var.remove(new_bot_uuid, name)

        move(
            fleet=fleet,
            targets=set(bot_to_delete.get("device_name").removeprefix("kiwibot")),
            keep_vars=False,
            keep_service_vars=False,
            clone=False,
        )
        logger.info(f"Device {bot_to_delete.get('device_name')} successfully initialized")



def rename(bot_id: str | dict, new_id: str | dict, version: str | None = None):

    """Rename TARGET with new ID. Optional new tags for corresponding version read from configuration file.

    Args:
        target (str): Target device ID (format: 4X000).
        new_id (str): New device ID (format: 4X000).
        version (str | None, optional): Overwrite tags with tags from configuration file for version. Defaults to None.
    """

    # --- helper: normalize any input (string or device dict) into a BOT_ID string ---
    def _to_bot_id(v) -> str:
        # If it's already a '4Xnnn' style string, return as-is
        if isinstance(v, str):
            return v
        # If a balena device dict is passed by mistake, try to derive BOT_ID
        if isinstance(v, dict):
            # Prefer deriving from device_name: "kiwibot4F047" -> "4F047"
            name = v.get("device_name") or v.get("device_name_at_init") or ""
            if isinstance(name, str) and name.startswith("kiwibot"):
                return name.removeprefix("kiwibot")
            # Fallbacks: look for fields that might carry the ID explicitly
            bid = v.get("bot_id") or v.get("BOT_ID")
            if isinstance(bid, str):
                return bid
        # Last resort: stringify and try to extract a BOT_ID-looking pattern
        s = str(v)
        m = BOT_ID_REGEX.search(s) if hasattr(BOT_ID_REGEX, "search") else None
        return m.group(0) if m else s

    # Normalize early and then only use these
    original_bot_id = _to_bot_id(bot_id)
    new_id_str      = _to_bot_id(new_id)

    # --- format validation using normalized IDs only ---
    if not BOT_ID_REGEX.match(original_bot_id):
        print(f"ERROR: invalid target ID format: {original_bot_id}")
        exit(1)
    if not BOT_ID_REGEX.match(new_id_str):
        print(f"ERROR: invalid new ID format: {new_id_str}")
        exit(1)

    # --- existence checks based on normalized IDs ---
    bot_to_rename = get_device_by_id(original_bot_id)
    if not bot_to_rename:
        exit(1)
    if get_device_by_id(new_id_str) is not None:
        print(f"ERROR: Bot with id {new_id_str} already exists")
        exit(1)

    # Confirm with user, showing only the plain BOT_IDs
    if click.confirm(f"Do you want to rename the device {original_bot_id} to {new_id_str}?", default=True):
        bot_uuid = bot_to_rename.get("uuid")

        # Read current tags as a dict (later logged as JSON for stability/legibility)
        tags = {
            t["tag_key"]: t["value"]
            for t in balena_sdk.models.device.tags.get_all_by_device(bot_uuid)
        }

        new_tags: dict | str = ""
        exclude = {"City", "ROUTER_URL", "Team"}

        # If a version was provided, reset and apply versioned tags (excluding some keys)
        if version is not None:
            tags_file = load_json(TAGS_BY_VERSION_FILE)
            # Remove existing non-excluded tags
            for k in list(tags.keys()):
                if k not in exclude:
                    balena_sdk.models.device.tags.remove(bot_uuid, k)
            # Apply new tags from the version file
            for k, v in tags_file[version].items():
                balena_sdk.models.device.tags.set(bot_uuid, k, v)
            # Re-read final tag state
            new_tags = {
                t["tag_key"]: t["value"]
                for t in balena_sdk.models.device.tags.get_all_by_device(bot_uuid)
            }

        # Perform rename and update BOT_ID env var using the normalized new_id_str
        balena_sdk.models.device.rename(bot_uuid, "kiwibot" + new_id_str)
        balena_sdk.models.device.env_var.set(bot_uuid, "BOT_ID", new_id_str)

        # --- Append a row to Google Sheets ---
        try:
            sheet = open_sheet(SERVICE_ACCOUNT, SPREADSHEET_NAME, "ID change log")
            sheet.append_row(
                [
                    original_bot_id,  # A: from_id (always the original BOT_ID string)
                    new_id_str,       # B: to_id   (always the new BOT_ID string)
                    os.uname().nodename,  # C: blame/host
                    datetime.datetime.now(datetime.timezone.utc).strftime("%Y/%m/%d %H:%M:%S"),  # D: UTC timestamp
                    json.dumps(tags, ensure_ascii=False),        # E: tags before (stable JSON, not Python repr)
                    json.dumps(new_tags, ensure_ascii=False) if isinstance(new_tags, dict) else str(new_tags),  # F: tags after
                    bot_uuid,  # G: UUID (for traceability)
                ],
                value_input_option="RAW",  # Prevent Sheets from reinterpreting values
            )
        except Exception as e:
            # Log error but do not roll back the rename; the rename already happened.
            logger.error(str(e))
            logger.warning(f"Error adding record to {SPREADSHEET_NAME}, rename still occurred")

        print(f"Device {original_bot_id} successfully renamed to {new_id_str}")

def pin(
    fleet_name: str,
    semver: str | None = None,
    targets: set | None = None,
    all: bool = False,
    exclude: set | None = None,
):
    """
    Pin target(s) to specified FLEET release.
    If no targets specified, pin fleet.
    If `all` is True, pin all devices in the fleet.

    Args:
        fleet_name (str): Chosen fleet's name (i.e: Test4_x).
        targets (set | None, optional): One or more target device IDs (format: 4X000).
        semver (str | None, optional): pin to specific release (format: 1.3.11+rev87). Defaults to latest.
    """

    fleet = get_fleet(fleet_name)
    release = find_release(fleet["id"], semver)

    if not targets and not all:
        pin_to_release(fleet, release)
    elif all:
        logger.info(
            f"Pinning all devices in fleet {fleet_name} to release {release['semver']}rev{release['revision']}"
            if release["semver"] == "0.0.0"
            else f"Pinning {fleet_name} to release {release['semver']}"
        )
        devices = balena_sdk.models.device.get_all_by_application(fleet["id"])
        exclude_set = set(exclude or [])
        for device in devices:
            device_name = device.get("device_name", "")
            # Remove "kiwibot" prefix if present for comparison
            device_id = device_name.removeprefix("kiwibot")
            if device_id in exclude_set:
                logger.info(f"Excluding device: {device_id}")
                continue
            pin_to_release(device, release)
    elif targets:
        for target_id in targets:
            if not BOT_ID_REGEX.match(target_id):
                logger.info(f"Skipping invalid target ID format: {target_id}")
                continue

            target_device = get_device_by_id(target_id)
            if not target_device:
                logger.info(f"No target with ID found: {target_id}")
                continue

            pin_to_release(target_device, release)


def compare(device1: str, device2: str) -> None:
    """Compare variables between two devices.

    Args:
        device1 (str): First device ID (format: 4X000).
        device2 (str): Second device ID (format: 4X000).

    Returns:
        None
    """
    from deepdiff import DeepDiff

    device1_vars = get(set([device1]), all_vars=True)
    device2_vars = get(set([device2]), all_vars=True)

    # Normalize service_vars to compare only the variable values, not service IDs
    def normalize_service_vars(vars_dict):
        """Normalize service_vars by extracting the first service's variables"""
        normalized = vars_dict.copy()
        if "service_vars" in normalized and normalized["service_vars"]:
            # Get the first (and typically only) service's variables
            first_service_id = next(iter(normalized["service_vars"].keys()))
            normalized["service_vars"] = {"main": normalized["service_vars"][first_service_id]}
        return normalized

    device1_normalized = normalize_service_vars(device1_vars[device1])
    device2_normalized = normalize_service_vars(device2_vars[device2])

    diff = DeepDiff(device1_normalized, device2_normalized, ignore_order=True, verbose_level=2)

    if not diff:
        logger.info("No differences found between the two devices.")
        return

    # Parse the JSON output
    diff_json = json.loads(diff.to_json())

    def clean_path(path: str) -> str:
        """Clean the path by replacing root['env_vars'] with env_vars and root['service_vars'] with service_vars"""
        return path.replace("root['env_vars']", "env_vars").replace(
            "root['service_vars']['main']", "service_vars[main]"
        )

    # Handle added items
    if "dictionary_item_added" in diff_json:
        logger.info(f"{COLORS['OK_GREEN']}Variables added in {device2}:{COLORS['RESET']}")
        for path, value in diff_json["dictionary_item_added"].items():
            clean_path_str = clean_path(path)
            logger.info(f"  + {clean_path_str}: {value}")

    # Handle removed items
    if "dictionary_item_removed" in diff_json:
        logger.info(f"{COLORS['ERROR']}Variables missing from {device2}:{COLORS['RESET']}")
        for path, value in diff_json["dictionary_item_removed"].items():
            clean_path_str = clean_path(path)
            logger.info(f"  - {clean_path_str}: {value}")

    # Handle changed values
    if "values_changed" in diff_json:
        logger.info(f"{COLORS['OK_BLUE']}Variables with different values:{COLORS['RESET']}")
        for path, change in diff_json["values_changed"].items():
            clean_path_str = clean_path(path)
            old_val = change["old_value"]
            new_val = change["new_value"]
            logger.info(f"  ~ {clean_path_str}:")
            logger.info(f"    {device1}: {old_val}")
            logger.info(f"    {device2}: {new_val}")
