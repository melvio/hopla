"""
The module with CLI code that handles the `hopla get user-inventory` command.
"""

import logging

import click

from hopla.hoplalib.clickhelper import data_on_success_else_exit
from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.cli.groupcmds.get import HabiticaUserRequest, HabiticaUser

log = logging.getLogger()

valid_item_groups = click.Choice([
    "pets", "mounts", "eggs", "food", "hatchingPotions",
    "gear", "quests", "currentPet", "currentMount",
    "lastDrop", "all"
])


def inventory_alias_to_official_habitica_name(inventory_name: str):
    """Take an inventory_name argument and return the canonical Habitica item name"""
    # pylint: disable=too-many-return-statements
    if inventory_name in ["hatchingpotions", "hatchingPotion"]:
        return "hatchingPotions"
    if inventory_name in ["pet"]:
        return "pets"
    if inventory_name in ["mount"]:
        return "mounts"
    if inventory_name in ["currentpet"]:
        return "currentPet"
    if inventory_name in ["currentmount"]:
        return "currentMount"
    if inventory_name in ["lastdrop"]:
        return "lastDrop"

    return inventory_name


@click.command(
    context_settings=dict(token_normalize_func=inventory_alias_to_official_habitica_name)
)
@click.argument("item_group_name", type=valid_item_groups, default="all")
def user_inventory(item_group_name) -> dict:
    """Get items from the user's inventory

    If no specific item group is specified,

    \f
    :param item_group_name: The type of items in the inventory (default: all)
    :return: The specified inventory
    """
    log.debug(f"hopla get user-inventory item_group={item_group_name}")
    response = HabiticaUserRequest().request_user()
    response_data: dict = data_on_success_else_exit(response)
    habitica_user = HabiticaUser(user_dict=response_data)
    data_items = habitica_user.get_inventory()

    if item_group_name == "all":
        data_requested_by_user = data_items
    else:
        data_requested_by_user = data_items[item_group_name]
    click.echo(
        JsonFormatter(data_requested_by_user).format_with_double_quotes())
    return data_requested_by_user
