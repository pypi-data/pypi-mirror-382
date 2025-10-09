# coding: utf-8

# flake8: noqa

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Extranet Monetize API This part of the documentation concerns itself with the management of cancellation policies, promotions, restrictions etc. This API lets you create:  1. Add-ons: Manage add-ons. 2. Cancellation policies: Manage cancellation policies for your property. 3. Rate plan: Manage property rate plans. 4. Master rates: Manage perks for room type / rate plan combos. 5. Promotions: Manage promotions. 6. Promotion bundle: Manage bundled promotions.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.23.0
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "0.0.47"

# Define package exports
__all__ = [
    "AddOnApi",
    "CancellationPolicyApi",
    "DailyRateApi",
    "InventoryApi",
    "InventoryUsageApi",
    "MasterRateApi",
    "PromotionApi",
    "PromotionBundleApi",
    "RatePlanApi",
    "ApiResponse",
    "ApiClient",
    "Configuration",
    "OpenApiException",
    "ApiTypeError",
    "ApiValueError",
    "ApiKeyError",
    "ApiAttributeError",
    "ApiException",
    "AddOn",
    "Address",
    "AddressSupplier",
    "AdvanceBookingRateQualifierSupplier",
    "AggregateDescriptorSupplier",
    "ArrivalDaysOfWeekRateQualifierSupplier",
    "AvailableDaysOfWeekRateQualifierSupplier",
    "BedSupplier",
    "BedroomConfigurationSupplier",
    "BedroomSupplier",
    "BlackoutDateSupplier",
    "CancellationPolicyException",
    "CancellationPolicyExceptionSupplier",
    "CancellationPolicyExceptions",
    "CancellationPolicyExceptionsSupplier",
    "CancellationPolicyLightweight",
    "CancellationPolicyLightweightSupplier",
    "CancellationPolicyRemovableResponseSupplier",
    "CancellationPolicySupplier",
    "CityRateQualifierSupplier",
    "CompositeFilterDescriptorSupplier",
    "Contact",
    "ContactSupplier",
    "ContinentRateQualifierSupplier",
    "CountryLightweight",
    "CountryLightweightSupplier",
    "CountryRateQualifierSupplier",
    "CustomMonetaryAmount",
    "DateRangeSupplier",
    "DepartureDaysOfWeekRateQualifierSupplier",
    "DowPatternGroup",
    "DowPatternGroupSupplier",
    "FilterDescriptorSupplier",
    "GenericErrorMessage",
    "GeoIpLightweightSupplier",
    "GeoJsonPoint",
    "GeoJsonPointSupplier",
    "GeoNameCountrySupplier",
    "GeoNameLightweight",
    "GeoNameLightweightSupplier",
    "GroupDescriptorSupplier",
    "IPRangeRateQualifierSupplier",
    "IdentifierNamePairSupplier",
    "InventoryUsageItemSupplier",
    "InventoryUsageSupplier",
    "KeyValuePairSupplier",
    "LengthOfStayRateQualifierSupplier",
    "LocalizedDescription",
    "LocalizedDescriptionSupplier",
    "MasterRateSupplier",
    "MediaAuthorAttribution",
    "MediaAuthorAttributionSupplier",
    "MinutesBeforeBookingStartDateRateQualifierSupplier",
    "PageRateSupplier",
    "PageableObjectSupplier",
    "PrepayRateQualifierSupplier",
    "PromotionRateQualifierSupplier",
    "RatePlanLevelFee",
    "RatePlanLevelFeeSupplier",
    "RatePlanLightweight",
    "RatePlanLightweightSupplier",
    "RatePlanSupplier",
    "RateSupplier",
    "RefundableRateQualifierSupplier",
    "RemoveEntryResponse",
    "RequiredDaysOfWeekRateQualifierSupplier",
    "RoomRangeRateQualifierSupplier",
    "RoomTypeLightweightSupplier",
    "SellDateRateQualifierSupplier",
    "SetMasterRatePerkRequestSupplier",
    "ShowRatePlan400Response",
    "SimpleDescription",
    "SimpleDescriptionSupplier",
    "SimpleMultimedia",
    "SimpleMultimediaSupplier",
    "Social",
    "SocialSupplier",
    "SortDescriptorSupplier",
    "SortObjectSupplier",
    "SpecialRateBundleSupplier",
    "SpecialRateSupplier",
    "StateSupplier",
    "StayDateRateQualifierSupplier",
    "SubCountryLightweight",
    "SubCountryLightweightSupplier",
    "SubSubCountryLightweight",
    "SubSubCountryLightweightSupplier",
    "TimezoneRateQualifierSupplier",
    "ToggleMasterRateRequestSupplier",
    "TransactionalTravelInventory",
    "TransactionalTravelInventorySupplier",
    "TravelInventoryRecognition",
    "TravelInventoryRecognitionSupplier",
    "UpsertAddOnRequest",
    "UpsertAddressRequest",
    "UpsertBulkRateRequestSupplier",
    "UpsertCancellationPolicyExceptionSupplier",
    "UpsertCancellationPolicyExceptionsSupplier",
    "UpsertCancellationPolicyRequestSupplier",
    "UpsertRatePlanRequestSupplier",
    "UpsertSimpleDescription",
    "UpsertSpecialRateBundleRequestSupplier",
    "UpsertSpecialRateRequestSupplier",
    "VariableCharge",
    "VariableChargeSupplier",
]

