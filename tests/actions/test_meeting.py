from unittest import TestCase

import simplejson as json

from openslides_backend.actions import ActionPayload
from openslides_backend.actions.meeting.create import MeetingCreate
from openslides_backend.actions.meeting.delete import MeetingDelete
from openslides_backend.actions.meeting.update import MeetingUpdate
from openslides_backend.shared.exceptions import ActionException, PermissionDenied

from ..fake_services.database import DatabaseTestAdapter
from ..fake_services.permission import PermissionTestAdapter
from ..utils import (
    Client,
    ResponseWrapper,
    create_test_application,
    get_fqfield,
    get_fqid,
)


class BaseMeetingCreateActionTester(TestCase):
    """
    Tests the meeting create action.
    """

    def setUp(self) -> None:
        self.valid_payload_1 = [{"committee_id": 5914213969, "name": "name_zusae6aD0a"}]
        self.datastore_content = {
            get_fqfield("committee/5914213969/meeting_ids"): [7816466305, 3908439961],
        }


class MeetingCreateActionUnitTester(BaseMeetingCreateActionTester):
    def setUp(self) -> None:
        super().setUp()
        user_id = 7121641734
        self.action = MeetingCreate(
            "meeting.create",
            PermissionTestAdapter(superuser=user_id),
            DatabaseTestAdapter(datastore_content=self.datastore_content),
        )
        self.action.user_id = user_id

    def test_validation_empty(self) -> None:
        payload: ActionPayload = []
        with self.assertRaises(ActionException):
            self.action.validate(payload)

    def test_validation_empty_2(self) -> None:
        payload: ActionPayload = [{}]
        with self.assertRaises(ActionException):
            self.action.validate(payload)

    def test_validation_fuzzy(self) -> None:
        payload = [{"wrong_field": "text_aeBiPei0xi"}]
        with self.assertRaises(ActionException):
            self.action.validate(payload)

    def test_validation_correct_1(self) -> None:
        self.action.validate(self.valid_payload_1)

    def test_prepare_dataset_1(self) -> None:
        dataset = self.action.prepare_dataset(self.valid_payload_1)
        self.assertEqual(
            dataset["data"],
            [
                {
                    "instance": self.valid_payload_1[0],
                    "new_id": 42,
                    "relations": {
                        get_fqfield("committee/5914213969/meeting_ids"): {
                            "type": "add",
                            "value": [7816466305, 3908439961, 42],
                        },
                    },
                }
            ],
        )


class MeetingCreateActionPerformTester(BaseMeetingCreateActionTester):
    def setUp(self) -> None:
        super().setUp()
        self.user_id = 7121641734
        self.action = MeetingCreate(
            "meeting.create",
            PermissionTestAdapter(superuser=self.user_id),
            DatabaseTestAdapter(datastore_content=self.datastore_content),
        )

    def test_perform_empty(self) -> None:
        payload: ActionPayload = []
        with self.assertRaises(ActionException):
            self.action.perform(payload, user_id=self.user_id)

    def test_perform_empty_2(self) -> None:
        payload: ActionPayload = [{}]
        with self.assertRaises(ActionException):
            self.action.perform(payload, user_id=self.user_id)

    def test_perform_fuzzy(self) -> None:
        payload = [{"wrong_field": "text_Ohgahc3ieb"}]
        with self.assertRaises(ActionException):
            self.action.perform(payload, user_id=self.user_id)

    def test_perform_correct_1(self) -> None:
        write_request_elements = self.action.perform(
            self.valid_payload_1, user_id=self.user_id
        )
        result = list(write_request_elements)
        expected = [
            {
                "events": [
                    {
                        "type": "create",
                        "fqid": get_fqid("meeting/42"),
                        "fields": {
                            "committee_id": 5914213969,
                            "name": "name_zusae6aD0a",
                        },
                    },
                    {
                        "type": "update",
                        "fqid": get_fqid("committee/5914213969"),
                        "fields": {"meeting_ids": [7816466305, 3908439961, 42]},
                    },
                ],
                "information": {
                    get_fqid("meeting/42"): ["Object created"],
                    get_fqid("committee/5914213969"): ["Object attached to meeting"],
                },
                "user_id": self.user_id,
            },
        ]
        self.assertEqual(result, expected)

    def test_perform_no_permission_1(self) -> None:
        with self.assertRaises(PermissionDenied):
            self.action.perform(self.valid_payload_1, user_id=4796568680)


