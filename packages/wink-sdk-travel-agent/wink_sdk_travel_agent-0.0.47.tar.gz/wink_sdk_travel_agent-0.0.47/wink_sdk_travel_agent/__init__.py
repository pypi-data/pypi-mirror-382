# coding: utf-8

# flake8: noqa

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Travel Agent API The Travel Agent API exposes endpoints to manage agent-facilitated bookings. This API lets you:  1. Travel Agent: Manage agent entity. 2. Booking: Create / Manage bookings  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.23.0
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


__version__ = "0.0.47"

# Define package exports
__all__ = [
    "AnalyticsApi",
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
    "AgentBookingRequestAgent",
    "AggregateDescriptorAgent",
    "AuthenticatedUserAgent",
    "BedAgent",
    "BedroomAgent",
    "BedroomConfigurationAgent",
    "BeneficiaryAgent",
    "BeneficiaryChargeAgent",
    "BookingAgent",
    "BookingAnalyticsSupplier",
    "BookingAncillaryAgent",
    "BookingConfirmationsAgent",
    "BookingContractAgent",
    "BookingContractItemAgent",
    "BookingContractPaymentDetailsAgent",
    "BookingItineraryAgent",
    "BookingItineraryRoomConfigurationAgent",
    "BookingItineraryRoomConfigurationChildAgent",
    "BookingOverviewRequestSupplier",
    "BookingUserAgent",
    "BookingUserRequestAgent",
    "BookingUserSessionAgent",
    "BooleanResponseAgent",
    "CancellationDetailAgent",
    "CancellationPolicyExceptionAgent",
    "CancellationPolicyExceptionsAgent",
    "CancellationPolicyLightweightAgent",
    "ChartCategoryAxisSupplier",
    "ChartLegendSupplier",
    "ChartSeriesSupplier",
    "ChartTitleSupplier",
    "ChildAgent",
    "CommissionableEntryAgent",
    "CompositeFilterDescriptorAgent",
    "ContactAgent",
    "CountryLightweightAgent",
    "CreateAgentBooking400Response",
    "CreateAgentBookingRequestAgent",
    "CustomMonetaryAmount",
    "CustomizationLightweightAgent",
    "CustomizationThemeColorsAgent",
    "ExtraChargeAgent",
    "ExtraChargesAgent",
    "FilterDescriptorAgent",
    "GeneralManagerAgent",
    "GenericErrorMessage",
    "GeoJsonPointAgent",
    "GeoNameLightweightAgent",
    "GroupDescriptorAgent",
    "GroupedBookingSalesMetricsSupplierDetails",
    "GuestRoomLightweightAgent",
    "GuestUserAgent",
    "LineChartSupplier",
    "LocalizedDescriptionAgent",
    "LocalizedPriceAgent",
    "MediaAuthorAttributionAgent",
    "PageBookingAgent",
    "PageableObjectAgent",
    "PayoutAgent",
    "PayoutFeeAgent",
    "PerkLightweightAgent",
    "PersonalAgent",
    "PreferencesAgent",
    "ProfileLightweightAgent",
    "ProfileUserAgent",
    "PropertyAggregateLightweightAgent",
    "PropertyPolicyAgent",
    "QuoteLightweightAgent",
    "RatePlanLevelFeeAgent",
    "RefundAgent",
    "ReviewAnswerAgent",
    "ReviewLightweightAgent",
    "ReviewUserAgent",
    "RoomConfigurationAgent",
    "RoomConfigurationPriceRatePlanAgent",
    "RoomStayAgent",
    "SimpleAddressAgent",
    "SimpleDateTimeItineraryAgent",
    "SimpleDescriptionAgent",
    "SimpleMultimediaAgent",
    "SocialAgent",
    "SortDescriptorAgent",
    "SortObjectAgent",
    "StateAgent",
    "StayRateAgent",
    "SubCountryLightweightAgent",
    "SubSubCountryLightweightAgent",
    "SupplierContractItemPolicyAgent",
    "TravelInventoryRecognitionAgent",
]

