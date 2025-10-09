# coding: utf-8

# flake8: noqa

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Browse API The Browse API exposes endpoints to find suppliers and inventory to sell. This API lets you:  1. Browse: Find inventory and suppliers. 2. Saved Search: Manage saved searches 3. Curated List: Manage curated lists  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.23.0
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "0.0.47"

# Define package exports
__all__ = [
    "BrowseApi",
    "CuratedListApi",
    "DynamicListApi",
    "ApiResponse",
    "ApiClient",
    "Configuration",
    "OpenApiException",
    "ApiTypeError",
    "ApiValueError",
    "ApiKeyError",
    "ApiAttributeError",
    "ApiException",
    "AddStaticListItemRequestAffiliate",
    "AddStaticListSupplierRequestAffiliate",
    "ContactAffiliate",
    "CopyMoveStaticListItemRequestAffiliate",
    "CreateStaticListAndAddItemRequestAffiliate",
    "CreateStaticListAndAddSupplierRequestAffiliate",
    "CustomMonetaryAmount",
    "DynamicListAffiliate",
    "DynamicSellerListRequestAffiliate",
    "GeneralManagerAffiliate",
    "GenericErrorMessage",
    "GeoJsonPointAffiliate",
    "InventoryAddressAffiliate",
    "InventoryAggregateLightweightAffiliate",
    "InventorySupplierAggregateLightweightAffiliate",
    "KeyValuePairAffiliate",
    "LocalizedDescriptionAffiliate",
    "MediaAuthorAttributionAffiliate",
    "PageInventoryAggregateLightweightAffiliate",
    "PageInventorySupplierAggregateLightweightAffiliate",
    "PageableObjectAffiliate",
    "PropertyAggregateLightweightAffiliate",
    "PropertyPolicyAffiliate",
    "SalesChannelLightweightAffiliate",
    "SearchCategoryAffiliate",
    "SimpleAddressAffiliate",
    "SimpleDescriptionAffiliate",
    "SimpleMultimediaAffiliate",
    "SocialAffiliate",
    "SortObjectAffiliate",
    "SortStaticListItemsRequestAffiliate",
    "SpecialRateBundleLightweightAffiliate",
    "SpecialRateLightweightAffiliate",
    "StaticListAffiliate",
    "StaticListItemAffiliate",
    "StaticListItemInventoryAffiliate",
    "StaticListLightweightAffiliate",
    "StaticListWrapperAffiliate",
    "TravelInventoryRecognitionAffiliate",
    "UpdateCuratedList400Response",
    "UpsertDynamicListRequestAffiliate",
    "UpsertDynamicSellerListRequestAffiliate",
    "UpsertStaticListRequestAffiliate",
]

# import apis into sdk package
from wink_sdk_affiliate_browse.api.browse_api import BrowseApi as BrowseApi
from wink_sdk_affiliate_browse.api.curated_list_api import CuratedListApi as CuratedListApi
from wink_sdk_affiliate_browse.api.dynamic_list_api import DynamicListApi as DynamicListApi

# import ApiClient
from wink_sdk_affiliate_browse.api_response import ApiResponse as ApiResponse
from wink_sdk_affiliate_browse.api_client import ApiClient as ApiClient
from wink_sdk_affiliate_browse.configuration import Configuration as Configuration
from wink_sdk_affiliate_browse.exceptions import OpenApiException as OpenApiException
from wink_sdk_affiliate_browse.exceptions import ApiTypeError as ApiTypeError
from wink_sdk_affiliate_browse.exceptions import ApiValueError as ApiValueError
from wink_sdk_affiliate_browse.exceptions import ApiKeyError as ApiKeyError
from wink_sdk_affiliate_browse.exceptions import ApiAttributeError as ApiAttributeError
from wink_sdk_affiliate_browse.exceptions import ApiException as ApiException

