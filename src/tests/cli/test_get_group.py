#!/usr/bin/env python3
from unittest.mock import MagicMock, patch
from click.testing import CliRunner, Result

from hopla.cli.get_group import HabiticaGroupRequest, get_group


class MockGroupResponse:
    def __init__(self, json, status_code: int = 200):
        self._json = json
        self.status_code = status_code

    def json(self):
        return self._json


class TestHabiticaGroupRequest:

    def test_path_party(self):
        party_request = HabiticaGroupRequest()
        assert party_request.path == "/groups/party"

    def test_path_uuid(self):
        comrades_uuid = "2ff9822b-27f2-4774-98da-db349b57a38e"
        comrades_request = HabiticaGroupRequest(comrades_uuid)
        assert comrades_request.path == f"/groups/{comrades_uuid}"

    @patch("hopla.cli.get_group.HabiticaGroupRequest.default_headers")
    @patch("hopla.cli.get_group.requests.get")
    def test_get_group_request(self, mock_get: MagicMock,
                               headers: MagicMock):
        party_request = HabiticaGroupRequest()

        mock_get.return_value = MockGroupResponse(
            json={"success": True, "data": get_test_party_dict()}
        )

        # No need for credentials, were mocking the API call
        headers.return_value = {"mock": "headers"}
        party_request.get_group_request()

        mock_get.assert_called_once()
        assert mock_get.call_args.url.endswith("/groups/party")

    @patch("hopla.cli.get_group.HabiticaGroupRequest.default_headers")
    @patch("hopla.cli.get_group.requests.get")
    def test_get_group_or_exit_ok(self,
                                  mock_get: MagicMock,
                                  headers: MagicMock):
        legends_uuid = "52f49529-58c1-4020-a59b-8bb8579e941f"
        legends_request = HabiticaGroupRequest()

        mock_get.return_value = MockGroupResponse(
            json={"success": True, "data": get_test_party_dict()}
        )

        # No need for credentials, were mocking the API call
        headers.return_value = {"mock": "headers"}
        legends_request.get_group_request()

        mock_get.assert_called_once()
        assert mock_get.call_args.url.endswith(f"/groups/{legends_uuid}")


class TestGetGroupCli:

    @patch("hopla.cli.get_group.HabiticaGroupRequest.default_headers")
    @patch("hopla.cli.get_group.requests.get")
    def test_get_group_ok(self,
                          mock_get: MagicMock,
                          headers: MagicMock):
        """A successful hopla get-group call."""
        party_data = get_test_party_dict()
        mock_get.return_value = MockGroupResponse(
            json={"success": True, "data": party_data}
        )

        # No need for credentials, were mocking the API call
        headers.return_value = {"mock": "headers"}

        runner = CliRunner()
        result: Result = runner.invoke(get_group)

        assert result.exit_code == 0

    @patch("hopla.cli.get_group.HabiticaGroupRequest.default_headers")
    @patch("hopla.cli.get_group.requests.get")
    def test_get_group_group_id_ok(self,
                                   mock_get: MagicMock,
                                   headers: MagicMock):
        """A successful hopla get-group call with a group_id."""
        group_id = "eeeeeeee-683b-4b8a-9ddd-b7b652470bdd"
        party_data = {"quest": {"active": False}}
        mock_get.return_value = MockGroupResponse(json={"success": True,
                                                        "data": party_data})
        # No need for credentials, were mocking the API call
        headers.return_value = {"mock": "headers"}

        runner = CliRunner()
        result: Result = runner.invoke(get_group, [group_id])

        mock_get.assert_called_once()
        assert mock_get.call_args.url.endswith(f"/group/{group_id}")
        assert result.exit_code == 0
        assert '"quest": {' in result.stdout
        assert '"active": false' in result.stdout

    @patch("hopla.cli.get_group.HabiticaGroupRequest.default_headers")
    @patch("hopla.cli.get_group.requests.get")
    def test_get_group_404fail(self,
                               mock_get: MagicMock,
                               headers: MagicMock):
        """A failed hopla get-group call."""
        group_id = "fake-uuid"

        err_msg = "NotFound: could not find this group"
        mock_get.return_value = MockGroupResponse(json={
            "success": False, "message": err_msg, "status_code": 404
        })
        headers.return_value = {"mock": "headers"}
        runner = CliRunner()
        result: Result = runner.invoke(get_group, [group_id])

        mock_get.assert_called_once()
        assert mock_get.call_args.url.endswith(f"/group/{group_id}")

        assert result.exit_code == 1
        assert err_msg in result.stdout


