from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .item.with_currency_type_item_request_builder import WithCurrencyTypeItemRequestBuilder

class TemporaryCurrencyEntitlementRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /licensing/TemporaryCurrencyEntitlement
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new TemporaryCurrencyEntitlementRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/licensing/TemporaryCurrencyEntitlement", path_parameters)
    
    def by_currency_type(self,currency_type: str) -> WithCurrencyTypeItemRequestBuilder:
        """
        Gets an item from the ApiSdk.licensing.TemporaryCurrencyEntitlement.item collection
        param currency_type: The currency type.
        Returns: WithCurrencyTypeItemRequestBuilder
        """
        if currency_type is None:
            raise TypeError("currency_type cannot be null.")
        from .item.with_currency_type_item_request_builder import WithCurrencyTypeItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["currencyType"] = currency_type
        return WithCurrencyTypeItemRequestBuilder(self.request_adapter, url_tpl_params)
    