# import apis into sdk package
from wink_sdk_extranet_monetize.api.add_on_api import AddOnApi as AddOnApi
from wink_sdk_extranet_monetize.api.cancellation_policy_api import CancellationPolicyApi as CancellationPolicyApi
from wink_sdk_extranet_monetize.api.daily_rate_api import DailyRateApi as DailyRateApi
from wink_sdk_extranet_monetize.api.inventory_api import InventoryApi as InventoryApi
from wink_sdk_extranet_monetize.api.inventory_usage_api import InventoryUsageApi as InventoryUsageApi
from wink_sdk_extranet_monetize.api.master_rate_api import MasterRateApi as MasterRateApi
from wink_sdk_extranet_monetize.api.promotion_api import PromotionApi as PromotionApi
from wink_sdk_extranet_monetize.api.promotion_bundle_api import PromotionBundleApi as PromotionBundleApi
from wink_sdk_extranet_monetize.api.rate_plan_api import RatePlanApi as RatePlanApi

# import ApiClient
from wink_sdk_extranet_monetize.api_response import ApiResponse as ApiResponse
from wink_sdk_extranet_monetize.api_client import ApiClient as ApiClient
from wink_sdk_extranet_monetize.configuration import Configuration as Configuration
from wink_sdk_extranet_monetize.exceptions import OpenApiException as OpenApiException
from wink_sdk_extranet_monetize.exceptions import ApiTypeError as ApiTypeError
from wink_sdk_extranet_monetize.exceptions import ApiValueError as ApiValueError
from wink_sdk_extranet_monetize.exceptions import ApiKeyError as ApiKeyError
from wink_sdk_extranet_monetize.exceptions import ApiAttributeError as ApiAttributeError
from wink_sdk_extranet_monetize.exceptions import ApiException as ApiException

