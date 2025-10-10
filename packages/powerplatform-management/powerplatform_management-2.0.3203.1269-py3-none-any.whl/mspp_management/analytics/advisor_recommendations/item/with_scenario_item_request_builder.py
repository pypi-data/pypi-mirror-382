from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .actionmetadata.actionmetadata_request_builder import ActionmetadataRequestBuilder
    from .actions.actions_request_builder import ActionsRequestBuilder
    from .resources.resources_request_builder import ResourcesRequestBuilder

class WithScenarioItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /analytics/advisorRecommendations/{scenario}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithScenarioItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/analytics/advisorRecommendations/{scenario}", path_parameters)
    
    @property
    def actionmetadata(self) -> ActionmetadataRequestBuilder:
        """
        The actionmetadata property
        """
        from .actionmetadata.actionmetadata_request_builder import ActionmetadataRequestBuilder

        return ActionmetadataRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def actions(self) -> ActionsRequestBuilder:
        """
        The actions property
        """
        from .actions.actions_request_builder import ActionsRequestBuilder

        return ActionsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def resources(self) -> ResourcesRequestBuilder:
        """
        The resources property
        """
        from .resources.resources_request_builder import ResourcesRequestBuilder

        return ResourcesRequestBuilder(self.request_adapter, self.path_parameters)
    

