# coding: utf-8

# flake8: noqa

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Affiliate API The Affiliate API exposes endpoints to manage affiliate accounts. This API lets you:  1. Create affiliates. 2. Create account managers  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.23.0
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "0.0.47"

# Define package exports
__all__ = [
    "AccountManagerApi",
    "AffiliateApi",
    "LeadsApi",
    "NotificationApi",
    "TravelAgentApi",
    "ApiResponse",
    "ApiClient",
    "Configuration",
    "OpenApiException",
    "ApiTypeError",
    "ApiValueError",
    "ApiKeyError",
    "ApiAttributeError",
    "ApiException",
    "AddressAffiliate",
    "AddressAgent",
    "AddressSupplier",
    "AffiliateAccountAffiliate",
    "AffiliateAccountAgent",
    "AffiliateAccountSupplier",
    "AffiliateAccountUserAffiliate",
    "AffiliateAccountUserAgent",
    "AffiliateAccountUserSupplier",
    "AggregateDescriptorSupplier",
    "CompositeFilterDescriptorSupplier",
    "CountResponseAffiliate",
    "CountryLightweightAffiliate",
    "CountryLightweightAgent",
    "CountryLightweightSupplier",
    "CreateAffiliate400Response",
    "CreateAffiliateAccountRequestAffiliate",
    "CustomMonetaryAmount",
    "FilterDescriptorSupplier",
    "GenericErrorMessage",
    "GeoJsonPointAffiliate",
    "GeoJsonPointAgent",
    "GeoJsonPointSupplier",
    "GeoNameLightweightAffiliate",
    "GeoNameLightweightAgent",
    "GeoNameLightweightSupplier",
    "GooglePlaceDetailRequestAffiliate",
    "GroupDescriptorSupplier",
    "InviteManagerRequestAffiliate",
    "KeyValuePairAffiliate",
    "ManagedByEntityAffiliate",
    "ManagedByEntityAgent",
    "ManagedByEntityRulesAffiliate",
    "ManagedByEntityRulesAgent",
    "ManagedByEntityRulesSupplier",
    "ManagedByEntitySupplier",
    "ManagerInviteAcceptedSupplier",
    "ManagerInviteAffiliate",
    "MediaAuthorAttributionAffiliate",
    "MediaAuthorAttributionAgent",
    "MediaAuthorAttributionSupplier",
    "NotificationAffiliate",
    "PageAffiliateAccountSupplier",
    "PageableObjectSupplier",
    "SimpleAddressAffiliate",
    "SimpleDescriptionAffiliate",
    "SimpleDescriptionAgent",
    "SimpleDescriptionSupplier",
    "SimpleMultimediaAffiliate",
    "SimpleMultimediaAgent",
    "SimpleMultimediaSupplier",
    "SortDescriptorSupplier",
    "SortObjectSupplier",
    "StateSupplier",
    "SubCountryLightweightAffiliate",
    "SubCountryLightweightAgent",
    "SubCountryLightweightSupplier",
    "SubSubCountryLightweightAffiliate",
    "SubSubCountryLightweightAgent",
    "SubSubCountryLightweightSupplier",
    "SupplierLeadAffiliate",
    "TravelAgentAgent",
    "TravelAgentSupplier",
    "UpsertAddressRequestAffiliate",
    "UpsertAffiliateAccountProfileRequestAffiliate",
    "UpsertCompanyLogoRequestAffiliate",
    "UpsertCompanyOnlinePresenceRequestAffiliate",
    "UpsertCompanyRequestAffiliate",
    "UpsertCompanyStatusRequestAffiliate",
    "UpsertManagedByAgencyRequestAffiliate",
    "UpsertTravelAgentRequestAgent",
]

# import apis into sdk package
from wink_sdk_affiliate.api.account_manager_api import AccountManagerApi as AccountManagerApi
from wink_sdk_affiliate.api.affiliate_api import AffiliateApi as AffiliateApi
from wink_sdk_affiliate.api.leads_api import LeadsApi as LeadsApi
from wink_sdk_affiliate.api.notification_api import NotificationApi as NotificationApi
from wink_sdk_affiliate.api.travel_agent_api import TravelAgentApi as TravelAgentApi

# import ApiClient
from wink_sdk_affiliate.api_response import ApiResponse as ApiResponse
from wink_sdk_affiliate.api_client import ApiClient as ApiClient
from wink_sdk_affiliate.configuration import Configuration as Configuration
from wink_sdk_affiliate.exceptions import OpenApiException as OpenApiException
from wink_sdk_affiliate.exceptions import ApiTypeError as ApiTypeError
from wink_sdk_affiliate.exceptions import ApiValueError as ApiValueError
from wink_sdk_affiliate.exceptions import ApiKeyError as ApiKeyError
from wink_sdk_affiliate.exceptions import ApiAttributeError as ApiAttributeError
from wink_sdk_affiliate.exceptions import ApiException as ApiException