def get_test_party_dict() -> dict:
    """Returns pseudo-realistic json as a dict for a party."""
    group_id = "eeeeeeee-683b-4b8a-9ddd-b7b652470bdd"
    group_leader_id = "dddddddd-9e07-434e-8ab4-aaaaaaaaaaaa"
    group_member_id = "eeeeeeee-79a2-4dbe-b8a8-bbbbbbbbbbbb"
    member_username = "melvio"
    leader_username = "maxoya"

    chat = get_test_chat_msgs(
        group_id=group_id,
        group_leader_id=group_leader_id,
        group_member_id=group_member_id,
        leader_username=leader_username,
        member_username=member_username
    )

    return {
        "leaderOnly": {"challenges": True, "getGems": False},
        "quest": {
            "progress": {"collect": {}},
            "active": False,
            "members": {group_leader_id: None, group_member_id: True},
            "extra": {},
            "key": "taskwoodsTerror1",
            "leader": group_leader_id
        },
        "tasksOrder": {"habits": [], "dailys": [], "todos": [], "rewards": []},
        "purchased": {},
        "privacy": "private",
        "chat": chat,
        "memberCount": 2,
        "challengeCount": 0,
        "balance": 0,
        "_id": group_leader_id,
        "summary": "Gut aussehen, Examen rocken",
        "type": "party",
        "name": "best party",
        "description": "Our Party!",
        "managers": {},
        "categories": [],
        "leader": {
            "auth": {"local": {"username": leader_username}},
            "flags": {"verifiedUsername": True},
            "profile": {"name": leader_username},
            "_id": group_id,
            "id": group_id
        },
        "id": group_id
    }


def get_test_chat_msgs(group_id: str, group_leader_id: str, group_member_id: str,
                       leader_username: str, member_username: str) -> list:
    """Returns pseudo-realistic chat json as a dict for a party."""
    chat_msg1 = {
        "flagCount": 0,
        "_id": group_leader_id,
        "flags": {},
        "id": group_leader_id,
        "text": "14000 perception... such overkill .. ",
        "unformattedText": "14000 perception... such overkill .. ",
        "info": {},
        "timestamp": 1632039168020,
        "likes": {},
        "client": "web",
        "uuid": group_leader_id, "contributor": {},
        "backer": {},
        "user": leader_username,
        "username": leader_username,
        "groupId": group_id,
        "userStyles": {
            "items": {
                "gear": {
                    "costume": {
                        "armor": "armor_armoire_vernalVestment",
                        "head": "head_armoire_vernalHennin", "shield": "shield_armoire_redRose",
                        "weapon": "weapon_base_0", "body": "body_base_0",
                        "eyewear": "eyewear_base_0", "back": "back_base_0",
                        "headAccessory": "headAccessory_base_0"},
                    "equipped": {
                        "armor": "armor_warrior_5", "head": "head_special_2",
                        "shield": "shield_special_goldenknight", "weapon": "weapon_warrior_6",
                        "eyewear": "eyewear_special_aetherMask",
                        "body": "body_special_aetherAmulet", "back": "back_special_aetherCloak"}
                },
                "currentMount": "Axolotl-CottonCandyPink", "currentPet": ""
            },
            "preferences": {
                "hair": {"color": "brown", "base": 0, "bangs": 3, "beard": 0, "mustache": 0,
                         "flower": 0},
                "skin": "f5a76e", "shirt": "blue", "chair": "none", "size": "slim",
                "background": "blue", "costume": True
            },
            "stats": {
                "class": "warrior",
                "buffs": {"seafoam": False, "shinySeed": False, "spookySparkles": False,
                          "snowball": False}
            }
        }
    }
    chat_msg2 = {
        "flagCount": 0,
        "_id": group_member_id,
        "flags": {},
        "id": group_member_id,
        "text": f"`{member_username} casts Ethereal Surge for the party.`",
        "unformattedText": f"{member_username} casts Ethereal Surge for the party.",
        "info": {"type": "spell_cast_party", "user": member_username, "class": "wizard",
                 "spell": "mpheal"},
        "timestamp": 1632038593015,
        "likes": {},
        "uuid": "system",
        "groupId": group_id
    }
    return [chat_msg1, chat_msg2]
