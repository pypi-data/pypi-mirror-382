"""Public API for the PI Web API Python SDK."""

from __future__ import annotations

from .client import PIWebAPIClient
from .config import AuthMethod, PIWebAPIConfig, WebIDType
from .controllers import (
    HomeController,
    SystemController,
    ConfigurationController,
    AssetServerController,
    AssetDatabaseController,
    ElementController,
    ElementCategoryController,
    ElementTemplateController,
    AttributeController,
    AttributeCategoryController,
    AttributeTemplateController,
    DataServerController,
    PointController,
    AnalysisController,
    AnalysisCategoryController,
    AnalysisRuleController,
    AnalysisTemplateController,
    BatchController,
    CalculationController,
    ChannelController,
    EnumerationSetController,
    EnumerationValueController,
    EventFrameController,
    StreamController,
    StreamSetController,
    TableController,
)
from .exceptions import PIWebAPIError

# Import all models for convenience
from .models import (
    # Base models
    PIWebAPIObject,
    WebIdInfo,
    SecurityRights,
    Links,
    # Asset models
    AssetServer,
    AssetDatabase,
    Element,
    ElementCategory,
    ElementTemplate,
    # Attribute models
    Attribute,
    AttributeCategory,
    AttributeTemplate,
    AttributeTrait,
    # Data models
    DataServer,
    Point,
    TimedValue,
    StreamValue,
    StreamValues,
    # Stream models
    Stream,
    StreamSet,
    # Analysis models
    Analysis,
    AnalysisTemplate,
    AnalysisCategory,
    AnalysisRule,
    # Event models
    EventFrame,
    EventFrameCategory,
    # Table models
    Table,
    TableCategory,
    TableData,
    # Unit models
    Unit,
    UnitClass,
    # Enumeration models
    EnumerationSet,
    EnumerationValue,
    # Security models
    SecurityIdentity,
    SecurityMapping,
    SecurityEntry,
    # Notification models
    NotificationRule,
    NotificationContactTemplate,
    # Time Rule models
    TimeRule,
    TimeRulePlugIn,
    # Batch models
    Batch,
    BatchRequest,
)

__version__ = '0.1.0'


__all__ = [
    # Core
    '__version__',
    'PIWebAPIClient',
    'PIWebAPIConfig',
    'AuthMethod',
    'WebIDType',
    'PIWebAPIError',
    # Controllers
    'HomeController',
    'SystemController',
    'ConfigurationController',
    'AssetServerController',
    'AssetDatabaseController',
    'ElementController',
    'ElementCategoryController',
    'ElementTemplateController',
    'AttributeController',
    'AttributeCategoryController',
    'AttributeTemplateController',
    'DataServerController',
    'PointController',
    'AnalysisController',
    'AnalysisCategoryController',
    'AnalysisRuleController',
    'AnalysisTemplateController',
    'BatchController',
    'CalculationController',
    'ChannelController',
    'EnumerationSetController',
    'EnumerationValueController',
    'EventFrameController',
    'StreamController',
    'StreamSetController',
    'TableController',
    # Base models
    'PIWebAPIObject',
    'WebIdInfo',
    'SecurityRights',
    'Links',
    # Asset models
    'AssetServer',
    'AssetDatabase',
    'Element',
    'ElementCategory',
    'ElementTemplate',
    # Attribute models
    'Attribute',
    'AttributeCategory',
    'AttributeTemplate',
    'AttributeTrait',
    # Data models
    'DataServer',
    'Point',
    'TimedValue',
    'StreamValue',
    'StreamValues',
    # Stream models
    'Stream',
    'StreamSet',
    # Analysis models
    'Analysis',
    'AnalysisTemplate',
    'AnalysisCategory',
    'AnalysisRule',
    # Event models
    'EventFrame',
    'EventFrameCategory',
    # Table models
    'Table',
    'TableCategory',
    'TableData',
    # Unit models
    'Unit',
    'UnitClass',
    # Enumeration models
    'EnumerationSet',
    'EnumerationValue',
    # Security models
    'SecurityIdentity',
    'SecurityMapping',
    'SecurityEntry',
    # Notification models
    'NotificationRule',
    'NotificationContactTemplate',
    # Time Rule models
    'TimeRule',
    'TimeRulePlugIn',
    # Batch models
    'Batch',
    'BatchRequest',
]