# import models into sdk package
from wink_sdk_affiliate.models.address_affiliate import AddressAffiliate as AddressAffiliate
from wink_sdk_affiliate.models.address_agent import AddressAgent as AddressAgent
from wink_sdk_affiliate.models.address_supplier import AddressSupplier as AddressSupplier
from wink_sdk_affiliate.models.affiliate_account_affiliate import AffiliateAccountAffiliate as AffiliateAccountAffiliate
from wink_sdk_affiliate.models.affiliate_account_agent import AffiliateAccountAgent as AffiliateAccountAgent
from wink_sdk_affiliate.models.affiliate_account_supplier import AffiliateAccountSupplier as AffiliateAccountSupplier
from wink_sdk_affiliate.models.affiliate_account_user_affiliate import AffiliateAccountUserAffiliate as AffiliateAccountUserAffiliate
from wink_sdk_affiliate.models.affiliate_account_user_agent import AffiliateAccountUserAgent as AffiliateAccountUserAgent
from wink_sdk_affiliate.models.affiliate_account_user_supplier import AffiliateAccountUserSupplier as AffiliateAccountUserSupplier
from wink_sdk_affiliate.models.aggregate_descriptor_supplier import AggregateDescriptorSupplier as AggregateDescriptorSupplier
from wink_sdk_affiliate.models.composite_filter_descriptor_supplier import CompositeFilterDescriptorSupplier as CompositeFilterDescriptorSupplier
from wink_sdk_affiliate.models.count_response_affiliate import CountResponseAffiliate as CountResponseAffiliate
from wink_sdk_affiliate.models.country_lightweight_affiliate import CountryLightweightAffiliate as CountryLightweightAffiliate
from wink_sdk_affiliate.models.country_lightweight_agent import CountryLightweightAgent as CountryLightweightAgent
from wink_sdk_affiliate.models.country_lightweight_supplier import CountryLightweightSupplier as CountryLightweightSupplier
from wink_sdk_affiliate.models.create_affiliate400_response import CreateAffiliate400Response as CreateAffiliate400Response
from wink_sdk_affiliate.models.create_affiliate_account_request_affiliate import CreateAffiliateAccountRequestAffiliate as CreateAffiliateAccountRequestAffiliate
from wink_sdk_affiliate.models.custom_monetary_amount import CustomMonetaryAmount as CustomMonetaryAmount
from wink_sdk_affiliate.models.filter_descriptor_supplier import FilterDescriptorSupplier as FilterDescriptorSupplier
from wink_sdk_affiliate.models.generic_error_message import GenericErrorMessage as GenericErrorMessage
from wink_sdk_affiliate.models.geo_json_point_affiliate import GeoJsonPointAffiliate as GeoJsonPointAffiliate
from wink_sdk_affiliate.models.geo_json_point_agent import GeoJsonPointAgent as GeoJsonPointAgent
from wink_sdk_affiliate.models.geo_json_point_supplier import GeoJsonPointSupplier as GeoJsonPointSupplier
from wink_sdk_affiliate.models.geo_name_lightweight_affiliate import GeoNameLightweightAffiliate as GeoNameLightweightAffiliate
from wink_sdk_affiliate.models.geo_name_lightweight_agent import GeoNameLightweightAgent as GeoNameLightweightAgent
from wink_sdk_affiliate.models.geo_name_lightweight_supplier import GeoNameLightweightSupplier as GeoNameLightweightSupplier
from wink_sdk_affiliate.models.google_place_detail_request_affiliate import GooglePlaceDetailRequestAffiliate as GooglePlaceDetailRequestAffiliate
from wink_sdk_affiliate.models.group_descriptor_supplier import GroupDescriptorSupplier as GroupDescriptorSupplier
from wink_sdk_affiliate.models.invite_manager_request_affiliate import InviteManagerRequestAffiliate as InviteManagerRequestAffiliate
from wink_sdk_affiliate.models.key_value_pair_affiliate import KeyValuePairAffiliate as KeyValuePairAffiliate
from wink_sdk_affiliate.models.managed_by_entity_affiliate import ManagedByEntityAffiliate as ManagedByEntityAffiliate
from wink_sdk_affiliate.models.managed_by_entity_agent import ManagedByEntityAgent as ManagedByEntityAgent
from wink_sdk_affiliate.models.managed_by_entity_rules_affiliate import ManagedByEntityRulesAffiliate as ManagedByEntityRulesAffiliate
from wink_sdk_affiliate.models.managed_by_entity_rules_agent import ManagedByEntityRulesAgent as ManagedByEntityRulesAgent
from wink_sdk_affiliate.models.managed_by_entity_rules_supplier import ManagedByEntityRulesSupplier as ManagedByEntityRulesSupplier
from wink_sdk_affiliate.models.managed_by_entity_supplier import ManagedByEntitySupplier as ManagedByEntitySupplier
from wink_sdk_affiliate.models.manager_invite_accepted_supplier import ManagerInviteAcceptedSupplier as ManagerInviteAcceptedSupplier
from wink_sdk_affiliate.models.manager_invite_affiliate import ManagerInviteAffiliate as ManagerInviteAffiliate
from wink_sdk_affiliate.models.media_author_attribution_affiliate import MediaAuthorAttributionAffiliate as MediaAuthorAttributionAffiliate
from wink_sdk_affiliate.models.media_author_attribution_agent import MediaAuthorAttributionAgent as MediaAuthorAttributionAgent
from wink_sdk_affiliate.models.media_author_attribution_supplier import MediaAuthorAttributionSupplier as MediaAuthorAttributionSupplier
from wink_sdk_affiliate.models.notification_affiliate import NotificationAffiliate as NotificationAffiliate
from wink_sdk_affiliate.models.page_affiliate_account_supplier import PageAffiliateAccountSupplier as PageAffiliateAccountSupplier
from wink_sdk_affiliate.models.pageable_object_supplier import PageableObjectSupplier as PageableObjectSupplier
from wink_sdk_affiliate.models.simple_address_affiliate import SimpleAddressAffiliate as SimpleAddressAffiliate
from wink_sdk_affiliate.models.simple_description_affiliate import SimpleDescriptionAffiliate as SimpleDescriptionAffiliate
from wink_sdk_affiliate.models.simple_description_agent import SimpleDescriptionAgent as SimpleDescriptionAgent
from wink_sdk_affiliate.models.simple_description_supplier import SimpleDescriptionSupplier as SimpleDescriptionSupplier
from wink_sdk_affiliate.models.simple_multimedia_affiliate import SimpleMultimediaAffiliate as SimpleMultimediaAffiliate
from wink_sdk_affiliate.models.simple_multimedia_agent import SimpleMultimediaAgent as SimpleMultimediaAgent
from wink_sdk_affiliate.models.simple_multimedia_supplier import SimpleMultimediaSupplier as SimpleMultimediaSupplier
from wink_sdk_affiliate.models.sort_descriptor_supplier import SortDescriptorSupplier as SortDescriptorSupplier
from wink_sdk_affiliate.models.sort_object_supplier import SortObjectSupplier as SortObjectSupplier
from wink_sdk_affiliate.models.state_supplier import StateSupplier as StateSupplier
from wink_sdk_affiliate.models.sub_country_lightweight_affiliate import SubCountryLightweightAffiliate as SubCountryLightweightAffiliate
from wink_sdk_affiliate.models.sub_country_lightweight_agent import SubCountryLightweightAgent as SubCountryLightweightAgent
from wink_sdk_affiliate.models.sub_country_lightweight_supplier import SubCountryLightweightSupplier as SubCountryLightweightSupplier
from wink_sdk_affiliate.models.sub_sub_country_lightweight_affiliate import SubSubCountryLightweightAffiliate as SubSubCountryLightweightAffiliate
from wink_sdk_affiliate.models.sub_sub_country_lightweight_agent import SubSubCountryLightweightAgent as SubSubCountryLightweightAgent
from wink_sdk_affiliate.models.sub_sub_country_lightweight_supplier import SubSubCountryLightweightSupplier as SubSubCountryLightweightSupplier
from wink_sdk_affiliate.models.supplier_lead_affiliate import SupplierLeadAffiliate as SupplierLeadAffiliate
from wink_sdk_affiliate.models.travel_agent_agent import TravelAgentAgent as TravelAgentAgent
from wink_sdk_affiliate.models.travel_agent_supplier import TravelAgentSupplier as TravelAgentSupplier
from wink_sdk_affiliate.models.upsert_address_request_affiliate import UpsertAddressRequestAffiliate as UpsertAddressRequestAffiliate
from wink_sdk_affiliate.models.upsert_affiliate_account_profile_request_affiliate import UpsertAffiliateAccountProfileRequestAffiliate as UpsertAffiliateAccountProfileRequestAffiliate
from wink_sdk_affiliate.models.upsert_company_logo_request_affiliate import UpsertCompanyLogoRequestAffiliate as UpsertCompanyLogoRequestAffiliate
from wink_sdk_affiliate.models.upsert_company_online_presence_request_affiliate import UpsertCompanyOnlinePresenceRequestAffiliate as UpsertCompanyOnlinePresenceRequestAffiliate
from wink_sdk_affiliate.models.upsert_company_request_affiliate import UpsertCompanyRequestAffiliate as UpsertCompanyRequestAffiliate
from wink_sdk_affiliate.models.upsert_company_status_request_affiliate import UpsertCompanyStatusRequestAffiliate as UpsertCompanyStatusRequestAffiliate
from wink_sdk_affiliate.models.upsert_managed_by_agency_request_affiliate import UpsertManagedByAgencyRequestAffiliate as UpsertManagedByAgencyRequestAffiliate
from wink_sdk_affiliate.models.upsert_travel_agent_request_agent import UpsertTravelAgentRequestAgent as UpsertTravelAgentRequestAgent

