"""
Test the views for the Fleet Finder application.
"""

# Standard Library
import json
from http import HTTPStatus
from types import SimpleNamespace
from unittest.mock import Mock, patch

# Django
from django.contrib.auth.models import Group
from django.test import TestCase
from django.urls import reverse
from django.utils.datetime_safe import datetime
from django.utils.timezone import now

# Alliance Auth
from allianceauth.groupmanagement.models import AuthGroup

# Alliance Auth (External Libs)
from app_utils.testing import create_fake_user

# AA Fleet Finder
from fleetfinder.models import Fleet


def dt_to_iso(dt: datetime) -> str:
    """
    Helper :: Convert a datetime object to ISO 8601 format.

    @see https://github.com/django/django/blob/main/django/core/serializers/json.py#L92-L98

    :param dt:
    :type dt:
    :return:
    :rtype:
    """

    r = dt.isoformat()

    if dt.microsecond:
        r = r[:23] + r[26:]

    if r.endswith("+00:00"):
        r = r.removesuffix("+00:00") + "Z"

    return r


class FleetfinderTestViews(TestCase):
    """
    Base test case for Fleet Finder views.
    This class sets up the necessary users and fleet ID for testing.
    It includes a user with the `fleetfinder.manage_fleets` permission
    and a user with `fleetfinder.access_fleetfinder` access permissions.
    The fleet ID is set to a predefined value for testing purposes.
    """

    @classmethod
    def setUp(cls):
        """
        Set up the test case.

        :return:
        :rtype:
        """

        cls.user_with_manage_perms = create_fake_user(
            character_id=1000,
            character_name="Jean Luc Picard",
            permissions=["fleetfinder.access_fleetfinder", "fleetfinder.manage_fleets"],
        )
        cls.user_with_basic_acces_perms = create_fake_user(
            character_id=1001,
            character_name="William Riker",
            permissions=["fleetfinder.access_fleetfinder"],
        )

        cls.fleet_created_at = now()

        cls.fleet = Fleet(
            fleet_id=12345,
            name="Starfleet",
            fleet_commander=cls.user_with_manage_perms.profile.main_character,
            created_at=cls.fleet_created_at,
            is_free_move=False,
        )
        cls.fleet.save()

        cls.fleet_id = 12345


