from __future__ import annotations
from collections.abc import Callable
from kiota_abstractions.api_client_builder import enable_backing_store_for_serialization_writer_factory, register_default_deserializer, register_default_serializer
from kiota_abstractions.base_request_builder import BaseRequestBuilder
from kiota_abstractions.get_path_parameters import get_path_parameters
from kiota_abstractions.request_adapter import RequestAdapter
from kiota_abstractions.serialization import ParseNodeFactoryRegistry, SerializationWriterFactoryRegistry
from kiota_serialization_form.form_parse_node_factory import FormParseNodeFactory
from kiota_serialization_form.form_serialization_writer_factory import FormSerializationWriterFactory
from kiota_serialization_json.json_parse_node_factory import JsonParseNodeFactory
from kiota_serialization_json.json_serialization_writer_factory import JsonSerializationWriterFactory
from kiota_serialization_multipart.multipart_serialization_writer_factory import MultipartSerializationWriterFactory
from kiota_serialization_text.text_parse_node_factory import TextParseNodeFactory
from kiota_serialization_text.text_serialization_writer_factory import TextSerializationWriterFactory
from typing import Any, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .analytics.analytics_request_builder import AnalyticsRequestBuilder
    from .appmanagement.appmanagement_request_builder import AppmanagementRequestBuilder
    from .authorization.authorization_request_builder import AuthorizationRequestBuilder
    from .connectivity.connectivity_request_builder import ConnectivityRequestBuilder
    from .environmentmanagement.environmentmanagement_request_builder import EnvironmentmanagementRequestBuilder
    from .governance.governance_request_builder import GovernanceRequestBuilder
    from .licensing.licensing_request_builder import LicensingRequestBuilder
    from .powerapps.powerapps_request_builder import PowerappsRequestBuilder
    from .powerautomate.powerautomate_request_builder import PowerautomateRequestBuilder
    from .powerpages.powerpages_request_builder import PowerpagesRequestBuilder
    from .powervirtualagents.powervirtualagents_request_builder import PowervirtualagentsRequestBuilder
    from .usermanagement.usermanagement_request_builder import UsermanagementRequestBuilder

class ServiceClientBase(BaseRequestBuilder):
    """
    The main entry point of the SDK, exposes the configuration and the fluent API.
    """
    def __init__(self,request_adapter: RequestAdapter) -> None:
        """
        Instantiates a new ServiceClientBase and sets the default values.
        param request_adapter: The request adapter to use to execute the requests.
        Returns: None
        """
        if request_adapter is None:
            raise TypeError("request_adapter cannot be null.")
        super().__init__(request_adapter, "{+baseurl}", None)
        register_default_serializer(JsonSerializationWriterFactory)
        register_default_serializer(TextSerializationWriterFactory)
        register_default_serializer(FormSerializationWriterFactory)
        register_default_serializer(MultipartSerializationWriterFactory)
        register_default_deserializer(JsonParseNodeFactory)
        register_default_deserializer(TextParseNodeFactory)
        register_default_deserializer(FormParseNodeFactory)
        if not self.request_adapter.base_url:
            self.request_adapter.base_url = "https://api.powerplatform.com"
        self.path_parameters["base_url"] = self.request_adapter.base_url
    
    @property
    def analytics(self) -> AnalyticsRequestBuilder:
        """
        The analytics property
        """
        from .analytics.analytics_request_builder import AnalyticsRequestBuilder

        return AnalyticsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def appmanagement(self) -> AppmanagementRequestBuilder:
        """
        The appmanagement property
        """
        from .appmanagement.appmanagement_request_builder import AppmanagementRequestBuilder

        return AppmanagementRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def authorization(self) -> AuthorizationRequestBuilder:
        """
        The authorization property
        """
        from .authorization.authorization_request_builder import AuthorizationRequestBuilder

        return AuthorizationRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def connectivity(self) -> ConnectivityRequestBuilder:
        """
        The connectivity property
        """
        from .connectivity.connectivity_request_builder import ConnectivityRequestBuilder

        return ConnectivityRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def environmentmanagement(self) -> EnvironmentmanagementRequestBuilder:
        """
        The environmentmanagement property
        """
        from .environmentmanagement.environmentmanagement_request_builder import EnvironmentmanagementRequestBuilder

        return EnvironmentmanagementRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def governance(self) -> GovernanceRequestBuilder:
        """
        The governance property
        """
        from .governance.governance_request_builder import GovernanceRequestBuilder

        return GovernanceRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def licensing(self) -> LicensingRequestBuilder:
        """
        The licensing property
        """
        from .licensing.licensing_request_builder import LicensingRequestBuilder

        return LicensingRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def powerapps(self) -> PowerappsRequestBuilder:
        """
        The powerapps property
        """
        from .powerapps.powerapps_request_builder import PowerappsRequestBuilder

        return PowerappsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def powerautomate(self) -> PowerautomateRequestBuilder:
        """
        The powerautomate property
        """
        from .powerautomate.powerautomate_request_builder import PowerautomateRequestBuilder

        return PowerautomateRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def powerpages(self) -> PowerpagesRequestBuilder:
        """
        The powerpages property
        """
        from .powerpages.powerpages_request_builder import PowerpagesRequestBuilder

        return PowerpagesRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def powervirtualagents(self) -> PowervirtualagentsRequestBuilder:
        """
        The powervirtualagents property
        """
        from .powervirtualagents.powervirtualagents_request_builder import PowervirtualagentsRequestBuilder

        return PowervirtualagentsRequestBuilder(self.request_adapter, self.path_parameters)
    
    @property
    def usermanagement(self) -> UsermanagementRequestBuilder:
        """
        The usermanagement property
        """
        from .usermanagement.usermanagement_request_builder import UsermanagementRequestBuilder

        return UsermanagementRequestBuilder(self.request_adapter, self.path_parameters)
    

