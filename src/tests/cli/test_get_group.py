#!/usr/bin/env python3

from hopla.cli.get_group import HabiticaGroupRequest


class TestHabiticaGroupRequest:

    def test_path(self):
        party_request = HabiticaGroupRequest()
        comrades_uuid = "2ff9822b-27f2-4774-98da-db349b57a38e"
        comrades_request = HabiticaGroupRequest(comrades_uuid)

        assert party_request.path == "/groups/party"
        assert comrades_request.path == f"/groups/{comrades_uuid}"