# import models into sdk package
from wink_sdk_affiliate_browse.models.add_static_list_item_request_affiliate import AddStaticListItemRequestAffiliate as AddStaticListItemRequestAffiliate
from wink_sdk_affiliate_browse.models.add_static_list_supplier_request_affiliate import AddStaticListSupplierRequestAffiliate as AddStaticListSupplierRequestAffiliate
from wink_sdk_affiliate_browse.models.contact_affiliate import ContactAffiliate as ContactAffiliate
from wink_sdk_affiliate_browse.models.copy_move_static_list_item_request_affiliate import CopyMoveStaticListItemRequestAffiliate as CopyMoveStaticListItemRequestAffiliate
from wink_sdk_affiliate_browse.models.create_static_list_and_add_item_request_affiliate import CreateStaticListAndAddItemRequestAffiliate as CreateStaticListAndAddItemRequestAffiliate
from wink_sdk_affiliate_browse.models.create_static_list_and_add_supplier_request_affiliate import CreateStaticListAndAddSupplierRequestAffiliate as CreateStaticListAndAddSupplierRequestAffiliate
from wink_sdk_affiliate_browse.models.custom_monetary_amount import CustomMonetaryAmount as CustomMonetaryAmount
from wink_sdk_affiliate_browse.models.dynamic_list_affiliate import DynamicListAffiliate as DynamicListAffiliate
from wink_sdk_affiliate_browse.models.dynamic_seller_list_request_affiliate import DynamicSellerListRequestAffiliate as DynamicSellerListRequestAffiliate
from wink_sdk_affiliate_browse.models.general_manager_affiliate import GeneralManagerAffiliate as GeneralManagerAffiliate
from wink_sdk_affiliate_browse.models.generic_error_message import GenericErrorMessage as GenericErrorMessage
from wink_sdk_affiliate_browse.models.geo_json_point_affiliate import GeoJsonPointAffiliate as GeoJsonPointAffiliate
from wink_sdk_affiliate_browse.models.inventory_address_affiliate import InventoryAddressAffiliate as InventoryAddressAffiliate
from wink_sdk_affiliate_browse.models.inventory_aggregate_lightweight_affiliate import InventoryAggregateLightweightAffiliate as InventoryAggregateLightweightAffiliate
from wink_sdk_affiliate_browse.models.inventory_supplier_aggregate_lightweight_affiliate import InventorySupplierAggregateLightweightAffiliate as InventorySupplierAggregateLightweightAffiliate
from wink_sdk_affiliate_browse.models.key_value_pair_affiliate import KeyValuePairAffiliate as KeyValuePairAffiliate
from wink_sdk_affiliate_browse.models.localized_description_affiliate import LocalizedDescriptionAffiliate as LocalizedDescriptionAffiliate
from wink_sdk_affiliate_browse.models.media_author_attribution_affiliate import MediaAuthorAttributionAffiliate as MediaAuthorAttributionAffiliate
from wink_sdk_affiliate_browse.models.page_inventory_aggregate_lightweight_affiliate import PageInventoryAggregateLightweightAffiliate as PageInventoryAggregateLightweightAffiliate
from wink_sdk_affiliate_browse.models.page_inventory_supplier_aggregate_lightweight_affiliate import PageInventorySupplierAggregateLightweightAffiliate as PageInventorySupplierAggregateLightweightAffiliate
from wink_sdk_affiliate_browse.models.pageable_object_affiliate import PageableObjectAffiliate as PageableObjectAffiliate
from wink_sdk_affiliate_browse.models.property_aggregate_lightweight_affiliate import PropertyAggregateLightweightAffiliate as PropertyAggregateLightweightAffiliate
from wink_sdk_affiliate_browse.models.property_policy_affiliate import PropertyPolicyAffiliate as PropertyPolicyAffiliate
from wink_sdk_affiliate_browse.models.sales_channel_lightweight_affiliate import SalesChannelLightweightAffiliate as SalesChannelLightweightAffiliate
from wink_sdk_affiliate_browse.models.search_category_affiliate import SearchCategoryAffiliate as SearchCategoryAffiliate
from wink_sdk_affiliate_browse.models.simple_address_affiliate import SimpleAddressAffiliate as SimpleAddressAffiliate
from wink_sdk_affiliate_browse.models.simple_description_affiliate import SimpleDescriptionAffiliate as SimpleDescriptionAffiliate
from wink_sdk_affiliate_browse.models.simple_multimedia_affiliate import SimpleMultimediaAffiliate as SimpleMultimediaAffiliate
from wink_sdk_affiliate_browse.models.social_affiliate import SocialAffiliate as SocialAffiliate
from wink_sdk_affiliate_browse.models.sort_object_affiliate import SortObjectAffiliate as SortObjectAffiliate
from wink_sdk_affiliate_browse.models.sort_static_list_items_request_affiliate import SortStaticListItemsRequestAffiliate as SortStaticListItemsRequestAffiliate
from wink_sdk_affiliate_browse.models.special_rate_bundle_lightweight_affiliate import SpecialRateBundleLightweightAffiliate as SpecialRateBundleLightweightAffiliate
from wink_sdk_affiliate_browse.models.special_rate_lightweight_affiliate import SpecialRateLightweightAffiliate as SpecialRateLightweightAffiliate
from wink_sdk_affiliate_browse.models.static_list_affiliate import StaticListAffiliate as StaticListAffiliate
from wink_sdk_affiliate_browse.models.static_list_item_affiliate import StaticListItemAffiliate as StaticListItemAffiliate
from wink_sdk_affiliate_browse.models.static_list_item_inventory_affiliate import StaticListItemInventoryAffiliate as StaticListItemInventoryAffiliate
from wink_sdk_affiliate_browse.models.static_list_lightweight_affiliate import StaticListLightweightAffiliate as StaticListLightweightAffiliate
from wink_sdk_affiliate_browse.models.static_list_wrapper_affiliate import StaticListWrapperAffiliate as StaticListWrapperAffiliate
from wink_sdk_affiliate_browse.models.travel_inventory_recognition_affiliate import TravelInventoryRecognitionAffiliate as TravelInventoryRecognitionAffiliate
from wink_sdk_affiliate_browse.models.update_curated_list400_response import UpdateCuratedList400Response as UpdateCuratedList400Response
from wink_sdk_affiliate_browse.models.upsert_dynamic_list_request_affiliate import UpsertDynamicListRequestAffiliate as UpsertDynamicListRequestAffiliate
from wink_sdk_affiliate_browse.models.upsert_dynamic_seller_list_request_affiliate import UpsertDynamicSellerListRequestAffiliate as UpsertDynamicSellerListRequestAffiliate
from wink_sdk_affiliate_browse.models.upsert_static_list_request_affiliate import UpsertStaticListRequestAffiliate as UpsertStaticListRequestAffiliate