class TestAjaxDashboardView(FleetfinderTestViews):
    """
    Test the ajax_dashboard view in the Fleet Finder application.
    This view is responsible for rendering the dashboard with fleet data.
    It should return a JSON response containing fleet information,
    including fleet names, commanders, and group associations.
    If no fleets are available, it should return an empty list.
    It should also filter fleets based on the user's groups.
    """

    @patch("fleetfinder.views.get_all_characters_from_user")
    def test_renders_dashboard_with_fleet_data_with_basic_access(
        self, mock_get_characters
    ):
        """
        Test that the ajax_dashboard view renders the dashboard with fleet data
        when the user has basic access permissions.

        :param mock_get_characters:
        :type mock_get_characters:
        :return:
        :rtype:
        """

        mock_get_characters.return_value = [
            self.user_with_manage_perms.profile.main_character
        ]

        fleet = self.fleet
        fleet.groups.set([])

        self.client.force_login(self.user_with_basic_acces_perms)
        url = reverse("fleetfinder:ajax_dashboard")
        join_url = reverse("fleetfinder:join_fleet", args=[self.fleet_id])
        response = self.client.get(url)

        expected_response = [
            {
                "fleet_commander": {
                    "html": '<img class="rounded eve-character-portrait" src="https://images.evetech.net/characters/1000/portrait?size=32" alt="Jean Luc Picard" loading="lazy">Jean Luc Picard',
                    "sort": "Jean Luc Picard",
                },
                "fleet_name": "Starfleet",
                "created_at": dt_to_iso(self.fleet_created_at),
                "actions": f'<a href="{join_url}" class="btn btn-sm btn-success ms-1" data-bs-tooltip="aa-fleetfinder" title="Join fleet"><i class="fa-solid fa-right-to-bracket"></i></a>',
            }
        ]

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("Starfleet", response.json()[0]["fleet_name"])
        self.assertIn("Jean Luc Picard", response.json()[0]["fleet_commander"]["html"])
        self.assertEqual(response.json(), expected_response)

    @patch("fleetfinder.views.get_all_characters_from_user")
    def test_renders_dashboard_with_fleet_data_with_manage_access(
        self, mock_get_characters
    ):
        """
        Test that the ajax_dashboard view renders the dashboard with fleet data
        when the user has manage access permissions.

        :param mock_get_characters:
        :type mock_get_characters:
        :return:
        :rtype:
        """

        mock_get_characters.return_value = [
            self.user_with_manage_perms.profile.main_character
        ]

        fleet = self.fleet
        fleet.groups.set([])

        self.client.force_login(self.user_with_manage_perms)
        url = reverse("fleetfinder:ajax_dashboard")
        join_url = reverse("fleetfinder:join_fleet", args=[self.fleet_id])
        details_url = reverse("fleetfinder:fleet_details", args=[self.fleet_id])
        edit_url = reverse("fleetfinder:edit_fleet", args=[self.fleet_id])
        response = self.client.get(url)

        expected_response = [
            {
                "fleet_commander": {
                    "html": '<img class="rounded eve-character-portrait" src="https://images.evetech.net/characters/1000/portrait?size=32" alt="Jean Luc Picard" loading="lazy">Jean Luc Picard',
                    "sort": "Jean Luc Picard",
                },
                "fleet_name": "Starfleet",
                "created_at": dt_to_iso(self.fleet_created_at),
                "actions": (
                    f'<a href="{join_url}" class="btn btn-sm btn-success ms-1" data-bs-tooltip="aa-fleetfinder" title="Join fleet"><i class="fa-solid fa-right-to-bracket"></i></a>'
                    f'<a href="{details_url}" class="btn btn-sm btn-info ms-1" data-bs-tooltip="aa-fleetfinder" title="View fleet details"><i class="fa-solid fa-eye"></i></a>'
                    f'<a href="{edit_url}" class="btn btn-sm btn-warning ms-1" data-bs-tooltip="aa-fleetfinder" title="Edit fleet advert"><i class="fa-solid fa-pen-to-square"></i></a>'
                ),
            }
        ]

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("Starfleet", response.json()[0]["fleet_name"])
        self.assertIn("Jean Luc Picard", response.json()[0]["fleet_commander"]["html"])
        self.assertEqual(response.json(), expected_response)

    @patch("fleetfinder.views.get_all_characters_from_user")
    def test_returns_empty_data_when_no_fleets_available(self, mock_get_characters):
        """
        Test that the ajax_dashboard view returns an empty list when no fleets are available.

        :param mock_get_characters:
        :type mock_get_characters:
        :return:
        :rtype:
        """

        mock_get_characters.return_value = [
            self.user_with_manage_perms.profile.main_character
        ]

        Fleet.objects.all().delete()  # Remove all fleets

        self.client.force_login(self.user_with_basic_acces_perms)
        url = reverse("fleetfinder:ajax_dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), [])

    @patch("fleetfinder.views.get_all_characters_from_user")
    def test_filters_fleets_by_user_groups(self, mock_get_characters):
        """
        Test that the ajax_dashboard view filters fleets based on the user's groups.

        :param mock_get_characters:
        :type mock_get_characters:
        :return:
        :rtype:
        """

        mock_get_characters.return_value = [
            self.user_with_manage_perms.profile.main_character
        ]

        group_obj = Group.objects.create(name="Starfleet Officers")
        auth_group, _ = AuthGroup.objects.get_or_create(group=group_obj)
        fleet = self.fleet
        fleet.groups.set([auth_group])

        self.client.force_login(self.user_with_basic_acces_perms)
        self.user_with_basic_acces_perms.groups.add(group_obj)
        url = reverse("fleetfinder:ajax_dashboard")
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertIn("Starfleet", response.json()[0]["fleet_name"])


class TestFleetEditView(FleetfinderTestViews):
    """
    Test the edit_fleet view in the Fleet Finder application.
    This view is responsible for editing fleet details.
    """

    @patch("fleetfinder.views.Fleet.objects.get")
    @patch("fleetfinder.views.AuthGroup.objects.filter")
    def test_renders_edit_fleet_template_with_correct_context(
        self, mock_filter_groups, mock_get_fleet
    ):
        """
        Test that the edit_fleet view renders the correct template and context.

        :param mock_filter_groups:
        :type mock_filter_groups:
        :param mock_get_fleet:
        :type mock_get_fleet:
        :return:
        :rtype:
        """

        mock_get_fleet.return_value = self.fleet
        group1 = Mock(spec=AuthGroup)
        group1.name = "Group1"
        group2 = Mock(spec=AuthGroup)
        group2.name = "Group2"
        mock_filter_groups.return_value = [group1, group2]

        self.client.force_login(self.user_with_manage_perms)
        url = reverse("fleetfinder:edit_fleet", args=[self.fleet_id])
        response = self.client.get(url)

        self.assertTemplateUsed(response, "fleetfinder/edit-fleet.html")
        self.assertEqual(response.context["fleet"].name, "Starfleet")
        self.assertEqual(response.context["character_id"], 1000)
        self.assertEqual(len(response.context["auth_groups"]), 2)

    @patch("fleetfinder.views.Fleet.objects.get")
    def test_redirects_to_dashboard_if_fleet_does_not_exist(self, mock_get_fleet):
        """
        Test that the edit_fleet view redirects to the dashboard if the fleet does not exist.

        :param mock_get_fleet:
        :type mock_get_fleet:
        :return:
        :rtype:
        """

        mock_get_fleet.side_effect = Fleet.DoesNotExist

        self.client.force_login(self.user_with_manage_perms)
        url = reverse("fleetfinder:edit_fleet", args=[99999])
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("fleetfinder:dashboard"))


