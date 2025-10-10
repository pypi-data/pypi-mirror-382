"""Controllers for analysis-related endpoints."""

from __future__ import annotations

from typing import Dict, Optional, Union

from .base import BaseController
from ..models.analysis import Analysis, AnalysisCategory, AnalysisRule, AnalysisTemplate

__all__ = [
    'AnalysisController',
    'AnalysisCategoryController',
    'AnalysisRuleController',
    'AnalysisRulePlugInController',
    'AnalysisTemplateController',
]


class AnalysisController(BaseController):
    """Controller for Analysis operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get analysis by WebID.
        
        Args:
            web_id: WebID of the analysis
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Analysis dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analyses/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get analysis by path.
        
        Args:
            path: Path to the analysis
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Analysis dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"analyses/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, analysis: Union[Analysis, Dict]) -> Dict:
        """Update an analysis.
        
        Args:
            web_id: WebID of the analysis to update
            analysis: Analysis model instance or dictionary with analysis data
            
        Returns:
            Updated analysis response
        """
        data = analysis.to_dict() if isinstance(analysis, Analysis) else analysis
        return self.client.patch(f"analyses/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an analysis.
        
        Args:
            web_id: WebID of the analysis to delete
            
        Returns:
            Delete response
        """
        return self.client.delete(f"analyses/{web_id}")

    def get_categories(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get categories for an analysis.
        
        Args:
            web_id: WebID of the analysis
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Dictionary containing Items array with category data
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analyses/{web_id}/categories", params=params)

    def get_security(
        self,
        web_id: str,
        user_identity: Optional[str] = None,
        force_refresh: bool = False,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security information for an analysis.
        
        Args:
            web_id: WebID of the analysis
            user_identity: Optional user identity filter
            force_refresh: Force refresh from the server
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Security information dictionary
        """
        params = {}
        if user_identity:
            params["userIdentity"] = user_identity
        if force_refresh:
            params["forceRefresh"] = force_refresh
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analyses/{web_id}/security", params=params)

    def get_security_entries(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entries for an analysis.
        
        Args:
            web_id: WebID of the analysis
            name_filter: Optional name filter pattern
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Dictionary containing Items array with security entry data
        """
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analyses/{web_id}/securityentries", params=params)

    def get_security_entry_by_name(
        self,
        web_id: str,
        name: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entry by name for an analysis.
        
        Args:
            web_id: WebID of the analysis
            name: Name of the security entry
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Security entry dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"analyses/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )

    def create_security_entry(
        self,
        web_id: str,
        security_entry: Dict,
        apply_to_children: bool = False
    ) -> Dict:
        """Create a security entry for the analysis.
        
        Args:
            web_id: WebID of the analysis
            security_entry: Security entry data
            apply_to_children: Apply to child objects
            
        Returns:
            Created security entry response
        """
        params = {}
        if apply_to_children:
            params["applyToChildren"] = apply_to_children
        return self.client.post(
            f"analyses/{web_id}/securityentries",
            data=security_entry,
            params=params
        )

    def update_security_entry(
        self,
        web_id: str,
        name: str,
        security_entry: Dict,
        apply_to_children: bool = False
    ) -> Dict:
        """Update a security entry for the analysis.
        
        Args:
            web_id: WebID of the analysis
            name: Name of the security entry
            security_entry: Security entry data
            apply_to_children: Apply to child objects
            
        Returns:
            Updated security entry response
        """
        params = {}
        if apply_to_children:
            params["applyToChildren"] = apply_to_children
        return self.client.put(
            f"analyses/{web_id}/securityentries/{self._encode_path(name)}",
            data=security_entry,
            params=params
        )

    def delete_security_entry(
        self,
        web_id: str,
        name: str,
        apply_to_children: bool = False
    ) -> Dict:
        """Delete a security entry from the analysis.
        
        Args:
            web_id: WebID of the analysis
            name: Name of the security entry
            apply_to_children: Apply to child objects
            
        Returns:
            Delete response
        """
        params = {}
        if apply_to_children:
            params["applyToChildren"] = apply_to_children
        return self.client.delete(
            f"analyses/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )


class AnalysisCategoryController(BaseController):
    """Controller for Analysis Category operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get analysis category by WebID.
        
        Args:
            web_id: WebID of the analysis category
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Analysis category dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analysiscategories/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get analysis category by path.
        
        Args:
            path: Path to the analysis category
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Analysis category dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"analysiscategories/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, category: Union[AnalysisCategory, Dict]) -> Dict:
        """Update an analysis category.
        
        Args:
            web_id: WebID of the category to update
            category: AnalysisCategory model instance or dictionary with category data
            
        Returns:
            Updated category response
        """
        data = category.to_dict() if isinstance(category, AnalysisCategory) else category
        return self.client.patch(f"analysiscategories/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an analysis category.
        
        Args:
            web_id: WebID of the category to delete
            
        Returns:
            Delete response
        """
        return self.client.delete(f"analysiscategories/{web_id}")

    def get_security(
        self,
        web_id: str,
        user_identity: Optional[str] = None,
        force_refresh: bool = False,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security information for an analysis category.
        
        Args:
            web_id: WebID of the analysis category
            user_identity: Optional user identity filter
            force_refresh: Force refresh from the server
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Security information dictionary
        """
        params = {}
        if user_identity:
            params["userIdentity"] = user_identity
        if force_refresh:
            params["forceRefresh"] = force_refresh
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analysiscategories/{web_id}/security", params=params)

    def get_security_entries(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entries for an analysis category.
        
        Args:
            web_id: WebID of the analysis category
            name_filter: Optional name filter pattern
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Dictionary containing Items array with security entry data
        """
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analysiscategories/{web_id}/securityentries", params=params)

    def get_security_entry_by_name(
        self,
        web_id: str,
        name: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entry by name for an analysis category.
        
        Args:
            web_id: WebID of the analysis category
            name: Name of the security entry
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Security entry dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"analysiscategories/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )

    def create_security_entry(
        self,
        web_id: str,
        security_entry: Dict,
        apply_to_children: bool = False
    ) -> Dict:
        """Create a security entry for the analysis category.
        
        Args:
            web_id: WebID of the analysis category
            security_entry: Security entry data
            apply_to_children: Apply to child objects
            
        Returns:
            Created security entry response
        """
        params = {}
        if apply_to_children:
            params["applyToChildren"] = apply_to_children
        return self.client.post(
            f"analysiscategories/{web_id}/securityentries",
            data=security_entry,
            params=params
        )

    def update_security_entry(
        self,
        web_id: str,
        name: str,
        security_entry: Dict,
        apply_to_children: bool = False
    ) -> Dict:
        """Update a security entry for the analysis category.
        
        Args:
            web_id: WebID of the analysis category
            name: Name of the security entry
            security_entry: Security entry data
            apply_to_children: Apply to child objects
            
        Returns:
            Updated security entry response
        """
        params = {}
        if apply_to_children:
            params["applyToChildren"] = apply_to_children
        return self.client.put(
            f"analysiscategories/{web_id}/securityentries/{self._encode_path(name)}",
            data=security_entry,
            params=params
        )

    def delete_security_entry(
        self,
        web_id: str,
        name: str,
        apply_to_children: bool = False
    ) -> Dict:
        """Delete a security entry from the analysis category.
        
        Args:
            web_id: WebID of the analysis category
            name: Name of the security entry
            apply_to_children: Apply to child objects
            
        Returns:
            Delete response
        """
        params = {}
        if apply_to_children:
            params["applyToChildren"] = apply_to_children
        return self.client.delete(
            f"analysiscategories/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )


class AnalysisRuleController(BaseController):
    """Controller for Analysis Rule operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get analysis rule by WebID.
        
        Args:
            web_id: WebID of the analysis rule
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Analysis rule dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analysisrules/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get analysis rule by path.
        
        Args:
            path: Path to the analysis rule
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Analysis rule dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"analysisrules/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, rule: Union[AnalysisRule, Dict]) -> Dict:
        """Update an analysis rule.
        
        Args:
            web_id: WebID of the rule to update
            rule: AnalysisRule model instance or dictionary with rule data
            
        Returns:
            Updated rule response
        """
        data = rule.to_dict() if isinstance(rule, AnalysisRule) else rule
        return self.client.patch(f"analysisrules/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an analysis rule.
        
        Args:
            web_id: WebID of the rule to delete
            
        Returns:
            Delete response
        """
        return self.client.delete(f"analysisrules/{web_id}")

    def get_analysis_rules(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        search_full_hierarchy: bool = False,
        selected_fields: Optional[str] = None,
        sort_field: Optional[str] = None,
        sort_order: Optional[str] = None,
        start_index: int = 0,
        max_count: int = 1000,
    ) -> Dict:
        """Get analysis rules for a parent analysis or template.
        
        Args:
            web_id: WebID of the parent
            name_filter: Optional name filter pattern
            search_full_hierarchy: Search full hierarchy
            selected_fields: Optional semicolon-delimited list of fields to include
            sort_field: Field to sort by
            sort_order: Sort order (Ascending or Descending)
            start_index: Starting index for pagination
            max_count: Maximum number of items to return
            
        Returns:
            Dictionary containing Items array with analysis rule data
        """
        params = {
            "startIndex": start_index,
            "maxCount": max_count,
            "searchFullHierarchy": search_full_hierarchy,
        }
        if name_filter:
            params["nameFilter"] = name_filter
        if sort_field:
            params["sortField"] = sort_field
        if sort_order:
            params["sortOrder"] = sort_order
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analysisrules/{web_id}/analysisrules", params=params)

    def create_analysis_rule(self, web_id: str, rule: Union[AnalysisRule, Dict]) -> Dict:
        """Create an analysis rule.
        
        Args:
            web_id: WebID of the parent analysis or template
            rule: AnalysisRule model instance or dictionary with rule data
            
        Returns:
            Created rule response
        """
        data = rule.to_dict() if isinstance(rule, AnalysisRule) else rule
        return self.client.post(f"analysisrules/{web_id}/analysisrules", data=data)


class AnalysisRulePlugInController(BaseController):
    """Controller for Analysis Rule Plug-in operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get analysis rule plug-in by WebID.
        
        Args:
            web_id: WebID of the analysis rule plug-in
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Analysis rule plug-in dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analysisruleplugins/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get analysis rule plug-in by path.
        
        Args:
            path: Path to the analysis rule plug-in
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Analysis rule plug-in dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"analysisruleplugins/path/{self._encode_path(path)}", params=params
        )


class AnalysisTemplateController(BaseController):
    """Controller for Analysis Template operations."""

    def get(self, web_id: str, selected_fields: Optional[str] = None) -> Dict:
        """Get analysis template by WebID.
        
        Args:
            web_id: WebID of the analysis template
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Analysis template dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analysistemplates/{web_id}", params=params)

    def get_by_path(self, path: str, selected_fields: Optional[str] = None) -> Dict:
        """Get analysis template by path.
        
        Args:
            path: Path to the analysis template
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Analysis template dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"analysistemplates/path/{self._encode_path(path)}", params=params
        )

    def update(self, web_id: str, template: Union[AnalysisTemplate, Dict]) -> Dict:
        """Update an analysis template.
        
        Args:
            web_id: WebID of the template to update
            template: AnalysisTemplate model instance or dictionary with template data
            
        Returns:
            Updated template response
        """
        data = template.to_dict() if isinstance(template, AnalysisTemplate) else template
        return self.client.patch(f"analysistemplates/{web_id}", data=data)

    def delete(self, web_id: str) -> Dict:
        """Delete an analysis template.
        
        Args:
            web_id: WebID of the template to delete
            
        Returns:
            Delete response
        """
        return self.client.delete(f"analysistemplates/{web_id}")

    def create_from_analysis(self, web_id: str, name: Optional[str] = None) -> Dict:
        """Create an analysis template from an existing analysis.
        
        Args:
            web_id: WebID of the source analysis
            name: Optional name for the new template
            
        Returns:
            Created template response
        """
        params = {}
        if name:
            params["name"] = name
        return self.client.post(f"analyses/{web_id}/analysistemplate", params=params)

    def get_categories(
        self,
        web_id: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get categories for an analysis template.
        
        Args:
            web_id: WebID of the analysis template
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Dictionary containing Items array with category data
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analysistemplates/{web_id}/categories", params=params)

    def get_security(
        self,
        web_id: str,
        user_identity: Optional[str] = None,
        force_refresh: bool = False,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security information for an analysis template.
        
        Args:
            web_id: WebID of the analysis template
            user_identity: Optional user identity filter
            force_refresh: Force refresh from the server
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Security information dictionary
        """
        params = {}
        if user_identity:
            params["userIdentity"] = user_identity
        if force_refresh:
            params["forceRefresh"] = force_refresh
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analysistemplates/{web_id}/security", params=params)

    def get_security_entries(
        self,
        web_id: str,
        name_filter: Optional[str] = None,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entries for an analysis template.
        
        Args:
            web_id: WebID of the analysis template
            name_filter: Optional name filter pattern
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Dictionary containing Items array with security entry data
        """
        params = {}
        if name_filter:
            params["nameFilter"] = name_filter
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(f"analysistemplates/{web_id}/securityentries", params=params)

    def get_security_entry_by_name(
        self,
        web_id: str,
        name: str,
        selected_fields: Optional[str] = None,
    ) -> Dict:
        """Get security entry by name for an analysis template.
        
        Args:
            web_id: WebID of the analysis template
            name: Name of the security entry
            selected_fields: Optional semicolon-delimited list of fields to include
            
        Returns:
            Security entry dictionary
        """
        params = {}
        if selected_fields:
            params["selectedFields"] = selected_fields
        return self.client.get(
            f"analysistemplates/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )

    def create_security_entry(
        self,
        web_id: str,
        security_entry: Dict,
        apply_to_children: bool = False
    ) -> Dict:
        """Create a security entry for the analysis template.
        
        Args:
            web_id: WebID of the analysis template
            security_entry: Security entry data
            apply_to_children: Apply to child objects
            
        Returns:
            Created security entry response
        """
        params = {}
        if apply_to_children:
            params["applyToChildren"] = apply_to_children
        return self.client.post(
            f"analysistemplates/{web_id}/securityentries",
            data=security_entry,
            params=params
        )

    def update_security_entry(
        self,
        web_id: str,
        name: str,
        security_entry: Dict,
        apply_to_children: bool = False
    ) -> Dict:
        """Update a security entry for the analysis template.
        
        Args:
            web_id: WebID of the analysis template
            name: Name of the security entry
            security_entry: Security entry data
            apply_to_children: Apply to child objects
            
        Returns:
            Updated security entry response
        """
        params = {}
        if apply_to_children:
            params["applyToChildren"] = apply_to_children
        return self.client.put(
            f"analysistemplates/{web_id}/securityentries/{self._encode_path(name)}",
            data=security_entry,
            params=params
        )

    def delete_security_entry(
        self,
        web_id: str,
        name: str,
        apply_to_children: bool = False
    ) -> Dict:
        """Delete a security entry from the analysis template.
        
        Args:
            web_id: WebID of the analysis template
            name: Name of the security entry
            apply_to_children: Apply to child objects
            
        Returns:
            Delete response
        """
        params = {}
        if apply_to_children:
            params["applyToChildren"] = apply_to_children
        return self.client.delete(
            f"analysistemplates/{web_id}/securityentries/{self._encode_path(name)}",
            params=params
        )
