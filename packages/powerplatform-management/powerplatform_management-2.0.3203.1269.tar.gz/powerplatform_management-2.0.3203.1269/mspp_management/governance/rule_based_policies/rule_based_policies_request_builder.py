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
    from ...models.list_policy_response import ListPolicyResponse
    from ...models.policy_request import PolicyRequest
    from ...models.rule_assignment import RuleAssignment
    from .assignments.assignments_request_builder import AssignmentsRequestBuilder
    from .environments.environments_request_builder import EnvironmentsRequestBuilder
    from .environment_groups.environment_groups_request_builder import EnvironmentGroupsRequestBuilder
    from .item.with_policy_item_request_builder import WithPolicyItemRequestBuilder

class RuleBasedPoliciesRequestBuilder(BaseRequestBuilder):
    """
    Builds and executes requests for operations under /governance/ruleBasedPolicies
    """
    def __init__(self,request_adapter: RequestAdapter, path_parameters: Union[str, dict[str, Any]]) -> None:
        """
        Instantiates a new RuleBasedPoliciesRequestBuilder and sets the default values.
        param path_parameters: The raw url or the url-template parameters for the request.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        super().__init__(request_adapter, "{+baseurl}/governance/ruleBasedPolicies?api-version={api%2Dversion}", path_parameters)
    
    def by_policy_id(self,policy_id: str) -> WithPolicyItemRequestBuilder:
        """
        Gets an item from the ApiSdk.governance.ruleBasedPolicies.item collection
        param policy_id: The unique identifier of the policy.
        Returns: WithPolicyItemRequestBuilder
        """
        if policy_id is None:
            raise TypeError("policy_id cannot be null.")
        from .item.with_policy_item_request_builder import WithPolicyItemRequestBuilder

        url_tpl_params = get_path_parameters(self.path_parameters)
        url_tpl_params["policyId"] = policy_id
        return WithPolicyItemRequestBuilder(self.request_adapter, url_tpl_params)
    
    async def get(self,request_configuration: Optional[RequestConfiguration[RuleBasedPoliciesRequestBuilderGetQueryParameters]] = None) -> Optional[ListPolicyResponse]:
        """
        List rule based policies available in the tenant.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[ListPolicyResponse]
        """
        request_info = self.to_get_request_information(
            request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.list_policy_response import ListPolicyResponse

        return await self.request_adapter.send_async(request_info, ListPolicyResponse, None)
    
    async def post(self,body: PolicyRequest, request_configuration: Optional[RequestConfiguration[RuleBasedPoliciesRequestBuilderPostQueryParameters]] = None) -> Optional[RuleAssignment]:
        """
        Create new rule based policy. The input includes rule sets, inputs, and other metadata related to the policy.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: Optional[RuleAssignment]
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = self.to_post_request_information(
            body, request_configuration
        )
        if not self.request_adapter:
            raise Exception("Http core is null") 
        from ...models.rule_assignment import RuleAssignment

        return await self.request_adapter.send_async(request_info, RuleAssignment, None)
    
    def to_get_request_information(self,request_configuration: Optional[RequestConfiguration[RuleBasedPoliciesRequestBuilderGetQueryParameters]] = None) -> RequestInformation:
        """
        List rule based policies available in the tenant.
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        request_info = RequestInformation(Method.GET, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        return request_info
    
    def to_post_request_information(self,body: PolicyRequest, request_configuration: Optional[RequestConfiguration[RuleBasedPoliciesRequestBuilderPostQueryParameters]] = None) -> RequestInformation:
        """
        Create new rule based policy. The input includes rule sets, inputs, and other metadata related to the policy.
        param body: The request body
        param request_configuration: Configuration for the request such as headers, query parameters, and middleware options.
        Returns: RequestInformation
        """
        if body is None:
            raise TypeError("body cannot be null.")
        request_info = RequestInformation(Method.POST, self.url_template, self.path_parameters)
        request_info.configure(request_configuration)
        request_info.headers.try_add("Accept", "application/json")
        request_info.set_content_from_parsable(self.request_adapter, "application/json", body)
        return request_info
    
    def with_url(self,raw_url: str) -> RuleBasedPoliciesRequestBuilder:
        """
        Returns a request builder with the provided arbitrary URL. Using this method means any other path or query parameters are ignored.
        param raw_url: The raw URL to use for the request builder.
        Returns: RuleBasedPoliciesRequestBuilder
        """
        if raw_url is None:
            raise TypeError("raw_url cannot be null.")
        return RuleBasedPoliciesRequestBuilder(self.request_adapter, raw_url)
    
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
    class RuleBasedPoliciesRequestBuilderGetQueryParameters():
        """
        List rule based policies available in the tenant.
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
    class RuleBasedPoliciesRequestBuilderGetRequestConfiguration(RequestConfiguration[RuleBasedPoliciesRequestBuilderGetQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    
    @dataclass
    class RuleBasedPoliciesRequestBuilderPostQueryParameters():
        """
        Create new rule based policy. The input includes rule sets, inputs, and other metadata related to the policy.
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
    class RuleBasedPoliciesRequestBuilderPostRequestConfiguration(RequestConfiguration[RuleBasedPoliciesRequestBuilderPostQueryParameters]):
        """
        Configuration for the request such as headers, query parameters, and middleware options.
        """
        warn("This class is deprecated. Please use the generic RequestConfiguration class generated by the generator.", DeprecationWarning)
    

