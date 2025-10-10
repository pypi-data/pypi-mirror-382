from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .api.api_request_builder import ApiRequestBuilder

class WithBotItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /powervirtualagents/environments/{EnvironmentId}/bots/{BotId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithBotItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/powervirtualagents/environments/{EnvironmentId}/bots/{BotId}", path_parameters)
    
    @property
    def api(self) -> ApiRequestBuilder:
        """
        The api property
        """
        from .api.api_request_builder import ApiRequestBuilder

        return ApiRequestBuilder(self.request_adapter, self.path_parameters)
    

