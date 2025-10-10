import urllib.parse
from unittest.mock import Mock

import pytest

from pi_web_sdk.controllers.event import EventFrameController


@pytest.fixture
def client_mock():
    mock = Mock()
    mock.get.return_value = {"result": "get"}
    mock.post.return_value = {"result": "post"}
    mock.patch.return_value = {"result": "patch"}
    mock.delete.return_value = {"result": "delete"}
    return mock


def test_get_event_frame_by_web_id(client_mock):
    controller = EventFrameController(client_mock)

    result = controller.get("EF1", selected_fields="Items")

    assert result == {"result": "get"}
    client_mock.get.assert_called_once_with(
        "eventframes/EF1", params={"selectedFields": "Items"}
    )


def test_get_event_frame_by_path_encodes_path(client_mock):
    controller = EventFrameController(client_mock)
    path = r"\\Server\AssetDb|EventFrame"

    controller.get_by_path(path, selected_fields="Name;WebId")

    encoded = urllib.parse.quote(path, safe="")
    client_mock.get.assert_called_once_with(
        f"eventframes/path/{encoded}",
        params={"selectedFields": "Name;WebId"},
    )


def test_create_event_frame(client_mock):
    controller = EventFrameController(client_mock)
    payload = {"Name": "Batch01"}

    result = controller.create("DB1", payload)

    assert result == {"result": "post"}
    client_mock.post.assert_called_once_with(
        "assetdatabases/DB1/eventframes", data=payload
    )


def test_get_event_frames_with_filters(client_mock):
    controller = EventFrameController(client_mock)

    controller.get_event_frames(
        database_web_id="DB1",
        name_filter="Batch*",
        category_name="Operations",
        template_name="BatchTemplate",
        start_time="*-1d",
        end_time="*",
        search_full_hierarchy=True,
        sort_field="Name",
        sort_order="Ascending",
        start_index=25,
        max_count=50,
        selected_fields="Items.Name;Items.WebId",
    )

    client_mock.get.assert_called_once_with(
        "assetdatabases/DB1/eventframes",
        params={
            "searchFullHierarchy": True,
            "startIndex": 25,
            "maxCount": 50,
            "nameFilter": "Batch*",
            "categoryName": "Operations",
            "templateName": "BatchTemplate",
            "startTime": "*-1d",
            "endTime": "*",
            "sortField": "Name",
            "sortOrder": "Ascending",
            "selectedFields": "Items.Name;Items.WebId",
        },
    )


def test_get_attributes_defaults(client_mock):
    controller = EventFrameController(client_mock)

    controller.get_attributes("EF1")

    client_mock.get.assert_called_once_with(
        "eventframes/EF1/attributes",
        params={"startIndex": 0, "maxCount": 1000},
    )


def test_create_attribute(client_mock):
    controller = EventFrameController(client_mock)
    attribute = {"Name": "Severity", "ValueType": "Int32"}

    result = controller.create_attribute("EF1", attribute)

    assert result == {"result": "post"}
    client_mock.post.assert_called_once_with(
        "eventframes/EF1/attributes", data=attribute
    )


def test_update_and_delete_event_frame(client_mock):
    controller = EventFrameController(client_mock)
    update_payload = {"Name": "Updated"}

    update_result = controller.update("EF1", update_payload)
    delete_result = controller.delete("EF1")

    assert update_result == {"result": "patch"}
    assert delete_result == {"result": "delete"}
    client_mock.patch.assert_called_once_with(
        "eventframes/EF1", data=update_payload
    )
    client_mock.delete.assert_called_once_with("eventframes/EF1")
