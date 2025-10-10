"""Tests for Table and TableCategory controllers."""

import pytest
from unittest.mock import MagicMock
from pi_web_sdk.controllers.table import TableController, TableCategoryController


@pytest.fixture
def mock_client():
    """Create a mock client."""
    client = MagicMock()
    return client


@pytest.fixture
def table_controller(mock_client):
    """Create a TableController with mock client."""
    return TableController(mock_client)


@pytest.fixture
def table_category_controller(mock_client):
    """Create a TableCategoryController with mock client."""
    return TableCategoryController(mock_client)


class TestTableController:
    """Tests for TableController."""

    def test_get(self, table_controller, mock_client):
        """Test get table by WebID."""
        mock_client.get.return_value = {"WebId": "F1Tb123", "Name": "MyTable"}

        result = table_controller.get("F1Tb123")

        mock_client.get.assert_called_once_with("tables/F1Tb123", params={})
        assert result["Name"] == "MyTable"

    def test_get_by_path(self, table_controller, mock_client):
        """Test get table by path."""
        mock_client.get.return_value = {"WebId": "F1Tb123"}

        result = table_controller.get_by_path("\\\\SERVER\\DB\\MyTable")

        # Verify path encoding was called
        assert mock_client.get.called
        call_args = mock_client.get.call_args
        assert "tables/path/" in call_args[0][0]

    def test_update(self, table_controller, mock_client):
        """Test update table."""
        table_data = {"Name": "UpdatedTable", "Description": "New desc"}
        mock_client.patch.return_value = {}

        table_controller.update("F1Tb123", table_data)

        mock_client.patch.assert_called_once_with(
            "tables/F1Tb123",
            data=table_data
        )

    def test_delete(self, table_controller, mock_client):
        """Test delete table."""
        mock_client.delete.return_value = {}

        table_controller.delete("F1Tb123")

        mock_client.delete.assert_called_once_with("tables/F1Tb123")

    def test_get_categories(self, table_controller, mock_client):
        """Test get categories for table."""
        mock_client.get.return_value = {"Items": [{"Name": "Cat1"}]}

        result = table_controller.get_categories("F1Tb123")

        mock_client.get.assert_called_once_with(
            "tables/F1Tb123/categories",
            params={}
        )

    def test_get_data(self, table_controller, mock_client):
        """Test get table data."""
        mock_client.get.return_value = {
            "Rows": [[1, 2, 3]],
            "Columns": ["A", "B", "C"]
        }

        result = table_controller.get_data("F1Tb123")

        mock_client.get.assert_called_once_with("tables/F1Tb123/data", params={})
        assert "Rows" in result

    def test_update_data(self, table_controller, mock_client):
        """Test update table data."""
        data = {"Rows": [[1, 2]], "Columns": ["X", "Y"]}
        mock_client.put.return_value = {}

        table_controller.update_data("F1Tb123", data)

        mock_client.put.assert_called_once_with("tables/F1Tb123/data", data=data)

    def test_get_security(self, table_controller, mock_client):
        """Test get security for table."""
        mock_client.get.return_value = {"CanRead": True, "CanWrite": False}

        result = table_controller.get_security(
            "F1Tb123",
            user_identity="DOMAIN\\User",
            force_refresh=True
        )

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "tables/F1Tb123/security"
        assert call_args[1]["params"]["userIdentity"] == "DOMAIN\\User"
        assert call_args[1]["params"]["forceRefresh"] is True

    def test_get_security_entries(self, table_controller, mock_client):
        """Test get security entries."""
        mock_client.get.return_value = {"Items": []}

        result = table_controller.get_security_entries("F1Tb123", name_filter="Admin*")

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "securityentries" in call_args[0][0]

    def test_create_security_entry(self, table_controller, mock_client):
        """Test create security entry."""
        entry = {"Name": "Admin", "SecurityIdentityName": "DOMAIN\\Admin"}
        mock_client.post.return_value = {}

        table_controller.create_security_entry("F1Tb123", entry)

        mock_client.post.assert_called_once_with(
            "tables/F1Tb123/securityentries",
            data=entry
        )

    def test_update_security_entry(self, table_controller, mock_client):
        """Test update security entry."""
        entry = {"AllowRead": True, "AllowWrite": False}
        mock_client.put.return_value = {}

        table_controller.update_security_entry("F1Tb123", "Admin", entry)

        assert mock_client.put.called
        call_args = mock_client.put.call_args
        assert "securityentries" in call_args[0][0]

    def test_delete_security_entry(self, table_controller, mock_client):
        """Test delete security entry."""
        mock_client.delete.return_value = {}

        table_controller.delete_security_entry("F1Tb123", "Admin")

        assert mock_client.delete.called
        call_args = mock_client.delete.call_args
        assert "securityentries" in call_args[0][0]


class TestTableCategoryController:
    """Tests for TableCategoryController."""

    def test_get(self, table_category_controller, mock_client):
        """Test get table category by WebID."""
        mock_client.get.return_value = {"WebId": "F1TbCat123", "Name": "Category"}

        result = table_category_controller.get("F1TbCat123")

        mock_client.get.assert_called_once_with("tablecategories/F1TbCat123", params={})
        assert result["Name"] == "Category"

    def test_get_by_path(self, table_category_controller, mock_client):
        """Test get table category by path."""
        mock_client.get.return_value = {"WebId": "F1TbCat123"}

        result = table_category_controller.get_by_path("\\\\SERVER\\DB\\Category")

        assert mock_client.get.called
        call_args = mock_client.get.call_args
        assert "tablecategories/path/" in call_args[0][0]

    def test_update(self, table_category_controller, mock_client):
        """Test update table category."""
        category_data = {"Name": "UpdatedCategory"}
        mock_client.patch.return_value = {}

        table_category_controller.update("F1TbCat123", category_data)

        mock_client.patch.assert_called_once_with(
            "tablecategories/F1TbCat123",
            data=category_data
        )

    def test_delete(self, table_category_controller, mock_client):
        """Test delete table category."""
        mock_client.delete.return_value = {}

        table_category_controller.delete("F1TbCat123")

        mock_client.delete.assert_called_once_with("tablecategories/F1TbCat123")

    def test_get_security(self, table_category_controller, mock_client):
        """Test get security for table category."""
        mock_client.get.return_value = {"CanRead": True}

        result = table_category_controller.get_security("F1TbCat123")

        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert "tablecategories/F1TbCat123/security" in call_args[0][0]

    def test_create_security_entry(self, table_category_controller, mock_client):
        """Test create security entry for table category."""
        entry = {"Name": "Admin"}
        mock_client.post.return_value = {}

        table_category_controller.create_security_entry("F1TbCat123", entry)

        mock_client.post.assert_called_once_with(
            "tablecategories/F1TbCat123/securityentries",
            data=entry
        )
