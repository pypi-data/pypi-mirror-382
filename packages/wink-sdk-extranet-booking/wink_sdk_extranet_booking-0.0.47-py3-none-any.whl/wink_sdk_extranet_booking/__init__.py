# coding: utf-8

# flake8: noqa

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md   # Extranet Booking API The Booking API exposes endpoints to manage bookings. This API lets you:  1. Booking: Manage bookings including cancellations. 2. Review: Manage user reviews. 3. Sync w. Calendar: Manage calendar sync with your favorite calendar software  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.23.0
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "0.0.47"

# Define package exports
__all__ = [
    "AnalyticsApi",
    "CalendarSyncApi",
    "ConsumerBookingApi",
    "PropertyBookingApi",
    "ReviewApi",
    "TestBookingApi",
    "ApiResponse",
    "ApiClient",
    "Configuration",
    "OpenApiException",
    "ApiTypeError",
    "ApiValueError",
    "ApiKeyError",
    "ApiAttributeError",
    "ApiException",
    "AggregateDescriptorSupplier",
    "AuthenticatedUserSupplier",
    "AuthenticatedUserSupplierDetails",
    "BedSupplier",
    "BedSupplierDetails",
    "BedroomConfigurationSupplier",
    "BedroomConfigurationSupplierDetails",
    "BedroomSupplier",
    "BedroomSupplierDetails",
    "BeneficiaryChargeSupplier",
    "BeneficiaryChargeSupplierDetails",
    "BeneficiarySupplier",
    "BeneficiarySupplierDetails",
    "BookingAnalyticsSupplier",
    "BookingAncillarySupplier",
    "BookingAncillarySupplierDetails",
    "BookingCancellableSupplier",
    "BookingContractItemSupplier",
    "BookingContractItemSupplierDetails",
    "BookingContractPaymentDetailsSupplier",
    "BookingContractPaymentDetailsSupplierDetails",
    "BookingContractSupplier",
    "BookingContractSupplierDetails",
    "BookingItineraryRoomConfigurationChildSupplier",
    "BookingItineraryRoomConfigurationChildSupplierDetails",
    "BookingItineraryRoomConfigurationSupplier",
    "BookingItineraryRoomConfigurationSupplierDetails",
    "BookingItinerarySupplier",
    "BookingItinerarySupplierDetails",
    "BookingOverviewRequestSupplier",
    "BookingSupplier",
    "BookingSupplierDetails",
    "BookingTestNotificationSupplierDetails",
    "BookingTestRequestSupplierDetails",
    "BookingUserSessionSupplier",
    "BookingUserSessionSupplierDetails",
    "BookingUserSupplier",
    "BookingUserSupplierDetails",
    "BooleanResponseSupplier",
    "CalDavResponseSupplier",
    "CancellationDetailSupplier",
    "CancellationPolicyExceptionSupplier",
    "CancellationPolicyExceptionSupplierDetails",
    "CancellationPolicyExceptionsSupplier",
    "CancellationPolicyExceptionsSupplierDetails",
    "CancellationPolicyLightweightSupplier",
    "CancellationPolicyLightweightSupplierDetails",
    "ChannelNameSupplierDetails",
    "ChartCategoryAxisSupplier",
    "ChartLegendSupplier",
    "ChartSeriesSupplier",
    "ChartTitleSupplier",
    "ChildSupplier",
    "ChildSupplierDetails",
    "CommissionableEntrySupplier",
    "CommissionableEntrySupplierDetails",
    "CompositeFilterDescriptorSupplier",
    "ContactSupplier",
    "ContactSupplierDetails",
    "CountResponseSupplier",
    "CountryLightweightSupplier",
    "CountryLightweightSupplierDetails",
    "CustomMonetaryAmount",
    "CustomizationLightweightSupplier",
    "CustomizationLightweightSupplierDetails",
    "CustomizationThemeColorsSupplier",
    "CustomizationThemeColorsSupplierDetails",
    "DailyRateRateSupplierDetails",
    "DailyRateSupplierDetails",
    "ExtraChargeSupplier",
    "ExtraChargeSupplierDetails",
    "ExtraChargesSupplier",
    "ExtraChargesSupplierDetails",
    "FilterDescriptorSupplier",
    "GeneralManagerSupplier",
    "GeneralManagerSupplierDetails",
    "GenericErrorMessage",
    "GeoIpLightweightSupplierDetails",
    "GeoJsonPointSupplier",
    "GeoJsonPointSupplierDetails",
    "GeoNameCountrySupplierDetails",
    "GeoNameLightweightSupplier",
    "GeoNameLightweightSupplierDetails",
    "GroupDescriptorSupplier",
    "GroupedBookingSalesMetricsSupplierDetails",
    "GuestRoomLightweightSupplier",
    "GuestRoomLightweightSupplierDetails",
    "GuestUserSupplier",
    "GuestUserSupplierDetails",
    "KeyValuePairSupplier",
    "LineChartSupplier",
    "LocalizedDescriptionSupplier",
    "LocalizedDescriptionSupplierDetails",
    "LocalizedPriceSupplier",
    "LocalizedPriceSupplierDetails",
    "LocalizedTransactionalTravelInventorySupplierDetails",
    "MediaAuthorAttributionSupplier",
    "MediaAuthorAttributionSupplierDetails",
    "PageBookingSupplier",
    "PageReviewSupplier",
    "PageableObjectSupplier",
    "PayoutFeeSupplier",
    "PayoutFeeSupplierDetails",
    "PayoutSupplier",
    "PayoutSupplierDetails",
    "PerkLightweightSupplier",
    "PerkLightweightSupplierDetails",
    "PersonalSupplier",
    "PersonalSupplierDetails",
    "PreferencesSupplier",
    "PreferencesSupplierDetails",
    "ProfileLightweightSupplier",
    "ProfileLightweightSupplierDetails",
    "ProfileUserSupplier",
    "ProfileUserSupplierDetails",
    "PropertyAggregateLightweightSupplier",
    "PropertyAggregateLightweightSupplierDetails",
    "PropertyBookingRefundRequestSupplier",
    "PropertyPolicySupplier",
    "PropertyPolicySupplierDetails",
    "QuoteLightweightSupplier",
    "QuoteLightweightSupplierDetails",
    "RatePlanLevelFeeSupplier",
    "RatePlanLevelFeeSupplierDetails",
    "RefundSupplier",
    "RefundSupplierDetails",
    "ReviewAnswerSupplier",
    "ReviewAnswerSupplierDetails",
    "ReviewLightweightSupplier",
    "ReviewLightweightSupplierDetails",
    "ReviewResponseSupplier",
    "ReviewSupplier",
    "ReviewUserSupplier",
    "ReviewUserSupplierDetails",
    "RoomConfigurationPriceRatePlanSupplier",
    "RoomConfigurationPriceRatePlanSupplierDetails",
    "RoomConfigurationPriceSupplierDetails",
    "RoomConfigurationSupplier",
    "RoomConfigurationSupplierDetails",
    "RoomStaySupplier",
    "RoomStaySupplierDetails",
    "ShowReview400Response",
    "SimpleAddressSupplier",
    "SimpleAddressSupplierDetails",
    "SimpleDateTimeItinerarySupplier",
    "SimpleDateTimeItinerarySupplierDetails",
    "SimpleDescriptionSupplier",
    "SimpleDescriptionSupplierDetails",
    "SimpleMultimediaSupplier",
    "SimpleMultimediaSupplierDetails",
    "SocialSupplier",
    "SocialSupplierDetails",
    "SortDescriptorSupplier",
    "SortObjectSupplier",
    "StateSupplier",
    "StayRateSupplier",
    "StayRateSupplierDetails",
    "SubCountryLightweightSupplier",
    "SubCountryLightweightSupplierDetails",
    "SubSubCountryLightweightSupplier",
    "SubSubCountryLightweightSupplierDetails",
    "SupplierContractItemPolicySupplier",
    "SupplierContractItemPolicySupplierDetails",
    "TransactionalTravelInventorySupplier",
    "TransactionalTravelInventorySupplierDetails",
    "TravelInventoryRecognitionSupplier",
    "TravelInventoryRecognitionSupplierDetails",
    "VariableChargeSupplier",
    "VariableChargeSupplierDetails",
    "VerifyRatesRequestSupplierDetails",
]

