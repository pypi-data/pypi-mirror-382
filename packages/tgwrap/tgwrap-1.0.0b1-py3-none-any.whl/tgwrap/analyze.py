"""Customisable terraform analysis helpers inspired by Terrasafe."""

from __future__ import annotations

import fnmatch
import os
import re
from collections.abc import Iterable, Sequence

from .printer import Printer

# Type aliases for readability
ResourceChange = dict[str, dict[str, Sequence[str]]]


def run_analyze(config, data, ignore_attributes, verbose=False):
    """Return drift information and whether the plan is authorized."""
    printer = Printer(verbose)

    changes = {
        "drifts": {
            "minor": 0,
            "medium": 0,
            "major": 0,
            "unknown": 0,
            "total": 0,
        },
        "all": [],
        "creations": [],
        "updates": [],
        "deletions": [],
        "unauthorized": [],
        "unknowns": [],
    }

    ignored_from_env_var = parse_ignored_from_env_var()
    detected_changes = get_resource_actions(data)

    ignorable_updates: list[str] = []
    if config:
        ts_config = build_terrasafe_config(config)
        ignorable_updates = collect_ignorable_updates(
            detected_changes.get("updates", []),
            ignore_attributes,
        )
        unauthorized = find_unauthorized_deletions(
            deletions=detected_changes.get("deletions", []),
            ts_config=ts_config,
            ignored_from_env_var=ignored_from_env_var,
            printer=printer,
        )
        changes["unauthorized"] = unauthorized
        if unauthorized:
            printer.verbose("Unauthorized deletion detected for those resources:")
            for resource in unauthorized:
                printer.verbose(f" - {resource}")
            printer.verbose(
                "If you really want to delete those resources: comment it or export this "
                "environment variable:"
            )
            exports = ";".join(unauthorized)
            printer.verbose(f'export TERRASAFE_ALLOW_DELETION="{exports}"')

        dd_config = build_dd_config(config)
        detected_changes = apply_drift_counts(
            detected_changes=detected_changes,
            ignorable_updates=ignorable_updates,
            dd_config=dd_config,
            changes=changes,
        )

    # remove ballast from the following lists
    changes["all"] = [
        resource["address"]
        for resource in detected_changes.get("all", [])
        if "change" in resource
        and "actions" in resource["change"]
        and not {"no-op", "read"} & set(resource["change"]["actions"])
    ]
    changes["deletions"] = [
        resource["address"]
        for resource in detected_changes.get("deletions", [])
        if resource["address"] not in changes["unauthorized"]
    ]
    changes["creations"] = [
        resource["address"] for resource in detected_changes.get("creations", [])
    ]
    changes["updates"] = [
        resource["address"] for resource in detected_changes.get("updates", [])
    ]
    changes["ignorable_updates"] = ignorable_updates

    # see if there are output changes
    output_changes = get_output_changes(data)
    changes["outputs"] = []
    relevant_changes = {"create", "update", "delete"}
    for key, value in output_changes.items():
        if relevant_changes.intersection(value.get("actions", [])):
            changes["outputs"].append(key)

    return changes, not changes["unauthorized"]


def build_terrasafe_config(config) -> dict[str, list[str]]:
    """Return the terrasafe configuration grouped by severity level."""
    ts_default_levels = {
        "low": "ignore_deletion",
        "medium": "ignore_deletion_if_recreation",
        "high": "unauthorized_deletion",
    }
    ts_config: dict[str, list[str]] = {
        value: [] for value in ts_default_levels.values()
    }
    for criticality, ts_level in ts_default_levels.items():
        for key, item in config[criticality].items():
            level = item.get("terrasafe_level", ts_level)
            ts_config.setdefault(level, []).append(f"*{key}*")
    return ts_config