class MeetingCreateActionWSGITester(BaseMeetingCreateActionTester):
    def setUp(self) -> None:
        super().setUp()
        self.user_id = 7121641734

    def test_wsgi_request_empty(self) -> None:
        expected_write_data = ""
        client = Client(
            create_test_application(
                user_id=self.user_id,
                view_name="ActionsView",
                superuser=self.user_id,
                datastore_content=self.datastore_content,
                expected_write_data=expected_write_data,
            ),
            ResponseWrapper,
        )
        response = client.post("/", json=[{"action": "meeting.create", "data": [{}]}])
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "data[0] must contain [\\'committee_id\\', \\'name\\'] properties",
            str(response.data),
        )

    def test_wsgi_request_fuzzy(self) -> None:
        expected_write_data = ""
        client = Client(
            create_test_application(
                user_id=self.user_id,
                view_name="ActionsView",
                superuser=self.user_id,
                datastore_content=self.datastore_content,
                expected_write_data=expected_write_data,
            ),
            ResponseWrapper,
        )
        response = client.post(
            "/",
            json=[
                {
                    "action": "meeting.create",
                    "data": [{"wrong_field": "text_AefohteiF8"}],
                }
            ],
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "data[0] must contain [\\'committee_id\\', \\'name\\'] properties",
            str(response.data),
        )

    def test_wsgi_request_correct_1(self) -> None:
        expected_write_data = json.dumps(
            {
                "events": [
                    {
                        "type": "create",
                        "fqid": "meeting/42",
                        "fields": {
                            "committee_id": 5914213969,
                            "name": "name_zusae6aD0a",
                        },
                    },
                    {
                        "type": "update",
                        "fqid": "committee/5914213969",
                        "fields": {"meeting_ids": [7816466305, 3908439961, 42]},
                    },
                ],
                "information": {
                    "meeting/42": ["Object created"],
                    "committee/5914213969": ["Object attached to meeting"],
                },
                "user_id": self.user_id,
                "locked_fields": {"committee/5914213969": 1},
            }
        )
        client = Client(
            create_test_application(
                user_id=self.user_id,
                view_name="ActionsView",
                superuser=self.user_id,
                datastore_content=self.datastore_content,
                expected_write_data=expected_write_data,
            ),
            ResponseWrapper,
        )
        response = client.post(
            "/", json=[{"action": "meeting.create", "data": self.valid_payload_1}],
        )
        self.assertEqual(response.status_code, 200)


class MeetingCreateActionWSGITesterNoPermission(BaseMeetingCreateActionTester):
    def setUp(self) -> None:
        super().setUp()
        self.user_id_no_permission = 9707919439

    def test_wsgi_request_no_permission_1(self) -> None:
        expected_write_data = ""
        client = Client(
            create_test_application(
                user_id=self.user_id_no_permission,
                view_name="ActionsView",
                superuser=0,
                datastore_content=self.datastore_content,
                expected_write_data=expected_write_data,
            ),
            ResponseWrapper,
        )
        response = client.post(
            "/", json=[{"action": "meeting.create", "data": self.valid_payload_1}],
        )
        self.assertEqual(response.status_code, 403)


class BaseMeetingUpdateActionTester(TestCase):
    """
    Tests the meeting update action.
    """

    def setUp(self) -> None:
        self.valid_payload_1 = [{"id": 7816466305, "name": "name_GeiduDohx0"}]
        self.datastore_content = {
            get_fqfield("meeting/7816466305/committee_id"): 5914213969,
            get_fqfield("meeting/7816466305/topic_ids"): [1312354708],
        }


class MeetingUpdateActionUnitTester(BaseMeetingUpdateActionTester):
    def setUp(self) -> None:
        super().setUp()
        user_id = 7121641734
        self.action = MeetingUpdate(
            "meeting.update",
            PermissionTestAdapter(superuser=user_id),
            DatabaseTestAdapter(datastore_content=self.datastore_content),
        )
        self.action.user_id = user_id

    def test_validation_correct_1(self) -> None:
        self.action.validate(self.valid_payload_1)

    def test_prepare_dataset_1(self) -> None:
        dataset = self.action.prepare_dataset(self.valid_payload_1)
        self.assertEqual(
            dataset["data"], [{"instance": self.valid_payload_1[0], "relations": {}}],
        )


class MeetingUpdateActionPerformTester(BaseMeetingUpdateActionTester):
    def setUp(self) -> None:
        super().setUp()
        self.user_id = 7121641734
        self.action = MeetingUpdate(
            "meeting.update",
            PermissionTestAdapter(superuser=self.user_id),
            DatabaseTestAdapter(datastore_content=self.datastore_content),
        )

    def test_perform_correct_1(self) -> None:
        write_request_elements = self.action.perform(
            self.valid_payload_1, user_id=self.user_id
        )
        expected = [
            {
                "events": [
                    {
                        "type": "update",
                        "fqid": get_fqid("meeting/7816466305"),
                        "fields": {"name": "name_GeiduDohx0"},
                    },
                ],
                "information": {get_fqid("meeting/7816466305"): ["Object updated"]},
                "user_id": self.user_id,
            },
        ]
        result = list(write_request_elements)
        self.assertEqual(result, expected)


