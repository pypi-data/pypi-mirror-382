from __future__ import annotations
from collections.abc import Callable
from dataclasses import dataclass, field
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.base_request_configuration import RequestConfiguration
from kiota_abstractions.default_query_parameters import QueryParameters
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.method import Method
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.request_information import RequestInformation
from kiota_abstractions.request_option import RequestOption
from kiota_abstractions.serialization import Parsable, ParsableFactory
from typing import Any, Optional, TYPE_CHECKING, Union
from warnings import warn

if TYPE_CHECKING:
    from ........models.bot_quarantine_status import BotQuarantineStatus
    from .set_as_quarantined.set_as_quarantined_request_builder import SetAsQuarantinedRequestBuilder
    from .set_as_unquarantined.set_as_unquarantined_request_builder import SetAsUnquarantinedRequestBuilder

class BotQuarantineRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /powervirtualagents/environments/{EnvironmentId}/bots/{BotId}/api/botQuarantine
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new BotQuarantineRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/powervirtualagents/environments/{EnvironmentId}/bots/{BotId}/api/botQuarantine?api-version={api%2Dversion}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[BotQuarantineRequestBuilderGetQueryParameters]] = None) -> Optional[BotQuarantineStatus]:
        """
        Retrieve the quarantine status of a bot.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[BotQuarantineStatus]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ........models.bot_quarantine_status import BotQuarantineStatus

        return await self.request_adapter.send_async(request_info, BotQuarantineStatus, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[BotQuarantineRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Retrieve the quarantine status of a bot.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> BotQuarantineRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: BotQuarantineRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return BotQuarantineRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def set_as_quarantined(self) -> SetAsQuarantinedRequestBuilder:
        """
        The SetAsQuarantined property
        """
        from .set_as_quarantined.set_as_quarantined_request_builder import SetAsQuarantinedRequestBuilder

        return SetAsQuarantinedRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def set_as_unquarantined(self) -> SetAsUnquarantinedRequestBuilder:
        """
        The SetAsUnquarantined property
        """
        from .set_as_unquarantined.set_as_unquarantined_request_builder import SetAsUnquarantinedRequestBuilder

        return SetAsUnquarantinedRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class BotQuarantineRequestBuilderGetQueryParameters():
        """
        Retrieve the quarantine status of a bot.
        """
        def get_query_parameter(self,original_name: str) -> str:
            """
            Maps the query parameters names to their encoded names for the URI template parsing.
            param original_name: The original query parameter name in the class.
            Returns: str
            """
            if original_name is None:
                raise TypeError("original_name cannot be null.")
            if original_name == "api_version":
                return "api%2Dversion"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

    
    @dataclass
    class BotQuarantineRequestBuilderGetRequestConfiguration(RequestConfiguration[BotQuarantineRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

