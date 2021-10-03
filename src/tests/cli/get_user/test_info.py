from hopla.cli.get_user.info import filter_on_user_info_name
from hopla.cli.groupcmds.get_user import HabiticaUser


class TestPrefilterOnUserInfo:
    def test_all_returns_user_unchanged(self):
        test_user: HabiticaUser = get_test_user()

        filter_result = filter_on_user_info_name(test_user, "all")

        assert filter_result == test_user.user_dict

    def test_gems_return_gems(self):
        balance = 2
        test_user = HabiticaUser({"balance": balance})

        filter_result = filter_on_user_info_name(test_user, "gems")

        expected_gems = balance * 4
        assert filter_result == expected_gems
        assert type(expected_gems) is int

    def test_id_returns_id(self):
        test_user: HabiticaUser = get_test_user()

        filter_result = filter_on_user_info_name(test_user, "id")

        expected_id = test_user["id"]
        assert filter_result == expected_id
        assert type(filter_result) is str

    def test_guilds_returns_list(self):
        test_user: HabiticaUser = get_test_user()

        filter_result = filter_on_user_info_name(test_user, "guilds")

        expected_guilds = test_user["guilds"]
        assert filter_result == expected_guilds
        assert type(filter_result) == list

    def test_tags_returns_list_of_objects(self):
        test_user: HabiticaUser = get_test_user()

        filter_result = filter_on_user_info_name(test_user, "tags")

        expected_tags = test_user["tags"]
        assert filter_result == expected_tags
        assert type(filter_result) == list


