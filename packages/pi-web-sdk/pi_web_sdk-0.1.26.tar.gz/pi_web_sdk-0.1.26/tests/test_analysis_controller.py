"""Tests for Analysis controller methods."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from pi_web_sdk.controllers.analysis import (
    AnalysisController,
    AnalysisCategoryController,
    AnalysisRuleController,
    AnalysisRulePlugInController,
    AnalysisTemplateController,
)


@pytest.fixture
def mock_client():
    """Create a mock PIWebAPIClient."""
    return MagicMock()


@pytest.fixture
def analysis_controller(mock_client):
    """Create AnalysisController instance."""
    return AnalysisController(mock_client)


@pytest.fixture
def analysis_category_controller(mock_client):
    """Create AnalysisCategoryController instance."""
    return AnalysisCategoryController(mock_client)


@pytest.fixture
def analysis_rule_controller(mock_client):
    """Create AnalysisRuleController instance."""
    return AnalysisRuleController(mock_client)


@pytest.fixture
def analysis_rule_plugin_controller(mock_client):
    """Create AnalysisRulePlugInController instance."""
    return AnalysisRulePlugInController(mock_client)


@pytest.fixture
def analysis_template_controller(mock_client):
    """Create AnalysisTemplateController instance."""
    return AnalysisTemplateController(mock_client)


class TestAnalysisController:
    """Test AnalysisController methods."""

    def test_get(self, analysis_controller, mock_client):
        """Test get analysis by WebID."""
        mock_client.get.return_value = {
            "WebId": "A1AbC123",
            "Name": "Test Analysis",
            "Description": "Test description",
        }

        result = analysis_controller.get("A1AbC123")

        assert result["WebId"] == "A1AbC123"
        assert result["Name"] == "Test Analysis"
        mock_client.get.assert_called_once_with("analyses/A1AbC123", params={})

    def test_get_with_selected_fields(self, analysis_controller, mock_client):
        """Test get analysis with selected fields."""
        mock_client.get.return_value = {"WebId": "A1AbC123", "Name": "Test Analysis"}

        result = analysis_controller.get("A1AbC123", selected_fields="WebId;Name")

        assert result["Name"] == "Test Analysis"
        mock_client.get.assert_called_once_with(
            "analyses/A1AbC123",
            params={"selectedFields": "WebId;Name"}
        )

    def test_get_by_path(self, analysis_controller, mock_client):
        """Test get analysis by path."""
        mock_client.get.return_value = {
            "WebId": "A1AbC123",
            "Path": r"\\AF-SERVER\Database\Element|Analysis",
        }

        result = analysis_controller.get_by_path(r"\\AF-SERVER\Database\Element|Analysis")

        assert result["WebId"] == "A1AbC123"
        mock_client.get.assert_called_once()

    def test_update(self, analysis_controller, mock_client):
        """Test update analysis."""
        mock_client.patch.return_value = {"WebId": "A1AbC123"}

        result = analysis_controller.update("A1AbC123", {"Description": "Updated"})

        assert result["WebId"] == "A1AbC123"
        mock_client.patch.assert_called_once_with(
            "analyses/A1AbC123",
            data={"Description": "Updated"}
        )

    def test_delete(self, analysis_controller, mock_client):
        """Test delete analysis."""
        mock_client.delete.return_value = {}

        result = analysis_controller.delete("A1AbC123")

        assert result == {}
        mock_client.delete.assert_called_once_with("analyses/A1AbC123")

    def test_get_categories(self, analysis_controller, mock_client):
        """Test get categories for analysis."""
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "C1", "Name": "Category1"},
                {"WebId": "C2", "Name": "Category2"},
            ]
        }

        result = analysis_controller.get_categories("A1AbC123")

        assert len(result["Items"]) == 2
        assert result["Items"][0]["Name"] == "Category1"
        mock_client.get.assert_called_once_with(
            "analyses/A1AbC123/categories",
            params={}
        )

    def test_get_security(self, analysis_controller, mock_client):
        """Test get security for analysis."""
        mock_client.get.return_value = {
            "CanRead": True,
            "CanWrite": False,
        }

        result = analysis_controller.get_security("A1AbC123")

        assert result["CanRead"] is True
        mock_client.get.assert_called_once_with(
            "analyses/A1AbC123/security",
            params={}
        )

    def test_get_security_with_params(self, analysis_controller, mock_client):
        """Test get security with parameters."""
        mock_client.get.return_value = {"CanRead": True}

        result = analysis_controller.get_security(
            "A1AbC123",
            user_identity="DOMAIN\\User",
            force_refresh=True
        )

        assert result["CanRead"] is True
        mock_client.get.assert_called_once_with(
            "analyses/A1AbC123/security",
            params={"userIdentity": "DOMAIN\\User", "forceRefresh": True}
        )

    def test_get_security_entries(self, analysis_controller, mock_client):
        """Test get security entries for analysis."""
        mock_client.get.return_value = {
            "Items": [
                {"Name": "DOMAIN\\User1", "SecurityRights": "Read"},
                {"Name": "DOMAIN\\User2", "SecurityRights": "ReadWrite"},
            ]
        }

        result = analysis_controller.get_security_entries("A1AbC123")

        assert len(result["Items"]) == 2
        mock_client.get.assert_called_once_with(
            "analyses/A1AbC123/securityentries",
            params={}
        )

    def test_get_security_entry_by_name(self, analysis_controller, mock_client):
        """Test get security entry by name."""
        mock_client.get.return_value = {
            "Name": "DOMAIN\\User",
            "SecurityRights": "Read"
        }

        result = analysis_controller.get_security_entry_by_name(
            "A1AbC123",
            "DOMAIN\\User"
        )

        assert result["Name"] == "DOMAIN\\User"
        mock_client.get.assert_called_once()

    def test_create_security_entry(self, analysis_controller, mock_client):
        """Test create security entry."""
        mock_client.post.return_value = {"WebId": "SE1"}

        result = analysis_controller.create_security_entry(
            "A1AbC123",
            {"Name": "DOMAIN\\User", "SecurityRights": "Read"}
        )

        assert result["WebId"] == "SE1"
        mock_client.post.assert_called_once_with(
            "analyses/A1AbC123/securityentries",
            data={"Name": "DOMAIN\\User", "SecurityRights": "Read"},
            params={}
        )

    def test_create_security_entry_with_children(self, analysis_controller, mock_client):
        """Test create security entry with apply to children."""
        mock_client.post.return_value = {"WebId": "SE1"}

        result = analysis_controller.create_security_entry(
            "A1AbC123",
            {"Name": "DOMAIN\\User", "SecurityRights": "Read"},
            apply_to_children=True
        )

        assert result["WebId"] == "SE1"
        mock_client.post.assert_called_once_with(
            "analyses/A1AbC123/securityentries",
            data={"Name": "DOMAIN\\User", "SecurityRights": "Read"},
            params={"applyToChildren": True}
        )

    def test_update_security_entry(self, analysis_controller, mock_client):
        """Test update security entry."""
        mock_client.put.return_value = {}

        result = analysis_controller.update_security_entry(
            "A1AbC123",
            "DOMAIN\\User",
            {"SecurityRights": "ReadWrite"}
        )

        assert result == {}
        mock_client.put.assert_called_once()

    def test_delete_security_entry(self, analysis_controller, mock_client):
        """Test delete security entry."""
        mock_client.delete.return_value = {}

        result = analysis_controller.delete_security_entry(
            "A1AbC123",
            "DOMAIN\\User"
        )

        assert result == {}
        mock_client.delete.assert_called_once()


class TestAnalysisCategoryController:
    """Test AnalysisCategoryController methods."""

    def test_get(self, analysis_category_controller, mock_client):
        """Test get analysis category by WebID."""
        mock_client.get.return_value = {
            "WebId": "AC1",
            "Name": "Production",
        }

        result = analysis_category_controller.get("AC1")

        assert result["WebId"] == "AC1"
        assert result["Name"] == "Production"
        mock_client.get.assert_called_once_with("analysiscategories/AC1", params={})

    def test_get_by_path(self, analysis_category_controller, mock_client):
        """Test get analysis category by path."""
        mock_client.get.return_value = {
            "WebId": "AC1",
            "Path": r"\\AF-SERVER\Database|Production",
        }

        result = analysis_category_controller.get_by_path(r"\\AF-SERVER\Database|Production")

        assert result["WebId"] == "AC1"
        mock_client.get.assert_called_once()

    def test_update(self, analysis_category_controller, mock_client):
        """Test update analysis category."""
        mock_client.patch.return_value = {"WebId": "AC1"}

        result = analysis_category_controller.update("AC1", {"Description": "Updated"})

        assert result["WebId"] == "AC1"
        mock_client.patch.assert_called_once_with(
            "analysiscategories/AC1",
            data={"Description": "Updated"}
        )

    def test_delete(self, analysis_category_controller, mock_client):
        """Test delete analysis category."""
        mock_client.delete.return_value = {}

        result = analysis_category_controller.delete("AC1")

        assert result == {}
        mock_client.delete.assert_called_once_with("analysiscategories/AC1")

    def test_get_security(self, analysis_category_controller, mock_client):
        """Test get security for analysis category."""
        mock_client.get.return_value = {"CanRead": True}

        result = analysis_category_controller.get_security("AC1")

        assert result["CanRead"] is True
        mock_client.get.assert_called_once_with(
            "analysiscategories/AC1/security",
            params={}
        )


class TestAnalysisRuleController:
    """Test AnalysisRuleController methods."""

    def test_get(self, analysis_rule_controller, mock_client):
        """Test get analysis rule by WebID."""
        mock_client.get.return_value = {
            "WebId": "AR1",
            "Name": "Rule1",
            "PlugIn": "PerformanceEquation",
        }

        result = analysis_rule_controller.get("AR1")

        assert result["WebId"] == "AR1"
        assert result["PlugIn"] == "PerformanceEquation"
        mock_client.get.assert_called_once_with("analysisrules/AR1", params={})

    def test_get_by_path(self, analysis_rule_controller, mock_client):
        """Test get analysis rule by path."""
        mock_client.get.return_value = {
            "WebId": "AR1",
            "Path": r"\\AF-SERVER\Database\Analysis|Rule",
        }

        result = analysis_rule_controller.get_by_path(r"\\AF-SERVER\Database\Analysis|Rule")

        assert result["WebId"] == "AR1"
        mock_client.get.assert_called_once()

    def test_update(self, analysis_rule_controller, mock_client):
        """Test update analysis rule."""
        mock_client.patch.return_value = {"WebId": "AR1"}

        result = analysis_rule_controller.update("AR1", {"ConfigString": "Updated"})

        assert result["WebId"] == "AR1"
        mock_client.patch.assert_called_once_with(
            "analysisrules/AR1",
            data={"ConfigString": "Updated"}
        )

    def test_delete(self, analysis_rule_controller, mock_client):
        """Test delete analysis rule."""
        mock_client.delete.return_value = {}

        result = analysis_rule_controller.delete("AR1")

        assert result == {}
        mock_client.delete.assert_called_once_with("analysisrules/AR1")

    def test_get_analysis_rules(self, analysis_rule_controller, mock_client):
        """Test get analysis rules."""
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "AR1", "Name": "Rule1"},
                {"WebId": "AR2", "Name": "Rule2"},
            ]
        }

        result = analysis_rule_controller.get_analysis_rules(
            "A1",
            name_filter="*temp*",
            search_full_hierarchy=True
        )

        assert len(result["Items"]) == 2
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert call_args[0][0] == "analysisrules/A1/analysisrules"
        assert call_args[1]["params"]["nameFilter"] == "*temp*"
        assert call_args[1]["params"]["searchFullHierarchy"] is True

    def test_create_analysis_rule(self, analysis_rule_controller, mock_client):
        """Test create analysis rule."""
        mock_client.post.return_value = {"WebId": "AR1"}

        result = analysis_rule_controller.create_analysis_rule(
            "A1",
            {"Name": "NewRule", "PlugIn": "PerformanceEquation"}
        )

        assert result["WebId"] == "AR1"
        mock_client.post.assert_called_once_with(
            "analysisrules/A1/analysisrules",
            data={"Name": "NewRule", "PlugIn": "PerformanceEquation"}
        )


class TestAnalysisRulePlugInController:
    """Test AnalysisRulePlugInController methods."""

    def test_get(self, analysis_rule_plugin_controller, mock_client):
        """Test get analysis rule plug-in by WebID."""
        mock_client.get.return_value = {
            "WebId": "ARP1",
            "Name": "PerformanceEquation",
        }

        result = analysis_rule_plugin_controller.get("ARP1")

        assert result["WebId"] == "ARP1"
        assert result["Name"] == "PerformanceEquation"
        mock_client.get.assert_called_once_with("analysisruleplugins/ARP1", params={})

    def test_get_by_path(self, analysis_rule_plugin_controller, mock_client):
        """Test get analysis rule plug-in by path."""
        mock_client.get.return_value = {
            "WebId": "ARP1",
            "Path": r"\\AF-SERVER|PerformanceEquation",
        }

        result = analysis_rule_plugin_controller.get_by_path(r"\\AF-SERVER|PerformanceEquation")

        assert result["WebId"] == "ARP1"
        mock_client.get.assert_called_once()


class TestAnalysisTemplateController:
    """Test AnalysisTemplateController methods."""

    def test_get(self, analysis_template_controller, mock_client):
        """Test get analysis template by WebID."""
        mock_client.get.return_value = {
            "WebId": "AT1",
            "Name": "Template1",
        }

        result = analysis_template_controller.get("AT1")

        assert result["WebId"] == "AT1"
        assert result["Name"] == "Template1"
        mock_client.get.assert_called_once_with("analysistemplates/AT1", params={})

    def test_get_by_path(self, analysis_template_controller, mock_client):
        """Test get analysis template by path."""
        mock_client.get.return_value = {
            "WebId": "AT1",
            "Path": r"\\AF-SERVER\Database|Template",
        }

        result = analysis_template_controller.get_by_path(r"\\AF-SERVER\Database|Template")

        assert result["WebId"] == "AT1"
        mock_client.get.assert_called_once()

    def test_update(self, analysis_template_controller, mock_client):
        """Test update analysis template."""
        mock_client.patch.return_value = {"WebId": "AT1"}

        result = analysis_template_controller.update("AT1", {"Description": "Updated"})

        assert result["WebId"] == "AT1"
        mock_client.patch.assert_called_once_with(
            "analysistemplates/AT1",
            data={"Description": "Updated"}
        )

    def test_delete(self, analysis_template_controller, mock_client):
        """Test delete analysis template."""
        mock_client.delete.return_value = {}

        result = analysis_template_controller.delete("AT1")

        assert result == {}
        mock_client.delete.assert_called_once_with("analysistemplates/AT1")

    def test_create_from_analysis(self, analysis_template_controller, mock_client):
        """Test create template from analysis."""
        mock_client.post.return_value = {"WebId": "AT1", "Name": "NewTemplate"}

        result = analysis_template_controller.create_from_analysis("A1", name="NewTemplate")

        assert result["WebId"] == "AT1"
        mock_client.post.assert_called_once_with(
            "analyses/A1/analysistemplate",
            params={"name": "NewTemplate"}
        )

    def test_create_from_analysis_no_name(self, analysis_template_controller, mock_client):
        """Test create template from analysis without name."""
        mock_client.post.return_value = {"WebId": "AT1"}

        result = analysis_template_controller.create_from_analysis("A1")

        assert result["WebId"] == "AT1"
        mock_client.post.assert_called_once_with(
            "analyses/A1/analysistemplate",
            params={}
        )

    def test_get_categories(self, analysis_template_controller, mock_client):
        """Test get categories for analysis template."""
        mock_client.get.return_value = {
            "Items": [
                {"WebId": "C1", "Name": "Category1"},
            ]
        }

        result = analysis_template_controller.get_categories("AT1")

        assert len(result["Items"]) == 1
        mock_client.get.assert_called_once_with(
            "analysistemplates/AT1/categories",
            params={}
        )

    def test_get_security(self, analysis_template_controller, mock_client):
        """Test get security for analysis template."""
        mock_client.get.return_value = {"CanRead": True}

        result = analysis_template_controller.get_security("AT1")

        assert result["CanRead"] is True
        mock_client.get.assert_called_once_with(
            "analysistemplates/AT1/security",
            params={}
        )

    def test_get_security_entries(self, analysis_template_controller, mock_client):
        """Test get security entries for analysis template."""
        mock_client.get.return_value = {
            "Items": [
                {"Name": "DOMAIN\\User", "SecurityRights": "Read"},
            ]
        }

        result = analysis_template_controller.get_security_entries("AT1")

        assert len(result["Items"]) == 1
        mock_client.get.assert_called_once_with(
            "analysistemplates/AT1/securityentries",
            params={}
        )

    def test_create_security_entry(self, analysis_template_controller, mock_client):
        """Test create security entry for analysis template."""
        mock_client.post.return_value = {"WebId": "SE1"}

        result = analysis_template_controller.create_security_entry(
            "AT1",
            {"Name": "DOMAIN\\User", "SecurityRights": "Read"}
        )

        assert result["WebId"] == "SE1"
        mock_client.post.assert_called_once_with(
            "analysistemplates/AT1/securityentries",
            data={"Name": "DOMAIN\\User", "SecurityRights": "Read"},
            params={}
        )
