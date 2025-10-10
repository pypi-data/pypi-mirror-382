from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_environment_item_request_builder import WithEnvironmentItemRequestBuilder

class EnvironmentsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /powerapps/environments
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new EnvironmentsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/powerapps/environments", path_parameters)
    
    def by_environment_id(self,environment_id: str) -> WithEnvironmentItemRequestBuilder:
        """
        Gets an item from the ApiSdk.powerapps.environments.item collection
        param environment_id: Name field of the environment.
        Returns: WithEnvironmentItemRequestBuilder
        """
        if environment_id is None:
            raise TypeError("environment_id cannot be null.")
        from .item.with_environment_item_request_builder import WithEnvironmentItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["environmentId"] = environment_id
        return WithEnvironmentItemRequestBuilder(self.request_adapter, url_tpl_params)
    

