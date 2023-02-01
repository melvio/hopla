"""
The module with CLI code that handles the `hopla get-user inventory` command.
"""

import logging

import click

from hopla.hoplalib.outputformatter import JsonFormatter
from hopla.cli.groupcmds.get_user import pass_user, HabiticaUser

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
    context_settings={"token_normalize_func": inventory_alias_to_official_habitica_name}
)
@click.argument("item_group_name", type=valid_item_groups, default="all")
@pass_user
def inventory(user: HabiticaUser, item_group_name: str) -> dict:
    """Get items from the user's inventory

    Get all items if no specific item group is specified.

    \f
    :param user:
    :param item_group_name: The type of items in the inventory (default: all)
    :return: The specified inventory
    """
    log.debug(f"hopla get-user inventory item_group={item_group_name}")

    data_items = user.get_inventory()
    if item_group_name == "all":
        requested_user_data = data_items
    else:
        requested_user_data = data_items[item_group_name]
    click.echo(JsonFormatter(requested_user_data).format_with_double_quotes())
    return requested_user_data