def collect_ignorable_updates(updates: Iterable[ResourceChange], ignore_attributes):
    """Return update addresses that only touch ignored attributes."""
    ignorable: list[str] = []
    for resource in updates:
        before = resource["change"].get("before", {}).copy()
        after = resource["change"].get("after", {}).copy()

        for attribute in ignore_attributes:
            before.pop(attribute, None)
            after.pop(attribute, None)

        if before == after:
            ignorable.append(resource["address"])
    return ignorable


def find_unauthorized_deletions(
    deletions: Iterable[ResourceChange],
    ts_config: dict[str, list[str]],
    ignored_from_env_var: Iterable[str],
    printer: Printer,
) -> list[str]:
    """Return the list of unauthorized deletions."""
    unauthorized: list[str] = []
    ignored_patterns = list(ignored_from_env_var)
    for resource in deletions:
        resource_address = resource["address"]

        if is_resource_match_any(
            resource_address, ts_config.get("unauthorized_deletion", [])
        ):
            printer.verbose(
                f"Resource {resource_address} cannot be destroyed for any reason"
            )
            unauthorized.append(resource_address)
            continue

        if _is_deletion_ignored(resource, ts_config, ignored_patterns, printer):
            continue

        unauthorized.append(resource_address)

    return unauthorized


def _is_deletion_ignored(resource, ts_config, ignored_from_env_var, printer):
    """Return True if deletion of resource is allowed by config or environment."""
    resource_address = resource["address"]
    if is_resource_match_any(resource_address, ts_config.get("ignore_deletion", [])):
        return True

    if is_resource_recreate(resource) and is_resource_match_any(
        resource_address,
        ts_config.get("ignore_deletion_if_recreation", []),
    ):
        return True

    if is_resource_match_any(resource_address, ignored_from_env_var):
        printer.verbose(f"deletion of {resource_address} authorized by env var.")
        return True

    if is_deletion_in_disabled_file(resource["type"], resource["name"]):
        printer.verbose(
            f"deletion of {resource_address} authorized by disabled file feature"
        )
        return True

    return False


def build_dd_config(config):
    """Return drift detection configuration expanded per resource."""
    dd_default_levels = {
        "low": {
            "default": "minor",
            "delete": "medium",
        },
        "medium": {
            "default": "medium",
            "delete": "major",
        },
        "high": {
            "default": "major",
            "update": "medium",
        },
    }
    dd_config = {}
    for criticality, settings in dd_default_levels.items():
        create = settings.get("create", settings.get("default"))
        update = settings.get("update", settings.get("default"))
        delete = settings.get("delete", settings.get("default"))

        for key, value in config[criticality].items():
            pattern = f"*{key}*"
            dd_config[pattern] = {
                "create": create,
                "update": update,
                "delete": delete,
            }
            if "drift_impact" in value:
                impacts = value["drift_impact"]
                dd_config[pattern] = {
                    "create": impacts.get("create", create),
                    "update": impacts.get("update", update),
                    "delete": impacts.get("delete", delete),
                }
    return dd_config


def apply_drift_counts(detected_changes, ignorable_updates, dd_config, changes):
    """Mutate drift counters based on detected changes and return updated changes list."""
    updated_changes = dict(detected_changes)
    mapping = {"deletions": "delete", "creations": "create", "updates": "update"}

    filtered_updates = []
    for key, action in mapping.items():
        for resource in detected_changes.get(key, []):
            resource_address = resource["address"]
            if key == "updates" and resource_address in ignorable_updates:
                continue

            has_match, resource_config = get_matching_dd_config(
                resource_address,
                dd_config,
            )
            if has_match:
                dd_class = resource_config[action]
                changes["drifts"][dd_class] += 1
            else:
                changes["drifts"]["unknown"] += 1
                if resource_address not in changes["unknowns"]:
                    changes["unknowns"].append(resource_address)

            changes["drifts"]["total"] += 1

            if key == "updates":
                filtered_updates.append(resource)

    if filtered_updates:
        updated_changes["updates"] = filtered_updates
    else:
        updated_changes["updates"] = []

    return updated_changes


