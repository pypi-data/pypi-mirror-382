from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_operation_item_request_builder import WithOperationItemRequestBuilder

class OperationsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /environmentmanagement/operations
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new OperationsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/environmentmanagement/operations", path_parameters)
    
    def by_operation_id(self,operation_id: str) -> WithOperationItemRequestBuilder:
        """
        Gets an item from the ApiSdk.environmentmanagement.operations.item collection
        param operation_id: The operation ID.
        Returns: WithOperationItemRequestBuilder
        """
        if operation_id is None:
            raise TypeError("operation_id cannot be null.")
        from .item.with_operation_item_request_builder import WithOperationItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["operationId"] = operation_id
        return WithOperationItemRequestBuilder(self.request_adapter, url_tpl_params)
    

