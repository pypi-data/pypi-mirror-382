# coding: utf-8

# flake8: noqa

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Extranet Distribution API The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink. This API lets you:  1. Verifier: Test your availability and promotions and create test bookings to simulate the entire booking workflow. 2. Sales Channels: Manage your sales channels. 3. Explore Network: Find new affiliates to work with. 4. Inventory: Manage inventory at the sales channel-level. 5. Calendars: Manage availability calendars for all your inventory.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.23.0
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "0.0.47"

# Define package exports
__all__ = [
    "AffiliateApi",
    "InventoryApi",
    "InventoryUsageApi",
    "SalesChannelApi",
    "SalesChannelRequestApi",
    "SchedulerApi",
    "ApiResponse",
    "ApiClient",
    "Configuration",
    "OpenApiException",
    "ApiTypeError",
    "ApiValueError",
    "ApiKeyError",
    "ApiAttributeError",
    "ApiException",
    "AdvanceBookingRateQualifierSupplier",
    "AggregateDescriptorSupplier",
    "ArrivalDaysOfWeekRateQualifierSupplier",
    "AvailableDaysOfWeekRateQualifierSupplier",
    "BlackoutDateSupplier",
    "BooleanResponseSupplier",
    "CityRateQualifierSupplier",
    "CompanyDetailsBookingSalesMetricsSupplier",
    "CompositeFilterDescriptorSupplier",
    "ContactSupplier",
    "ContinentRateQualifierSupplier",
    "CountryRateQualifierSupplier",
    "CreateScheduleItemRequestSupplier",
    "CustomMonetaryAmount",
    "DepartureDaysOfWeekRateQualifierSupplier",
    "DisplayCompanySupplier",
    "DisplayCompanyWithSalesMetricsSupplier",
    "DowPatternGroupSupplier",
    "FilterDescriptorSupplier",
    "GenericErrorMessage",
    "GeoIpLightweightSupplier",
    "GeoJsonPointSupplier",
    "GeoNameCountrySupplier",
    "GroupDescriptorSupplier",
    "GroupedBookingSalesMetricsSupplier",
    "IPRangeRateQualifierSupplier",
    "InventoryAddressSupplier",
    "InventorySupplier",
    "InventoryUpdateRequestSupplier",
    "InventoryUsageItemSupplier",
    "InventoryUsageSupplier",
    "InviteAffiliateRequestSupplier",
    "KeyValuePairSupplier",
    "LengthOfStayRateQualifierSupplier",
    "LocalizedDescriptionSupplier",
    "MediaAuthorAttributionSupplier",
    "MinutesBeforeBookingStartDateRateQualifierSupplier",
    "PageDisplayCompanyWithSalesMetricsSupplier",
    "PageInventorySupplier",
    "PageableObjectSupplier",
    "PrepayRateQualifierSupplier",
    "PromotionRateQualifierSupplier",
    "RefundableRateQualifierSupplier",
    "RequiredDaysOfWeekRateQualifierSupplier",
    "RoomRangeRateQualifierSupplier",
    "SalesChannelCreateRequestSupplier",
    "SalesChannelLightweightSupplier",
    "SalesChannelRequestSupplier",
    "SalesChannelSupplier",
    "SalesChannelUpdateRequestSupplier",
    "ScheduleItemSupplier",
    "SelectableKeyValuePairSupplier",
    "SellDateRateQualifierSupplier",
    "ShowInventory400Response",
    "SimpleAddressSupplier",
    "SimpleDescriptionSupplier",
    "SimpleMultimediaSupplier",
    "SortDescriptorSupplier",
    "SortObjectSupplier",
    "SpecialRateBundleLightweightSupplier",
    "SpecialRateLightweightSupplier",
    "StateSupplier",
    "StayDateRateQualifierSupplier",
    "TimezoneRateQualifierSupplier",
    "TravelAgentSupplier",
    "UpdateScheduleItemRequestSupplier",
    "UpsertSalesChannelRequestRequestSupplier",
    "VariableChargeSupplier",
]