def parse_ignored_from_env_var():
    """Return deletions explicitly authorised via TERRASAFE_ALLOW_DELETION."""
    ignored = os.environ.get("TERRASAFE_ALLOW_DELETION")
    if ignored:
        return [item.strip() for item in ignored.split(";") if item.strip()]
    return []


def get_resource_actions(data):
    """Return the resource change sets grouped by action."""
    if not data or "format_version" not in data:
        return {"all": [], "deletions": [], "creations": [], "updates": []}
    major = data["format_version"].split(".")[0]
    if major not in {"0", "1"}:
        raise ValueError("Only format major version 0 or 1 is supported")

    resource_changes = data.get("resource_changes", [])

    return {
        "all": resource_changes,
        "deletions": list(filter(has_delete_action, resource_changes)),
        "creations": list(filter(has_create_action, resource_changes)),
        "updates": list(filter(has_update_action, resource_changes)),
    }


def get_output_changes(data):
    """Return terraform output change set for supported versions."""
    if not data or "format_version" not in data:
        return {}
    major = data["format_version"].split(".")[0]
    if major not in {"0", "1"}:
        raise ValueError("Only format major version 0 or 1 is supported")

    return data.get("output_changes", {})


def has_delete_action(resource):
    """Return True when the resource contains a delete action."""
    return (
        "change" in resource
        and "actions" in resource["change"]
        and "delete" in resource["change"]["actions"]
    )


def has_create_action(resource):
    """Return True when the resource contains a create action."""
    return (
        "change" in resource
        and "actions" in resource["change"]
        and "create" in resource["change"]["actions"]
    )


def has_update_action(resource):
    """Return True when the resource contains an update action."""
    return (
        "change" in resource
        and "actions" in resource["change"]
        and "update" in resource["change"]["actions"]
    )


def is_resource_match_any(resource_address, pattern_list):
    """Return True if the resource address matches any of the provided patterns."""
    for pattern in pattern_list:
        escaped_pattern = re.sub(r"\[(.+?)\]", "[[]\\g<1>[]]", pattern)
        if fnmatch.fnmatch(resource_address, escaped_pattern):
            return True
    return False


def get_matching_dd_config(resource_address, dd_config):
    """Return the drift configuration entry matching the resource address."""
    for pattern, config in dd_config.items():
        escaped_pattern = re.sub(r"\[(.+?)\]", "[[]\\g<1>[]]", pattern)
        if fnmatch.fnmatch(resource_address, escaped_pattern):
            if isinstance(config, dict) and any(
                key in config for key in ("create", "update", "delete")
            ):
                return True, config
            return True, {"create": "minor", "update": "minor", "delete": "minor"}
    return False, None


# 1 \*databricks_dbfs_file* {'create': 'minor', 'update': 'minor', 'delete': 'minor'}
# 2 \*databricks_dbfs_file* module.dbx_ws_conf.databricks_dbfs_file.spark_jars["spark-listeners-loganalytics_3.1.1_2.12-1.0.0.jar"]


def is_resource_recreate(resource):
    """Return True when resource actions include a recreate (delete+create)."""
    if "change" in resource and "actions" in resource["change"]:
        actions = resource["change"]["actions"]
        return "create" in actions and "delete" in actions
    return False


def is_deletion_in_disabled_file(resource_type, resource_name):
    """Return True if the deletion is present inside a .tf.disabled file."""
    regex = re.compile(rf'\s*resource\s*"{resource_type}"\s*"{resource_name}"')
    tf_files = get_all_files(".tf.disabled")
    for filepath in tf_files:
        with open(filepath, encoding="utf-8") as file:
            for line in file:
                if regex.match(line):
                    return True
    return False


def get_all_files(extension):
    """Return all files in the current tree that match the provided extension."""
    matches = []
    for root, _, file_names in os.walk("."):
        for file_name in file_names:
            if fnmatch.fnmatch(file_name, "*" + extension):
                matches.append(os.path.join(root, file_name))
    return matches