def get_test_user() -> HabiticaUser:
    """
    This user dict has been edited as follows:
    * All ids have been changed completely, only their syntax is intact
    * All dates have been changed (most to the future)
    * long lists have been cut down significantly to remove the duplication
      of data that is largely similar in syntax (.g. finished quests).
      The was to keep the original range of data intact (e.g. at least
      keep a large value, negative value, and default value for feed
      status of pets. e.g. within 'history' dates came in multiple formats,
      (millis and iso dates) so both formats were kept).
    * care was taken to not modify the underlying structure and
      realisticness of the data. However, the data is note entirely valid
      because e.g. available eggs don't match finished quests. Sort order
      ids dont match actual ids or do not exist, etc.
    * null from javascript were replaced with "null" strings
    * unicode chars were remove (\\u)
    """
    contributions: str = (
        "[x xx GitHub](https://github.com/x), "
        "[xxx on the wiki](https://habitica.fandom.com/wiki/User:xxx)\n"
        "* Tier 2 (in progress): "
        "[dsklaf DSL dklasfalsjfjsts](https://github.com/xxx/xxxx/pull/21389)"
    )
    semi_realistic_user: dict = {
        "auth": {
            "local": {
                "username": "vioman",
                "lowerCaseUsername": "vioman",
                "email": "vioman@vioman.io"
            },
            "timestamps": {
                "created": "2024-03-20T20:23:38.119Z",
                "loggedin": "2027-07-08T04:47:51.661Z",
                "updated": "2028-07-08T05:34:02.781Z"
            },
            "facebook": {},
            "google": {},
            "apple": {}
        },
        "achievements": {
            "ultimateGearSets": {
                "healer": False,
                "wizard": True,
                "rogue": True,
                "warrior": False
            },
            "streak": 172,
            "challenges": [],
            "perfect": 109,
            "quests": {
                "goldenknight2": 2,
                "goldenknight3": 1,
                "unicorn": 3,
                "egg": 1,
                "slime": 1,
                "rooster": 1
            },
            "completedTask": True,
            "createdTask": True,
            "hatchedPet": True,
            "fedPet": True,
            "purchasedEquipment": True,
            "joinedGuild": True,
            "partyUp": True,
            "partyOn": True,
            "joinedChallenge": True,
            "freshwaterFriends": True,
            "dustDevil": True,
            "boneCollector": True,
            "backToBasics": True,
            "monsterMagus": True,
            "thankyou": 1,
            "goodAsGold": True,
            "primedForPainting": True,
            "tickledPink": True,
            "congrats": 1,
            "beastMaster": True,
            "seeingRed": True,
            "violetsAreBlue": True,
            "rosyOutlook": True,
            "skeletonCrew": True,
            "allYourBase": True,
            "undeadUndertaker": True,
            "aridAuthority": True,
            "allThatGlitters": True,
            "pearlyPro": True,
            "wildBlueYonder": True,
            "mountMaster": True,
            "redLetterDay": True,
            "triadBingo": True,
            "seafoam": 5,
            "rebirthLevel": 100,
            "rebirths": 1,
            "justAddWater": True,
            "habiticaDays": 1,
            "bugBonanza": True,
            "bareNecessities": True,
            "mindOverMatter": True
        },
        "backer": {},
        "contributor": {
            "contributions": contributions,
            "level": 1,
            "text": "Comrade, Blacksmith",
            "admin": False
        },
        "purchased": {
            "ads": False,
            "txnCount": 1,
            "skin": {},
            "hair": {},
            "shirt": {},
            "background": {
                "violet": True,
                "blue": True,
                "green": True,
                "purple": True,
                "red": True,
                "yellow": True,
                "blacksmithy": True,
                "crystal_cave": True,
                "distant_castle": True
            },
            "plan": {
                "consecutive": {
                    "count": 2,
                    "offset": 1,
                    "gemCapExtra": 5,
                    "trinkets": 1
                },
                "quantity": 1,
                "extraMonths": 0,
                "gemsBought": 9000,
                "mysteryItems": [],
                "dateUpdated": "2034-06-01T04:52:21.012Z",
                "customerId": "X-XX111AA3",
                "dateCreated": "2034-05-03T04:52:04.117Z",
                "dateTerminated": "null",
                "lastReminderDate": "null",
                "owner": "0000fd00-ffe0-0fb0-b0fa-0d00b0000ff0",
                "paymentMethod": "something",
                "planId": "basic_6mo"
            }
        },
        "flags": {
            "tour": {
                "intro": -2,
                "classes": -1,
                "stats": -1,
                "tavern": -2,
                "party": -2,
                "guilds": -2,
                "challenges": -1,
                "market": -2,
                "pets": -2,
                "mounts": -1,
                "hall": -2,
                "equipment": -2
            },
            "tutorial": {
                "common": {
                    "habits": True,
                    "dailies": True,
                    "todos": True,
                    "rewards": True,
                    "party": True,
                    "pets": True,
                    "gems": True,
                    "skills": True,
                    "classes": True,
                    "tavern": True,
                    "equipment": True,
                    "items": True,
                    "mounts": True,
                    "inbox": True,
                    "stats": True
                },
                "ios": {
                    "addTask": False,
                    "editTask": False,
                    "deleteTask": False,
                    "filterTask": False,
                    "groupPets": False,
                    "inviteParty": False,
                    "reorderTask": False
                }
            },
            "customizationsNotification": True,
            "showTour": True,
            "dropsEnabled": False,
            "itemsEnabled": True,
            "lastNewStuffRead": "aaaaaaaa-bbbb-ccccccccc-dddddddddddd",
            "rewrite": True,
            "classSelected": True,
            "rebirthEnabled": True,
            "recaptureEmailsPhase": 0,
            "weeklyRecapEmailsPhase": 0,
            "communityGuidelinesAccepted": True,
            "cronCount": 171,
            "welcomed": True,
            "armoireEnabled": True,
            "armoireOpened": True,
            "armoireEmpty": False,
            "cardReceived": False,
            "warnedLowHealth": True,
            "verifiedUsername": True,
            "levelDrops": {
                "atom1": True,
                "vice1": True,
                "goldenknight1": True,
                "moonstone1": True
            },
            "lastWeeklyRecap": "2022-03-21T20:23:38.119Z",
            "onboardingEmailsPhase": "9-b-1111111112234",
            "lastFreeRebirth": "2022-07-15T18:42:05.630Z",
            "newStuff": False
        },
        "history": {
            "exp": [
                {
                    "date": 1616475808219,
                    "value": 708.66015625
                },
                {
                    "date": 1617253819642,
                    "value": 10388.243710296229
                },
                {
                    "date": 1619843534792,
                    "value": 13132.75
                },
                {
                    "date": "2021-05-04T04:42:22.770Z",
                    "value": 14551
                }
            ],
            "todos": [
                {
                    "date": 1616475808219,
                    "value": -12.781333149500004
                },
                {
                    "date": 1617253819642,
                    "value": -219.47350071428951
                },
                {
                    "date": "2021-06-26T07:04:53.202Z",
                    "value": -1951.1495238060916
                },
                {
                    "date": "2021-06-27T04:29:01.504Z",
                    "value": -2065.735204333207
                },
                {
                    "date": "2021-09-08T04:44:44.422Z",
                    "value": -14520.782668485932
                },
                {
                    "date": "2021-09-09T04:47:51.661Z",
                    "value": -14927.3409270358
                }
            ]
        },
        "items": {
            "gear": {
                "equipped": {
                    "armor": "armor_rogue_5",
                    "head": "head_special_pageHelm",
                    "shield": "shield_special_goldenknight",
                    "headAccessory": "headAccessory_armoire_gogglesOfBookbinding",
                    "weapon": "weapon_special_2",
                    "eyewear": "eyewear_armoire_goofyGlasses",
                    "body": "body_armoire_cozyScarf",
                    "back": "back_special_aetherCloak"
                },
                "costume": {
                    "armor": "armor_armoire_autumnEnchantersCloak",
                    "head": "head_wizard_3",
                    "shield": "shield_base_0",
                    "weapon": "weapon_base_0",
                    "headAccessory": "headAccessory_base_0",
                    "eyewear": "eyewear_base_0",
                    "back": "back_base_0",
                    "body": "body_base_0"
                },
                "owned": {
                    "headAccessory_special_blackHeadband": True,
                    "headAccessory_special_blueHeadband": True,
                    "back_mystery_202109": True,
                    "headAccessory_mystery_202109": True,
                    "head_special_snowSovereignCrown": True,
                    "armor_special_snowSovereignRobes": True,
                    "weapon_armoire_heraldsBuisine": True,
                    "armor_armoire_heraldsTunic": True,
                    "head_armoire_heraldsCap": True
                }
            },
            "special": {
                "snowball": 0,
                "spookySparkles": 0,
                "shinySeed": 5,
                "seafoam": 2,
                "valentine": 0,
                "valentineReceived": [],
                "nye": 0,
                "nyeReceived": [],
                "greeting": 0,
                "greetingReceived": [],
                "thankyou": 0,
                "thankyouReceived": [],
                "birthday": 0,
                "birthdayReceived": [],
                "congrats": 0,
                "congratsReceived": [],
                "getwell": 0,
                "getwellReceived": [],
                "goodluck": 0,
                "goodluckReceived": []
            },
            "lastDrop": {
                "count": 11,
                "date": "2044-09-09T04:52:33.115Z"
            },
            "pets": {
                "Dragon-Desert": 5,
                "Triceratops-CottonCandyBlue": -1,
                "Wolf-Windup": 5,
                "Beetle-Shade": -1,
                "Beetle-CottonCandyPink": 15,
                "Beetle-Skeleton": -1,
                "Snail-Desert": -1
            },
            "eggs": {
                "Dragon": 188,
                "LionCub": 196,
                "Axolotl": 0,
                "Seahorse": 3,
                "Whale": 3,
                "Beetle": 0,
                "Snail": 2,
                "Rock": 3,
                "Egg": 10,
                "Slime": 3,
                "Rooster": 3
            },
            "hatchingPotions": {
                "CottonCandyBlue": 129,
                "RoyalPurple": 3,
                "Golden": 112,
                "CottonCandyPink": 138,
                "Bronze": 0,
                "BlackPearl": 0,
                "Windup": 0
            },
            "food": {
                "RottenMeat": 406,
                "Potatoe": 362,
                "Saddle": 1,
                "Cake_White": 1,
                "Cake_Zombie": 1
            },
            "mounts": {
                "Fox-RoyalPurple": True,
                "FlyingPig-Zombie": True,
                "Fox-Base": True,
                "Fox-Golden": True,
                "Turtle-CottonCandyPink": True,
                "Whale-White": True,
                "Seahorse-Red": True,
                "Seahorse-CottonCandyPink": True,
                "Axolotl-Base": True,
                "Nudibranch-CottonCandyBlue": True,
                "Triceratops-Base": True,
                "SeaSerpent-Base": True,
                "Hippo-Base": True,
                "TigerCub-RoyalPurple": True,
                "PandaCub-RoyalPurple": True,
                "Dolphin-Base": True,
                "Gryphon-RoyalPurple": True,
                "Beetle-Shade": True,
                "Beetle-Skeleton": True,
                "Snail-Desert": True
            },
            "quests": {
                "atom1": 2,
                "basilist": 1,
                "moon3": 1,
                "goldenknight1": 2,
                "vice2": 0,
                "vice3": 0
            },
            "currentPet": "Wolf-Base",
            "currentMount": "Aether-Invisible"
        },
        "invitations": {
            "guilds": [],
            "party": {},
            "parties": []
        },
        "party": {
            "quest": {
                "progress": {
                    "up": 22.051118316159503,
                    "down": 0,
                    "collectedItems": 14,
                    "collect": {}
                },
                "RSVPNeeded": False,
                "key": "solarSystem",
                "completed": "null"
            },
            "order": "auth.timestamps.loggedin",
            "orderAscending": "asc",
            "_id": "eeeeeeee-bbbb-0000-dddd-afedfeafedad"
        },
        "preferences": {
            "hair": {
                "color": "blond",
                "base": 3,
                "bangs": 2,
                "beard": 0,
                "mustache": 0,
                "flower": 6
            },
            "emailNotifications": {
                "unsubscribeFromAll": True,
                "newPM": True,
                "kickedGroup": True,
                "wonChallenge": True,
                "giftedGems": True,
                "giftedSubscription": True,
                "invitedParty": True,
                "invitedGuild": True,
                "questStarted": True,
                "invitedQuest": True,
                "importantAnnouncements": True,
                "weeklyRecaps": True,
                "onboarding": True,
                "majorUpdates": True,
                "subscriptionReminders": False
            },
            "pushNotifications": {
                "unsubscribeFromAll": False,
                "newPM": False,
                "wonChallenge": True,
                "giftedGems": False,
                "giftedSubscription": False,
                "invitedParty": False,
                "invitedGuild": False,
                "questStarted": False,
                "invitedQuest": False,
                "majorUpdates": False,
                "mentionParty": False,
                "mentionJoinedGuild": False,
                "mentionUnjoinedGuild": False,
                "partyActivity": False
            },
            "suppressModals": {
                "levelUp": False,
                "hatchPet": False,
                "raisePet": True,
                "streak": False
            },
            "tasks": {
                "groupByChallenge": False,
                "confirmScoreNotes": False
            },
            "dayStart": 0,
            "size": "slim",
            "hideHeader": False,
            "skin": "f5a76e",
            "shirt": "pink",
            "timezoneOffset": -120,
            "sound": "danielTheBard",
            "chair": "none",
            "allocationMode": "taskbased",
            "autoEquip": False,
            "dateFormat": "dd/MM/yyyy",
            "sleep": False,
            "stickyHeader": True,
            "disableClasses": False,
            "newTaskEdit": False,
            "dailyDueDefaultView": True,
            "advancedCollapsed": True,
            "toolbarCollapsed": False,
            "reverseChatOrder": False,
            "displayInviteToPartyWhenPartyIs1": True,
            "improvementCategories": [],
            "language": "en",
            "webhooks": {},
            "background": "distant_castle",
            "timezoneOffsetAtLastCron": -120,
            "costume": True,
            "automaticAllocation": False
        },
        "profile": {
            "name": "vioman",
            "imageUrl": "https://example.com/my.jpg",
            "blurb": "Creator of Hopla"
        },
        "stats": {
            "buffs": {
                "str": 50,
                "int": 50,
                "per": 50,
                "con": 50,
                "stealth": 0,
                "streaks": False,
                "snowball": False,
                "spookySparkles": False,
                "shinySeed": False,
                "seafoam": False
            },
            "training": {
                "int": 0,
                "per": 0,
                "str": 0,
                "con": 0
            },
            "hp": 47.10095169004215,
            "mp": 11.912692307692595,
            "exp": 701,
            "gp": 523808.2384303317,
            "lvl": 101,
            "class": "wizard",
            "points": 0,
            "str": 0,
            "con": 0,
            "int": 12,
            "per": 88,
            "toNextLevel": 3700,
            "maxHealth": 50,
            "maxMP": 254
        },
        "inbox": {
            "newMessages": 0,
            "optOut": False,
            "blocks": [
                "31aa247a-5432-0000-b6b3-111111e20eb0"
            ],
            "messages": {
                "aaaaaa82-b9b7-ccc4-dddd-11111148f725": {
                    "sent": True,
                    "flagCount": 0,
                    "_id": "aaaaaa82-b9b7-ccc4-dddd-11111148f725",
                    "ownerId": "79551d98-31e9-42b4-b7fa-9d89b0944319",
                    "flags": {},
                    "id": "aaaaaaaa-d9b7-42a4-0000-00000048f725",
                    "text": "dsjk :blush:. \nR .asdjfkl asdflasf'asdfljksdf jsdalf   :smiley:",
                    "unformattedText": "sdaf :blush:. fjkl.\nI  djsklajw :smiley:",
                    "info": {},
                    "timestamp": "2024-03-09T04:54:32.565Z",
                    "likes": {},
                    "uuid": "aaaaaaaa-324a-aaaa-abbb-bbbbbbbbbbeb",
                    "contributor": {
                        "contributions": contributions,
                        "level": 1,
                        "text": "Comrade, Blacksmith",
                        "admin": False
                    },

                    "backer": {},
                    "user": "minsun",
                    "username": "minsun",
                    "userStyles": {
                        "items": {
                            "gear": {
                                "costume": {
                                    "armor": "armor_armoire_autumnEnchantersCloak",
                                    "head": "head_wizard_3",
                                    "shield": "shield_base_0",
                                    "weapon": "weapon_base_0",
                                    "headAccessory": "headAccessory_base_0",
                                    "eyewear": "eyewear_base_0",
                                    "back": "back_base_0",
                                    "body": "body_base_0"
                                },
                                "equipped": {
                                    "armor": "armor_rogue_5",
                                    "head": "head_special_pageHelm",
                                    "shield": "shield_special_goldenknight",
                                    "headAccessory": "headAccessory_armoire_gogglesOfBookbinding",
                                    "weapon": "weapon_special_2",
                                    "eyewear": "eyewear_armoire_goofyGlasses",
                                    "body": "body_armoire_cozyScarf",
                                    "back": "back_special_aetherCloak"
                                }
                            },
                            "currentMount": "Aether-Invisible",
                            "currentPet": "Wolf-Base"
                        },
                        "preferences": {
                            "hair": {
                                "color": "blond",
                                "base": 3,
                                "bangs": 2,
                                "beard": 0,
                                "mustache": 0,
                                "flower": 6
                            },
                            "skin": "f5a76e",
                            "shirt": "pink",
                            "chair": "none",
                            "size": "slim",
                            "background": "distant_castle",
                            "costume": True
                        },
                        "stats": {
                            "class": "wizard",
                            "buffs": {
                                "seafoam": False,
                                "shinySeed": False,
                                "spookySparkles": False,
                                "snowball": False
                            }
                        }
                    }
                }
            }
        },
        "tasksOrder": {
            "habits": [
                "dddddddd-30bc-dddd-bebb-fd713096ac83",
                "b09897da-3249-4131-862a-fffffffff765"
            ],
            "dailys": [
                "3f70cf50-bbbb-42f5-a279-aaaaaaaaaaa8",
                "140791fb-b6be-cccc-9918-aaaaaaaaaaa1"
            ],
            "todos": [
                "aaaaaaaa-02ef-4f8e-91b8-b78d03fffba5",
                "bbbbbb7c-7f96-4672-b0ad-85422fff5cf0"
            ],
            "rewards": []
        },
        "_v": 54081,
        "balance": 24.5,
        "challenges": [
            "10101010-1000-4fe1-b6a4-84ce8ef8885d"
        ],
        "guilds": [
            "10101011-1010-4e52-87de-5c040ed0f8f8",
            "fffffff0-087f-4b08-9432-86fe77c2f1ef"
        ],
        "loginIncentives": 177,
        "invitesSent": 0,
        "pinnedItemsOrder": [],
        "_id": "aaaaaaa8-aaa9-42b4-b7fa-9d89b0944319",
        "lastCron": "2026-09-09T04:47:51.661Z",
        "newMessages": {
            "aaaaaaaa-ffff-aaa9-874e-e6e14c53549e": {
                "name": "asdjfk RJKLE dfjklsa LJRK",
                "value": True
            },
            "aaaaaaa0-087f-4b08-9432-86fe77c2f1ef": {
                "name": "dsklfa jkldsa fadskjlfnts and health professionals",
                "value": True
            }
        },
        "notifications": [
            {
                "type": "NEW_CHAT_MESSAGE",
                "data": {
                    "group": {
                        "id": "aaaaaaaa-1fae-4b39-111e-da1fa1df549e",
                        "name": "dsjkladsaf kljafes of Habitica"
                    }
                },
                "id": "aaaa370d-0000-000b-0003-1111166ecd93",
                "seen": False
            },
            {
                "type": "NEW_CHAT_MESSAGE",
                "data": {
                    "group": {
                        "id": "aaaaaaaa-087f-4b08-9432-86fe77c2f1ef",
                        "name": "dsaklf,sd sdjkla asdf, kdlasfjkdl"
                    }
                },
                "id": "aaaaae61-a31b-4588-a54a-23d51c42dbc8",
                "seen": False
            }
        ],
        "tags": [
            {
                "name": "Work",
                "id": "dddddddd-30bc-dddd-bebb-fd713096ac83"
            },
            {
                "id": "b09897da-3249-4131-862a-fffffffff765",
                "name": "BXX2024",
                "challenge": True
            }
        ],
        "extra": {},
        "pushDevices": [
            {
                "regId": "aaaaaaaaaaaaaaa:PPPPPPPPPPPPp099999999999_dsklaffjasdkl-AAAA",
                "type": "android",
                "createdAt": "2023-02-25T16:19:50.079Z",
                "updatedAt": "2025-09-09T04:54:32.599Z"
            }
        ],
        "webhooks": [],
        "pinnedItems": [
            {
                "type": "potion",
                "path": "potion"
            },
            {
                "type": "armoire",
                "path": "armoire"
            },
            {
                "path": "special.gems",
                "type": "gem"
            }
        ],
        "unpinnedItems": [
            {
                "path": "gear.flat.weapon_special_spring2021Rogue",
                "type": "marketGear"
            },
            {
                "path": "gear.flat.armor_special_spring2021Rogue",
                "type": "marketGear"
            },
            {
                "path": "gear.flat.head_special_spring2021Rogue",
                "type": "marketGear"
            },
            {
                "path": "gear.flat.shield_special_spring2021Rogue",
                "type": "marketGear"
            }
        ],
        "_ABTests": {
            "onboardingPushNotification": "Onboarding-Step6-Phasea-VersionD"
        },
        "migration": "20220924_pet_group_achievements",
        "id": "79553d98-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        "needsCron": False

    }
    return HabiticaUser(semi_realistic_user)