# import apis into sdk package
from wink_sdk_extranet_distribution.api.affiliate_api import AffiliateApi as AffiliateApi
from wink_sdk_extranet_distribution.api.inventory_api import InventoryApi as InventoryApi
from wink_sdk_extranet_distribution.api.inventory_usage_api import InventoryUsageApi as InventoryUsageApi
from wink_sdk_extranet_distribution.api.sales_channel_api import SalesChannelApi as SalesChannelApi
from wink_sdk_extranet_distribution.api.sales_channel_request_api import SalesChannelRequestApi as SalesChannelRequestApi
from wink_sdk_extranet_distribution.api.scheduler_api import SchedulerApi as SchedulerApi

# import ApiClient
from wink_sdk_extranet_distribution.api_response import ApiResponse as ApiResponse
from wink_sdk_extranet_distribution.api_client import ApiClient as ApiClient
from wink_sdk_extranet_distribution.configuration import Configuration as Configuration
from wink_sdk_extranet_distribution.exceptions import OpenApiException as OpenApiException
from wink_sdk_extranet_distribution.exceptions import ApiTypeError as ApiTypeError
from wink_sdk_extranet_distribution.exceptions import ApiValueError as ApiValueError
from wink_sdk_extranet_distribution.exceptions import ApiKeyError as ApiKeyError
from wink_sdk_extranet_distribution.exceptions import ApiAttributeError as ApiAttributeError
from wink_sdk_extranet_distribution.exceptions import ApiException as ApiException