# import apis into sdk package
from wink_sdk_extranet_booking.api.analytics_api import AnalyticsApi as AnalyticsApi
from wink_sdk_extranet_booking.api.calendar_sync_api import CalendarSyncApi as CalendarSyncApi
from wink_sdk_extranet_booking.api.consumer_booking_api import ConsumerBookingApi as ConsumerBookingApi
from wink_sdk_extranet_booking.api.property_booking_api import PropertyBookingApi as PropertyBookingApi
from wink_sdk_extranet_booking.api.review_api import ReviewApi as ReviewApi
from wink_sdk_extranet_booking.api.test_booking_api import TestBookingApi as TestBookingApi

# import ApiClient
from wink_sdk_extranet_booking.api_response import ApiResponse as ApiResponse
from wink_sdk_extranet_booking.api_client import ApiClient as ApiClient
from wink_sdk_extranet_booking.configuration import Configuration as Configuration
from wink_sdk_extranet_booking.exceptions import OpenApiException as OpenApiException
from wink_sdk_extranet_booking.exceptions import ApiTypeError as ApiTypeError
from wink_sdk_extranet_booking.exceptions import ApiValueError as ApiValueError
from wink_sdk_extranet_booking.exceptions import ApiKeyError as ApiKeyError
from wink_sdk_extranet_booking.exceptions import ApiAttributeError as ApiAttributeError
from wink_sdk_extranet_booking.exceptions import ApiException as ApiException