class MeetingUpdateActionWSGITester(BaseMeetingUpdateActionTester):
    def setUp(self) -> None:
        super().setUp()
        self.user_id = 7121641734

    def test_wsgi_request_correct_1(self) -> None:
        expected_write_data = json.dumps(
            {
                "events": [
                    {
                        "type": "update",
                        "fqid": "meeting/7816466305",
                        "fields": {"name": "name_GeiduDohx0"},
                    },
                ],
                "information": {"meeting/7816466305": ["Object updated"]},
                "user_id": self.user_id,
                # "locked_fields": {"meeting/7816466305": 1},
                "locked_fields": {},
            }
        )
        client = Client(
            create_test_application(
                user_id=self.user_id,
                view_name="ActionsView",
                superuser=self.user_id,
                datastore_content=self.datastore_content,
                expected_write_data=expected_write_data,
            ),
            ResponseWrapper,
        )
        response = client.post(
            "/", json=[{"action": "meeting.update", "data": self.valid_payload_1}],
        )
        self.assertEqual(response.status_code, 200)


class MeetingUpdateActionWSGITesterNoPermission(BaseMeetingUpdateActionTester):
    def setUp(self) -> None:
        super().setUp()
        self.user_id_no_permission = 9707919439

    def test_wsgi_request_no_permission_1(self) -> None:
        expected_write_data = ""
        client = Client(
            create_test_application(
                user_id=self.user_id_no_permission,
                view_name="ActionsView",
                superuser=0,
                datastore_content=self.datastore_content,
                expected_write_data=expected_write_data,
            ),
            ResponseWrapper,
        )
        response = client.post(
            "/", json=[{"action": "meeting.update", "data": self.valid_payload_1}],
        )
        self.assertEqual(response.status_code, 403)


class BaseMeetingDeleteActionTester(TestCase):
    """
    Tests the meeting delete action.
    """

    def setUp(self) -> None:
        self.valid_payload_1 = [{"id": 3908439961}]
        self.invalid_payload_1 = [
            {"id": 3908439961},
            {"id": 7816466305},
        ]
        self.datastore_content = {
            get_fqfield("meeting/3908439961/committee_id"): 5914213969,
            get_fqfield("meeting/7816466305/committee_id"): 5914213969,
            get_fqfield("committee/5914213969/meeting_ids"): [7816466305, 3908439961],
            get_fqfield("meeting/7816466305/topic_ids"): [1312354708],
            get_fqfield("topic/1312354708/meeting_ids"): 7816466305,
        }


class MeetingDeleteActionUnitTester(BaseMeetingDeleteActionTester):
    def setUp(self) -> None:
        super().setUp()
        user_id = 7121641734
        self.action = MeetingDelete(
            "meeting.delete",
            PermissionTestAdapter(superuser=user_id),
            DatabaseTestAdapter(datastore_content=self.datastore_content),
        )
        self.action.user_id = user_id

    def test_validation_correct_1(self) -> None:
        self.action.validate(self.valid_payload_1)

    def test_validation_correct_2(self) -> None:
        self.action.validate(self.invalid_payload_1)

    def test_prepare_dataset_1(self) -> None:
        dataset = self.action.prepare_dataset(self.valid_payload_1)
        self.assertEqual(
            dataset["data"],
            [
                {
                    "instance": {
                        "id": self.valid_payload_1[0]["id"],
                        "agenda_item_ids": None,
                        "committee_id": None,
                        "motion_ids": None,
                        "topic_ids": None,
                    },
                    "relations": {
                        get_fqfield("committee/5914213969/meeting_ids"): {
                            "type": "remove",
                            "value": [7816466305],
                        },
                    },
                }
            ],
        )

    def test_prepare_dataset_2(self) -> None:
        with self.assertRaises(ActionException) as context_manager:
            self.action.prepare_dataset(self.invalid_payload_1)
        self.assertEqual(
            context_manager.exception.message,
            "You are not allowed to delete meeting 7816466305 as long as there are "
            "some required related objects (see topic_ids).",
        )