# import models into sdk package
from wink_sdk_extranet_monetize.models.add_on import AddOn as AddOn
from wink_sdk_extranet_monetize.models.address import Address as Address
from wink_sdk_extranet_monetize.models.address_supplier import AddressSupplier as AddressSupplier
from wink_sdk_extranet_monetize.models.advance_booking_rate_qualifier_supplier import AdvanceBookingRateQualifierSupplier as AdvanceBookingRateQualifierSupplier
from wink_sdk_extranet_monetize.models.aggregate_descriptor_supplier import AggregateDescriptorSupplier as AggregateDescriptorSupplier
from wink_sdk_extranet_monetize.models.arrival_days_of_week_rate_qualifier_supplier import ArrivalDaysOfWeekRateQualifierSupplier as ArrivalDaysOfWeekRateQualifierSupplier
from wink_sdk_extranet_monetize.models.available_days_of_week_rate_qualifier_supplier import AvailableDaysOfWeekRateQualifierSupplier as AvailableDaysOfWeekRateQualifierSupplier
from wink_sdk_extranet_monetize.models.bed_supplier import BedSupplier as BedSupplier
from wink_sdk_extranet_monetize.models.bedroom_configuration_supplier import BedroomConfigurationSupplier as BedroomConfigurationSupplier
from wink_sdk_extranet_monetize.models.bedroom_supplier import BedroomSupplier as BedroomSupplier
from wink_sdk_extranet_monetize.models.blackout_date_supplier import BlackoutDateSupplier as BlackoutDateSupplier
from wink_sdk_extranet_monetize.models.cancellation_policy_exception import CancellationPolicyException as CancellationPolicyException
from wink_sdk_extranet_monetize.models.cancellation_policy_exception_supplier import CancellationPolicyExceptionSupplier as CancellationPolicyExceptionSupplier
from wink_sdk_extranet_monetize.models.cancellation_policy_exceptions import CancellationPolicyExceptions as CancellationPolicyExceptions
from wink_sdk_extranet_monetize.models.cancellation_policy_exceptions_supplier import CancellationPolicyExceptionsSupplier as CancellationPolicyExceptionsSupplier
from wink_sdk_extranet_monetize.models.cancellation_policy_lightweight import CancellationPolicyLightweight as CancellationPolicyLightweight
from wink_sdk_extranet_monetize.models.cancellation_policy_lightweight_supplier import CancellationPolicyLightweightSupplier as CancellationPolicyLightweightSupplier
from wink_sdk_extranet_monetize.models.cancellation_policy_removable_response_supplier import CancellationPolicyRemovableResponseSupplier as CancellationPolicyRemovableResponseSupplier
from wink_sdk_extranet_monetize.models.cancellation_policy_supplier import CancellationPolicySupplier as CancellationPolicySupplier
from wink_sdk_extranet_monetize.models.city_rate_qualifier_supplier import CityRateQualifierSupplier as CityRateQualifierSupplier
from wink_sdk_extranet_monetize.models.composite_filter_descriptor_supplier import CompositeFilterDescriptorSupplier as CompositeFilterDescriptorSupplier
from wink_sdk_extranet_monetize.models.contact import Contact as Contact
from wink_sdk_extranet_monetize.models.contact_supplier import ContactSupplier as ContactSupplier
from wink_sdk_extranet_monetize.models.continent_rate_qualifier_supplier import ContinentRateQualifierSupplier as ContinentRateQualifierSupplier
from wink_sdk_extranet_monetize.models.country_lightweight import CountryLightweight as CountryLightweight
from wink_sdk_extranet_monetize.models.country_lightweight_supplier import CountryLightweightSupplier as CountryLightweightSupplier
from wink_sdk_extranet_monetize.models.country_rate_qualifier_supplier import CountryRateQualifierSupplier as CountryRateQualifierSupplier
from wink_sdk_extranet_monetize.models.custom_monetary_amount import CustomMonetaryAmount as CustomMonetaryAmount
from wink_sdk_extranet_monetize.models.date_range_supplier import DateRangeSupplier as DateRangeSupplier
from wink_sdk_extranet_monetize.models.departure_days_of_week_rate_qualifier_supplier import DepartureDaysOfWeekRateQualifierSupplier as DepartureDaysOfWeekRateQualifierSupplier
from wink_sdk_extranet_monetize.models.dow_pattern_group import DowPatternGroup as DowPatternGroup
from wink_sdk_extranet_monetize.models.dow_pattern_group_supplier import DowPatternGroupSupplier as DowPatternGroupSupplier
from wink_sdk_extranet_monetize.models.filter_descriptor_supplier import FilterDescriptorSupplier as FilterDescriptorSupplier
from wink_sdk_extranet_monetize.models.generic_error_message import GenericErrorMessage as GenericErrorMessage
from wink_sdk_extranet_monetize.models.geo_ip_lightweight_supplier import GeoIpLightweightSupplier as GeoIpLightweightSupplier
from wink_sdk_extranet_monetize.models.geo_json_point import GeoJsonPoint as GeoJsonPoint
from wink_sdk_extranet_monetize.models.geo_json_point_supplier import GeoJsonPointSupplier as GeoJsonPointSupplier
from wink_sdk_extranet_monetize.models.geo_name_country_supplier import GeoNameCountrySupplier as GeoNameCountrySupplier
from wink_sdk_extranet_monetize.models.geo_name_lightweight import GeoNameLightweight as GeoNameLightweight
from wink_sdk_extranet_monetize.models.geo_name_lightweight_supplier import GeoNameLightweightSupplier as GeoNameLightweightSupplier
from wink_sdk_extranet_monetize.models.group_descriptor_supplier import GroupDescriptorSupplier as GroupDescriptorSupplier
from wink_sdk_extranet_monetize.models.ip_range_rate_qualifier_supplier import IPRangeRateQualifierSupplier as IPRangeRateQualifierSupplier
from wink_sdk_extranet_monetize.models.identifier_name_pair_supplier import IdentifierNamePairSupplier as IdentifierNamePairSupplier
from wink_sdk_extranet_monetize.models.inventory_usage_item_supplier import InventoryUsageItemSupplier as InventoryUsageItemSupplier
from wink_sdk_extranet_monetize.models.inventory_usage_supplier import InventoryUsageSupplier as InventoryUsageSupplier
from wink_sdk_extranet_monetize.models.key_value_pair_supplier import KeyValuePairSupplier as KeyValuePairSupplier
from wink_sdk_extranet_monetize.models.length_of_stay_rate_qualifier_supplier import LengthOfStayRateQualifierSupplier as LengthOfStayRateQualifierSupplier
from wink_sdk_extranet_monetize.models.localized_description import LocalizedDescription as LocalizedDescription
from wink_sdk_extranet_monetize.models.localized_description_supplier import LocalizedDescriptionSupplier as LocalizedDescriptionSupplier
from wink_sdk_extranet_monetize.models.master_rate_supplier import MasterRateSupplier as MasterRateSupplier
from wink_sdk_extranet_monetize.models.media_author_attribution import MediaAuthorAttribution as MediaAuthorAttribution
from wink_sdk_extranet_monetize.models.media_author_attribution_supplier import MediaAuthorAttributionSupplier as MediaAuthorAttributionSupplier
from wink_sdk_extranet_monetize.models.minutes_before_booking_start_date_rate_qualifier_supplier import MinutesBeforeBookingStartDateRateQualifierSupplier as MinutesBeforeBookingStartDateRateQualifierSupplier
from wink_sdk_extranet_monetize.models.page_rate_supplier import PageRateSupplier as PageRateSupplier
from wink_sdk_extranet_monetize.models.pageable_object_supplier import PageableObjectSupplier as PageableObjectSupplier
from wink_sdk_extranet_monetize.models.prepay_rate_qualifier_supplier import PrepayRateQualifierSupplier as PrepayRateQualifierSupplier
from wink_sdk_extranet_monetize.models.promotion_rate_qualifier_supplier import PromotionRateQualifierSupplier as PromotionRateQualifierSupplier
from wink_sdk_extranet_monetize.models.rate_plan_level_fee import RatePlanLevelFee as RatePlanLevelFee
from wink_sdk_extranet_monetize.models.rate_plan_level_fee_supplier import RatePlanLevelFeeSupplier as RatePlanLevelFeeSupplier
from wink_sdk_extranet_monetize.models.rate_plan_lightweight import RatePlanLightweight as RatePlanLightweight
from wink_sdk_extranet_monetize.models.rate_plan_lightweight_supplier import RatePlanLightweightSupplier as RatePlanLightweightSupplier
from wink_sdk_extranet_monetize.models.rate_plan_supplier import RatePlanSupplier as RatePlanSupplier
from wink_sdk_extranet_monetize.models.rate_supplier import RateSupplier as RateSupplier
from wink_sdk_extranet_monetize.models.refundable_rate_qualifier_supplier import RefundableRateQualifierSupplier as RefundableRateQualifierSupplier
from wink_sdk_extranet_monetize.models.remove_entry_response import RemoveEntryResponse as RemoveEntryResponse
from wink_sdk_extranet_monetize.models.required_days_of_week_rate_qualifier_supplier import RequiredDaysOfWeekRateQualifierSupplier as RequiredDaysOfWeekRateQualifierSupplier
from wink_sdk_extranet_monetize.models.room_range_rate_qualifier_supplier import RoomRangeRateQualifierSupplier as RoomRangeRateQualifierSupplier
from wink_sdk_extranet_monetize.models.room_type_lightweight_supplier import RoomTypeLightweightSupplier as RoomTypeLightweightSupplier
from wink_sdk_extranet_monetize.models.sell_date_rate_qualifier_supplier import SellDateRateQualifierSupplier as SellDateRateQualifierSupplier
from wink_sdk_extranet_monetize.models.set_master_rate_perk_request_supplier import SetMasterRatePerkRequestSupplier as SetMasterRatePerkRequestSupplier
from wink_sdk_extranet_monetize.models.show_rate_plan400_response import ShowRatePlan400Response as ShowRatePlan400Response
from wink_sdk_extranet_monetize.models.simple_description import SimpleDescription as SimpleDescription
from wink_sdk_extranet_monetize.models.simple_description_supplier import SimpleDescriptionSupplier as SimpleDescriptionSupplier
from wink_sdk_extranet_monetize.models.simple_multimedia import SimpleMultimedia as SimpleMultimedia
from wink_sdk_extranet_monetize.models.simple_multimedia_supplier import SimpleMultimediaSupplier as SimpleMultimediaSupplier
from wink_sdk_extranet_monetize.models.social import Social as Social
from wink_sdk_extranet_monetize.models.social_supplier import SocialSupplier as SocialSupplier
from wink_sdk_extranet_monetize.models.sort_descriptor_supplier import SortDescriptorSupplier as SortDescriptorSupplier
from wink_sdk_extranet_monetize.models.sort_object_supplier import SortObjectSupplier as SortObjectSupplier
from wink_sdk_extranet_monetize.models.special_rate_bundle_supplier import SpecialRateBundleSupplier as SpecialRateBundleSupplier
from wink_sdk_extranet_monetize.models.special_rate_supplier import SpecialRateSupplier as SpecialRateSupplier
from wink_sdk_extranet_monetize.models.state_supplier import StateSupplier as StateSupplier
from wink_sdk_extranet_monetize.models.stay_date_rate_qualifier_supplier import StayDateRateQualifierSupplier as StayDateRateQualifierSupplier
from wink_sdk_extranet_monetize.models.sub_country_lightweight import SubCountryLightweight as SubCountryLightweight
from wink_sdk_extranet_monetize.models.sub_country_lightweight_supplier import SubCountryLightweightSupplier as SubCountryLightweightSupplier
from wink_sdk_extranet_monetize.models.sub_sub_country_lightweight import SubSubCountryLightweight as SubSubCountryLightweight
from wink_sdk_extranet_monetize.models.sub_sub_country_lightweight_supplier import SubSubCountryLightweightSupplier as SubSubCountryLightweightSupplier
from wink_sdk_extranet_monetize.models.timezone_rate_qualifier_supplier import TimezoneRateQualifierSupplier as TimezoneRateQualifierSupplier
from wink_sdk_extranet_monetize.models.toggle_master_rate_request_supplier import ToggleMasterRateRequestSupplier as ToggleMasterRateRequestSupplier
from wink_sdk_extranet_monetize.models.transactional_travel_inventory import TransactionalTravelInventory as TransactionalTravelInventory
from wink_sdk_extranet_monetize.models.transactional_travel_inventory_supplier import TransactionalTravelInventorySupplier as TransactionalTravelInventorySupplier
from wink_sdk_extranet_monetize.models.travel_inventory_recognition import TravelInventoryRecognition as TravelInventoryRecognition
from wink_sdk_extranet_monetize.models.travel_inventory_recognition_supplier import TravelInventoryRecognitionSupplier as TravelInventoryRecognitionSupplier
from wink_sdk_extranet_monetize.models.upsert_add_on_request import UpsertAddOnRequest as UpsertAddOnRequest
from wink_sdk_extranet_monetize.models.upsert_address_request import UpsertAddressRequest as UpsertAddressRequest
from wink_sdk_extranet_monetize.models.upsert_bulk_rate_request_supplier import UpsertBulkRateRequestSupplier as UpsertBulkRateRequestSupplier
from wink_sdk_extranet_monetize.models.upsert_cancellation_policy_exception_supplier import UpsertCancellationPolicyExceptionSupplier as UpsertCancellationPolicyExceptionSupplier
from wink_sdk_extranet_monetize.models.upsert_cancellation_policy_exceptions_supplier import UpsertCancellationPolicyExceptionsSupplier as UpsertCancellationPolicyExceptionsSupplier
from wink_sdk_extranet_monetize.models.upsert_cancellation_policy_request_supplier import UpsertCancellationPolicyRequestSupplier as UpsertCancellationPolicyRequestSupplier
from wink_sdk_extranet_monetize.models.upsert_rate_plan_request_supplier import UpsertRatePlanRequestSupplier as UpsertRatePlanRequestSupplier
from wink_sdk_extranet_monetize.models.upsert_simple_description import UpsertSimpleDescription as UpsertSimpleDescription
from wink_sdk_extranet_monetize.models.upsert_special_rate_bundle_request_supplier import UpsertSpecialRateBundleRequestSupplier as UpsertSpecialRateBundleRequestSupplier
from wink_sdk_extranet_monetize.models.upsert_special_rate_request_supplier import UpsertSpecialRateRequestSupplier as UpsertSpecialRateRequestSupplier
from wink_sdk_extranet_monetize.models.variable_charge import VariableCharge as VariableCharge
from wink_sdk_extranet_monetize.models.variable_charge_supplier import VariableChargeSupplier as VariableChargeSupplier