# import models into sdk package
from wink_sdk_extranet_booking.models.aggregate_descriptor_supplier import AggregateDescriptorSupplier as AggregateDescriptorSupplier
from wink_sdk_extranet_booking.models.authenticated_user_supplier import AuthenticatedUserSupplier as AuthenticatedUserSupplier
from wink_sdk_extranet_booking.models.authenticated_user_supplier_details import AuthenticatedUserSupplierDetails as AuthenticatedUserSupplierDetails
from wink_sdk_extranet_booking.models.bed_supplier import BedSupplier as BedSupplier
from wink_sdk_extranet_booking.models.bed_supplier_details import BedSupplierDetails as BedSupplierDetails
from wink_sdk_extranet_booking.models.bedroom_configuration_supplier import BedroomConfigurationSupplier as BedroomConfigurationSupplier
from wink_sdk_extranet_booking.models.bedroom_configuration_supplier_details import BedroomConfigurationSupplierDetails as BedroomConfigurationSupplierDetails
from wink_sdk_extranet_booking.models.bedroom_supplier import BedroomSupplier as BedroomSupplier
from wink_sdk_extranet_booking.models.bedroom_supplier_details import BedroomSupplierDetails as BedroomSupplierDetails
from wink_sdk_extranet_booking.models.beneficiary_charge_supplier import BeneficiaryChargeSupplier as BeneficiaryChargeSupplier
from wink_sdk_extranet_booking.models.beneficiary_charge_supplier_details import BeneficiaryChargeSupplierDetails as BeneficiaryChargeSupplierDetails
from wink_sdk_extranet_booking.models.beneficiary_supplier import BeneficiarySupplier as BeneficiarySupplier
from wink_sdk_extranet_booking.models.beneficiary_supplier_details import BeneficiarySupplierDetails as BeneficiarySupplierDetails
from wink_sdk_extranet_booking.models.booking_analytics_supplier import BookingAnalyticsSupplier as BookingAnalyticsSupplier
from wink_sdk_extranet_booking.models.booking_ancillary_supplier import BookingAncillarySupplier as BookingAncillarySupplier
from wink_sdk_extranet_booking.models.booking_ancillary_supplier_details import BookingAncillarySupplierDetails as BookingAncillarySupplierDetails
from wink_sdk_extranet_booking.models.booking_cancellable_supplier import BookingCancellableSupplier as BookingCancellableSupplier
from wink_sdk_extranet_booking.models.booking_contract_item_supplier import BookingContractItemSupplier as BookingContractItemSupplier
from wink_sdk_extranet_booking.models.booking_contract_item_supplier_details import BookingContractItemSupplierDetails as BookingContractItemSupplierDetails
from wink_sdk_extranet_booking.models.booking_contract_payment_details_supplier import BookingContractPaymentDetailsSupplier as BookingContractPaymentDetailsSupplier
from wink_sdk_extranet_booking.models.booking_contract_payment_details_supplier_details import BookingContractPaymentDetailsSupplierDetails as BookingContractPaymentDetailsSupplierDetails
from wink_sdk_extranet_booking.models.booking_contract_supplier import BookingContractSupplier as BookingContractSupplier
from wink_sdk_extranet_booking.models.booking_contract_supplier_details import BookingContractSupplierDetails as BookingContractSupplierDetails
from wink_sdk_extranet_booking.models.booking_itinerary_room_configuration_child_supplier import BookingItineraryRoomConfigurationChildSupplier as BookingItineraryRoomConfigurationChildSupplier
from wink_sdk_extranet_booking.models.booking_itinerary_room_configuration_child_supplier_details import BookingItineraryRoomConfigurationChildSupplierDetails as BookingItineraryRoomConfigurationChildSupplierDetails
from wink_sdk_extranet_booking.models.booking_itinerary_room_configuration_supplier import BookingItineraryRoomConfigurationSupplier as BookingItineraryRoomConfigurationSupplier
from wink_sdk_extranet_booking.models.booking_itinerary_room_configuration_supplier_details import BookingItineraryRoomConfigurationSupplierDetails as BookingItineraryRoomConfigurationSupplierDetails
from wink_sdk_extranet_booking.models.booking_itinerary_supplier import BookingItinerarySupplier as BookingItinerarySupplier
from wink_sdk_extranet_booking.models.booking_itinerary_supplier_details import BookingItinerarySupplierDetails as BookingItinerarySupplierDetails
from wink_sdk_extranet_booking.models.booking_overview_request_supplier import BookingOverviewRequestSupplier as BookingOverviewRequestSupplier
from wink_sdk_extranet_booking.models.booking_supplier import BookingSupplier as BookingSupplier
from wink_sdk_extranet_booking.models.booking_supplier_details import BookingSupplierDetails as BookingSupplierDetails
from wink_sdk_extranet_booking.models.booking_test_notification_supplier_details import BookingTestNotificationSupplierDetails as BookingTestNotificationSupplierDetails
from wink_sdk_extranet_booking.models.booking_test_request_supplier_details import BookingTestRequestSupplierDetails as BookingTestRequestSupplierDetails
from wink_sdk_extranet_booking.models.booking_user_session_supplier import BookingUserSessionSupplier as BookingUserSessionSupplier
from wink_sdk_extranet_booking.models.booking_user_session_supplier_details import BookingUserSessionSupplierDetails as BookingUserSessionSupplierDetails
from wink_sdk_extranet_booking.models.booking_user_supplier import BookingUserSupplier as BookingUserSupplier
from wink_sdk_extranet_booking.models.booking_user_supplier_details import BookingUserSupplierDetails as BookingUserSupplierDetails
from wink_sdk_extranet_booking.models.boolean_response_supplier import BooleanResponseSupplier as BooleanResponseSupplier
from wink_sdk_extranet_booking.models.cal_dav_response_supplier import CalDavResponseSupplier as CalDavResponseSupplier
from wink_sdk_extranet_booking.models.cancellation_detail_supplier import CancellationDetailSupplier as CancellationDetailSupplier
from wink_sdk_extranet_booking.models.cancellation_policy_exception_supplier import CancellationPolicyExceptionSupplier as CancellationPolicyExceptionSupplier
from wink_sdk_extranet_booking.models.cancellation_policy_exception_supplier_details import CancellationPolicyExceptionSupplierDetails as CancellationPolicyExceptionSupplierDetails
from wink_sdk_extranet_booking.models.cancellation_policy_exceptions_supplier import CancellationPolicyExceptionsSupplier as CancellationPolicyExceptionsSupplier
from wink_sdk_extranet_booking.models.cancellation_policy_exceptions_supplier_details import CancellationPolicyExceptionsSupplierDetails as CancellationPolicyExceptionsSupplierDetails
from wink_sdk_extranet_booking.models.cancellation_policy_lightweight_supplier import CancellationPolicyLightweightSupplier as CancellationPolicyLightweightSupplier
from wink_sdk_extranet_booking.models.cancellation_policy_lightweight_supplier_details import CancellationPolicyLightweightSupplierDetails as CancellationPolicyLightweightSupplierDetails
from wink_sdk_extranet_booking.models.channel_name_supplier_details import ChannelNameSupplierDetails as ChannelNameSupplierDetails
from wink_sdk_extranet_booking.models.chart_category_axis_supplier import ChartCategoryAxisSupplier as ChartCategoryAxisSupplier
from wink_sdk_extranet_booking.models.chart_legend_supplier import ChartLegendSupplier as ChartLegendSupplier
from wink_sdk_extranet_booking.models.chart_series_supplier import ChartSeriesSupplier as ChartSeriesSupplier
from wink_sdk_extranet_booking.models.chart_title_supplier import ChartTitleSupplier as ChartTitleSupplier
from wink_sdk_extranet_booking.models.child_supplier import ChildSupplier as ChildSupplier
from wink_sdk_extranet_booking.models.child_supplier_details import ChildSupplierDetails as ChildSupplierDetails
from wink_sdk_extranet_booking.models.commissionable_entry_supplier import CommissionableEntrySupplier as CommissionableEntrySupplier
from wink_sdk_extranet_booking.models.commissionable_entry_supplier_details import CommissionableEntrySupplierDetails as CommissionableEntrySupplierDetails
from wink_sdk_extranet_booking.models.composite_filter_descriptor_supplier import CompositeFilterDescriptorSupplier as CompositeFilterDescriptorSupplier
from wink_sdk_extranet_booking.models.contact_supplier import ContactSupplier as ContactSupplier
from wink_sdk_extranet_booking.models.contact_supplier_details import ContactSupplierDetails as ContactSupplierDetails
from wink_sdk_extranet_booking.models.count_response_supplier import CountResponseSupplier as CountResponseSupplier
from wink_sdk_extranet_booking.models.country_lightweight_supplier import CountryLightweightSupplier as CountryLightweightSupplier
from wink_sdk_extranet_booking.models.country_lightweight_supplier_details import CountryLightweightSupplierDetails as CountryLightweightSupplierDetails
from wink_sdk_extranet_booking.models.custom_monetary_amount import CustomMonetaryAmount as CustomMonetaryAmount
from wink_sdk_extranet_booking.models.customization_lightweight_supplier import CustomizationLightweightSupplier as CustomizationLightweightSupplier
from wink_sdk_extranet_booking.models.customization_lightweight_supplier_details import CustomizationLightweightSupplierDetails as CustomizationLightweightSupplierDetails
from wink_sdk_extranet_booking.models.customization_theme_colors_supplier import CustomizationThemeColorsSupplier as CustomizationThemeColorsSupplier
from wink_sdk_extranet_booking.models.customization_theme_colors_supplier_details import CustomizationThemeColorsSupplierDetails as CustomizationThemeColorsSupplierDetails
from wink_sdk_extranet_booking.models.daily_rate_rate_supplier_details import DailyRateRateSupplierDetails as DailyRateRateSupplierDetails
from wink_sdk_extranet_booking.models.daily_rate_supplier_details import DailyRateSupplierDetails as DailyRateSupplierDetails
from wink_sdk_extranet_booking.models.extra_charge_supplier import ExtraChargeSupplier as ExtraChargeSupplier
from wink_sdk_extranet_booking.models.extra_charge_supplier_details import ExtraChargeSupplierDetails as ExtraChargeSupplierDetails
from wink_sdk_extranet_booking.models.extra_charges_supplier import ExtraChargesSupplier as ExtraChargesSupplier
from wink_sdk_extranet_booking.models.extra_charges_supplier_details import ExtraChargesSupplierDetails as ExtraChargesSupplierDetails
from wink_sdk_extranet_booking.models.filter_descriptor_supplier import FilterDescriptorSupplier as FilterDescriptorSupplier
from wink_sdk_extranet_booking.models.general_manager_supplier import GeneralManagerSupplier as GeneralManagerSupplier
from wink_sdk_extranet_booking.models.general_manager_supplier_details import GeneralManagerSupplierDetails as GeneralManagerSupplierDetails
from wink_sdk_extranet_booking.models.generic_error_message import GenericErrorMessage as GenericErrorMessage
from wink_sdk_extranet_booking.models.geo_ip_lightweight_supplier_details import GeoIpLightweightSupplierDetails as GeoIpLightweightSupplierDetails
from wink_sdk_extranet_booking.models.geo_json_point_supplier import GeoJsonPointSupplier as GeoJsonPointSupplier
from wink_sdk_extranet_booking.models.geo_json_point_supplier_details import GeoJsonPointSupplierDetails as GeoJsonPointSupplierDetails
from wink_sdk_extranet_booking.models.geo_name_country_supplier_details import GeoNameCountrySupplierDetails as GeoNameCountrySupplierDetails
from wink_sdk_extranet_booking.models.geo_name_lightweight_supplier import GeoNameLightweightSupplier as GeoNameLightweightSupplier
from wink_sdk_extranet_booking.models.geo_name_lightweight_supplier_details import GeoNameLightweightSupplierDetails as GeoNameLightweightSupplierDetails
from wink_sdk_extranet_booking.models.group_descriptor_supplier import GroupDescriptorSupplier as GroupDescriptorSupplier
from wink_sdk_extranet_booking.models.grouped_booking_sales_metrics_supplier_details import GroupedBookingSalesMetricsSupplierDetails as GroupedBookingSalesMetricsSupplierDetails
from wink_sdk_extranet_booking.models.guest_room_lightweight_supplier import GuestRoomLightweightSupplier as GuestRoomLightweightSupplier
from wink_sdk_extranet_booking.models.guest_room_lightweight_supplier_details import GuestRoomLightweightSupplierDetails as GuestRoomLightweightSupplierDetails
from wink_sdk_extranet_booking.models.guest_user_supplier import GuestUserSupplier as GuestUserSupplier
from wink_sdk_extranet_booking.models.guest_user_supplier_details import GuestUserSupplierDetails as GuestUserSupplierDetails
from wink_sdk_extranet_booking.models.key_value_pair_supplier import KeyValuePairSupplier as KeyValuePairSupplier
from wink_sdk_extranet_booking.models.line_chart_supplier import LineChartSupplier as LineChartSupplier
from wink_sdk_extranet_booking.models.localized_description_supplier import LocalizedDescriptionSupplier as LocalizedDescriptionSupplier
from wink_sdk_extranet_booking.models.localized_description_supplier_details import LocalizedDescriptionSupplierDetails as LocalizedDescriptionSupplierDetails
from wink_sdk_extranet_booking.models.localized_price_supplier import LocalizedPriceSupplier as LocalizedPriceSupplier
from wink_sdk_extranet_booking.models.localized_price_supplier_details import LocalizedPriceSupplierDetails as LocalizedPriceSupplierDetails
from wink_sdk_extranet_booking.models.localized_transactional_travel_inventory_supplier_details import LocalizedTransactionalTravelInventorySupplierDetails as LocalizedTransactionalTravelInventorySupplierDetails
from wink_sdk_extranet_booking.models.media_author_attribution_supplier import MediaAuthorAttributionSupplier as MediaAuthorAttributionSupplier
from wink_sdk_extranet_booking.models.media_author_attribution_supplier_details import MediaAuthorAttributionSupplierDetails as MediaAuthorAttributionSupplierDetails
from wink_sdk_extranet_booking.models.page_booking_supplier import PageBookingSupplier as PageBookingSupplier
from wink_sdk_extranet_booking.models.page_review_supplier import PageReviewSupplier as PageReviewSupplier
from wink_sdk_extranet_booking.models.pageable_object_supplier import PageableObjectSupplier as PageableObjectSupplier
from wink_sdk_extranet_booking.models.payout_fee_supplier import PayoutFeeSupplier as PayoutFeeSupplier
from wink_sdk_extranet_booking.models.payout_fee_supplier_details import PayoutFeeSupplierDetails as PayoutFeeSupplierDetails
from wink_sdk_extranet_booking.models.payout_supplier import PayoutSupplier as PayoutSupplier
from wink_sdk_extranet_booking.models.payout_supplier_details import PayoutSupplierDetails as PayoutSupplierDetails
from wink_sdk_extranet_booking.models.perk_lightweight_supplier import PerkLightweightSupplier as PerkLightweightSupplier
from wink_sdk_extranet_booking.models.perk_lightweight_supplier_details import PerkLightweightSupplierDetails as PerkLightweightSupplierDetails
from wink_sdk_extranet_booking.models.personal_supplier import PersonalSupplier as PersonalSupplier
from wink_sdk_extranet_booking.models.personal_supplier_details import PersonalSupplierDetails as PersonalSupplierDetails
from wink_sdk_extranet_booking.models.preferences_supplier import PreferencesSupplier as PreferencesSupplier
from wink_sdk_extranet_booking.models.preferences_supplier_details import PreferencesSupplierDetails as PreferencesSupplierDetails
from wink_sdk_extranet_booking.models.profile_lightweight_supplier import ProfileLightweightSupplier as ProfileLightweightSupplier
from wink_sdk_extranet_booking.models.profile_lightweight_supplier_details import ProfileLightweightSupplierDetails as ProfileLightweightSupplierDetails
from wink_sdk_extranet_booking.models.profile_user_supplier import ProfileUserSupplier as ProfileUserSupplier
from wink_sdk_extranet_booking.models.profile_user_supplier_details import ProfileUserSupplierDetails as ProfileUserSupplierDetails
from wink_sdk_extranet_booking.models.property_aggregate_lightweight_supplier import PropertyAggregateLightweightSupplier as PropertyAggregateLightweightSupplier
from wink_sdk_extranet_booking.models.property_aggregate_lightweight_supplier_details import PropertyAggregateLightweightSupplierDetails as PropertyAggregateLightweightSupplierDetails
from wink_sdk_extranet_booking.models.property_booking_refund_request_supplier import PropertyBookingRefundRequestSupplier as PropertyBookingRefundRequestSupplier
from wink_sdk_extranet_booking.models.property_policy_supplier import PropertyPolicySupplier as PropertyPolicySupplier
from wink_sdk_extranet_booking.models.property_policy_supplier_details import PropertyPolicySupplierDetails as PropertyPolicySupplierDetails
from wink_sdk_extranet_booking.models.quote_lightweight_supplier import QuoteLightweightSupplier as QuoteLightweightSupplier
from wink_sdk_extranet_booking.models.quote_lightweight_supplier_details import QuoteLightweightSupplierDetails as QuoteLightweightSupplierDetails
from wink_sdk_extranet_booking.models.rate_plan_level_fee_supplier import RatePlanLevelFeeSupplier as RatePlanLevelFeeSupplier
from wink_sdk_extranet_booking.models.rate_plan_level_fee_supplier_details import RatePlanLevelFeeSupplierDetails as RatePlanLevelFeeSupplierDetails
from wink_sdk_extranet_booking.models.refund_supplier import RefundSupplier as RefundSupplier
from wink_sdk_extranet_booking.models.refund_supplier_details import RefundSupplierDetails as RefundSupplierDetails
from wink_sdk_extranet_booking.models.review_answer_supplier import ReviewAnswerSupplier as ReviewAnswerSupplier
from wink_sdk_extranet_booking.models.review_answer_supplier_details import ReviewAnswerSupplierDetails as ReviewAnswerSupplierDetails
from wink_sdk_extranet_booking.models.review_lightweight_supplier import ReviewLightweightSupplier as ReviewLightweightSupplier
from wink_sdk_extranet_booking.models.review_lightweight_supplier_details import ReviewLightweightSupplierDetails as ReviewLightweightSupplierDetails
from wink_sdk_extranet_booking.models.review_response_supplier import ReviewResponseSupplier as ReviewResponseSupplier
from wink_sdk_extranet_booking.models.review_supplier import ReviewSupplier as ReviewSupplier
from wink_sdk_extranet_booking.models.review_user_supplier import ReviewUserSupplier as ReviewUserSupplier
from wink_sdk_extranet_booking.models.review_user_supplier_details import ReviewUserSupplierDetails as ReviewUserSupplierDetails
from wink_sdk_extranet_booking.models.room_configuration_price_rate_plan_supplier import RoomConfigurationPriceRatePlanSupplier as RoomConfigurationPriceRatePlanSupplier
from wink_sdk_extranet_booking.models.room_configuration_price_rate_plan_supplier_details import RoomConfigurationPriceRatePlanSupplierDetails as RoomConfigurationPriceRatePlanSupplierDetails
from wink_sdk_extranet_booking.models.room_configuration_price_supplier_details import RoomConfigurationPriceSupplierDetails as RoomConfigurationPriceSupplierDetails
from wink_sdk_extranet_booking.models.room_configuration_supplier import RoomConfigurationSupplier as RoomConfigurationSupplier
from wink_sdk_extranet_booking.models.room_configuration_supplier_details import RoomConfigurationSupplierDetails as RoomConfigurationSupplierDetails
from wink_sdk_extranet_booking.models.room_stay_supplier import RoomStaySupplier as RoomStaySupplier
from wink_sdk_extranet_booking.models.room_stay_supplier_details import RoomStaySupplierDetails as RoomStaySupplierDetails
from wink_sdk_extranet_booking.models.show_review400_response import ShowReview400Response as ShowReview400Response
from wink_sdk_extranet_booking.models.simple_address_supplier import SimpleAddressSupplier as SimpleAddressSupplier
from wink_sdk_extranet_booking.models.simple_address_supplier_details import SimpleAddressSupplierDetails as SimpleAddressSupplierDetails
from wink_sdk_extranet_booking.models.simple_date_time_itinerary_supplier import SimpleDateTimeItinerarySupplier as SimpleDateTimeItinerarySupplier
from wink_sdk_extranet_booking.models.simple_date_time_itinerary_supplier_details import SimpleDateTimeItinerarySupplierDetails as SimpleDateTimeItinerarySupplierDetails
from wink_sdk_extranet_booking.models.simple_description_supplier import SimpleDescriptionSupplier as SimpleDescriptionSupplier
from wink_sdk_extranet_booking.models.simple_description_supplier_details import SimpleDescriptionSupplierDetails as SimpleDescriptionSupplierDetails
from wink_sdk_extranet_booking.models.simple_multimedia_supplier import SimpleMultimediaSupplier as SimpleMultimediaSupplier
from wink_sdk_extranet_booking.models.simple_multimedia_supplier_details import SimpleMultimediaSupplierDetails as SimpleMultimediaSupplierDetails
from wink_sdk_extranet_booking.models.social_supplier import SocialSupplier as SocialSupplier
from wink_sdk_extranet_booking.models.social_supplier_details import SocialSupplierDetails as SocialSupplierDetails
from wink_sdk_extranet_booking.models.sort_descriptor_supplier import SortDescriptorSupplier as SortDescriptorSupplier
from wink_sdk_extranet_booking.models.sort_object_supplier import SortObjectSupplier as SortObjectSupplier
from wink_sdk_extranet_booking.models.state_supplier import StateSupplier as StateSupplier
from wink_sdk_extranet_booking.models.stay_rate_supplier import StayRateSupplier as StayRateSupplier
from wink_sdk_extranet_booking.models.stay_rate_supplier_details import StayRateSupplierDetails as StayRateSupplierDetails
from wink_sdk_extranet_booking.models.sub_country_lightweight_supplier import SubCountryLightweightSupplier as SubCountryLightweightSupplier
from wink_sdk_extranet_booking.models.sub_country_lightweight_supplier_details import SubCountryLightweightSupplierDetails as SubCountryLightweightSupplierDetails
from wink_sdk_extranet_booking.models.sub_sub_country_lightweight_supplier import SubSubCountryLightweightSupplier as SubSubCountryLightweightSupplier
from wink_sdk_extranet_booking.models.sub_sub_country_lightweight_supplier_details import SubSubCountryLightweightSupplierDetails as SubSubCountryLightweightSupplierDetails
from wink_sdk_extranet_booking.models.supplier_contract_item_policy_supplier import SupplierContractItemPolicySupplier as SupplierContractItemPolicySupplier
from wink_sdk_extranet_booking.models.supplier_contract_item_policy_supplier_details import SupplierContractItemPolicySupplierDetails as SupplierContractItemPolicySupplierDetails
from wink_sdk_extranet_booking.models.transactional_travel_inventory_supplier import TransactionalTravelInventorySupplier as TransactionalTravelInventorySupplier
from wink_sdk_extranet_booking.models.transactional_travel_inventory_supplier_details import TransactionalTravelInventorySupplierDetails as TransactionalTravelInventorySupplierDetails
from wink_sdk_extranet_booking.models.travel_inventory_recognition_supplier import TravelInventoryRecognitionSupplier as TravelInventoryRecognitionSupplier
from wink_sdk_extranet_booking.models.travel_inventory_recognition_supplier_details import TravelInventoryRecognitionSupplierDetails as TravelInventoryRecognitionSupplierDetails
from wink_sdk_extranet_booking.models.variable_charge_supplier import VariableChargeSupplier as VariableChargeSupplier
from wink_sdk_extranet_booking.models.variable_charge_supplier_details import VariableChargeSupplierDetails as VariableChargeSupplierDetails
from wink_sdk_extranet_booking.models.verify_rates_request_supplier_details import VerifyRatesRequestSupplierDetails as VerifyRatesRequestSupplierDetails

