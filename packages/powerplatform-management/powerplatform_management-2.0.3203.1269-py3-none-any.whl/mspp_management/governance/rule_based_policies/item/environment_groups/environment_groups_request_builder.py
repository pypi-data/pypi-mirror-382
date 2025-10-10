from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_group_item_request_builder import WithGroupItemRequestBuilder

class EnvironmentGroupsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /governance/ruleBasedPolicies/{policyId}/environmentGroups
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new EnvironmentGroupsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/governance/ruleBasedPolicies/{policyId}/environmentGroups", path_parameters)
    
    def by_group_id(self,group_id: str) -> WithGroupItemRequestBuilder:
        """
        Gets an item from the ApiSdk.governance.ruleBasedPolicies.item.environmentGroups.item collection
        param group_id: The unique identifier of the environment group.
        Returns: WithGroupItemRequestBuilder
        """
        if group_id is None:
            raise TypeError("group_id cannot be null.")
        from .item.with_group_item_request_builder import WithGroupItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["groupId"] = group_id
        return WithGroupItemRequestBuilder(self.request_adapter, url_tpl_params)
    

