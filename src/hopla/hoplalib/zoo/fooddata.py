"""
Module with data about Habitica food information.
"""


class FoodData:
    """
    Helper class with valid Habitica food and drop hatching potions and
    the relationship between them.
    """

    hatch_potion_favorite_food_mapping = {
        "Base": "Meat",
        "White": "Milk",
        "Desert": "Potatoe",
        "Red": "Strawberry",
        "Shade": "Chocolate",
        "Skeleton": "Fish",
        "Zombie": "RottenMeat",
        "CottonCandyPink": "CottonCandyPink",
        "CottonCandyBlue": "CottonCandyBlue",
        "Golden": "Honey"
    }
    """
    Note: Pets hatched with magic hatching potions prefer any type of food.
    These pets are not supported by this dict.
    Rare favorite foods are also not supported such as Cake, Candy, and Pie.

    @see:
    * <https://habitica.fandom.com/wiki/Food_Preferences>
    * hopla api content | jq .dropHatchingPotions
    * hopla api content | jq .dropEggs

    also interesting:
    * hopla api content | jq .questEggs
    * hopla api content | jq .hatchingPotions
    * hopla api content | jq .premiumHatchingPotions
    * hopla api content | jq. wackyHatchingPotions
    """

    drop_food_names = list(hatch_potion_favorite_food_mapping.values())
    """A list of food items that can be dropped by doing tasks.

    These dont include cakes etc., those are rare collectibles.

    # for more info @see:
    #    hopla api content | jq .food
    #    hopla api content | jq '.food[] | select(.canDrop==true)'
    #    hopla api content | jq '[.food[] | select(.canDrop==true) | .key]'
    """
