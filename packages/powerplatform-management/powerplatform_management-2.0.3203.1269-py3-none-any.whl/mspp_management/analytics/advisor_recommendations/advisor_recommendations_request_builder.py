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
    from ...models.advisor_recommendation_i_enumerable_response_with_continuation import AdvisorRecommendationIEnumerableResponseWithContinuation
    from .item.with_scenario_item_request_builder import WithScenarioItemRequestBuilder
    from .scenarios.scenarios_request_builder import ScenariosRequestBuilder

class AdvisorRecommendationsRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /analytics/advisorRecommendations
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new AdvisorRecommendationsRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/analytics/advisorRecommendations?api-version={api%2Dversion}{&%24skipToken*}", path_parameters)
    
    def by_scenario(self,scenario: str) -> WithScenarioItemRequestBuilder:
        """
        Gets an item from the ApiSdk.analytics.advisorRecommendations.item collection
        param scenario: The recommendation name.
        Returns: WithScenarioItemRequestBuilder
        """
        if scenario is None:
            raise TypeError("scenario cannot be null.")
        from .item.with_scenario_item_request_builder import WithScenarioItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["scenario"] = scenario
        return WithScenarioItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[AdvisorRecommendationsRequestBuilderGetQueryParameters]] = None) -> Optional[AdvisorRecommendationIEnumerableResponseWithContinuation]:
        """
        Gets the list of recommendations for the tenant.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[AdvisorRecommendationIEnumerableResponseWithContinuation]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.advisor_recommendation_i_enumerable_response_with_continuation import AdvisorRecommendationIEnumerableResponseWithContinuation

        return await self.request_adapter.send_async(request_info, AdvisorRecommendationIEnumerableResponseWithContinuation, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[AdvisorRecommendationsRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Gets the list of recommendations for the tenant.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def with_url(self,raw_url: str) -> AdvisorRecommendationsRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: AdvisorRecommendationsRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return AdvisorRecommendationsRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def scenarios(self) -> ScenariosRequestBuilder:
        """
        The scenarios property
        """
        from .scenarios.scenarios_request_builder import ScenariosRequestBuilder

        return ScenariosRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class AdvisorRecommendationsRequestBuilderGetQueryParameters():
        """
        Gets the list of recommendations for the tenant.
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
            if original_name == "skip_token":
                return "%24skipToken"
            return original_name
        
        # The API version.
        api_version: Optional[str] = None

        # Skip token for the next page of recommendations.
        skip_token: Optional[str] = None

    
    @dataclass
    class AdvisorRecommendationsRequestBuilderGetRequestConfiguration(RequestConfiguration[AdvisorRecommendationsRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

