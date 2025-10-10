from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .deep.deep_request_builder import DeepRequestBuilder
    from .quick.quick_request_builder import QuickRequestBuilder

class ScanRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /powerpages/environments/{environmentId}/websites/{id}/scan
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new ScanRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/powerpages/environments/{environmentId}/websites/{id}/scan", path_parameters)
    
    @property
    def deep(self) -> DeepRequestBuilder:
        """
        The deep property
        """
        from .deep.deep_request_builder import DeepRequestBuilder

        return DeepRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def quick(self) -> QuickRequestBuilder:
        """
        The quick property
        """
        from .quick.quick_request_builder import QuickRequestBuilder

        return QuickRequestBuilder(self.request_adapter, self.path_parameters)
    

