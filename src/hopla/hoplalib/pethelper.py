"""
A helper module for Pet logic.
"""
from hopla.hoplalib.clickhelper import PrintableException

from hopla.hoplalib.common import GlobalConstants


class InvalidPet(PrintableException):
    """Exception raised when a pet is invalid."""

    def __init__(self, msg: str, *, pet=None):
        super().__init__(msg)
        self.pet = pet


class Pet:
    """A habitica pet"""

    def __init__(self, pet_name: str, *, feeding_status: int = 0):
        if pet_name not in FeedingData.pet_names:
            raise InvalidPet(f"{pet_name=} is not recognized by hopla.\n"
                             "Potential causes: \n"
                             "* did you spell it correctly?\n"
                             "* Is your pet relatively new? If so, please raise\n"
                             f" an issue at {GlobalConstants.NEW_ISSUE_URL}")

        if (feeding_status < -1
                or feeding_status in [1, 2, 3, 4]  # every pet starts at 5
                or feeding_status >= 50):  # 50 would turn the pet into a mount
            raise InvalidPet(f"{feeding_status=} is invalid")

        self.pet_name = pet_name
        self.feeding_status = feeding_status

    def feeding_status_explanation(self) -> str:
        """Explain the feeding status of a pet"""
        if self.feeding_status == -1:
            return f"You can't feed {self.pet_name=} you only have the mount"

        if self.feeding_status == 5:
            # remark: if we really want to know more, we can query the
            #         API to check if we have the self.pet_name in the
            #         Users: jq .data.items.mounts
            return (f"Cannot determine if {self.pet_name=} can be fed. \n"
                    "You either have:\n"
                    "1. both the pet and mount: You cannot feed the pet \n"
                    "2. a pet that hasn't been fed but you don't have \n"
                    "   the mount: You can feed your pet")

        if self.feeding_status < 50:
            return f"{self.pet_name=} can be fed"

        raise InvalidPet(f"Did not expect {self.feeding_status=}. \n"
                         f"Looks like we failed to validate the Pet properly.",
                         pet=self)

    def feeding_status_to_percentage(self):
        """
        Turn feeding status into percentage understandable by the
        website user.
        https://habitica.fandom.com/wiki/Food_Preferences
        """
        if self.feeding_status == -1:
            return 100  # The pet is now a mount
        return self.feeding_status * 2

    def favorite_food(self, *, default_value_when_no_favorite_food: str = "any"):
        """Return the favorite food of this pet."""
        # This logic might break, but seems to be solid for past few years due to
        # stabling naming convention by the Habitica API developers.
        _, potion = self.pet_name.split("-")
        return (FeedingData.hatching_potion_favorite_food_mapping
                .get(potion, default=default_value_when_no_favorite_food))


