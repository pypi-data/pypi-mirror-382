# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md   # Extranet Booking API The Booking API exposes endpoints to manage bookings. This API lets you:  1. Booking: Manage bookings including cancellations. 2. Review: Manage user reviews. 3. Sync w. Calendar: Manage calendar sync with your favorite calendar software  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.20.0
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from wink_sdk_extranet_booking.models.booking_test_request_supplier_details import BookingTestRequestSupplierDetails

class TestBookingTestRequestSupplierDetails(unittest.TestCase):
    """BookingTestRequestSupplierDetails unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> BookingTestRequestSupplierDetails:
        """Test BookingTestRequestSupplierDetails
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `BookingTestRequestSupplierDetails`
        """
        model = BookingTestRequestSupplierDetails()
        if include_optional:
            return BookingTestRequestSupplierDetails(
                query = wink_sdk_extranet_booking.models.verify_rates_request_supplier_details.VerifyRatesRequest_SupplierDetails(
                    channel = wink_sdk_extranet_booking.models.channel_name_supplier_details.ChannelName_SupplierDetails(
                        property_identifier = '0', 
                        sub_type = 'DIRECT', 
                        owner_identifier = '', 
                        name = '0', ), 
                    stay_start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    stay_end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    room_configurations = [
                        null
                        ], 
                    currency = '0', 
                    booking_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    sell_start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    sell_end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    promotion = '', 
                    city = wink_sdk_extranet_booking.models.geo_ip_lightweight_supplier_details.GeoIpLightweight_SupplierDetails(
                        geo_name_id = '8798734', 
                        locale_code = 'en', 
                        continent_code = 'NA', 
                        continent_name = 'North America', 
                        country_iso_code = 'US', 
                        country_name = 'United States', 
                        city_name = 'New York', 
                        timezone = 'America/New_York', 
                        sub_division1_code = 'NY', 
                        sub_division1_name = 'NY', 
                        sub_division2_code = '', 
                        sub_division2_name = '', ), 
                    country = wink_sdk_extranet_booking.models.geo_name_country_supplier_details.GeoNameCountry_SupplierDetails(
                        geo_name_id = '', 
                        continent_code = '', 
                        continent_name = '', 
                        country_iso_code = '', 
                        country_name = '', ), 
                    continent = '', 
                    ip_number = '', 
                    timezone = '', 
                    latitude = 1.337, 
                    longitude = 1.337, ),
                room = wink_sdk_extranet_booking.models.room_configuration_price_supplier_details.RoomConfigurationPrice_SupplierDetails(
                    channel_inventory_identifier = '', 
                    list = [
                        wink_sdk_extranet_booking.models.localized_transactional_travel_inventory_supplier_details.LocalizedTransactionalTravelInventory_SupplierDetails(
                            identifier = 'travel-blocking-1', 
                            name = '1', 
                            descriptions = [
                                wink_sdk_extranet_booking.models.simple_description_supplier_details.SimpleDescription_SupplierDetails(
                                    name = 'An example title', 
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', 
                                    creator = 'USER', 
                                    md5_content_hash = '', 
                                    hash_mismatch = True, )
                                ], 
                            pricing_type = 'PER_STAY', 
                            price = wink_sdk_extranet_booking.models.localized_price_supplier_details.LocalizedPrice_SupplierDetails(
                                source_to_user_currency_quote = wink_sdk_extranet_booking.models.quote_lightweight_supplier_details.QuoteLightweight_SupplierDetails(
                                    source = '0', 
                                    target = '0', 
                                    exchange_rate = 1.337, 
                                    timestamp = 56, ), 
                                source_to_internal_currency_quote = wink_sdk_extranet_booking.models.quote_lightweight_supplier_details.QuoteLightweight_SupplierDetails(
                                    source = '0', 
                                    target = '0', 
                                    exchange_rate = 1.337, 
                                    timestamp = 56, ), 
                                user_specified_currency_base_total = wink_sdk_extranet_booking.models.custom_monetary_amount.CustomMonetaryAmount(
                                    amount = 1.337, 
                                    currency = '0', ), 
                                source_base_total = wink_sdk_extranet_booking.models.custom_monetary_amount.CustomMonetaryAmount(
                                    amount = 1.337, 
                                    currency = '0', ), 
                                internal_base_total = , 
                                user_specified_currency_promotional_modifier = -40, 
                                source_promotional_modifier = -40, 
                                internal_promotional_modifier = -40, 
                                user_specified_currency_premium_modifier = 40, 
                                source_premium_modifier = 40, 
                                internal_premium_modifier = 40, 
                                user_specified_currency_channel_modifier = -10, 
                                source_channel_modifier = -10, 
                                internal_channel_modifier = -10, 
                                quantity = 56, 
                                promotional_discount_percent = 1.337, 
                                channel_discount_percent = 1.337, 
                                premium_percent = 1.337, 
                                total_discount_percent = 1.337, 
                                source_total = , 
                                user_specified_currency_total = , 
                                internal_total = , 
                                has_channel_discount = True, 
                                has_premium = True, 
                                has_promotion = True, ), 
                            multimedias = [
                                wink_sdk_extranet_booking.models.simple_multimedia_supplier_details.SimpleMultimedia_SupplierDetails(
                                    multimedia_identifier = 'image-1', 
                                    identifier = 'cloudinary-image-1', 
                                    type = 'IMAGE', 
                                    source = 'CLOUDINARY', 
                                    sort = 10, 
                                    angle = '-90', 
                                    width = 2560, 
                                    height = 1600, 
                                    published = True, 
                                    category = '1', 
                                    lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                                    attribution = [
                                        wink_sdk_extranet_booking.models.media_author_attribution_supplier_details.MediaAuthorAttribution_SupplierDetails(
                                            url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                            name = 'Samuel Adams', )
                                        ], 
                                    is_landscape = True, )
                                ], 
                            min_pax = 2, 
                            max_pax = 10, 
                            offer_details = [
                                wink_sdk_extranet_booking.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', 
                                    creator = 'USER', 
                                    md5_content_hash = '', 
                                    hash_mismatch = True, )
                                ], 
                            promotion = '', )
                        ], 
                    commissionable = True, 
                    commission = 0.1, 
                    direct = True, 
                    adults = 56, 
                    children = 56, 
                    start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    room_rate_identifier = '', 
                    room_rate_internal_name = '', 
                    rate_plan = wink_sdk_extranet_booking.models.room_configuration_price_rate_plan_supplier_details.RoomConfigurationPriceRatePlan_SupplierDetails(
                        identifier = '0', 
                        name = 'BAR 1', 
                        breakfast = False, 
                        brunch = False, 
                        lunch = False, 
                        dinner = False, 
                        all_inclusive = False, 
                        all_inclusive_plus_alcohol = False, 
                        early_check_in_charge = wink_sdk_extranet_booking.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                            type = 'FIXED', 
                            percent = 0.25, 
                            fixed_amount = , ), 
                        late_check_out_charge = wink_sdk_extranet_booking.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                            type = 'FIXED', 
                            percent = 0.25, ), 
                        cancellation_policy = wink_sdk_extranet_booking.models.cancellation_policy_lightweight_supplier_details.CancellationPolicyLightweight_SupplierDetails(
                            identifier = '', 
                            hotel_identifier = '', 
                            refundable = False, 
                            advance_cancellation_free_of_charge = 'UNTIL_EIGHTEEN_HUNDRED_HOURS_ON_DAY_OF_ARRIVAL', 
                            refundable_cancellation_charge = 'FIFTY_PERCENT', 
                            no_show_charge = 'SAME_AS_CANCELLATION_FEE', 
                            non_refundable_cancellation_charge = 'SEVENTY_PERCENT', 
                            non_refundable_deadline = 'SEVEN_DAYS_BEFORE_ARRIVAL', 
                            non_refundable_after_deadline_cancellation_charge = 'ONE_HUNDRED_PERCENT', 
                            policy_code = '', ), 
                        cancellation_policy_exceptions = wink_sdk_extranet_booking.models.cancellation_policy_exceptions_supplier_details.CancellationPolicyExceptions_SupplierDetails(
                            list = [
                                wink_sdk_extranet_booking.models.cancellation_policy_exception_supplier_details.CancellationPolicyException_SupplierDetails(
                                    cancellation_policy_identifier = '0', 
                                    cancellation_policy = wink_sdk_extranet_booking.models.cancellation_policy_lightweight_supplier_details.CancellationPolicyLightweight_SupplierDetails(
                                        identifier = '', 
                                        hotel_identifier = '', 
                                        refundable = False, 
                                        advance_cancellation_free_of_charge = 'UNTIL_EIGHTEEN_HUNDRED_HOURS_ON_DAY_OF_ARRIVAL', 
                                        refundable_cancellation_charge = 'FIFTY_PERCENT', 
                                        no_show_charge = 'SAME_AS_CANCELLATION_FEE', 
                                        non_refundable_cancellation_charge = 'SEVENTY_PERCENT', 
                                        non_refundable_deadline = 'SEVEN_DAYS_BEFORE_ARRIVAL', 
                                        non_refundable_after_deadline_cancellation_charge = 'ONE_HUNDRED_PERCENT', 
                                        policy_code = '', ), 
                                    start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                                    end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), )
                                ], ), ), 
                    perk_types = [
                        null
                        ], 
                    price = wink_sdk_extranet_booking.models.stay_rate_supplier_details.StayRate_SupplierDetails(
                        source_extra_pax_modifier = 15, 
                        internal_extra_pax_modifier = 15, 
                        user_specified_currency_extra_pax_modifier = 15, 
                        source_extra_child_modifier = 15, 
                        internal_extra_child_modifier = 15, 
                        user_specified_currency_extra_child_modifier = 15, 
                        source_single_occupant_modifier = -15, 
                        internal_single_occupant_modifier = -15, 
                        user_specified_currency_single_occupant_modifier = -15, 
                        source_promotional_modifier = -40, 
                        internal_promotional_modifier = -40, 
                        user_specified_currency_promotional_modifier = -40, 
                        source_premium_modifier = 40, 
                        internal_premium_modifier = 40, 
                        user_specified_currency_premium_modifier = 40, 
                        source_channel_modifier = -10, 
                        internal_channel_modifier = -10, 
                        user_specified_currency_channel_modifier = -10, 
                        quantity = 56, 
                        min_occupancy = 56, 
                        max_occupancy = 56, 
                        rate_source = '', 
                        promotional_discount_percent = 1.337, 
                        channel_discount_percent = 1.337, 
                        premium_percent = 1.337, 
                        available = True, 
                        promotional_codes = [
                            ''
                            ], 
                        user_specified_currency_total = , 
                        internal_total = , 
                        user_specified_currency_average_price_per_night = , 
                        internal_average_price_per_night = , 
                        source_average_price_per_night = , 
                        total_discount_percent = 1.337, ), 
                    extra_charges = wink_sdk_extranet_booking.models.extra_charges_supplier_details.ExtraCharges_SupplierDetails(
                        items = [
                            wink_sdk_extranet_booking.models.extra_charge_supplier_details.ExtraCharge_SupplierDetails(
                                rate_plan_level_fee = wink_sdk_extranet_booking.models.rate_plan_level_fee_supplier_details.RatePlanLevelFee_SupplierDetails(
                                    descriptions = [
                                        wink_sdk_extranet_booking.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                                            description = 'This is a longer description in the specified language.', 
                                            language = 'en', 
                                            creator = 'USER', 
                                            md5_content_hash = '', 
                                            hash_mismatch = True, )
                                        ], 
                                    fixed_amount = , 
                                    type = 'PER_DAY', ), 
                                unit_price = wink_sdk_extranet_booking.models.localized_price_supplier_details.LocalizedPrice_SupplierDetails(
                                    source_to_user_currency_quote = , 
                                    source_to_internal_currency_quote = , 
                                    user_specified_currency_base_total = , 
                                    source_base_total = , 
                                    internal_base_total = , 
                                    user_specified_currency_promotional_modifier = -40, 
                                    source_promotional_modifier = -40, 
                                    internal_promotional_modifier = -40, 
                                    user_specified_currency_premium_modifier = 40, 
                                    source_premium_modifier = 40, 
                                    internal_premium_modifier = 40, 
                                    user_specified_currency_channel_modifier = -10, 
                                    source_channel_modifier = -10, 
                                    internal_channel_modifier = -10, 
                                    quantity = 56, 
                                    promotional_discount_percent = 1.337, 
                                    channel_discount_percent = 1.337, 
                                    premium_percent = 1.337, 
                                    total_discount_percent = 1.337, 
                                    has_channel_discount = True, 
                                    has_premium = True, 
                                    has_promotion = True, ), )
                            ], ), 
                    configuration = wink_sdk_extranet_booking.models.room_configuration_supplier_details.RoomConfiguration_SupplierDetails(
                        adults = 2, 
                        children = [
                            wink_sdk_extranet_booking.models.child_supplier_details.Child_SupplierDetails(
                                quantity = 1, 
                                age = 0, )
                            ], ), 
                    add_on_offers = [
                        null
                        ], 
                    perk_value = 56, 
                    active_cancellation_policy = , 
                    room_nights = 56, 
                    price_list = [
                        null
                        ], 
                    available = True, 
                    source_total = , 
                    user_specified_currency_total = , 
                    internal_total = , 
                    rate_source = '', ),
                announcement = wink_sdk_extranet_booking.models.booking_test_notification_supplier_details.BookingTestNotification_SupplierDetails(
                    notify_property = True, 
                    notify_channel_manager = True, 
                    notify_booker = True, 
                    booker = wink_sdk_extranet_booking.models.booking_user_supplier_details.BookingUser_SupplierDetails(
                        user_identifier = '', 
                        first_name = 'John', 
                        last_name = 'Smith', 
                        email = 'john.smith@email.com', 
                        telephone = '+1 212 555 1212', 
                        full_name = 'John Smith', ), ),
                notification = wink_sdk_extranet_booking.models.booking_test_notification_supplier_details.BookingTestNotification_SupplierDetails(
                    notify_property = True, 
                    notify_channel_manager = True, 
                    notify_booker = True, 
                    booker = wink_sdk_extranet_booking.models.booking_user_supplier_details.BookingUser_SupplierDetails(
                        user_identifier = '', 
                        first_name = 'John', 
                        last_name = 'Smith', 
                        email = 'john.smith@email.com', 
                        telephone = '+1 212 555 1212', 
                        full_name = 'John Smith', ), )
            )
        else:
            return BookingTestRequestSupplierDetails(
                query = wink_sdk_extranet_booking.models.verify_rates_request_supplier_details.VerifyRatesRequest_SupplierDetails(
                    channel = wink_sdk_extranet_booking.models.channel_name_supplier_details.ChannelName_SupplierDetails(
                        property_identifier = '0', 
                        sub_type = 'DIRECT', 
                        owner_identifier = '', 
                        name = '0', ), 
                    stay_start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    stay_end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    room_configurations = [
                        null
                        ], 
                    currency = '0', 
                    booking_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    sell_start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    sell_end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    promotion = '', 
                    city = wink_sdk_extranet_booking.models.geo_ip_lightweight_supplier_details.GeoIpLightweight_SupplierDetails(
                        geo_name_id = '8798734', 
                        locale_code = 'en', 
                        continent_code = 'NA', 
                        continent_name = 'North America', 
                        country_iso_code = 'US', 
                        country_name = 'United States', 
                        city_name = 'New York', 
                        timezone = 'America/New_York', 
                        sub_division1_code = 'NY', 
                        sub_division1_name = 'NY', 
                        sub_division2_code = '', 
                        sub_division2_name = '', ), 
                    country = wink_sdk_extranet_booking.models.geo_name_country_supplier_details.GeoNameCountry_SupplierDetails(
                        geo_name_id = '', 
                        continent_code = '', 
                        continent_name = '', 
                        country_iso_code = '', 
                        country_name = '', ), 
                    continent = '', 
                    ip_number = '', 
                    timezone = '', 
                    latitude = 1.337, 
                    longitude = 1.337, ),
                room = wink_sdk_extranet_booking.models.room_configuration_price_supplier_details.RoomConfigurationPrice_SupplierDetails(
                    channel_inventory_identifier = '', 
                    list = [
                        wink_sdk_extranet_booking.models.localized_transactional_travel_inventory_supplier_details.LocalizedTransactionalTravelInventory_SupplierDetails(
                            identifier = 'travel-blocking-1', 
                            name = '1', 
                            descriptions = [
                                wink_sdk_extranet_booking.models.simple_description_supplier_details.SimpleDescription_SupplierDetails(
                                    name = 'An example title', 
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', 
                                    creator = 'USER', 
                                    md5_content_hash = '', 
                                    hash_mismatch = True, )
                                ], 
                            pricing_type = 'PER_STAY', 
                            price = wink_sdk_extranet_booking.models.localized_price_supplier_details.LocalizedPrice_SupplierDetails(
                                source_to_user_currency_quote = wink_sdk_extranet_booking.models.quote_lightweight_supplier_details.QuoteLightweight_SupplierDetails(
                                    source = '0', 
                                    target = '0', 
                                    exchange_rate = 1.337, 
                                    timestamp = 56, ), 
                                source_to_internal_currency_quote = wink_sdk_extranet_booking.models.quote_lightweight_supplier_details.QuoteLightweight_SupplierDetails(
                                    source = '0', 
                                    target = '0', 
                                    exchange_rate = 1.337, 
                                    timestamp = 56, ), 
                                user_specified_currency_base_total = wink_sdk_extranet_booking.models.custom_monetary_amount.CustomMonetaryAmount(
                                    amount = 1.337, 
                                    currency = '0', ), 
                                source_base_total = wink_sdk_extranet_booking.models.custom_monetary_amount.CustomMonetaryAmount(
                                    amount = 1.337, 
                                    currency = '0', ), 
                                internal_base_total = , 
                                user_specified_currency_promotional_modifier = -40, 
                                source_promotional_modifier = -40, 
                                internal_promotional_modifier = -40, 
                                user_specified_currency_premium_modifier = 40, 
                                source_premium_modifier = 40, 
                                internal_premium_modifier = 40, 
                                user_specified_currency_channel_modifier = -10, 
                                source_channel_modifier = -10, 
                                internal_channel_modifier = -10, 
                                quantity = 56, 
                                promotional_discount_percent = 1.337, 
                                channel_discount_percent = 1.337, 
                                premium_percent = 1.337, 
                                total_discount_percent = 1.337, 
                                source_total = , 
                                user_specified_currency_total = , 
                                internal_total = , 
                                has_channel_discount = True, 
                                has_premium = True, 
                                has_promotion = True, ), 
                            multimedias = [
                                wink_sdk_extranet_booking.models.simple_multimedia_supplier_details.SimpleMultimedia_SupplierDetails(
                                    multimedia_identifier = 'image-1', 
                                    identifier = 'cloudinary-image-1', 
                                    type = 'IMAGE', 
                                    source = 'CLOUDINARY', 
                                    sort = 10, 
                                    angle = '-90', 
                                    width = 2560, 
                                    height = 1600, 
                                    published = True, 
                                    category = '1', 
                                    lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                                    attribution = [
                                        wink_sdk_extranet_booking.models.media_author_attribution_supplier_details.MediaAuthorAttribution_SupplierDetails(
                                            url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                            name = 'Samuel Adams', )
                                        ], 
                                    is_landscape = True, )
                                ], 
                            min_pax = 2, 
                            max_pax = 10, 
                            offer_details = [
                                wink_sdk_extranet_booking.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', 
                                    creator = 'USER', 
                                    md5_content_hash = '', 
                                    hash_mismatch = True, )
                                ], 
                            promotion = '', )
                        ], 
                    commissionable = True, 
                    commission = 0.1, 
                    direct = True, 
                    adults = 56, 
                    children = 56, 
                    start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                    room_rate_identifier = '', 
                    room_rate_internal_name = '', 
                    rate_plan = wink_sdk_extranet_booking.models.room_configuration_price_rate_plan_supplier_details.RoomConfigurationPriceRatePlan_SupplierDetails(
                        identifier = '0', 
                        name = 'BAR 1', 
                        breakfast = False, 
                        brunch = False, 
                        lunch = False, 
                        dinner = False, 
                        all_inclusive = False, 
                        all_inclusive_plus_alcohol = False, 
                        early_check_in_charge = wink_sdk_extranet_booking.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                            type = 'FIXED', 
                            percent = 0.25, 
                            fixed_amount = , ), 
                        late_check_out_charge = wink_sdk_extranet_booking.models.variable_charge_supplier_details.VariableCharge_SupplierDetails(
                            type = 'FIXED', 
                            percent = 0.25, ), 
                        cancellation_policy = wink_sdk_extranet_booking.models.cancellation_policy_lightweight_supplier_details.CancellationPolicyLightweight_SupplierDetails(
                            identifier = '', 
                            hotel_identifier = '', 
                            refundable = False, 
                            advance_cancellation_free_of_charge = 'UNTIL_EIGHTEEN_HUNDRED_HOURS_ON_DAY_OF_ARRIVAL', 
                            refundable_cancellation_charge = 'FIFTY_PERCENT', 
                            no_show_charge = 'SAME_AS_CANCELLATION_FEE', 
                            non_refundable_cancellation_charge = 'SEVENTY_PERCENT', 
                            non_refundable_deadline = 'SEVEN_DAYS_BEFORE_ARRIVAL', 
                            non_refundable_after_deadline_cancellation_charge = 'ONE_HUNDRED_PERCENT', 
                            policy_code = '', ), 
                        cancellation_policy_exceptions = wink_sdk_extranet_booking.models.cancellation_policy_exceptions_supplier_details.CancellationPolicyExceptions_SupplierDetails(
                            list = [
                                wink_sdk_extranet_booking.models.cancellation_policy_exception_supplier_details.CancellationPolicyException_SupplierDetails(
                                    cancellation_policy_identifier = '0', 
                                    cancellation_policy = wink_sdk_extranet_booking.models.cancellation_policy_lightweight_supplier_details.CancellationPolicyLightweight_SupplierDetails(
                                        identifier = '', 
                                        hotel_identifier = '', 
                                        refundable = False, 
                                        advance_cancellation_free_of_charge = 'UNTIL_EIGHTEEN_HUNDRED_HOURS_ON_DAY_OF_ARRIVAL', 
                                        refundable_cancellation_charge = 'FIFTY_PERCENT', 
                                        no_show_charge = 'SAME_AS_CANCELLATION_FEE', 
                                        non_refundable_cancellation_charge = 'SEVENTY_PERCENT', 
                                        non_refundable_deadline = 'SEVEN_DAYS_BEFORE_ARRIVAL', 
                                        non_refundable_after_deadline_cancellation_charge = 'ONE_HUNDRED_PERCENT', 
                                        policy_code = '', ), 
                                    start_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), 
                                    end_date = datetime.datetime.strptime('1975-12-30', '%Y-%m-%d').date(), )
                                ], ), ), 
                    perk_types = [
                        null
                        ], 
                    price = wink_sdk_extranet_booking.models.stay_rate_supplier_details.StayRate_SupplierDetails(
                        source_extra_pax_modifier = 15, 
                        internal_extra_pax_modifier = 15, 
                        user_specified_currency_extra_pax_modifier = 15, 
                        source_extra_child_modifier = 15, 
                        internal_extra_child_modifier = 15, 
                        user_specified_currency_extra_child_modifier = 15, 
                        source_single_occupant_modifier = -15, 
                        internal_single_occupant_modifier = -15, 
                        user_specified_currency_single_occupant_modifier = -15, 
                        source_promotional_modifier = -40, 
                        internal_promotional_modifier = -40, 
                        user_specified_currency_promotional_modifier = -40, 
                        source_premium_modifier = 40, 
                        internal_premium_modifier = 40, 
                        user_specified_currency_premium_modifier = 40, 
                        source_channel_modifier = -10, 
                        internal_channel_modifier = -10, 
                        user_specified_currency_channel_modifier = -10, 
                        quantity = 56, 
                        min_occupancy = 56, 
                        max_occupancy = 56, 
                        rate_source = '', 
                        promotional_discount_percent = 1.337, 
                        channel_discount_percent = 1.337, 
                        premium_percent = 1.337, 
                        available = True, 
                        promotional_codes = [
                            ''
                            ], 
                        user_specified_currency_total = , 
                        internal_total = , 
                        user_specified_currency_average_price_per_night = , 
                        internal_average_price_per_night = , 
                        source_average_price_per_night = , 
                        total_discount_percent = 1.337, ), 
                    extra_charges = wink_sdk_extranet_booking.models.extra_charges_supplier_details.ExtraCharges_SupplierDetails(
                        items = [
                            wink_sdk_extranet_booking.models.extra_charge_supplier_details.ExtraCharge_SupplierDetails(
                                rate_plan_level_fee = wink_sdk_extranet_booking.models.rate_plan_level_fee_supplier_details.RatePlanLevelFee_SupplierDetails(
                                    descriptions = [
                                        wink_sdk_extranet_booking.models.localized_description_supplier_details.LocalizedDescription_SupplierDetails(
                                            description = 'This is a longer description in the specified language.', 
                                            language = 'en', 
                                            creator = 'USER', 
                                            md5_content_hash = '', 
                                            hash_mismatch = True, )
                                        ], 
                                    fixed_amount = , 
                                    type = 'PER_DAY', ), 
                                unit_price = wink_sdk_extranet_booking.models.localized_price_supplier_details.LocalizedPrice_SupplierDetails(
                                    source_to_user_currency_quote = , 
                                    source_to_internal_currency_quote = , 
                                    user_specified_currency_base_total = , 
                                    source_base_total = , 
                                    internal_base_total = , 
                                    user_specified_currency_promotional_modifier = -40, 
                                    source_promotional_modifier = -40, 
                                    internal_promotional_modifier = -40, 
                                    user_specified_currency_premium_modifier = 40, 
                                    source_premium_modifier = 40, 
                                    internal_premium_modifier = 40, 
                                    user_specified_currency_channel_modifier = -10, 
                                    source_channel_modifier = -10, 
                                    internal_channel_modifier = -10, 
                                    quantity = 56, 
                                    promotional_discount_percent = 1.337, 
                                    channel_discount_percent = 1.337, 
                                    premium_percent = 1.337, 
                                    total_discount_percent = 1.337, 
                                    has_channel_discount = True, 
                                    has_premium = True, 
                                    has_promotion = True, ), )
                            ], ), 
                    configuration = wink_sdk_extranet_booking.models.room_configuration_supplier_details.RoomConfiguration_SupplierDetails(
                        adults = 2, 
                        children = [
                            wink_sdk_extranet_booking.models.child_supplier_details.Child_SupplierDetails(
                                quantity = 1, 
                                age = 0, )
                            ], ), 
                    add_on_offers = [
                        null
                        ], 
                    perk_value = 56, 
                    active_cancellation_policy = , 
                    room_nights = 56, 
                    price_list = [
                        null
                        ], 
                    available = True, 
                    source_total = , 
                    user_specified_currency_total = , 
                    internal_total = , 
                    rate_source = '', ),
                notification = wink_sdk_extranet_booking.models.booking_test_notification_supplier_details.BookingTestNotification_SupplierDetails(
                    notify_property = True, 
                    notify_channel_manager = True, 
                    notify_booker = True, 
                    booker = wink_sdk_extranet_booking.models.booking_user_supplier_details.BookingUser_SupplierDetails(
                        user_identifier = '', 
                        first_name = 'John', 
                        last_name = 'Smith', 
                        email = 'john.smith@email.com', 
                        telephone = '+1 212 555 1212', 
                        full_name = 'John Smith', ), ),
        )
        """

    def testBookingTestRequestSupplierDetails(self):
        """Test BookingTestRequestSupplierDetails"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