class TestJoinFleetView(FleetfinderTestViews):
    """
    Test the join_fleet view in the Fleet Finder application.
    This view is responsible for allowing users to join a fleet.
    It should redirect to the fleet details page after joining.
    If the fleet does not exist, it should return a 404 status code.
    """

    @patch("fleetfinder.views.Fleet.objects.get")
    def test_join_fleet_redirects_to_dashboard(self, mock_get_fleet):
        """
        Test that the join_fleet view redirects to the dashboard after joining a fleet.

        :param mock_get_fleet:
        :type mock_get_fleet:
        :return:
        :rtype:
        """

        mock_get_fleet.return_value = Fleet(fleet_id=self.fleet_id)

        self.client.force_login(self.user_with_manage_perms)
        url = reverse("fleetfinder:join_fleet", args=[self.fleet_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "fleetfinder/join-fleet.html")

    @patch("fleetfinder.views.Fleet.objects.get")
    def test_join_fleet_handles_non_existent_fleet(self, mock_get_fleet):
        """
        Test that the join_fleet view handles a non-existent fleet correctly.

        :param mock_get_fleet:
        :type mock_get_fleet:
        :return:
        :rtype:
        """

        mock_get_fleet.side_effect = Fleet.DoesNotExist

        self.client.force_login(self.user_with_manage_perms)
        url = reverse("fleetfinder:join_fleet", args=[123456])  # Non-existent fleet ID
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, reverse("fleetfinder:dashboard"))