class FeedingData:
    """Class with valid food and pet names"""
    # Didn't include cakes because those are rare collectibles
    # for more info @see:
    #    hopla api content | jq .food
    #    hopla api content | jq '.food[] | select(.canDrop==true)'
    #    hopla api content | jq '[.food[] | select(.canDrop==true) | .key]'
    normal_food_names = [
        "Meat", "Milk", "Potatoe", "Strawberry", "Chocolate", "Fish", "RottenMeat",
        "CottonCandyPink", "CottonCandyBlue", "Honey"
    ]

    hatching_potion_favorite_food_mapping = {
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
    """

    # @see: hopla api content | jq '[.petInfo[] | .key]'
    pet_names = [
        "Wolf-Base", "Wolf-White", "Wolf-Desert", "Wolf-Red", "Wolf-Shade", "Wolf-Skeleton",
        "Wolf-Zombie", "Wolf-CottonCandyPink", "Wolf-CottonCandyBlue", "Wolf-Golden",
        "TigerCub-Base", "TigerCub-White", "TigerCub-Desert", "TigerCub-Red", "TigerCub-Shade",
        "TigerCub-Skeleton", "TigerCub-Zombie", "TigerCub-CottonCandyPink",
        "TigerCub-CottonCandyBlue", "TigerCub-Golden", "PandaCub-Base", "PandaCub-White",
        "PandaCub-Desert", "PandaCub-Red", "PandaCub-Shade", "PandaCub-Skeleton",
        "PandaCub-Zombie", "PandaCub-CottonCandyPink", "PandaCub-CottonCandyBlue",
        "PandaCub-Golden", "LionCub-Base", "LionCub-White", "LionCub-Desert", "LionCub-Red",
        "LionCub-Shade", "LionCub-Skeleton", "LionCub-Zombie", "LionCub-CottonCandyPink",
        "LionCub-CottonCandyBlue", "LionCub-Golden", "Fox-Base", "Fox-White", "Fox-Desert",
        "Fox-Red", "Fox-Shade", "Fox-Skeleton", "Fox-Zombie", "Fox-CottonCandyPink",
        "Fox-CottonCandyBlue", "Fox-Golden", "FlyingPig-Base", "FlyingPig-White",
        "FlyingPig-Desert", "FlyingPig-Red", "FlyingPig-Shade", "FlyingPig-Skeleton",
        "FlyingPig-Zombie", "FlyingPig-CottonCandyPink", "FlyingPig-CottonCandyBlue",
        "FlyingPig-Golden", "Dragon-Base", "Dragon-White", "Dragon-Desert", "Dragon-Red",
        "Dragon-Shade", "Dragon-Skeleton", "Dragon-Zombie", "Dragon-CottonCandyPink",
        "Dragon-CottonCandyBlue", "Dragon-Golden", "Cactus-Base", "Cactus-White", "Cactus-Desert",
        "Cactus-Red", "Cactus-Shade", "Cactus-Skeleton", "Cactus-Zombie", "Cactus-CottonCandyPink",
        "Cactus-CottonCandyBlue", "Cactus-Golden", "BearCub-Base", "BearCub-White",
        "BearCub-Desert", "BearCub-Red", "BearCub-Shade", "BearCub-Skeleton", "BearCub-Zombie",
        "BearCub-CottonCandyPink", "BearCub-CottonCandyBlue", "BearCub-Golden", "Wolf-RoyalPurple",
        "Wolf-Cupid", "Wolf-Shimmer", "Wolf-Fairy", "Wolf-Floral", "Wolf-Aquatic", "Wolf-Ember",
        "Wolf-Thunderstorm", "Wolf-Spooky", "Wolf-Ghost", "Wolf-Holly", "Wolf-Peppermint",
        "Wolf-StarryNight", "Wolf-Rainbow", "Wolf-Glass", "Wolf-Glow", "Wolf-Frost",
        "Wolf-IcySnow", "Wolf-RoseQuartz", "Wolf-Celestial", "Wolf-Sunshine", "Wolf-Bronze",
        "Wolf-Watery", "Wolf-Silver", "Wolf-Shadow", "Wolf-Amber", "Wolf-Aurora", "Wolf-Ruby",
        "Wolf-BirchBark", "Wolf-Fluorite", "Wolf-SandSculpture", "Wolf-Windup", "Wolf-Turquoise",
        "Wolf-Vampire", "Wolf-AutumnLeaf", "Wolf-BlackPearl", "Wolf-StainedGlass", "Wolf-PolkaDot",
        "Wolf-MossyStone", "Wolf-Sunset", "Wolf-Moonglow", "Wolf-SolarSystem",
        "TigerCub-RoyalPurple", "TigerCub-Cupid", "TigerCub-Shimmer", "TigerCub-Fairy",
        "TigerCub-Floral", "TigerCub-Aquatic", "TigerCub-Ember", "TigerCub-Thunderstorm",
        "TigerCub-Spooky", "TigerCub-Ghost", "TigerCub-Holly", "TigerCub-Peppermint",
        "TigerCub-StarryNight", "TigerCub-Rainbow", "TigerCub-Glass", "TigerCub-Glow",
        "TigerCub-Frost", "TigerCub-IcySnow", "TigerCub-RoseQuartz", "TigerCub-Celestial",
        "TigerCub-Sunshine", "TigerCub-Bronze", "TigerCub-Watery", "TigerCub-Silver",
        "TigerCub-Shadow", "TigerCub-Amber", "TigerCub-Aurora", "TigerCub-Ruby",
        "TigerCub-BirchBark", "TigerCub-Fluorite", "TigerCub-SandSculpture", "TigerCub-Windup",
        "TigerCub-Turquoise", "TigerCub-Vampire", "TigerCub-AutumnLeaf", "TigerCub-BlackPearl",
        "TigerCub-StainedGlass", "TigerCub-PolkaDot", "TigerCub-MossyStone", "TigerCub-Sunset",
        "TigerCub-Moonglow", "TigerCub-SolarSystem", "PandaCub-RoyalPurple", "PandaCub-Cupid",
        "PandaCub-Shimmer", "PandaCub-Fairy", "PandaCub-Floral", "PandaCub-Aquatic",
        "PandaCub-Ember", "PandaCub-Thunderstorm", "PandaCub-Spooky", "PandaCub-Ghost",
        "PandaCub-Holly", "PandaCub-Peppermint", "PandaCub-StarryNight", "PandaCub-Rainbow",
        "PandaCub-Glass", "PandaCub-Glow", "PandaCub-Frost", "PandaCub-IcySnow",
        "PandaCub-RoseQuartz", "PandaCub-Celestial", "PandaCub-Sunshine", "PandaCub-Bronze",
        "PandaCub-Watery", "PandaCub-Silver", "PandaCub-Shadow", "PandaCub-Amber",
        "PandaCub-Aurora", "PandaCub-Ruby", "PandaCub-BirchBark", "PandaCub-Fluorite",
        "PandaCub-SandSculpture", "PandaCub-Windup", "PandaCub-Turquoise", "PandaCub-Vampire",
        "PandaCub-AutumnLeaf", "PandaCub-BlackPearl", "PandaCub-StainedGlass", "PandaCub-PolkaDot",
        "PandaCub-MossyStone", "PandaCub-Sunset", "PandaCub-Moonglow", "PandaCub-SolarSystem",
        "LionCub-RoyalPurple", "LionCub-Cupid", "LionCub-Shimmer", "LionCub-Fairy",
        "LionCub-Floral", "LionCub-Aquatic", "LionCub-Ember", "LionCub-Thunderstorm",
        "LionCub-Spooky", "LionCub-Ghost", "LionCub-Holly", "LionCub-Peppermint",
        "LionCub-StarryNight", "LionCub-Rainbow", "LionCub-Glass", "LionCub-Glow", "LionCub-Frost",
        "LionCub-IcySnow", "LionCub-RoseQuartz", "LionCub-Celestial", "LionCub-Sunshine",
        "LionCub-Bronze", "LionCub-Watery", "LionCub-Silver", "LionCub-Shadow", "LionCub-Amber",
        "LionCub-Aurora", "LionCub-Ruby", "LionCub-BirchBark", "LionCub-Fluorite",
        "LionCub-SandSculpture", "LionCub-Windup", "LionCub-Turquoise", "LionCub-Vampire",
        "LionCub-AutumnLeaf", "LionCub-BlackPearl", "LionCub-StainedGlass", "LionCub-PolkaDot",
        "LionCub-MossyStone", "LionCub-Sunset", "LionCub-Moonglow", "LionCub-SolarSystem",
        "Fox-RoyalPurple", "Fox-Cupid", "Fox-Shimmer", "Fox-Fairy", "Fox-Floral", "Fox-Aquatic",
        "Fox-Ember", "Fox-Thunderstorm", "Fox-Spooky", "Fox-Ghost", "Fox-Holly", "Fox-Peppermint",
        "Fox-StarryNight", "Fox-Rainbow", "Fox-Glass", "Fox-Glow", "Fox-Frost", "Fox-IcySnow",
        "Fox-RoseQuartz", "Fox-Celestial", "Fox-Sunshine", "Fox-Bronze", "Fox-Watery",
        "Fox-Silver", "Fox-Shadow", "Fox-Amber", "Fox-Aurora", "Fox-Ruby", "Fox-BirchBark",
        "Fox-Fluorite", "Fox-SandSculpture", "Fox-Windup", "Fox-Turquoise", "Fox-Vampire",
        "Fox-AutumnLeaf", "Fox-BlackPearl", "Fox-StainedGlass", "Fox-PolkaDot", "Fox-MossyStone",
        "Fox-Sunset", "Fox-Moonglow", "Fox-SolarSystem", "FlyingPig-RoyalPurple",
        "FlyingPig-Cupid", "FlyingPig-Shimmer", "FlyingPig-Fairy", "FlyingPig-Floral",
        "FlyingPig-Aquatic", "FlyingPig-Ember", "FlyingPig-Thunderstorm", "FlyingPig-Spooky",
        "FlyingPig-Ghost", "FlyingPig-Holly", "FlyingPig-Peppermint", "FlyingPig-StarryNight",
        "FlyingPig-Rainbow", "FlyingPig-Glass", "FlyingPig-Glow", "FlyingPig-Frost",
        "FlyingPig-IcySnow", "FlyingPig-RoseQuartz", "FlyingPig-Celestial", "FlyingPig-Sunshine",
        "FlyingPig-Bronze", "FlyingPig-Watery", "FlyingPig-Silver", "FlyingPig-Shadow",
        "FlyingPig-Amber", "FlyingPig-Aurora", "FlyingPig-Ruby", "FlyingPig-BirchBark",
        "FlyingPig-Fluorite", "FlyingPig-SandSculpture", "FlyingPig-Windup", "FlyingPig-Turquoise",
        "FlyingPig-Vampire", "FlyingPig-AutumnLeaf", "FlyingPig-BlackPearl",
        "FlyingPig-StainedGlass", "FlyingPig-PolkaDot", "FlyingPig-MossyStone", "FlyingPig-Sunset",
        "FlyingPig-Moonglow", "FlyingPig-SolarSystem", "Dragon-RoyalPurple", "Dragon-Cupid",
        "Dragon-Shimmer", "Dragon-Fairy", "Dragon-Floral", "Dragon-Aquatic", "Dragon-Ember",
        "Dragon-Thunderstorm", "Dragon-Spooky", "Dragon-Ghost", "Dragon-Holly",
        "Dragon-Peppermint", "Dragon-StarryNight", "Dragon-Rainbow", "Dragon-Glass", "Dragon-Glow",
        "Dragon-Frost", "Dragon-IcySnow", "Dragon-RoseQuartz", "Dragon-Celestial",
        "Dragon-Sunshine", "Dragon-Bronze", "Dragon-Watery", "Dragon-Silver", "Dragon-Shadow",
        "Dragon-Amber", "Dragon-Aurora", "Dragon-Ruby", "Dragon-BirchBark", "Dragon-Fluorite",
        "Dragon-SandSculpture", "Dragon-Windup", "Dragon-Turquoise", "Dragon-Vampire",
        "Dragon-AutumnLeaf", "Dragon-BlackPearl", "Dragon-StainedGlass", "Dragon-PolkaDot",
        "Dragon-MossyStone", "Dragon-Sunset", "Dragon-Moonglow", "Dragon-SolarSystem",
        "Cactus-RoyalPurple", "Cactus-Cupid", "Cactus-Shimmer", "Cactus-Fairy", "Cactus-Floral",
        "Cactus-Aquatic", "Cactus-Ember", "Cactus-Thunderstorm", "Cactus-Spooky", "Cactus-Ghost",
        "Cactus-Holly", "Cactus-Peppermint", "Cactus-StarryNight", "Cactus-Rainbow",
        "Cactus-Glass", "Cactus-Glow", "Cactus-Frost", "Cactus-IcySnow", "Cactus-RoseQuartz",
        "Cactus-Celestial", "Cactus-Sunshine", "Cactus-Bronze", "Cactus-Watery", "Cactus-Silver",
        "Cactus-Shadow", "Cactus-Amber", "Cactus-Aurora", "Cactus-Ruby", "Cactus-BirchBark",
        "Cactus-Fluorite", "Cactus-SandSculpture", "Cactus-Windup", "Cactus-Turquoise",
        "Cactus-Vampire", "Cactus-AutumnLeaf", "Cactus-BlackPearl", "Cactus-StainedGlass",
        "Cactus-PolkaDot", "Cactus-MossyStone", "Cactus-Sunset", "Cactus-Moonglow",
        "Cactus-SolarSystem", "BearCub-RoyalPurple", "BearCub-Cupid", "BearCub-Shimmer",
        "BearCub-Fairy", "BearCub-Floral", "BearCub-Aquatic", "BearCub-Ember",
        "BearCub-Thunderstorm", "BearCub-Spooky", "BearCub-Ghost", "BearCub-Holly",
        "BearCub-Peppermint", "BearCub-StarryNight", "BearCub-Rainbow", "BearCub-Glass",
        "BearCub-Glow", "BearCub-Frost", "BearCub-IcySnow", "BearCub-RoseQuartz",
        "BearCub-Celestial", "BearCub-Sunshine", "BearCub-Bronze", "BearCub-Watery",
        "BearCub-Silver", "BearCub-Shadow", "BearCub-Amber", "BearCub-Aurora", "BearCub-Ruby",
        "BearCub-BirchBark", "BearCub-Fluorite", "BearCub-SandSculpture", "BearCub-Windup",
        "BearCub-Turquoise", "BearCub-Vampire", "BearCub-AutumnLeaf", "BearCub-BlackPearl",
        "BearCub-StainedGlass", "BearCub-PolkaDot", "BearCub-MossyStone", "BearCub-Sunset",
        "BearCub-Moonglow", "BearCub-SolarSystem", "Gryphon-Base", "Gryphon-White",
        "Gryphon-Desert", "Gryphon-Red", "Gryphon-Shade", "Gryphon-Skeleton", "Gryphon-Zombie",
        "Gryphon-CottonCandyPink", "Gryphon-CottonCandyBlue", "Gryphon-Golden", "Hedgehog-Base",
        "Hedgehog-White", "Hedgehog-Desert", "Hedgehog-Red", "Hedgehog-Shade", "Hedgehog-Skeleton",
        "Hedgehog-Zombie", "Hedgehog-CottonCandyPink", "Hedgehog-CottonCandyBlue",
        "Hedgehog-Golden", "Deer-Base", "Deer-White", "Deer-Desert", "Deer-Red", "Deer-Shade",
        "Deer-Skeleton", "Deer-Zombie", "Deer-CottonCandyPink", "Deer-CottonCandyBlue",
        "Deer-Golden", "Egg-Base", "Egg-White", "Egg-Desert", "Egg-Red", "Egg-Shade",
        "Egg-Skeleton", "Egg-Zombie", "Egg-CottonCandyPink", "Egg-CottonCandyBlue", "Egg-Golden",
        "Rat-Base", "Rat-White", "Rat-Desert", "Rat-Red", "Rat-Shade", "Rat-Skeleton",
        "Rat-Zombie", "Rat-CottonCandyPink", "Rat-CottonCandyBlue", "Rat-Golden", "Octopus-Base",
        "Octopus-White", "Octopus-Desert", "Octopus-Red", "Octopus-Shade", "Octopus-Skeleton",
        "Octopus-Zombie", "Octopus-CottonCandyPink", "Octopus-CottonCandyBlue", "Octopus-Golden",
        "Seahorse-Base", "Seahorse-White", "Seahorse-Desert", "Seahorse-Red", "Seahorse-Shade",
        "Seahorse-Skeleton", "Seahorse-Zombie", "Seahorse-CottonCandyPink",
        "Seahorse-CottonCandyBlue", "Seahorse-Golden", "Parrot-Base", "Parrot-White",
        "Parrot-Desert", "Parrot-Red", "Parrot-Shade", "Parrot-Skeleton", "Parrot-Zombie",
        "Parrot-CottonCandyPink", "Parrot-CottonCandyBlue", "Parrot-Golden", "Rooster-Base",
        "Rooster-White", "Rooster-Desert", "Rooster-Red", "Rooster-Shade", "Rooster-Skeleton",
        "Rooster-Zombie", "Rooster-CottonCandyPink", "Rooster-CottonCandyBlue", "Rooster-Golden",
        "Spider-Base", "Spider-White", "Spider-Desert", "Spider-Red", "Spider-Shade",
        "Spider-Skeleton", "Spider-Zombie", "Spider-CottonCandyPink", "Spider-CottonCandyBlue",
        "Spider-Golden", "Owl-Base", "Owl-White", "Owl-Desert", "Owl-Red", "Owl-Shade",
        "Owl-Skeleton", "Owl-Zombie", "Owl-CottonCandyPink", "Owl-CottonCandyBlue", "Owl-Golden",
        "Penguin-Base", "Penguin-White", "Penguin-Desert", "Penguin-Red", "Penguin-Shade",
        "Penguin-Skeleton", "Penguin-Zombie", "Penguin-CottonCandyPink", "Penguin-CottonCandyBlue",
        "Penguin-Golden", "TRex-Base", "TRex-White", "TRex-Desert", "TRex-Red", "TRex-Shade",
        "TRex-Skeleton", "TRex-Zombie", "TRex-CottonCandyPink", "TRex-CottonCandyBlue",
        "TRex-Golden", "Rock-Base", "Rock-White", "Rock-Desert", "Rock-Red", "Rock-Shade",
        "Rock-Skeleton", "Rock-Zombie", "Rock-CottonCandyPink", "Rock-CottonCandyBlue",
        "Rock-Golden", "Bunny-Base", "Bunny-White", "Bunny-Desert", "Bunny-Red", "Bunny-Shade",
        "Bunny-Skeleton", "Bunny-Zombie", "Bunny-CottonCandyPink", "Bunny-CottonCandyBlue",
        "Bunny-Golden", "Slime-Base", "Slime-White", "Slime-Desert", "Slime-Red", "Slime-Shade",
        "Slime-Skeleton", "Slime-Zombie", "Slime-CottonCandyPink", "Slime-CottonCandyBlue",
        "Slime-Golden", "Sheep-Base", "Sheep-White", "Sheep-Desert", "Sheep-Red", "Sheep-Shade",
        "Sheep-Skeleton", "Sheep-Zombie", "Sheep-CottonCandyPink", "Sheep-CottonCandyBlue",
        "Sheep-Golden", "Cuttlefish-Base", "Cuttlefish-White", "Cuttlefish-Desert",
        "Cuttlefish-Red", "Cuttlefish-Shade", "Cuttlefish-Skeleton", "Cuttlefish-Zombie",
        "Cuttlefish-CottonCandyPink", "Cuttlefish-CottonCandyBlue", "Cuttlefish-Golden",
        "Whale-Base", "Whale-White", "Whale-Desert", "Whale-Red", "Whale-Shade", "Whale-Skeleton",
        "Whale-Zombie", "Whale-CottonCandyPink", "Whale-CottonCandyBlue", "Whale-Golden",
        "Cheetah-Base", "Cheetah-White", "Cheetah-Desert", "Cheetah-Red", "Cheetah-Shade",
        "Cheetah-Skeleton", "Cheetah-Zombie", "Cheetah-CottonCandyPink", "Cheetah-CottonCandyBlue",
        "Cheetah-Golden", "Horse-Base", "Horse-White", "Horse-Desert", "Horse-Red", "Horse-Shade",
        "Horse-Skeleton", "Horse-Zombie", "Horse-CottonCandyPink", "Horse-CottonCandyBlue",
        "Horse-Golden", "Frog-Base", "Frog-White", "Frog-Desert", "Frog-Red", "Frog-Shade",
        "Frog-Skeleton", "Frog-Zombie", "Frog-CottonCandyPink", "Frog-CottonCandyBlue",
        "Frog-Golden", "Snake-Base", "Snake-White", "Snake-Desert", "Snake-Red", "Snake-Shade",
        "Snake-Skeleton", "Snake-Zombie", "Snake-CottonCandyPink", "Snake-CottonCandyBlue",
        "Snake-Golden", "Unicorn-Base", "Unicorn-White", "Unicorn-Desert", "Unicorn-Red",
        "Unicorn-Shade", "Unicorn-Skeleton", "Unicorn-Zombie", "Unicorn-CottonCandyPink",
        "Unicorn-CottonCandyBlue", "Unicorn-Golden", "Sabretooth-Base", "Sabretooth-White",
        "Sabretooth-Desert", "Sabretooth-Red", "Sabretooth-Shade", "Sabretooth-Skeleton",
        "Sabretooth-Zombie", "Sabretooth-CottonCandyPink", "Sabretooth-CottonCandyBlue",
        "Sabretooth-Golden", "Monkey-Base", "Monkey-White", "Monkey-Desert", "Monkey-Red",
        "Monkey-Shade", "Monkey-Skeleton", "Monkey-Zombie", "Monkey-CottonCandyPink",
        "Monkey-CottonCandyBlue", "Monkey-Golden", "Snail-Base", "Snail-White", "Snail-Desert",
        "Snail-Red", "Snail-Shade", "Snail-Skeleton", "Snail-Zombie", "Snail-CottonCandyPink",
        "Snail-CottonCandyBlue", "Snail-Golden", "Falcon-Base", "Falcon-White", "Falcon-Desert",
        "Falcon-Red", "Falcon-Shade", "Falcon-Skeleton", "Falcon-Zombie", "Falcon-CottonCandyPink",
        "Falcon-CottonCandyBlue", "Falcon-Golden", "Treeling-Base", "Treeling-White",
        "Treeling-Desert", "Treeling-Red", "Treeling-Shade", "Treeling-Skeleton",
        "Treeling-Zombie", "Treeling-CottonCandyPink", "Treeling-CottonCandyBlue",
        "Treeling-Golden", "Axolotl-Base", "Axolotl-White", "Axolotl-Desert", "Axolotl-Red",
        "Axolotl-Shade", "Axolotl-Skeleton", "Axolotl-Zombie", "Axolotl-CottonCandyPink",
        "Axolotl-CottonCandyBlue", "Axolotl-Golden", "Turtle-Base", "Turtle-White",
        "Turtle-Desert", "Turtle-Red", "Turtle-Shade", "Turtle-Skeleton", "Turtle-Zombie",
        "Turtle-CottonCandyPink", "Turtle-CottonCandyBlue", "Turtle-Golden", "Armadillo-Base",
        "Armadillo-White", "Armadillo-Desert", "Armadillo-Red", "Armadillo-Shade",
        "Armadillo-Skeleton", "Armadillo-Zombie", "Armadillo-CottonCandyPink",
        "Armadillo-CottonCandyBlue", "Armadillo-Golden", "Cow-Base", "Cow-White", "Cow-Desert",
        "Cow-Red", "Cow-Shade", "Cow-Skeleton", "Cow-Zombie", "Cow-CottonCandyPink",
        "Cow-CottonCandyBlue", "Cow-Golden", "Beetle-Base", "Beetle-White", "Beetle-Desert",
        "Beetle-Red", "Beetle-Shade", "Beetle-Skeleton", "Beetle-Zombie", "Beetle-CottonCandyPink",
        "Beetle-CottonCandyBlue", "Beetle-Golden", "Ferret-Base", "Ferret-White", "Ferret-Desert",
        "Ferret-Red", "Ferret-Shade", "Ferret-Skeleton", "Ferret-Zombie", "Ferret-CottonCandyPink",
        "Ferret-CottonCandyBlue", "Ferret-Golden", "Sloth-Base", "Sloth-White", "Sloth-Desert",
        "Sloth-Red", "Sloth-Shade", "Sloth-Skeleton", "Sloth-Zombie", "Sloth-CottonCandyPink",
        "Sloth-CottonCandyBlue", "Sloth-Golden", "Triceratops-Base", "Triceratops-White",
        "Triceratops-Desert", "Triceratops-Red", "Triceratops-Shade", "Triceratops-Skeleton",
        "Triceratops-Zombie", "Triceratops-CottonCandyPink", "Triceratops-CottonCandyBlue",
        "Triceratops-Golden", "GuineaPig-Base", "GuineaPig-White", "GuineaPig-Desert",
        "GuineaPig-Red", "GuineaPig-Shade", "GuineaPig-Skeleton", "GuineaPig-Zombie",
        "GuineaPig-CottonCandyPink", "GuineaPig-CottonCandyBlue", "GuineaPig-Golden",
        "Peacock-Base", "Peacock-White", "Peacock-Desert", "Peacock-Red", "Peacock-Shade",
        "Peacock-Skeleton", "Peacock-Zombie", "Peacock-CottonCandyPink", "Peacock-CottonCandyBlue",
        "Peacock-Golden", "Butterfly-Base", "Butterfly-White", "Butterfly-Desert", "Butterfly-Red",
        "Butterfly-Shade", "Butterfly-Skeleton", "Butterfly-Zombie", "Butterfly-CottonCandyPink",
        "Butterfly-CottonCandyBlue", "Butterfly-Golden", "Nudibranch-Base", "Nudibranch-White",
        "Nudibranch-Desert", "Nudibranch-Red", "Nudibranch-Shade", "Nudibranch-Skeleton",
        "Nudibranch-Zombie", "Nudibranch-CottonCandyPink", "Nudibranch-CottonCandyBlue",
        "Nudibranch-Golden", "Hippo-Base", "Hippo-White", "Hippo-Desert", "Hippo-Red",
        "Hippo-Shade", "Hippo-Skeleton", "Hippo-Zombie", "Hippo-CottonCandyPink",
        "Hippo-CottonCandyBlue", "Hippo-Golden", "Yarn-Base", "Yarn-White", "Yarn-Desert",
        "Yarn-Red", "Yarn-Shade", "Yarn-Skeleton", "Yarn-Zombie", "Yarn-CottonCandyPink",
        "Yarn-CottonCandyBlue", "Yarn-Golden", "Pterodactyl-Base", "Pterodactyl-White",
        "Pterodactyl-Desert", "Pterodactyl-Red", "Pterodactyl-Shade", "Pterodactyl-Skeleton",
        "Pterodactyl-Zombie", "Pterodactyl-CottonCandyPink", "Pterodactyl-CottonCandyBlue",
        "Pterodactyl-Golden", "Badger-Base", "Badger-White", "Badger-Desert", "Badger-Red",
        "Badger-Shade", "Badger-Skeleton", "Badger-Zombie", "Badger-CottonCandyPink",
        "Badger-CottonCandyBlue", "Badger-Golden", "Squirrel-Base", "Squirrel-White",
        "Squirrel-Desert", "Squirrel-Red", "Squirrel-Shade", "Squirrel-Skeleton",
        "Squirrel-Zombie", "Squirrel-CottonCandyPink", "Squirrel-CottonCandyBlue",
        "Squirrel-Golden", "SeaSerpent-Base", "SeaSerpent-White", "SeaSerpent-Desert",
        "SeaSerpent-Red", "SeaSerpent-Shade", "SeaSerpent-Skeleton", "SeaSerpent-Zombie",
        "SeaSerpent-CottonCandyPink", "SeaSerpent-CottonCandyBlue", "SeaSerpent-Golden",
        "Kangaroo-Base", "Kangaroo-White", "Kangaroo-Desert", "Kangaroo-Red", "Kangaroo-Shade",
        "Kangaroo-Skeleton", "Kangaroo-Zombie", "Kangaroo-CottonCandyPink",
        "Kangaroo-CottonCandyBlue", "Kangaroo-Golden", "Alligator-Base", "Alligator-White",
        "Alligator-Desert", "Alligator-Red", "Alligator-Shade", "Alligator-Skeleton",
        "Alligator-Zombie", "Alligator-CottonCandyPink", "Alligator-CottonCandyBlue",
        "Alligator-Golden", "Velociraptor-Base", "Velociraptor-White", "Velociraptor-Desert",
        "Velociraptor-Red", "Velociraptor-Shade", "Velociraptor-Skeleton", "Velociraptor-Zombie",
        "Velociraptor-CottonCandyPink", "Velociraptor-CottonCandyBlue", "Velociraptor-Golden",
        "Dolphin-Base", "Dolphin-White", "Dolphin-Desert", "Dolphin-Red", "Dolphin-Shade",
        "Dolphin-Skeleton", "Dolphin-Zombie", "Dolphin-CottonCandyPink", "Dolphin-CottonCandyBlue",
        "Dolphin-Golden", "Robot-Base", "Robot-White", "Robot-Desert", "Robot-Red", "Robot-Shade",
        "Robot-Skeleton", "Robot-Zombie", "Robot-CottonCandyPink", "Robot-CottonCandyBlue",
        "Robot-Golden", "Wolf-Veggie", "Wolf-Dessert", "TigerCub-Veggie", "TigerCub-Dessert",
        "PandaCub-Veggie", "PandaCub-Dessert", "LionCub-Veggie", "LionCub-Dessert", "Fox-Veggie",
        "Fox-Dessert", "FlyingPig-Veggie", "FlyingPig-Dessert", "Dragon-Veggie", "Dragon-Dessert",
        "Cactus-Veggie", "Cactus-Dessert", "BearCub-Veggie", "BearCub-Dessert", "Wolf-Veteran",
        "Wolf-Cerberus", "Dragon-Hydra", "Turkey-Base", "BearCub-Polar", "MantisShrimp-Base",
        "JackOLantern-Base", "Mammoth-Base", "Tiger-Veteran", "Phoenix-Base", "Turkey-Gilded",
        "MagicalBee-Base", "Lion-Veteran", "Gryphon-RoyalPurple", "JackOLantern-Ghost",
        "Jackalope-RoyalPurple", "Orca-Base", "Bear-Veteran", "Hippogriff-Hopeful", "Fox-Veteran",
        "JackOLantern-Glow", "Gryphon-Gryphatrice", "JackOLantern-RoyalPurple"
    ]
