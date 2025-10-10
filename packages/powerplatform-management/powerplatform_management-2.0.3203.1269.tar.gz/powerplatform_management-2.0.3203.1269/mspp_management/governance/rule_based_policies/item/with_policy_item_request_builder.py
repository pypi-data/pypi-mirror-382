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
    from ....models.policy import Policy
    from ....models.policy_request import PolicyRequest
    from ....models.rule_assignment import RuleAssignment
    from .assignments.assignments_request_builder import AssignmentsRequestBuilder
    from .environments.environments_request_builder import EnvironmentsRequestBuilder
    from .environment_groups.environment_groups_request_builder import EnvironmentGroupsRequestBuilder

class WithPolicyItemRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /governance/ruleBasedPolicies/{policyId}
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new WithPolicyItemRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/governance/ruleBasedPolicies/{policyId}?api-version={api%2Dversion}", path_parameters)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[WithPolicyItemRequestBuilderGetQueryParameters]] = None) -> Optional[Policy]:
        """
        Retrieves details about a specific policy based on the policy ID. The response includes rule sets, inputs, and other metadata related to the policy.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[Policy]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.policy import Policy

        return await self.request_adapter.send_async(request_info, Policy, None)
    
    async def put(self,body: PolicyRequest, request_configuration: Optional[RequestConfiguration[WithPolicyItemRequestBuilderPutQueryParameters]] = None) -> Optional[RuleAssignment]:
        """
        Updates details about a specific policy based on the policy ID. The input includes rule sets, inputs, and other metadata related to the policy.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[RuleAssignment]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_put_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ....models.rule_assignment import RuleAssignment

        return await self.request_adapter.send_async(request_info, RuleAssignment, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[WithPolicyItemRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        Retrieves details about a specific policy based on the policy ID. The response includes rule sets, inputs, and other metadata related to the policy.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_put_request_information(self,body: PolicyRequest, request_configuration: Optional[RequestConfiguration[WithPolicyItemRequestBuilderPutQueryParameters]] = None) -> RequestInformation:
        """
        Updates details about a specific policy based on the policy ID. The input includes rule sets, inputs, and other metadata related to the policy.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.PUT, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> WithPolicyItemRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: WithPolicyItemRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return WithPolicyItemRequestBuilder(self.request_adapter, raw_url)
    
    @property
    def assignments(self) -> AssignmentsRequestBuilder:
        """
        The assignments property
        """
        from .assignments.assignments_request_builder import AssignmentsRequestBuilder

        return AssignmentsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def environment_groups(self) -> EnvironmentGroupsRequestBuilder:
        """
        The environmentGroups property
        """
        from .environment_groups.environment_groups_request_builder import EnvironmentGroupsRequestBuilder

        return EnvironmentGroupsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def environments(self) -> EnvironmentsRequestBuilder:
        """
        The environments property
        """
        from .environments.environments_request_builder import EnvironmentsRequestBuilder

        return EnvironmentsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @dataclass
    class WithPolicyItemRequestBuilderGetQueryParameters():
        """
        Retrieves details about a specific policy based on the policy ID. The response includes rule sets, inputs, and other metadata related to the policy.
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
    class WithPolicyItemRequestBuilderGetRequestConfiguration(RequestConfiguration[WithPolicyItemRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class WithPolicyItemRequestBuilderPutQueryParameters():
        """
        Updates details about a specific policy based on the policy ID. The input includes rule sets, inputs, and other metadata related to the policy.
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
    class WithPolicyItemRequestBuilderPutRequestConfiguration(RequestConfiguration[WithPolicyItemRequestBuilderPutQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