# import apis into sdk package
from wink_sdk_travel_agent.api.analytics_api import AnalyticsApi as AnalyticsApi
from wink_sdk_travel_agent.api.travel_agent_api import TravelAgentApi as TravelAgentApi

# import ApiClient
from wink_sdk_travel_agent.api_response import ApiResponse as ApiResponse
from wink_sdk_travel_agent.api_client import ApiClient as ApiClient
from wink_sdk_travel_agent.configuration import Configuration as Configuration
from wink_sdk_travel_agent.exceptions import OpenApiException as OpenApiException
from wink_sdk_travel_agent.exceptions import ApiTypeError as ApiTypeError
from wink_sdk_travel_agent.exceptions import ApiValueError as ApiValueError
from wink_sdk_travel_agent.exceptions import ApiKeyError as ApiKeyError
from wink_sdk_travel_agent.exceptions import ApiAttributeError as ApiAttributeError
from wink_sdk_travel_agent.exceptions import ApiException as ApiException

# import models into sdk package
from wink_sdk_travel_agent.models.agent_booking_request_agent import AgentBookingRequestAgent as AgentBookingRequestAgent
from wink_sdk_travel_agent.models.aggregate_descriptor_agent import AggregateDescriptorAgent as AggregateDescriptorAgent
from wink_sdk_travel_agent.models.authenticated_user_agent import AuthenticatedUserAgent as AuthenticatedUserAgent
from wink_sdk_travel_agent.models.bed_agent import BedAgent as BedAgent
from wink_sdk_travel_agent.models.bedroom_agent import BedroomAgent as BedroomAgent
from wink_sdk_travel_agent.models.bedroom_configuration_agent import BedroomConfigurationAgent as BedroomConfigurationAgent
from wink_sdk_travel_agent.models.beneficiary_agent import BeneficiaryAgent as BeneficiaryAgent
from wink_sdk_travel_agent.models.beneficiary_charge_agent import BeneficiaryChargeAgent as BeneficiaryChargeAgent
from wink_sdk_travel_agent.models.booking_agent import BookingAgent as BookingAgent
from wink_sdk_travel_agent.models.booking_analytics_supplier import BookingAnalyticsSupplier as BookingAnalyticsSupplier
from wink_sdk_travel_agent.models.booking_ancillary_agent import BookingAncillaryAgent as BookingAncillaryAgent
from wink_sdk_travel_agent.models.booking_confirmations_agent import BookingConfirmationsAgent as BookingConfirmationsAgent
from wink_sdk_travel_agent.models.booking_contract_agent import BookingContractAgent as BookingContractAgent
from wink_sdk_travel_agent.models.booking_contract_item_agent import BookingContractItemAgent as BookingContractItemAgent
from wink_sdk_travel_agent.models.booking_contract_payment_details_agent import BookingContractPaymentDetailsAgent as BookingContractPaymentDetailsAgent
from wink_sdk_travel_agent.models.booking_itinerary_agent import BookingItineraryAgent as BookingItineraryAgent
from wink_sdk_travel_agent.models.booking_itinerary_room_configuration_agent import BookingItineraryRoomConfigurationAgent as BookingItineraryRoomConfigurationAgent
from wink_sdk_travel_agent.models.booking_itinerary_room_configuration_child_agent import BookingItineraryRoomConfigurationChildAgent as BookingItineraryRoomConfigurationChildAgent
from wink_sdk_travel_agent.models.booking_overview_request_supplier import BookingOverviewRequestSupplier as BookingOverviewRequestSupplier
from wink_sdk_travel_agent.models.booking_user_agent import BookingUserAgent as BookingUserAgent
from wink_sdk_travel_agent.models.booking_user_request_agent import BookingUserRequestAgent as BookingUserRequestAgent
from wink_sdk_travel_agent.models.booking_user_session_agent import BookingUserSessionAgent as BookingUserSessionAgent
from wink_sdk_travel_agent.models.boolean_response_agent import BooleanResponseAgent as BooleanResponseAgent
from wink_sdk_travel_agent.models.cancellation_detail_agent import CancellationDetailAgent as CancellationDetailAgent
from wink_sdk_travel_agent.models.cancellation_policy_exception_agent import CancellationPolicyExceptionAgent as CancellationPolicyExceptionAgent
from wink_sdk_travel_agent.models.cancellation_policy_exceptions_agent import CancellationPolicyExceptionsAgent as CancellationPolicyExceptionsAgent
from wink_sdk_travel_agent.models.cancellation_policy_lightweight_agent import CancellationPolicyLightweightAgent as CancellationPolicyLightweightAgent
from wink_sdk_travel_agent.models.chart_category_axis_supplier import ChartCategoryAxisSupplier as ChartCategoryAxisSupplier
from wink_sdk_travel_agent.models.chart_legend_supplier import ChartLegendSupplier as ChartLegendSupplier
from wink_sdk_travel_agent.models.chart_series_supplier import ChartSeriesSupplier as ChartSeriesSupplier
from wink_sdk_travel_agent.models.chart_title_supplier import ChartTitleSupplier as ChartTitleSupplier
from wink_sdk_travel_agent.models.child_agent import ChildAgent as ChildAgent
from wink_sdk_travel_agent.models.commissionable_entry_agent import CommissionableEntryAgent as CommissionableEntryAgent
from wink_sdk_travel_agent.models.composite_filter_descriptor_agent import CompositeFilterDescriptorAgent as CompositeFilterDescriptorAgent
from wink_sdk_travel_agent.models.contact_agent import ContactAgent as ContactAgent
from wink_sdk_travel_agent.models.country_lightweight_agent import CountryLightweightAgent as CountryLightweightAgent
from wink_sdk_travel_agent.models.create_agent_booking400_response import CreateAgentBooking400Response as CreateAgentBooking400Response
from wink_sdk_travel_agent.models.create_agent_booking_request_agent import CreateAgentBookingRequestAgent as CreateAgentBookingRequestAgent
from wink_sdk_travel_agent.models.custom_monetary_amount import CustomMonetaryAmount as CustomMonetaryAmount
from wink_sdk_travel_agent.models.customization_lightweight_agent import CustomizationLightweightAgent as CustomizationLightweightAgent
from wink_sdk_travel_agent.models.customization_theme_colors_agent import CustomizationThemeColorsAgent as CustomizationThemeColorsAgent
from wink_sdk_travel_agent.models.extra_charge_agent import ExtraChargeAgent as ExtraChargeAgent
from wink_sdk_travel_agent.models.extra_charges_agent import ExtraChargesAgent as ExtraChargesAgent
from wink_sdk_travel_agent.models.filter_descriptor_agent import FilterDescriptorAgent as FilterDescriptorAgent
from wink_sdk_travel_agent.models.general_manager_agent import GeneralManagerAgent as GeneralManagerAgent
from wink_sdk_travel_agent.models.generic_error_message import GenericErrorMessage as GenericErrorMessage
from wink_sdk_travel_agent.models.geo_json_point_agent import GeoJsonPointAgent as GeoJsonPointAgent
from wink_sdk_travel_agent.models.geo_name_lightweight_agent import GeoNameLightweightAgent as GeoNameLightweightAgent
from wink_sdk_travel_agent.models.group_descriptor_agent import GroupDescriptorAgent as GroupDescriptorAgent
from wink_sdk_travel_agent.models.grouped_booking_sales_metrics_supplier_details import GroupedBookingSalesMetricsSupplierDetails as GroupedBookingSalesMetricsSupplierDetails
from wink_sdk_travel_agent.models.guest_room_lightweight_agent import GuestRoomLightweightAgent as GuestRoomLightweightAgent
from wink_sdk_travel_agent.models.guest_user_agent import GuestUserAgent as GuestUserAgent
from wink_sdk_travel_agent.models.line_chart_supplier import LineChartSupplier as LineChartSupplier
from wink_sdk_travel_agent.models.localized_description_agent import LocalizedDescriptionAgent as LocalizedDescriptionAgent
from wink_sdk_travel_agent.models.localized_price_agent import LocalizedPriceAgent as LocalizedPriceAgent
from wink_sdk_travel_agent.models.media_author_attribution_agent import MediaAuthorAttributionAgent as MediaAuthorAttributionAgent
from wink_sdk_travel_agent.models.page_booking_agent import PageBookingAgent as PageBookingAgent
from wink_sdk_travel_agent.models.pageable_object_agent import PageableObjectAgent as PageableObjectAgent
from wink_sdk_travel_agent.models.payout_agent import PayoutAgent as PayoutAgent
from wink_sdk_travel_agent.models.payout_fee_agent import PayoutFeeAgent as PayoutFeeAgent
from wink_sdk_travel_agent.models.perk_lightweight_agent import PerkLightweightAgent as PerkLightweightAgent
from wink_sdk_travel_agent.models.personal_agent import PersonalAgent as PersonalAgent
from wink_sdk_travel_agent.models.preferences_agent import PreferencesAgent as PreferencesAgent
from wink_sdk_travel_agent.models.profile_lightweight_agent import ProfileLightweightAgent as ProfileLightweightAgent
from wink_sdk_travel_agent.models.profile_user_agent import ProfileUserAgent as ProfileUserAgent
from wink_sdk_travel_agent.models.property_aggregate_lightweight_agent import PropertyAggregateLightweightAgent as PropertyAggregateLightweightAgent
from wink_sdk_travel_agent.models.property_policy_agent import PropertyPolicyAgent as PropertyPolicyAgent
from wink_sdk_travel_agent.models.quote_lightweight_agent import QuoteLightweightAgent as QuoteLightweightAgent
from wink_sdk_travel_agent.models.rate_plan_level_fee_agent import RatePlanLevelFeeAgent as RatePlanLevelFeeAgent
from wink_sdk_travel_agent.models.refund_agent import RefundAgent as RefundAgent
from wink_sdk_travel_agent.models.review_answer_agent import ReviewAnswerAgent as ReviewAnswerAgent
from wink_sdk_travel_agent.models.review_lightweight_agent import ReviewLightweightAgent as ReviewLightweightAgent
from wink_sdk_travel_agent.models.review_user_agent import ReviewUserAgent as ReviewUserAgent
from wink_sdk_travel_agent.models.room_configuration_agent import RoomConfigurationAgent as RoomConfigurationAgent
from wink_sdk_travel_agent.models.room_configuration_price_rate_plan_agent import RoomConfigurationPriceRatePlanAgent as RoomConfigurationPriceRatePlanAgent
from wink_sdk_travel_agent.models.room_stay_agent import RoomStayAgent as RoomStayAgent
from wink_sdk_travel_agent.models.simple_address_agent import SimpleAddressAgent as SimpleAddressAgent
from wink_sdk_travel_agent.models.simple_date_time_itinerary_agent import SimpleDateTimeItineraryAgent as SimpleDateTimeItineraryAgent
from wink_sdk_travel_agent.models.simple_description_agent import SimpleDescriptionAgent as SimpleDescriptionAgent
from wink_sdk_travel_agent.models.simple_multimedia_agent import SimpleMultimediaAgent as SimpleMultimediaAgent
from wink_sdk_travel_agent.models.social_agent import SocialAgent as SocialAgent
from wink_sdk_travel_agent.models.sort_descriptor_agent import SortDescriptorAgent as SortDescriptorAgent
from wink_sdk_travel_agent.models.sort_object_agent import SortObjectAgent as SortObjectAgent
from wink_sdk_travel_agent.models.state_agent import StateAgent as StateAgent
from wink_sdk_travel_agent.models.stay_rate_agent import StayRateAgent as StayRateAgent
from wink_sdk_travel_agent.models.sub_country_lightweight_agent import SubCountryLightweightAgent as SubCountryLightweightAgent
from wink_sdk_travel_agent.models.sub_sub_country_lightweight_agent import SubSubCountryLightweightAgent as SubSubCountryLightweightAgent
from wink_sdk_travel_agent.models.supplier_contract_item_policy_agent import SupplierContractItemPolicyAgent as SupplierContractItemPolicyAgent
from wink_sdk_travel_agent.models.travel_inventory_recognition_agent import TravelInventoryRecognitionAgent as TravelInventoryRecognitionAgent