class MeetingDeleteActionPerformTester(BaseMeetingDeleteActionTester):
    def setUp(self) -> None:
        super().setUp()
        self.user_id = 7121641734
        self.action = MeetingDelete(
            "meeting.delete",
            PermissionTestAdapter(superuser=self.user_id),
            DatabaseTestAdapter(datastore_content=self.datastore_content),
        )

    def test_perform_correct_1(self) -> None:
        write_request_elements = self.action.perform(
            self.valid_payload_1, user_id=self.user_id
        )
        expected = [
            {
                "events": [
                    {"type": "delete", "fqid": get_fqid("meeting/3908439961")},
                    {
                        "type": "update",
                        "fqid": get_fqid("committee/5914213969"),
                        "fields": {"meeting_ids": [7816466305]},
                    },
                ],
                "information": {
                    get_fqid("meeting/3908439961"): ["Object deleted"],
                    get_fqid("committee/5914213969"): [
                        "Object attachment to meeting reset"
                    ],
                },
                "user_id": self.user_id,
            },
        ]
        result = list(write_request_elements)
        self.assertEqual(result, expected)

    def test_perform_incorrect_1(self) -> None:
        with self.assertRaises(ActionException) as context_manager:
            self.action.perform(self.invalid_payload_1, user_id=self.user_id)
        self.assertEqual(
            context_manager.exception.message,
            "You are not allowed to delete meeting 7816466305 as long as there are "
            "some required related objects (see topic_ids).",
        )

    def test_perform_no_permission_1(self) -> None:
        with self.assertRaises(PermissionDenied):
            self.action.perform(self.valid_payload_1, user_id=4796568680)

    def test_perform_no_permission_2(self) -> None:
        with self.assertRaises(PermissionDenied):
            self.action.perform(self.invalid_payload_1, user_id=4796568680)


class MeetingDeleteActionWSGITester(BaseMeetingDeleteActionTester):
    def setUp(self) -> None:
        super().setUp()
        self.user_id = 7121641734

    def test_wsgi_request_correct_1(self) -> None:
        expected_write_data = json.dumps(
            {
                "events": [
                    {"type": "delete", "fqid": "meeting/3908439961"},
                    {
                        "type": "update",
                        "fqid": "committee/5914213969",
                        "fields": {"meeting_ids": [7816466305]},
                    },
                ],
                "information": {
                    "meeting/3908439961": ["Object deleted"],
                    "committee/5914213969": ["Object attachment to meeting reset"],
                },
                "user_id": self.user_id,
                "locked_fields": {"meeting/3908439961": 1, "committee/5914213969": 1},
            }
        )

        client = Client(
            create_test_application(
                user_id=self.user_id,
                view_name="ActionsView",
                superuser=self.user_id,
                datastore_content=self.datastore_content,
                expected_write_data=expected_write_data,
            ),
            ResponseWrapper,
        )
        response = client.post(
            "/", json=[{"action": "meeting.delete", "data": self.valid_payload_1}],
        )
        self.assertEqual(response.status_code, 200)

    def test_wsgi_request_incorrect_2(self) -> None:
        expected_write_data = ""
        client = Client(
            create_test_application(
                user_id=self.user_id,
                view_name="ActionsView",
                superuser=self.user_id,
                datastore_content=self.datastore_content,
                expected_write_data=expected_write_data,
            ),
            ResponseWrapper,
        )
        response = client.post(
            "/", json=[{"action": "meeting.delete", "data": self.invalid_payload_1}],
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "You are not allowed to delete meeting 7816466305 as long as there are "
            "some required related objects (see topic_ids).",
            str(response.data),
        )


class MeetingDeleteActionWSGITesterNoPermission(BaseMeetingDeleteActionTester):
    def setUp(self) -> None:
        super().setUp()
        self.user_id_no_permission = 9707919439

    def test_wsgi_request_no_permission_1(self) -> None:
        expected_write_data = ""
        client = Client(
            create_test_application(
                user_id=self.user_id_no_permission,
                view_name="ActionsView",
                superuser=0,
                datastore_content=self.datastore_content,
                expected_write_data=expected_write_data,
            ),
            ResponseWrapper,
        )
        response = client.post(
            "/", json=[{"action": "meeting.delete", "data": self.valid_payload_1}],
        )
        self.assertEqual(response.status_code, 403)

    def test_wsgi_request_no_permission_2(self) -> None:
        expected_write_data = ""
        client = Client(
            create_test_application(
                user_id=self.user_id_no_permission,
                view_name="ActionsView",
                superuser=0,
                datastore_content=self.datastore_content,
                expected_write_data=expected_write_data,
            ),
            ResponseWrapper,
        )
        response = client.post(
            "/", json=[{"action": "meeting.delete", "data": self.invalid_payload_1}],
        )
        self.assertEqual(response.status_code, 403)
