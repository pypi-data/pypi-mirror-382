from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_action_name_item_request_builder import WithActionNameItemRequestBuilder

class ActionmetadataRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /analytics/advisorRecommendations/{scenario}/actionmetadata
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ActionmetadataRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/analytics/advisorRecommendations/{scenario}/actionmetadata", path_parameters)
    
    def by_action_name(self,action_name: str) -> WithActionNameItemRequestBuilder:
        """
        Gets an item from the ApiSdk.analytics.advisorRecommendations.item.actionmetadata.item collection
        param action_name: The name of the action.
        Returns: WithActionNameItemRequestBuilder
        """
        if action_name is None:
            raise TypeError("action_name cannot be null.")
        from .item.with_action_name_item_request_builder import WithActionNameItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["actionName"] = action_name
        return WithActionNameItemRequestBuilder(self.request_adapter, url_tpl_params)
    