class TestFleetDetailsView(FleetfinderTestViews):
    """
    Test the fleet_details view in the Fleet Finder application.
    This view is responsible for rendering the fleet details page.
    It should render the correct template and require the user to have
    the 'fleetfinder.manage_fleets' permission to access it.
    If the fleet does not exist, it should return a 404 status code.
    """

    @patch("fleetfinder.views.Fleet.objects.get")
    def test_fleet_details_renders_correct_template(self, mock_get_fleet):
        """
        Test that the fleet_details view renders the correct template.

        :param mock_get_fleet:
        :type mock_get_fleet:
        :return:
        :rtype:
        """

        mock_get_fleet.return_value = Fleet(fleet_id=self.fleet_id)

        self.client.force_login(self.user_with_manage_perms)
        url = reverse("fleetfinder:fleet_details", args=[self.fleet_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertTemplateUsed(response, "fleetfinder/fleet-details.html")

    @patch("fleetfinder.views.Fleet.objects.get")
    def test_fleet_details_requires_manage_permission(self, mock_get_fleet):
        """
        Test that the fleet_details view requires the user to have the 'fleetfinder.manage_fleets' permission.

        :param mock_get_fleet:
        :type mock_get_fleet:
        :return:
        :rtype:
        """

        mock_get_fleet.return_value = Fleet(fleet_id=self.fleet_id)

        self.client.force_login(self.user_with_basic_acces_perms)
        url = reverse("fleetfinder:fleet_details", args=[self.fleet_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_fleet_redirects_to_dashboard_if_not_found(self):
        """
        Test that the fleet_details view redirects to the dashboard if the fleet does not exist.

        :return:
        :rtype:
        """

        self.client.force_login(self.user_with_manage_perms)

        response = self.client.get(reverse("fleetfinder:fleet_details", args=[123]))

        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response.url, reverse("fleetfinder:dashboard"))


class TestAjaxFleetDetailsView(FleetfinderTestViews):
    """
    Test the ajax_fleet_details view in the Fleet Finder application.
    This view is responsible for returning fleet details in JSON format.
    It should return the fleet members and their ship types, or an empty list if the fleet is empty.
    """

    @patch("fleetfinder.views.get_fleet_composition")
    def test_returns_correct_fleet_details(self, mock_get_fleet_composition):
        """
        Test that the ajax_fleet_details view returns the correct fleet details.

        :param mock_get_fleet_composition:
        :type mock_get_fleet_composition:
        :return:
        :rtype:
        """

        mock_get_fleet_composition.return_value = SimpleNamespace(
            fleet=[{"name": "Pilot1"}, {"name": "Pilot2"}, {"name": "Pilot3"}],
            aggregate={"Frigate": 2, "Cruiser": 1},
        )

        self.client.force_login(user=self.user_with_manage_perms)

        url = reverse("fleetfinder:ajax_fleet_details", args=[self.fleet_id])
        response = self.client.get(url)

        expected_fleet_composition = {
            "fleet_member": [
                {"name": "Pilot1"},
                {"name": "Pilot2"},
                {"name": "Pilot3"},
            ],
            "fleet_composition": [
                {"ship_type_name": "Frigate", "number": 2},
                {"ship_type_name": "Cruiser", "number": 1},
            ],
        }

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(json.loads(response.content), expected_fleet_composition)

    @patch("fleetfinder.views.get_fleet_composition")
    def test_handles_empty_fleet(self, mock_get_fleet_composition):
        """
        Test that the ajax_fleet_details view handles an empty fleet correctly.

        :param mock_get_fleet_composition:
        :type mock_get_fleet_composition:
        :return:
        :rtype:
        """

        mock_get_fleet_composition.return_value = SimpleNamespace(
            fleet=[],
            aggregate={},
        )

        self.client.force_login(user=self.user_with_manage_perms)

        url = reverse("fleetfinder:ajax_fleet_details", args=[self.fleet_id])
        response = self.client.get(url)

        expected_fleet_composition = {"fleet_member": [], "fleet_composition": []}

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(json.loads(response.content), expected_fleet_composition)

    @patch("fleetfinder.views.get_fleet_composition")
    def test_returns_error_when_fleet_does_not_exist(self, mock_get_fleet_composition):
        """
        Test that the ajax_fleet_details view returns an error when the fleet does not exist.

        :param mock_get_fleet_composition:
        :type mock_get_fleet_composition:
        :return:
        :rtype:
        """

        mock_get_fleet_composition.side_effect = Fleet.DoesNotExist

        self.client.force_login(user=self.user_with_manage_perms)

        url = reverse("fleetfinder:ajax_fleet_details", args=[123])
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(
            response.content,
            {"error": "Fleet with ID 123 does not exist."},
        )

    @patch("fleetfinder.views.get_fleet_composition")
    def test_returns_error_when_runtime_error_occurs(self, mock_get_fleet_composition):
        """
        Test that the ajax_fleet_details view returns an error when a runtime error occurs.

        :param mock_get_fleet_composition:
        :type mock_get_fleet_composition:
        :return:
        :rtype:
        """

        mock_get_fleet_composition.side_effect = RuntimeError("Unexpected error")

        self.client.force_login(user=self.user_with_manage_perms)

        url = reverse("fleetfinder:ajax_fleet_details", args=[123])
        response = self.client.get(url)

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertJSONEqual(
            response.content,
            {"error": "Error retrieving fleet composition: Unexpected error"},
        )