# import models into sdk package
from wink_sdk_extranet_distribution.models.advance_booking_rate_qualifier_supplier import AdvanceBookingRateQualifierSupplier as AdvanceBookingRateQualifierSupplier
from wink_sdk_extranet_distribution.models.aggregate_descriptor_supplier import AggregateDescriptorSupplier as AggregateDescriptorSupplier
from wink_sdk_extranet_distribution.models.arrival_days_of_week_rate_qualifier_supplier import ArrivalDaysOfWeekRateQualifierSupplier as ArrivalDaysOfWeekRateQualifierSupplier
from wink_sdk_extranet_distribution.models.available_days_of_week_rate_qualifier_supplier import AvailableDaysOfWeekRateQualifierSupplier as AvailableDaysOfWeekRateQualifierSupplier
from wink_sdk_extranet_distribution.models.blackout_date_supplier import BlackoutDateSupplier as BlackoutDateSupplier
from wink_sdk_extranet_distribution.models.boolean_response_supplier import BooleanResponseSupplier as BooleanResponseSupplier
from wink_sdk_extranet_distribution.models.city_rate_qualifier_supplier import CityRateQualifierSupplier as CityRateQualifierSupplier
from wink_sdk_extranet_distribution.models.company_details_booking_sales_metrics_supplier import CompanyDetailsBookingSalesMetricsSupplier as CompanyDetailsBookingSalesMetricsSupplier
from wink_sdk_extranet_distribution.models.composite_filter_descriptor_supplier import CompositeFilterDescriptorSupplier as CompositeFilterDescriptorSupplier
from wink_sdk_extranet_distribution.models.contact_supplier import ContactSupplier as ContactSupplier
from wink_sdk_extranet_distribution.models.continent_rate_qualifier_supplier import ContinentRateQualifierSupplier as ContinentRateQualifierSupplier
from wink_sdk_extranet_distribution.models.country_rate_qualifier_supplier import CountryRateQualifierSupplier as CountryRateQualifierSupplier
from wink_sdk_extranet_distribution.models.create_schedule_item_request_supplier import CreateScheduleItemRequestSupplier as CreateScheduleItemRequestSupplier
from wink_sdk_extranet_distribution.models.custom_monetary_amount import CustomMonetaryAmount as CustomMonetaryAmount
from wink_sdk_extranet_distribution.models.departure_days_of_week_rate_qualifier_supplier import DepartureDaysOfWeekRateQualifierSupplier as DepartureDaysOfWeekRateQualifierSupplier
from wink_sdk_extranet_distribution.models.display_company_supplier import DisplayCompanySupplier as DisplayCompanySupplier
from wink_sdk_extranet_distribution.models.display_company_with_sales_metrics_supplier import DisplayCompanyWithSalesMetricsSupplier as DisplayCompanyWithSalesMetricsSupplier
from wink_sdk_extranet_distribution.models.dow_pattern_group_supplier import DowPatternGroupSupplier as DowPatternGroupSupplier
from wink_sdk_extranet_distribution.models.filter_descriptor_supplier import FilterDescriptorSupplier as FilterDescriptorSupplier
from wink_sdk_extranet_distribution.models.generic_error_message import GenericErrorMessage as GenericErrorMessage
from wink_sdk_extranet_distribution.models.geo_ip_lightweight_supplier import GeoIpLightweightSupplier as GeoIpLightweightSupplier
from wink_sdk_extranet_distribution.models.geo_json_point_supplier import GeoJsonPointSupplier as GeoJsonPointSupplier
from wink_sdk_extranet_distribution.models.geo_name_country_supplier import GeoNameCountrySupplier as GeoNameCountrySupplier
from wink_sdk_extranet_distribution.models.group_descriptor_supplier import GroupDescriptorSupplier as GroupDescriptorSupplier
from wink_sdk_extranet_distribution.models.grouped_booking_sales_metrics_supplier import GroupedBookingSalesMetricsSupplier as GroupedBookingSalesMetricsSupplier
from wink_sdk_extranet_distribution.models.ip_range_rate_qualifier_supplier import IPRangeRateQualifierSupplier as IPRangeRateQualifierSupplier
from wink_sdk_extranet_distribution.models.inventory_address_supplier import InventoryAddressSupplier as InventoryAddressSupplier
from wink_sdk_extranet_distribution.models.inventory_supplier import InventorySupplier as InventorySupplier
from wink_sdk_extranet_distribution.models.inventory_update_request_supplier import InventoryUpdateRequestSupplier as InventoryUpdateRequestSupplier
from wink_sdk_extranet_distribution.models.inventory_usage_item_supplier import InventoryUsageItemSupplier as InventoryUsageItemSupplier
from wink_sdk_extranet_distribution.models.inventory_usage_supplier import InventoryUsageSupplier as InventoryUsageSupplier
from wink_sdk_extranet_distribution.models.invite_affiliate_request_supplier import InviteAffiliateRequestSupplier as InviteAffiliateRequestSupplier
from wink_sdk_extranet_distribution.models.key_value_pair_supplier import KeyValuePairSupplier as KeyValuePairSupplier
from wink_sdk_extranet_distribution.models.length_of_stay_rate_qualifier_supplier import LengthOfStayRateQualifierSupplier as LengthOfStayRateQualifierSupplier
from wink_sdk_extranet_distribution.models.localized_description_supplier import LocalizedDescriptionSupplier as LocalizedDescriptionSupplier
from wink_sdk_extranet_distribution.models.media_author_attribution_supplier import MediaAuthorAttributionSupplier as MediaAuthorAttributionSupplier
from wink_sdk_extranet_distribution.models.minutes_before_booking_start_date_rate_qualifier_supplier import MinutesBeforeBookingStartDateRateQualifierSupplier as MinutesBeforeBookingStartDateRateQualifierSupplier
from wink_sdk_extranet_distribution.models.page_display_company_with_sales_metrics_supplier import PageDisplayCompanyWithSalesMetricsSupplier as PageDisplayCompanyWithSalesMetricsSupplier
from wink_sdk_extranet_distribution.models.page_inventory_supplier import PageInventorySupplier as PageInventorySupplier
from wink_sdk_extranet_distribution.models.pageable_object_supplier import PageableObjectSupplier as PageableObjectSupplier
from wink_sdk_extranet_distribution.models.prepay_rate_qualifier_supplier import PrepayRateQualifierSupplier as PrepayRateQualifierSupplier
from wink_sdk_extranet_distribution.models.promotion_rate_qualifier_supplier import PromotionRateQualifierSupplier as PromotionRateQualifierSupplier
from wink_sdk_extranet_distribution.models.refundable_rate_qualifier_supplier import RefundableRateQualifierSupplier as RefundableRateQualifierSupplier
from wink_sdk_extranet_distribution.models.required_days_of_week_rate_qualifier_supplier import RequiredDaysOfWeekRateQualifierSupplier as RequiredDaysOfWeekRateQualifierSupplier
from wink_sdk_extranet_distribution.models.room_range_rate_qualifier_supplier import RoomRangeRateQualifierSupplier as RoomRangeRateQualifierSupplier
from wink_sdk_extranet_distribution.models.sales_channel_create_request_supplier import SalesChannelCreateRequestSupplier as SalesChannelCreateRequestSupplier
from wink_sdk_extranet_distribution.models.sales_channel_lightweight_supplier import SalesChannelLightweightSupplier as SalesChannelLightweightSupplier
from wink_sdk_extranet_distribution.models.sales_channel_request_supplier import SalesChannelRequestSupplier as SalesChannelRequestSupplier
from wink_sdk_extranet_distribution.models.sales_channel_supplier import SalesChannelSupplier as SalesChannelSupplier
from wink_sdk_extranet_distribution.models.sales_channel_update_request_supplier import SalesChannelUpdateRequestSupplier as SalesChannelUpdateRequestSupplier
from wink_sdk_extranet_distribution.models.schedule_item_supplier import ScheduleItemSupplier as ScheduleItemSupplier
from wink_sdk_extranet_distribution.models.selectable_key_value_pair_supplier import SelectableKeyValuePairSupplier as SelectableKeyValuePairSupplier
from wink_sdk_extranet_distribution.models.sell_date_rate_qualifier_supplier import SellDateRateQualifierSupplier as SellDateRateQualifierSupplier
from wink_sdk_extranet_distribution.models.show_inventory400_response import ShowInventory400Response as ShowInventory400Response
from wink_sdk_extranet_distribution.models.simple_address_supplier import SimpleAddressSupplier as SimpleAddressSupplier
from wink_sdk_extranet_distribution.models.simple_description_supplier import SimpleDescriptionSupplier as SimpleDescriptionSupplier
from wink_sdk_extranet_distribution.models.simple_multimedia_supplier import SimpleMultimediaSupplier as SimpleMultimediaSupplier
from wink_sdk_extranet_distribution.models.sort_descriptor_supplier import SortDescriptorSupplier as SortDescriptorSupplier
from wink_sdk_extranet_distribution.models.sort_object_supplier import SortObjectSupplier as SortObjectSupplier
from wink_sdk_extranet_distribution.models.special_rate_bundle_lightweight_supplier import SpecialRateBundleLightweightSupplier as SpecialRateBundleLightweightSupplier
from wink_sdk_extranet_distribution.models.special_rate_lightweight_supplier import SpecialRateLightweightSupplier as SpecialRateLightweightSupplier
from wink_sdk_extranet_distribution.models.state_supplier import StateSupplier as StateSupplier
from wink_sdk_extranet_distribution.models.stay_date_rate_qualifier_supplier import StayDateRateQualifierSupplier as StayDateRateQualifierSupplier
from wink_sdk_extranet_distribution.models.timezone_rate_qualifier_supplier import TimezoneRateQualifierSupplier as TimezoneRateQualifierSupplier
from wink_sdk_extranet_distribution.models.travel_agent_supplier import TravelAgentSupplier as TravelAgentSupplier
from wink_sdk_extranet_distribution.models.update_schedule_item_request_supplier import UpdateScheduleItemRequestSupplier as UpdateScheduleItemRequestSupplier
from wink_sdk_extranet_distribution.models.upsert_sales_channel_request_request_supplier import UpsertSalesChannelRequestRequestSupplier as UpsertSalesChannelRequestRequestSupplier
from wink_sdk_extranet_distribution.models.variable_charge_supplier import VariableChargeSupplier as VariableChargeSupplier

