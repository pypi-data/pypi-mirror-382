# coding: utf-8

"""
    Wink API

     # Introduction  Welcome to the Wink API - A programmer-friendly way to manage, sell and book travel inventory on the Wink platform. The API gives you all the tools you need to ready your properties and inventory for sale across 1000s of our native sales channels.  Integrators, affiliates, travel agents and content creators have the ability search for your travel inventory and promote / sell it in a wide variety of ways.   # Integrations  We have already integrated with the most well-known channel managers so you don't have to. To see our current integrations, please go to https://extranet.wink.travel and scroll to Connectivity section. Once your properties are set up, you can finish the setup by mapping your property to Wink using your channel manager partner portal. If your properties don't have a channel manager, you can easily manage rates and availability with this API.   # Intended Audience  Programmers are [most likely] a requirement to start integrating with Wink. Companies and organizations that would most benefit from integrating with us are new and existing travel companies that have relationships with suppliers and that need an advanced system from which to manage their travel inventory and get that same inventory out to as many eyeballs as possible at the lowest price possible.  - Hotel chains  - Hotel brands  - Travel tech companies  - Destination sites  - Integrators  - Aggregators  - Destination management companies  - Travel agencies  - OTAs   ## APIs  Not every integrator needs every API. For that reason, we have separated APIs into context.  ### Test API   - [Ping](/ping): The Ping API is a quick test endpoint to verify that your credentials work Wink.  ### Common APIs  - [Notifications](/notifications): The Notifications API is a way for us to stay in touch with your user, property or affiliate account. - [User Settings](/user-settings): The User Settings API exposes endpoints to allow 3rd party integrators to communicate with Wink.  ### Consume APIs Consume endpoints are for developers who want to find existing travel inventory and either book it or use it to advertise through one of their Wink affiliate accounts.   - [Configuration](/customization-client): A single endpoint to retrieve whitelabel + customization information for the booking customization.  - [Lookup](/lookup): All APIs related to locating inventory by region, locale and property flags.  - [Inventory](/inventory): All APIs related to retrieve known travel inventory as it was found using the Lookup API..  - [Booking](/booking): All APIs related to creating bookings on the platform.  - [Travel Agent](/travel-agent): The Travel Agent API exposes endpoints to manage agent-facilitated bookings.   ### Produce APIs  Produce endpoints are for developers who want to create and manage travel inventory.   #### Property  - [Property registration](/extranet/property/register): As a producer, this is, oftentimes, where you start your journey. These endpoints let you create properties on Wink.  - [Property](/extranet/property): This collection of property endpoints are mostly management endpoints that let you display, change status and similar for your existing properties.  - [Facilities](/extranet/facilities): This collection of endpoints let you manage facilities; such as room types.  - [Experiences](/extranet/experiences): This collection of endpoints let you manage experiences, such as activities.  - [Monetize](/extranet/monetize): The Monetize API exposes endpoints for managing cancellation polies, rate plans, promotions and more on Wink.  - [Distribution](/extranet/distribution): The Distribution API exposes endpoints for sales channels, connecting with affiliates, managing rates and inventory calendars and more on Wink.  - [Property Booking](/extranet/booking): The Property Booking API exposes endpoints for managing bookings and reviews at the property-level.   #### Affiliate  - [Affiliate](/affiliate): This collection of affiliate endpoints are mostly management endpoints that let you display, change status and similar for your existing accounts.  - [Browse](/affiliate/browse): The Browse API exposes endpoints for affiliates to find suppliers and inventory to sell.  - [Inventory](/affiliate/inventory): The Inventory API exposes endpoints for affiliates to manage the inventory they want to sell and how they want to sell it.  - [Sales Channel](/affiliate/sales-channel): The Sales Channel API exposes endpoints for affiliates to manage existing sales channels as well as find new ones.  - [WinkLinks](/affiliate/winklinks): The WinkLinks API exposes endpoints for affiliates to manage their WinkLinks page.   #### Rate provider  - [Channel manager](/channel-manager): The Channel Manager API enables external channel manager partners to map, exchange rate / availability information with us as well as be informed of bookings that occur on the Wink platform for one of their properties.   ### Taxonomy APIs  Taxonomy endpoints are for developers who want to consume and produce travel inventory and need taxonomies of standard and non-standard codes for inventory types, classes, statuses etc.   - [Reference](/reference): All APIs related to retrieving platform-supported taxonomies.   ### Insight APIs  Insight endpoints do exactly what the name implies - They offer platform-level insight into the activities of producers and consumers.   - [Analytics](/analytics): All APIs related to tracking metrics across a wide variety of data source segments including, more entertaining, leaderboard metrics.   ### Payment APIs  Payment endpoints are for developers who want to purchase travel inventory. This can be done via the API as a registered Travel Agent or using our API in conjunction with our PCI compliant payment widget for all other entities.   - [TripPay](/payment): All APIs related to TripPay account management, booking, mapping and integration features.   ## SDKs  We are actively working on supporting the most used languages out there. If you don't see your language here, reach out to us with a request to officially add your language. In the meantime, if you want to roll your own SDK, you can do so by downloading the OpenAPI spec and using one of the many available OpenAPI generators available: [https://openapi-generator.tech/docs/generators](https://openapi-generator.tech/docs/generators).   - Java SDK [https://github.com/wink-travel/wink-sdk-java](https://github.com/wink-travel/wink-sdk-java)   ## Usage  These features are made available to you via a [REST API](https://en.wikipedia.org/wiki/Representational_state_transfer). This API is language agnostic.   ## Versioning  We chose to version our endpoints in a way that we hope affects your integration minimally. You request the version of our API you wish to work with via the `Wink-Version` header. When it's time for you to upgrade, you only have to change the version number to get access to our updated endpoints.   ## Release history  - Follow updates on Github: https://github.com/wink-travel/wink-sdk-java/blob/master/CHANGELOG.md    # Inventory API The Inventory API exposes endpoints to retrieve inventory you already know. This API lets you:  1. Consume shareable links. 2. Consume property. 3. Load up all types of inventories that were created by you such as grids, lists, maps, and individual items.  Browse the endpoints in the left navigation bar to get started.  

    The version of the OpenAPI document: 30.20.0
    Contact: bjorn@wink.travel
    Generated by OpenAPI Generator (https://openapi-generator.tech)

    Do not edit the class manually.
"""  # noqa: E501


import unittest

from wink_sdk_inventory.models.property_inventory_response_non_authenticated_entity import PropertyInventoryResponseNonAuthenticatedEntity

class TestPropertyInventoryResponseNonAuthenticatedEntity(unittest.TestCase):
    """PropertyInventoryResponseNonAuthenticatedEntity unit test stubs"""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_instance(self, include_optional) -> PropertyInventoryResponseNonAuthenticatedEntity:
        """Test PropertyInventoryResponseNonAuthenticatedEntity
            include_optional is a boolean, when False only required
            params are included, when True both required and
            optional params are included """
        # uncomment below to create an instance of `PropertyInventoryResponseNonAuthenticatedEntity`
        """
        model = PropertyInventoryResponseNonAuthenticatedEntity()
        if include_optional:
            return PropertyInventoryResponseNonAuthenticatedEntity(
                hotel_identifier = 'hotel-1',
                url_name = 'the-most-fantastic-hotel',
                hotel = wink_sdk_inventory.models.property_aggregate_lightweight_non_authenticated_entity.PropertyAggregateLightweight_Non_Authenticated_Entity(
                    hotel_identifier = 'hotel-1', 
                    name = 'The Loveliest Hotel', 
                    local_name = 'Det Beste Hotellet', 
                    chain = 'Hotel chain', 
                    brand = 'Hotel brand', 
                    url_name = 'the-loveliest-hotel-new-york-united-states', 
                    unique_id = 'abc123', 
                    star_rating = 4, 
                    bookings = 6054, 
                    aggregate_review_rating = 7.8, 
                    location = {type=POINT, coordinates=[100.5581533, 13.7370197]}, 
                    descriptions = [
                        wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                            name = 'An example title', 
                            description = 'This is a longer description in the specified language.', 
                            language = 'en', )
                        ], 
                    aggregate_greendex_rating = 7.0, 
                    lifestyle_types = [
                        null
                        ], 
                    total_reviews = 989, 
                    reservations = wink_sdk_inventory.models.contact_non_authenticated_entity.Contact_Non_Authenticated_Entity(
                        first_name = 'John', 
                        last_name = 'Smith', 
                        email = 'johnsmith@email.com', 
                        secondary_email = 'johnsmith2@email.com', 
                        phone_number = '+12125551212', 
                        full_name = 'John Smith', 
                        summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                    socials = [
                        wink_sdk_inventory.models.social_non_authenticated_entity.Social_Non_Authenticated_Entity(
                            type = 'FACEBOOK', 
                            location = '', )
                        ], 
                    images = [
                        wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                                wink_sdk_inventory.models.media_author_attribution_non_authenticated_entity.MediaAuthorAttribution_Non_Authenticated_Entity(
                                    url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                    name = 'Samuel Adams', )
                                ], 
                            is_landscape = True, )
                        ], 
                    videos = [
                        wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                            is_landscape = True, )
                        ], 
                    policy = wink_sdk_inventory.models.property_policy_non_authenticated_entity.PropertyPolicy_Non_Authenticated_Entity(
                        children_allowed = True, 
                        children_minimum_age = 6, 
                        internet_availability = 'YES', 
                        internet_connection_type = 'WIFI', 
                        internet_connection_location = 'ENTIRE_PROPERTY', 
                        parking_availability = 'YES', 
                        parking_access = 'PRIVATE', 
                        pets_allowed = True, 
                        pet_max_weight_in_kilos = 10, 
                        pet_charge = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
                            amount = 1.337, 
                            currency = '0', ), 
                        check_out_time = '10:00', 
                        check_in_time = '14:00', ), 
                    third_party_reviews = [
                        wink_sdk_inventory.models.travel_inventory_recognition_non_authenticated_entity.TravelInventoryRecognition_Non_Authenticated_Entity(
                            identifier = 'recognition-1', 
                            category = 'AWARD', 
                            type = 'PERCENT_RATING', 
                            provider = 'Michelin', 
                            rating = 8.5, 
                            max_rating = 10, 
                            date = '2020-10-24', 
                            official_appointment_ind = True, 
                            rating_symbol = '*', )
                        ], 
                    attractions = 5, 
                    activities = 3, 
                    places = 9, 
                    restaurants = 2, 
                    meeting_rooms = 2, 
                    spas = 1, 
                    add_ons = 5, 
                    general_manager = wink_sdk_inventory.models.general_manager_non_authenticated_entity.GeneralManager_Non_Authenticated_Entity(
                        name = 'Jane Doe', 
                        image = cl-image-1, ), 
                    location_category = '34', 
                    segment_category = '7', 
                    hotel_category = '45', 
                    architectural_style = '7', 
                    when_built = '1927', 
                    currency_code = 'USD', 
                    membership_rate_discount = 9, 
                    price_score = 9, 
                    perk_score = 4, 
                    add_on_score = 4, 
                    loyalty_score = 5, 
                    popular_score = 45, 
                    experience_score = 5, 
                    hotel_amenity_codes = [1, 7], 
                    property_accessibility_codes = [1, 7], 
                    property_security_codes = [1, 7], 
                    number_of_rooms = 32, 
                    address = wink_sdk_inventory.models.simple_address_non_authenticated_entity.SimpleAddress_Non_Authenticated_Entity(
                        address1 = '234', 
                        address2 = 'Pebble #5001', 
                        state = 'CA', 
                        postal_code = '90210', 
                        county = 'Alameda county', 
                        city = '0', 
                        country_code = '0', 
                        country = 'United States', 
                        full_address = '11', ), 
                    active = True, 
                    url_parameters = '', ),
                green_index_scores = wink_sdk_inventory.models.property_aggregate_green_index_answers_non_authenticated_entity.PropertyAggregateGreenIndexAnswers_Non_Authenticated_Entity(
                    hotel_identifier = '', 
                    list = [
                        wink_sdk_inventory.models.property_aggregate_green_index_answer_non_authenticated_entity.PropertyAggregateGreenIndexAnswer_Non_Authenticated_Entity(
                            question_key = '', 
                            value = 56, )
                        ], 
                    high_score = 100, 
                    total_score = 50, 
                    aggregate_score = 50, 
                    scores_by_category = [
                        wink_sdk_inventory.models.property_aggregate_green_index_score_by_category_non_authenticated_entity.PropertyAggregateGreenIndexScoreByCategory_Non_Authenticated_Entity(
                            category = 'GENERAL', 
                            high_score = 100, 
                            total_score = 50, 
                            aggregate_score = 50, )
                        ], ),
                room_types = [
                    wink_sdk_inventory.models.room_type_with_price_configurations_non_authenticated_entity.RoomTypeWithPriceConfigurations_Non_Authenticated_Entity(
                        room = wink_sdk_inventory.models.guest_room_lightweight_non_authenticated_entity.GuestRoomLightweight_Non_Authenticated_Entity(
                            identifier = 'document-1', 
                            hotel_identifier = 'hotel-1', 
                            featured_ind = False, 
                            lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                            location = {type=POINT, coordinates=[100.5581533, 13.7370197]}, 
                            descriptions = [
                                wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                    name = 'An example title', 
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', )
                                ], 
                            multimedias = [
                                wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                                        wink_sdk_inventory.models.media_author_attribution_non_authenticated_entity.MediaAuthorAttribution_Non_Authenticated_Entity(
                                            url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                            name = 'Samuel Adams', )
                                        ], 
                                    is_landscape = True, )
                                ], 
                            contact = wink_sdk_inventory.models.contact_non_authenticated_entity.Contact_Non_Authenticated_Entity(
                                first_name = 'John', 
                                last_name = 'Smith', 
                                email = 'johnsmith@email.com', 
                                secondary_email = 'johnsmith2@email.com', 
                                phone_number = '+12125551212', 
                                full_name = 'John Smith', 
                                summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                            address = wink_sdk_inventory.models.simple_address_non_authenticated_entity.SimpleAddress_Non_Authenticated_Entity(
                                address1 = '234', 
                                address2 = 'Pebble #5001', 
                                state = 'CA', 
                                postal_code = '90210', 
                                county = 'Alameda county', 
                                city = '0', 
                                country_code = '0', 
                                country = 'United States', 
                                full_address = '11', ), 
                            commissionable = True, 
                            name = 'Archery lesson', 
                            proximity_code = '1', 
                            sort = 1, 
                            min_age_appropriate_code = '1', 
                            bookable = True, 
                            active = True, 
                            disability_features = [
                                ''
                                ], 
                            security_features = [
                                ''
                                ], 
                            socials = [
                                wink_sdk_inventory.models.social_non_authenticated_entity.Social_Non_Authenticated_Entity(
                                    type = 'FACEBOOK', 
                                    location = '', )
                                ], 
                            price_point = 'THREE', 
                            recognition_list = [
                                wink_sdk_inventory.models.travel_inventory_recognition_non_authenticated_entity.TravelInventoryRecognition_Non_Authenticated_Entity(
                                    identifier = 'recognition-1', 
                                    category = 'AWARD', 
                                    type = 'PERCENT_RATING', 
                                    provider = 'Michelin', 
                                    rating = 8.5, 
                                    max_rating = 10, 
                                    date = '2020-10-24', 
                                    official_appointment_ind = True, 
                                    rating_symbol = '*', )
                                ], 
                            max_occupancy = 2, 
                            min_occupancy = 1, 
                            quantity = 40, 
                            non_smoking = True, 
                            bedroom_configuration_list = [
                                wink_sdk_inventory.models.bedroom_configuration_non_authenticated_entity.BedroomConfiguration_Non_Authenticated_Entity(
                                    identifier = '0', 
                                    name = '0', 
                                    bedroom_list = [
                                        wink_sdk_inventory.models.bedroom_non_authenticated_entity.Bedroom_Non_Authenticated_Entity(
                                            type = 'MASTER', 
                                            bed_list = [
                                                wink_sdk_inventory.models.bed_non_authenticated_entity.Bed_Non_Authenticated_Entity(
                                                    bed_type_code = '1', 
                                                    quantity = 10, )
                                                ], )
                                        ], )
                                ], 
                            size = 55, 
                            max_adult_occupancy = 1, 
                            max_child_occupancy = 0, 
                            bathroom_count = 0, 
                            living_room_count = 0, 
                            max_rollaways = 0, 
                            room_category = '1', 
                            floor = '', 
                            room_location_code = '1', 
                            room_view_code = '1', 
                            composite = False, 
                            composite_count = 2, 
                            room_classification_code = '1', 
                            room_architecture_code = '1', 
                            room_gender = 'Unknown', 
                            shared_room_ind = False, 
                            max_cribs = 1, 
                            amenities = [
                                ''
                                ], 
                            included_adult_occupancy = 2, 
                            included_child_occupancy = 0, ), 
                        price_configurations = [
                            null
                            ], 
                        available = True, 
                        lowest_price = wink_sdk_inventory.models.room_configuration_price_non_authenticated_entity.RoomConfigurationPrice_Non_Authenticated_Entity(
                            channel_inventory_identifier = '', 
                            list = [
                                wink_sdk_inventory.models.localized_transactional_travel_inventory_non_authenticated_entity.LocalizedTransactionalTravelInventory_Non_Authenticated_Entity(
                                    identifier = 'travel-blocking-1', 
                                    name = '1', 
                                    descriptions = [
                                        wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                            name = 'An example title', 
                                            description = 'This is a longer description in the specified language.', 
                                            language = 'en', )
                                        ], 
                                    pricing_type = 'PER_STAY', 
                                    price = wink_sdk_inventory.models.localized_price_non_authenticated_entity.LocalizedPrice_Non_Authenticated_Entity(
                                        source_to_user_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                            source = '0', 
                                            target = '0', 
                                            exchange_rate = 1.337, 
                                            timestamp = 56, ), 
                                        source_to_internal_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                            source = '0', 
                                            target = '0', 
                                            exchange_rate = 1.337, 
                                            timestamp = 56, ), 
                                        user_specified_currency_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
                                            amount = 1.337, 
                                            currency = '0', ), 
                                        source_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
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
                                    min_pax = 2, 
                                    max_pax = 10, 
                                    offer_details = [
                                        wink_sdk_inventory.models.localized_description_non_authenticated_entity.LocalizedDescription_Non_Authenticated_Entity(
                                            description = 'This is a longer description in the specified language.', 
                                            language = 'en', )
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
                            rate_plan = wink_sdk_inventory.models.room_configuration_price_rate_plan_non_authenticated_entity.RoomConfigurationPriceRatePlan_Non_Authenticated_Entity(
                                identifier = '0', 
                                name = 'BAR 1', 
                                breakfast = False, 
                                brunch = False, 
                                lunch = False, 
                                dinner = False, 
                                all_inclusive = False, 
                                all_inclusive_plus_alcohol = False, 
                                early_check_in_charge = null, 
                                late_check_out_charge = null, 
                                cancellation_policy = wink_sdk_inventory.models.cancellation_policy_lightweight_non_authenticated_entity.CancellationPolicyLightweight_Non_Authenticated_Entity(
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
                                cancellation_policy_exceptions = wink_sdk_inventory.models.cancellation_policy_exceptions_non_authenticated_entity.CancellationPolicyExceptions_Non_Authenticated_Entity(
                                    list = [
                                        wink_sdk_inventory.models.cancellation_policy_exception_non_authenticated_entity.CancellationPolicyException_Non_Authenticated_Entity(
                                            cancellation_policy_identifier = '0', 
                                            cancellation_policy = wink_sdk_inventory.models.cancellation_policy_lightweight_non_authenticated_entity.CancellationPolicyLightweight_Non_Authenticated_Entity(
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
                            price = wink_sdk_inventory.models.stay_rate_non_authenticated_entity.StayRate_Non_Authenticated_Entity(
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
                            extra_charges = wink_sdk_inventory.models.extra_charges_non_authenticated_entity.ExtraCharges_Non_Authenticated_Entity(
                                items = [
                                    wink_sdk_inventory.models.extra_charge_non_authenticated_entity.ExtraCharge_Non_Authenticated_Entity(
                                        rate_plan_level_fee = wink_sdk_inventory.models.rate_plan_level_fee_non_authenticated_entity.RatePlanLevelFee_Non_Authenticated_Entity(
                                            descriptions = [
                                                wink_sdk_inventory.models.localized_description_non_authenticated_entity.LocalizedDescription_Non_Authenticated_Entity(
                                                    description = 'This is a longer description in the specified language.', 
                                                    language = 'en', )
                                                ], 
                                            fixed_amount = , 
                                            type = 'PER_DAY', ), 
                                        unit_price = wink_sdk_inventory.models.localized_price_non_authenticated_entity.LocalizedPrice_Non_Authenticated_Entity(
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
                            configuration = wink_sdk_inventory.models.room_configuration_non_authenticated_entity.RoomConfiguration_Non_Authenticated_Entity(
                                adults = 2, 
                                children = [
                                    wink_sdk_inventory.models.child_non_authenticated_entity.Child_Non_Authenticated_Entity(
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
                            rate_source = '', ), )
                    ],
                meeting_rooms = [
                    wink_sdk_inventory.models.meeting_room_localized_inventory_non_authenticated_entity.MeetingRoomLocalizedInventory_Non_Authenticated_Entity(
                        meeting_room = wink_sdk_inventory.models.meeting_room_lightweight_non_authenticated_entity.MeetingRoomLightweight_Non_Authenticated_Entity(
                            identifier = 'document-1', 
                            hotel_identifier = 'hotel-1', 
                            featured_ind = False, 
                            lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                            location = {type=POINT, coordinates=[100.5581533, 13.7370197]}, 
                            descriptions = [
                                wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                    name = 'An example title', 
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', )
                                ], 
                            multimedias = [
                                wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                                        wink_sdk_inventory.models.media_author_attribution_non_authenticated_entity.MediaAuthorAttribution_Non_Authenticated_Entity(
                                            url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                            name = 'Samuel Adams', )
                                        ], 
                                    is_landscape = True, )
                                ], 
                            contact = wink_sdk_inventory.models.contact_non_authenticated_entity.Contact_Non_Authenticated_Entity(
                                first_name = 'John', 
                                last_name = 'Smith', 
                                email = 'johnsmith@email.com', 
                                secondary_email = 'johnsmith2@email.com', 
                                phone_number = '+12125551212', 
                                full_name = 'John Smith', 
                                summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                            address = wink_sdk_inventory.models.simple_address_non_authenticated_entity.SimpleAddress_Non_Authenticated_Entity(
                                address1 = '234', 
                                address2 = 'Pebble #5001', 
                                state = 'CA', 
                                postal_code = '90210', 
                                county = 'Alameda county', 
                                city = '0', 
                                country_code = '0', 
                                country = 'United States', 
                                full_address = '11', ), 
                            commissionable = True, 
                            name = 'Archery lesson', 
                            proximity_code = '1', 
                            sort = 1, 
                            min_age_appropriate_code = '1', 
                            bookable = True, 
                            active = True, 
                            disability_features = [
                                ''
                                ], 
                            security_features = [
                                ''
                                ], 
                            socials = [
                                wink_sdk_inventory.models.social_non_authenticated_entity.Social_Non_Authenticated_Entity(
                                    type = 'FACEBOOK', 
                                    location = '', )
                                ], 
                            price_point = 'THREE', 
                            recognition_list = [
                                wink_sdk_inventory.models.travel_inventory_recognition_non_authenticated_entity.TravelInventoryRecognition_Non_Authenticated_Entity(
                                    identifier = 'recognition-1', 
                                    category = 'AWARD', 
                                    type = 'PERCENT_RATING', 
                                    provider = 'Michelin', 
                                    rating = 8.5, 
                                    max_rating = 10, 
                                    date = '2020-10-24', 
                                    official_appointment_ind = True, 
                                    rating_symbol = '*', )
                                ], 
                            applicable_start = '1970-1-1', 
                            applicable_end = '1970-12-1', 
                            reservation_required_ind = False, 
                            opens = '09:00', 
                            closes = '17:30', 
                            days_of_week = wink_sdk_inventory.models.dow_pattern_group_non_authenticated_entity.DowPatternGroup_Non_Authenticated_Entity(
                                mon = True, 
                                tue = True, 
                                wed = True, 
                                thu = True, 
                                fri = True, 
                                sat = True, 
                                sun = True, 
                                disabled = True, ), 
                            irregular = True, 
                            meeting_room_capacity = 100, 
                            access = 'MEETING_ROOM_ACCESS_PRIVATE', 
                            meeting_room_type_code = '[1]', 
                            meeting_room_level = 'LOBBY', 
                            dedicated_ind = False, 
                            area = 100, 
                            height = 4, 
                            width = 5, 
                            length = 5, 
                            amenities = [
                                ''
                                ], ), 
                        list = [
                            wink_sdk_inventory.models.localized_transactional_travel_inventory_non_authenticated_entity.LocalizedTransactionalTravelInventory_Non_Authenticated_Entity(
                                identifier = 'travel-blocking-1', 
                                name = '1', 
                                descriptions = [
                                    wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                        name = 'An example title', 
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                pricing_type = 'PER_STAY', 
                                price = wink_sdk_inventory.models.localized_price_non_authenticated_entity.LocalizedPrice_Non_Authenticated_Entity(
                                    source_to_user_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    source_to_internal_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    user_specified_currency_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
                                        amount = 1.337, 
                                        currency = '0', ), 
                                    source_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
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
                                min_pax = 2, 
                                max_pax = 10, 
                                offer_details = [
                                    wink_sdk_inventory.models.localized_description_non_authenticated_entity.LocalizedDescription_Non_Authenticated_Entity(
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                promotion = '', )
                            ], 
                        channel_inventory_identifier = '', 
                        commissionable = True, 
                        commission = 0.1, 
                        direct = True, 
                        price_list = [
                            null
                            ], )
                    ],
                restaurants = [
                    wink_sdk_inventory.models.restaurant_localized_inventory_non_authenticated_entity.RestaurantLocalizedInventory_Non_Authenticated_Entity(
                        restaurant = wink_sdk_inventory.models.restaurant_lightweight_non_authenticated_entity.RestaurantLightweight_Non_Authenticated_Entity(
                            identifier = 'document-1', 
                            hotel_identifier = 'hotel-1', 
                            featured_ind = False, 
                            lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                            location = {type=POINT, coordinates=[100.5581533, 13.7370197]}, 
                            descriptions = [
                                wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                    name = 'An example title', 
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', )
                                ], 
                            multimedias = [
                                wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                                        wink_sdk_inventory.models.media_author_attribution_non_authenticated_entity.MediaAuthorAttribution_Non_Authenticated_Entity(
                                            url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                            name = 'Samuel Adams', )
                                        ], 
                                    is_landscape = True, )
                                ], 
                            contact = wink_sdk_inventory.models.contact_non_authenticated_entity.Contact_Non_Authenticated_Entity(
                                first_name = 'John', 
                                last_name = 'Smith', 
                                email = 'johnsmith@email.com', 
                                secondary_email = 'johnsmith2@email.com', 
                                phone_number = '+12125551212', 
                                full_name = 'John Smith', 
                                summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                            address = wink_sdk_inventory.models.simple_address_non_authenticated_entity.SimpleAddress_Non_Authenticated_Entity(
                                address1 = '234', 
                                address2 = 'Pebble #5001', 
                                state = 'CA', 
                                postal_code = '90210', 
                                county = 'Alameda county', 
                                city = '0', 
                                country_code = '0', 
                                country = 'United States', 
                                full_address = '11', ), 
                            commissionable = True, 
                            name = 'Archery lesson', 
                            proximity_code = '1', 
                            sort = 1, 
                            min_age_appropriate_code = '1', 
                            bookable = True, 
                            active = True, 
                            disability_features = [
                                ''
                                ], 
                            security_features = [
                                ''
                                ], 
                            socials = [
                                wink_sdk_inventory.models.social_non_authenticated_entity.Social_Non_Authenticated_Entity(
                                    type = 'FACEBOOK', 
                                    location = '', )
                                ], 
                            price_point = 'THREE', 
                            recognition_list = [
                                wink_sdk_inventory.models.travel_inventory_recognition_non_authenticated_entity.TravelInventoryRecognition_Non_Authenticated_Entity(
                                    identifier = 'recognition-1', 
                                    category = 'AWARD', 
                                    type = 'PERCENT_RATING', 
                                    provider = 'Michelin', 
                                    rating = 8.5, 
                                    max_rating = 10, 
                                    date = '2020-10-24', 
                                    official_appointment_ind = True, 
                                    rating_symbol = '*', )
                                ], 
                            applicable_start = '1970-1-1', 
                            applicable_end = '1970-12-1', 
                            reservation_required_ind = False, 
                            opens = '09:00', 
                            closes = '17:30', 
                            days_of_week = wink_sdk_inventory.models.dow_pattern_group_non_authenticated_entity.DowPatternGroup_Non_Authenticated_Entity(
                                mon = True, 
                                tue = True, 
                                wed = True, 
                                thu = True, 
                                fri = True, 
                                sat = True, 
                                sun = True, 
                                disabled = True, ), 
                            max_seating_capacity = 100, 
                            max_single_party = 10, 
                            offer_breakfast = True, 
                            offer_lunch = True, 
                            offer_dinner = True, 
                            offer_brunch = True, 
                            amenities = [
                                ''
                                ], 
                            info_codes = [
                                ''
                                ], 
                            cuisine_codes = [
                                ''
                                ], ), 
                        list = [
                            wink_sdk_inventory.models.localized_transactional_travel_inventory_non_authenticated_entity.LocalizedTransactionalTravelInventory_Non_Authenticated_Entity(
                                identifier = 'travel-blocking-1', 
                                name = '1', 
                                descriptions = [
                                    wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                        name = 'An example title', 
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                pricing_type = 'PER_STAY', 
                                price = wink_sdk_inventory.models.localized_price_non_authenticated_entity.LocalizedPrice_Non_Authenticated_Entity(
                                    source_to_user_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    source_to_internal_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    user_specified_currency_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
                                        amount = 1.337, 
                                        currency = '0', ), 
                                    source_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
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
                                min_pax = 2, 
                                max_pax = 10, 
                                offer_details = [
                                    wink_sdk_inventory.models.localized_description_non_authenticated_entity.LocalizedDescription_Non_Authenticated_Entity(
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                promotion = '', )
                            ], 
                        channel_inventory_identifier = '', 
                        commissionable = True, 
                        commission = 0.1, 
                        direct = True, 
                        price_list = [
                            null
                            ], )
                    ],
                spas = [
                    wink_sdk_inventory.models.spa_localized_inventory_non_authenticated_entity.SpaLocalizedInventory_Non_Authenticated_Entity(
                        spa = wink_sdk_inventory.models.spa_lightweight_non_authenticated_entity.SpaLightweight_Non_Authenticated_Entity(
                            identifier = 'document-1', 
                            hotel_identifier = 'hotel-1', 
                            featured_ind = False, 
                            lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                            location = {type=POINT, coordinates=[100.5581533, 13.7370197]}, 
                            descriptions = [
                                wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                    name = 'An example title', 
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', )
                                ], 
                            multimedias = [
                                wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                                        wink_sdk_inventory.models.media_author_attribution_non_authenticated_entity.MediaAuthorAttribution_Non_Authenticated_Entity(
                                            url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                            name = 'Samuel Adams', )
                                        ], 
                                    is_landscape = True, )
                                ], 
                            contact = wink_sdk_inventory.models.contact_non_authenticated_entity.Contact_Non_Authenticated_Entity(
                                first_name = 'John', 
                                last_name = 'Smith', 
                                email = 'johnsmith@email.com', 
                                secondary_email = 'johnsmith2@email.com', 
                                phone_number = '+12125551212', 
                                full_name = 'John Smith', 
                                summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                            address = wink_sdk_inventory.models.simple_address_non_authenticated_entity.SimpleAddress_Non_Authenticated_Entity(
                                address1 = '234', 
                                address2 = 'Pebble #5001', 
                                state = 'CA', 
                                postal_code = '90210', 
                                county = 'Alameda county', 
                                city = '0', 
                                country_code = '0', 
                                country = 'United States', 
                                full_address = '11', ), 
                            commissionable = True, 
                            name = 'Archery lesson', 
                            proximity_code = '1', 
                            sort = 1, 
                            min_age_appropriate_code = '1', 
                            bookable = True, 
                            active = True, 
                            disability_features = [
                                ''
                                ], 
                            security_features = [
                                ''
                                ], 
                            socials = [
                                wink_sdk_inventory.models.social_non_authenticated_entity.Social_Non_Authenticated_Entity(
                                    type = 'FACEBOOK', 
                                    location = '', )
                                ], 
                            price_point = 'THREE', 
                            recognition_list = [
                                wink_sdk_inventory.models.travel_inventory_recognition_non_authenticated_entity.TravelInventoryRecognition_Non_Authenticated_Entity(
                                    identifier = 'recognition-1', 
                                    category = 'AWARD', 
                                    type = 'PERCENT_RATING', 
                                    provider = 'Michelin', 
                                    rating = 8.5, 
                                    max_rating = 10, 
                                    date = '2020-10-24', 
                                    official_appointment_ind = True, 
                                    rating_symbol = '*', )
                                ], 
                            applicable_start = '1970-1-1', 
                            applicable_end = '1970-12-1', 
                            reservation_required_ind = False, 
                            opens = '09:00', 
                            closes = '17:30', 
                            days_of_week = wink_sdk_inventory.models.dow_pattern_group_non_authenticated_entity.DowPatternGroup_Non_Authenticated_Entity(
                                mon = True, 
                                tue = True, 
                                wed = True, 
                                thu = True, 
                                fri = True, 
                                sat = True, 
                                sun = True, 
                                disabled = True, ), 
                            amenities = [
                                ''
                                ], ), 
                        list = [
                            wink_sdk_inventory.models.localized_transactional_travel_inventory_non_authenticated_entity.LocalizedTransactionalTravelInventory_Non_Authenticated_Entity(
                                identifier = 'travel-blocking-1', 
                                name = '1', 
                                descriptions = [
                                    wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                        name = 'An example title', 
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                pricing_type = 'PER_STAY', 
                                price = wink_sdk_inventory.models.localized_price_non_authenticated_entity.LocalizedPrice_Non_Authenticated_Entity(
                                    source_to_user_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    source_to_internal_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    user_specified_currency_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
                                        amount = 1.337, 
                                        currency = '0', ), 
                                    source_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
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
                                min_pax = 2, 
                                max_pax = 10, 
                                offer_details = [
                                    wink_sdk_inventory.models.localized_description_non_authenticated_entity.LocalizedDescription_Non_Authenticated_Entity(
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                promotion = '', )
                            ], 
                        channel_inventory_identifier = '', 
                        commissionable = True, 
                        commission = 0.1, 
                        direct = True, 
                        price_list = [
                            null
                            ], )
                    ],
                activities = [
                    wink_sdk_inventory.models.activity_localized_inventory_non_authenticated_entity.ActivityLocalizedInventory_Non_Authenticated_Entity(
                        activity = wink_sdk_inventory.models.activity_lightweight_non_authenticated_entity.ActivityLightweight_Non_Authenticated_Entity(
                            identifier = 'document-1', 
                            hotel_identifier = 'hotel-1', 
                            featured_ind = False, 
                            lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                            location = {type=POINT, coordinates=[100.5581533, 13.7370197]}, 
                            descriptions = [
                                wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                    name = 'An example title', 
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', )
                                ], 
                            multimedias = [
                                wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                                        wink_sdk_inventory.models.media_author_attribution_non_authenticated_entity.MediaAuthorAttribution_Non_Authenticated_Entity(
                                            url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                            name = 'Samuel Adams', )
                                        ], 
                                    is_landscape = True, )
                                ], 
                            contact = wink_sdk_inventory.models.contact_non_authenticated_entity.Contact_Non_Authenticated_Entity(
                                first_name = 'John', 
                                last_name = 'Smith', 
                                email = 'johnsmith@email.com', 
                                secondary_email = 'johnsmith2@email.com', 
                                phone_number = '+12125551212', 
                                full_name = 'John Smith', 
                                summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                            address = wink_sdk_inventory.models.simple_address_non_authenticated_entity.SimpleAddress_Non_Authenticated_Entity(
                                address1 = '234', 
                                address2 = 'Pebble #5001', 
                                state = 'CA', 
                                postal_code = '90210', 
                                county = 'Alameda county', 
                                city = '0', 
                                country_code = '0', 
                                country = 'United States', 
                                full_address = '11', ), 
                            commissionable = True, 
                            name = 'Archery lesson', 
                            proximity_code = '1', 
                            sort = 1, 
                            min_age_appropriate_code = '1', 
                            bookable = True, 
                            active = True, 
                            disability_features = [
                                ''
                                ], 
                            security_features = [
                                ''
                                ], 
                            socials = [
                                wink_sdk_inventory.models.social_non_authenticated_entity.Social_Non_Authenticated_Entity(
                                    type = 'FACEBOOK', 
                                    location = '', )
                                ], 
                            price_point = 'THREE', 
                            recognition_list = [
                                wink_sdk_inventory.models.travel_inventory_recognition_non_authenticated_entity.TravelInventoryRecognition_Non_Authenticated_Entity(
                                    identifier = 'recognition-1', 
                                    category = 'AWARD', 
                                    type = 'PERCENT_RATING', 
                                    provider = 'Michelin', 
                                    rating = 8.5, 
                                    max_rating = 10, 
                                    date = '2020-10-24', 
                                    official_appointment_ind = True, 
                                    rating_symbol = '*', )
                                ], 
                            applicable_start = '1970-1-1', 
                            applicable_end = '1970-12-1', 
                            reservation_required_ind = False, 
                            opens = '09:00', 
                            closes = '17:30', 
                            days_of_week = wink_sdk_inventory.models.dow_pattern_group_non_authenticated_entity.DowPatternGroup_Non_Authenticated_Entity(
                                mon = True, 
                                tue = True, 
                                wed = True, 
                                thu = True, 
                                fri = True, 
                                sat = True, 
                                sun = True, 
                                disabled = True, ), 
                            recreation_category_code = '1', 
                            amenities = [
                                ''
                                ], ), 
                        list = [
                            wink_sdk_inventory.models.localized_transactional_travel_inventory_non_authenticated_entity.LocalizedTransactionalTravelInventory_Non_Authenticated_Entity(
                                identifier = 'travel-blocking-1', 
                                name = '1', 
                                descriptions = [
                                    wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                        name = 'An example title', 
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                pricing_type = 'PER_STAY', 
                                price = wink_sdk_inventory.models.localized_price_non_authenticated_entity.LocalizedPrice_Non_Authenticated_Entity(
                                    source_to_user_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    source_to_internal_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    user_specified_currency_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
                                        amount = 1.337, 
                                        currency = '0', ), 
                                    source_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
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
                                min_pax = 2, 
                                max_pax = 10, 
                                offer_details = [
                                    wink_sdk_inventory.models.localized_description_non_authenticated_entity.LocalizedDescription_Non_Authenticated_Entity(
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                promotion = '', )
                            ], 
                        channel_inventory_identifier = '', 
                        commissionable = True, 
                        commission = 0.1, 
                        direct = True, 
                        price_list = [
                            null
                            ], )
                    ],
                attractions = [
                    wink_sdk_inventory.models.attraction_localized_inventory_non_authenticated_entity.AttractionLocalizedInventory_Non_Authenticated_Entity(
                        attraction = wink_sdk_inventory.models.attraction_lightweight_non_authenticated_entity.AttractionLightweight_Non_Authenticated_Entity(
                            identifier = 'document-1', 
                            hotel_identifier = 'hotel-1', 
                            featured_ind = False, 
                            lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                            location = {type=POINT, coordinates=[100.5581533, 13.7370197]}, 
                            descriptions = [
                                wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                    name = 'An example title', 
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', )
                                ], 
                            multimedias = [
                                wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                                        wink_sdk_inventory.models.media_author_attribution_non_authenticated_entity.MediaAuthorAttribution_Non_Authenticated_Entity(
                                            url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                            name = 'Samuel Adams', )
                                        ], 
                                    is_landscape = True, )
                                ], 
                            contact = wink_sdk_inventory.models.contact_non_authenticated_entity.Contact_Non_Authenticated_Entity(
                                first_name = 'John', 
                                last_name = 'Smith', 
                                email = 'johnsmith@email.com', 
                                secondary_email = 'johnsmith2@email.com', 
                                phone_number = '+12125551212', 
                                full_name = 'John Smith', 
                                summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                            address = wink_sdk_inventory.models.simple_address_non_authenticated_entity.SimpleAddress_Non_Authenticated_Entity(
                                address1 = '234', 
                                address2 = 'Pebble #5001', 
                                state = 'CA', 
                                postal_code = '90210', 
                                county = 'Alameda county', 
                                city = '0', 
                                country_code = '0', 
                                country = 'United States', 
                                full_address = '11', ), 
                            commissionable = True, 
                            name = 'Archery lesson', 
                            proximity_code = '1', 
                            sort = 1, 
                            min_age_appropriate_code = '1', 
                            bookable = True, 
                            active = True, 
                            disability_features = [
                                ''
                                ], 
                            security_features = [
                                ''
                                ], 
                            socials = [
                                wink_sdk_inventory.models.social_non_authenticated_entity.Social_Non_Authenticated_Entity(
                                    type = 'FACEBOOK', 
                                    location = '', )
                                ], 
                            price_point = 'THREE', 
                            recognition_list = [
                                wink_sdk_inventory.models.travel_inventory_recognition_non_authenticated_entity.TravelInventoryRecognition_Non_Authenticated_Entity(
                                    identifier = 'recognition-1', 
                                    category = 'AWARD', 
                                    type = 'PERCENT_RATING', 
                                    provider = 'Michelin', 
                                    rating = 8.5, 
                                    max_rating = 10, 
                                    date = '2020-10-24', 
                                    official_appointment_ind = True, 
                                    rating_symbol = '*', )
                                ], 
                            applicable_start = '1970-1-1', 
                            applicable_end = '1970-12-1', 
                            reservation_required_ind = False, 
                            opens = '09:00', 
                            closes = '17:30', 
                            days_of_week = wink_sdk_inventory.models.dow_pattern_group_non_authenticated_entity.DowPatternGroup_Non_Authenticated_Entity(
                                mon = True, 
                                tue = True, 
                                wed = True, 
                                thu = True, 
                                fri = True, 
                                sat = True, 
                                sun = True, 
                                disabled = True, ), 
                            attraction_category_code = '1', 
                            courtesy_phone = True, ), 
                        list = [
                            wink_sdk_inventory.models.localized_transactional_travel_inventory_non_authenticated_entity.LocalizedTransactionalTravelInventory_Non_Authenticated_Entity(
                                identifier = 'travel-blocking-1', 
                                name = '1', 
                                descriptions = [
                                    wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                        name = 'An example title', 
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                pricing_type = 'PER_STAY', 
                                price = wink_sdk_inventory.models.localized_price_non_authenticated_entity.LocalizedPrice_Non_Authenticated_Entity(
                                    source_to_user_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    source_to_internal_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    user_specified_currency_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
                                        amount = 1.337, 
                                        currency = '0', ), 
                                    source_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
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
                                min_pax = 2, 
                                max_pax = 10, 
                                offer_details = [
                                    wink_sdk_inventory.models.localized_description_non_authenticated_entity.LocalizedDescription_Non_Authenticated_Entity(
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                promotion = '', )
                            ], 
                        channel_inventory_identifier = '', 
                        commissionable = True, 
                        commission = 0.1, 
                        direct = True, 
                        price_list = [
                            null
                            ], )
                    ],
                places = [
                    wink_sdk_inventory.models.place_localized_inventory_non_authenticated_entity.PlaceLocalizedInventory_Non_Authenticated_Entity(
                        place = wink_sdk_inventory.models.place_lightweight_non_authenticated_entity.PlaceLightweight_Non_Authenticated_Entity(
                            identifier = 'document-1', 
                            hotel_identifier = 'hotel-1', 
                            featured_ind = False, 
                            lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                            location = {type=POINT, coordinates=[100.5581533, 13.7370197]}, 
                            descriptions = [
                                wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                    name = 'An example title', 
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', )
                                ], 
                            multimedias = [
                                wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                                        wink_sdk_inventory.models.media_author_attribution_non_authenticated_entity.MediaAuthorAttribution_Non_Authenticated_Entity(
                                            url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                            name = 'Samuel Adams', )
                                        ], 
                                    is_landscape = True, )
                                ], 
                            contact = wink_sdk_inventory.models.contact_non_authenticated_entity.Contact_Non_Authenticated_Entity(
                                first_name = 'John', 
                                last_name = 'Smith', 
                                email = 'johnsmith@email.com', 
                                secondary_email = 'johnsmith2@email.com', 
                                phone_number = '+12125551212', 
                                full_name = 'John Smith', 
                                summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                            address = wink_sdk_inventory.models.simple_address_non_authenticated_entity.SimpleAddress_Non_Authenticated_Entity(
                                address1 = '234', 
                                address2 = 'Pebble #5001', 
                                state = 'CA', 
                                postal_code = '90210', 
                                county = 'Alameda county', 
                                city = '0', 
                                country_code = '0', 
                                country = 'United States', 
                                full_address = '11', ), 
                            commissionable = True, 
                            name = 'Archery lesson', 
                            proximity_code = '1', 
                            sort = 1, 
                            min_age_appropriate_code = '1', 
                            bookable = True, 
                            active = True, 
                            disability_features = [
                                ''
                                ], 
                            security_features = [
                                ''
                                ], 
                            socials = [
                                wink_sdk_inventory.models.social_non_authenticated_entity.Social_Non_Authenticated_Entity(
                                    type = 'FACEBOOK', 
                                    location = '', )
                                ], 
                            price_point = 'THREE', 
                            recognition_list = [
                                wink_sdk_inventory.models.travel_inventory_recognition_non_authenticated_entity.TravelInventoryRecognition_Non_Authenticated_Entity(
                                    identifier = 'recognition-1', 
                                    category = 'AWARD', 
                                    type = 'PERCENT_RATING', 
                                    provider = 'Michelin', 
                                    rating = 8.5, 
                                    max_rating = 10, 
                                    date = '2020-10-24', 
                                    official_appointment_ind = True, 
                                    rating_symbol = '*', )
                                ], 
                            applicable_start = '1970-1-1', 
                            applicable_end = '1970-12-1', 
                            reservation_required_ind = False, 
                            opens = '09:00', 
                            closes = '17:30', 
                            days_of_week = wink_sdk_inventory.models.dow_pattern_group_non_authenticated_entity.DowPatternGroup_Non_Authenticated_Entity(
                                mon = True, 
                                tue = True, 
                                wed = True, 
                                thu = True, 
                                fri = True, 
                                sat = True, 
                                sun = True, 
                                disabled = True, ), 
                            ref_point_category_code = '[1]', ), 
                        list = [
                            wink_sdk_inventory.models.localized_transactional_travel_inventory_non_authenticated_entity.LocalizedTransactionalTravelInventory_Non_Authenticated_Entity(
                                identifier = 'travel-blocking-1', 
                                name = '1', 
                                descriptions = [
                                    wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                        name = 'An example title', 
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                pricing_type = 'PER_STAY', 
                                price = wink_sdk_inventory.models.localized_price_non_authenticated_entity.LocalizedPrice_Non_Authenticated_Entity(
                                    source_to_user_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    source_to_internal_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    user_specified_currency_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
                                        amount = 1.337, 
                                        currency = '0', ), 
                                    source_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
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
                                min_pax = 2, 
                                max_pax = 10, 
                                offer_details = [
                                    wink_sdk_inventory.models.localized_description_non_authenticated_entity.LocalizedDescription_Non_Authenticated_Entity(
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                promotion = '', )
                            ], 
                        channel_inventory_identifier = '', 
                        commissionable = True, 
                        commission = 0.1, 
                        direct = True, 
                        price_list = [
                            null
                            ], )
                    ],
                metadata = [
                    wink_sdk_inventory.models.meta_data_non_authenticated_entity.MetaData_Non_Authenticated_Entity(
                        type = 'PAGE_TITLE', 
                        key = '', 
                        value = '', )
                    ],
                images = [
                    wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                        descriptions = [
                            wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                name = 'An example title', 
                                description = 'This is a longer description in the specified language.', 
                                language = 'en', )
                            ], 
                        lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                        attribution = [
                            wink_sdk_inventory.models.media_author_attribution_non_authenticated_entity.MediaAuthorAttribution_Non_Authenticated_Entity(
                                url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                name = 'Samuel Adams', )
                            ], 
                        is_landscape = True, )
                    ],
                videos = [
                    wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                        descriptions = [
                            wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                name = 'An example title', 
                                description = 'This is a longer description in the specified language.', 
                                language = 'en', )
                            ], 
                        lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                        attribution = [
                            wink_sdk_inventory.models.media_author_attribution_non_authenticated_entity.MediaAuthorAttribution_Non_Authenticated_Entity(
                                url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                name = 'Samuel Adams', )
                            ], 
                        is_landscape = True, )
                    ],
                recognitions = [
                    wink_sdk_inventory.models.travel_inventory_recognition_non_authenticated_entity.TravelInventoryRecognition_Non_Authenticated_Entity(
                        identifier = 'recognition-1', 
                        category = 'AWARD', 
                        type = 'PERCENT_RATING', 
                        provider = 'Michelin', 
                        rating = 8.5, 
                        max_rating = 10, 
                        date = '2020-10-24', 
                        official_appointment_ind = True, 
                        rating_symbol = '*', )
                    ],
                announcements = [
                    wink_sdk_inventory.models.announcement_lightweight_non_authenticated_entity.AnnouncementLightweight_Non_Authenticated_Entity(
                        start_date = '2022-10-24', 
                        end_date = '2022-11-25', 
                        descriptions = [
                            wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                name = 'An example title', 
                                description = 'This is a longer description in the specified language.', 
                                language = 'en', )
                            ], 
                        show_title = True, 
                        show_always = True, )
                    ],
                reviews = [
                    wink_sdk_inventory.models.user_review_non_authenticated_entity.UserReview_Non_Authenticated_Entity(
                        review_by = '', 
                        reviewed_on = '2017-12-22T03:07:58.742+0000', 
                        average_score = 8.7, 
                        answers = [
                            wink_sdk_inventory.models.user_review_answer_non_authenticated_entity.UserReviewAnswer_Non_Authenticated_Entity(
                                category = 'COMFORT', 
                                sort = 56, 
                                value = 56, )
                            ], 
                        response_from_hotel = 'It was so great to have you at our hotel. Please recommend your friends and come again soon.', 
                        image_identifier = 'cloudinary-image-1', 
                        review = 'Our stay was amazing! Can recommend highly to all. Felt like home.', 
                        likes = reviewBy-1, )
                    ],
                sales_channel = wink_sdk_inventory.models.sales_channel_info_non_authenticated_entity.SalesChannelInfo_Non_Authenticated_Entity(
                    name = 'Kim Kardashian', 
                    channel_discount_percent = 0.2, 
                    commission_percent = 0.2, ),
                cheapest_room_types = [
                    wink_sdk_inventory.models.room_type_with_price_configuration_non_authenticated_entity.RoomTypeWithPriceConfiguration_Non_Authenticated_Entity(
                        room = wink_sdk_inventory.models.guest_room_lightweight_non_authenticated_entity.GuestRoomLightweight_Non_Authenticated_Entity(
                            identifier = 'document-1', 
                            hotel_identifier = 'hotel-1', 
                            featured_ind = False, 
                            lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                            location = {type=POINT, coordinates=[100.5581533, 13.7370197]}, 
                            descriptions = [
                                wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                    name = 'An example title', 
                                    description = 'This is a longer description in the specified language.', 
                                    language = 'en', )
                                ], 
                            multimedias = [
                                wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                                        wink_sdk_inventory.models.media_author_attribution_non_authenticated_entity.MediaAuthorAttribution_Non_Authenticated_Entity(
                                            url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                            name = 'Samuel Adams', )
                                        ], 
                                    is_landscape = True, )
                                ], 
                            contact = wink_sdk_inventory.models.contact_non_authenticated_entity.Contact_Non_Authenticated_Entity(
                                first_name = 'John', 
                                last_name = 'Smith', 
                                email = 'johnsmith@email.com', 
                                secondary_email = 'johnsmith2@email.com', 
                                phone_number = '+12125551212', 
                                full_name = 'John Smith', 
                                summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                            address = wink_sdk_inventory.models.simple_address_non_authenticated_entity.SimpleAddress_Non_Authenticated_Entity(
                                address1 = '234', 
                                address2 = 'Pebble #5001', 
                                state = 'CA', 
                                postal_code = '90210', 
                                county = 'Alameda county', 
                                city = '0', 
                                country_code = '0', 
                                country = 'United States', 
                                full_address = '11', ), 
                            commissionable = True, 
                            name = 'Archery lesson', 
                            proximity_code = '1', 
                            sort = 1, 
                            min_age_appropriate_code = '1', 
                            bookable = True, 
                            active = True, 
                            disability_features = [
                                ''
                                ], 
                            security_features = [
                                ''
                                ], 
                            socials = [
                                wink_sdk_inventory.models.social_non_authenticated_entity.Social_Non_Authenticated_Entity(
                                    type = 'FACEBOOK', 
                                    location = '', )
                                ], 
                            price_point = 'THREE', 
                            recognition_list = [
                                wink_sdk_inventory.models.travel_inventory_recognition_non_authenticated_entity.TravelInventoryRecognition_Non_Authenticated_Entity(
                                    identifier = 'recognition-1', 
                                    category = 'AWARD', 
                                    type = 'PERCENT_RATING', 
                                    provider = 'Michelin', 
                                    rating = 8.5, 
                                    max_rating = 10, 
                                    date = '2020-10-24', 
                                    official_appointment_ind = True, 
                                    rating_symbol = '*', )
                                ], 
                            max_occupancy = 2, 
                            min_occupancy = 1, 
                            quantity = 40, 
                            non_smoking = True, 
                            bedroom_configuration_list = [
                                wink_sdk_inventory.models.bedroom_configuration_non_authenticated_entity.BedroomConfiguration_Non_Authenticated_Entity(
                                    identifier = '0', 
                                    name = '0', 
                                    bedroom_list = [
                                        wink_sdk_inventory.models.bedroom_non_authenticated_entity.Bedroom_Non_Authenticated_Entity(
                                            type = 'MASTER', 
                                            bed_list = [
                                                wink_sdk_inventory.models.bed_non_authenticated_entity.Bed_Non_Authenticated_Entity(
                                                    bed_type_code = '1', 
                                                    quantity = 10, )
                                                ], )
                                        ], )
                                ], 
                            size = 55, 
                            max_adult_occupancy = 1, 
                            max_child_occupancy = 0, 
                            bathroom_count = 0, 
                            living_room_count = 0, 
                            max_rollaways = 0, 
                            room_category = '1', 
                            floor = '', 
                            room_location_code = '1', 
                            room_view_code = '1', 
                            composite = False, 
                            composite_count = 2, 
                            room_classification_code = '1', 
                            room_architecture_code = '1', 
                            room_gender = 'Unknown', 
                            shared_room_ind = False, 
                            max_cribs = 1, 
                            amenities = [
                                ''
                                ], 
                            included_adult_occupancy = 2, 
                            included_child_occupancy = 0, ), 
                        price = wink_sdk_inventory.models.room_configuration_price_non_authenticated_entity.RoomConfigurationPrice_Non_Authenticated_Entity(
                            channel_inventory_identifier = '', 
                            list = [
                                wink_sdk_inventory.models.localized_transactional_travel_inventory_non_authenticated_entity.LocalizedTransactionalTravelInventory_Non_Authenticated_Entity(
                                    identifier = 'travel-blocking-1', 
                                    name = '1', 
                                    descriptions = [
                                        wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                            name = 'An example title', 
                                            description = 'This is a longer description in the specified language.', 
                                            language = 'en', )
                                        ], 
                                    pricing_type = 'PER_STAY', 
                                    price = wink_sdk_inventory.models.localized_price_non_authenticated_entity.LocalizedPrice_Non_Authenticated_Entity(
                                        source_to_user_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                            source = '0', 
                                            target = '0', 
                                            exchange_rate = 1.337, 
                                            timestamp = 56, ), 
                                        source_to_internal_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                            source = '0', 
                                            target = '0', 
                                            exchange_rate = 1.337, 
                                            timestamp = 56, ), 
                                        user_specified_currency_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
                                            amount = 1.337, 
                                            currency = '0', ), 
                                        source_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
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
                                    min_pax = 2, 
                                    max_pax = 10, 
                                    offer_details = [
                                        wink_sdk_inventory.models.localized_description_non_authenticated_entity.LocalizedDescription_Non_Authenticated_Entity(
                                            description = 'This is a longer description in the specified language.', 
                                            language = 'en', )
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
                            rate_plan = wink_sdk_inventory.models.room_configuration_price_rate_plan_non_authenticated_entity.RoomConfigurationPriceRatePlan_Non_Authenticated_Entity(
                                identifier = '0', 
                                name = 'BAR 1', 
                                breakfast = False, 
                                brunch = False, 
                                lunch = False, 
                                dinner = False, 
                                all_inclusive = False, 
                                all_inclusive_plus_alcohol = False, 
                                early_check_in_charge = null, 
                                late_check_out_charge = null, 
                                cancellation_policy = wink_sdk_inventory.models.cancellation_policy_lightweight_non_authenticated_entity.CancellationPolicyLightweight_Non_Authenticated_Entity(
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
                                cancellation_policy_exceptions = wink_sdk_inventory.models.cancellation_policy_exceptions_non_authenticated_entity.CancellationPolicyExceptions_Non_Authenticated_Entity(
                                    list = [
                                        wink_sdk_inventory.models.cancellation_policy_exception_non_authenticated_entity.CancellationPolicyException_Non_Authenticated_Entity(
                                            cancellation_policy_identifier = '0', 
                                            cancellation_policy = wink_sdk_inventory.models.cancellation_policy_lightweight_non_authenticated_entity.CancellationPolicyLightweight_Non_Authenticated_Entity(
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
                            price = wink_sdk_inventory.models.stay_rate_non_authenticated_entity.StayRate_Non_Authenticated_Entity(
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
                            extra_charges = wink_sdk_inventory.models.extra_charges_non_authenticated_entity.ExtraCharges_Non_Authenticated_Entity(
                                items = [
                                    wink_sdk_inventory.models.extra_charge_non_authenticated_entity.ExtraCharge_Non_Authenticated_Entity(
                                        rate_plan_level_fee = wink_sdk_inventory.models.rate_plan_level_fee_non_authenticated_entity.RatePlanLevelFee_Non_Authenticated_Entity(
                                            descriptions = [
                                                wink_sdk_inventory.models.localized_description_non_authenticated_entity.LocalizedDescription_Non_Authenticated_Entity(
                                                    description = 'This is a longer description in the specified language.', 
                                                    language = 'en', )
                                                ], 
                                            fixed_amount = , 
                                            type = 'PER_DAY', ), 
                                        unit_price = wink_sdk_inventory.models.localized_price_non_authenticated_entity.LocalizedPrice_Non_Authenticated_Entity(
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
                            configuration = wink_sdk_inventory.models.room_configuration_non_authenticated_entity.RoomConfiguration_Non_Authenticated_Entity(
                                adults = 2, 
                                children = [
                                    wink_sdk_inventory.models.child_non_authenticated_entity.Child_Non_Authenticated_Entity(
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
                        available = True, )
                    ],
                available = True,
                lowest_price = wink_sdk_inventory.models.room_type_with_price_configuration_non_authenticated_entity.RoomTypeWithPriceConfiguration_Non_Authenticated_Entity(
                    room = wink_sdk_inventory.models.guest_room_lightweight_non_authenticated_entity.GuestRoomLightweight_Non_Authenticated_Entity(
                        identifier = 'document-1', 
                        hotel_identifier = 'hotel-1', 
                        featured_ind = False, 
                        lifestyle_type = 'LIFESTYLE_HEALTH_FITNESS', 
                        location = {type=POINT, coordinates=[100.5581533, 13.7370197]}, 
                        descriptions = [
                            wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                name = 'An example title', 
                                description = 'This is a longer description in the specified language.', 
                                language = 'en', )
                            ], 
                        multimedias = [
                            wink_sdk_inventory.models.simple_multimedia_non_authenticated_entity.SimpleMultimedia_Non_Authenticated_Entity(
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
                                    wink_sdk_inventory.models.media_author_attribution_non_authenticated_entity.MediaAuthorAttribution_Non_Authenticated_Entity(
                                        url = 'https://maps.google.com/maps/contrib/111628493169070103594', 
                                        name = 'Samuel Adams', )
                                    ], 
                                is_landscape = True, )
                            ], 
                        contact = wink_sdk_inventory.models.contact_non_authenticated_entity.Contact_Non_Authenticated_Entity(
                            first_name = 'John', 
                            last_name = 'Smith', 
                            email = 'johnsmith@email.com', 
                            secondary_email = 'johnsmith2@email.com', 
                            phone_number = '+12125551212', 
                            full_name = 'John Smith', 
                            summary = 'John Smith (johnsmith@gmail.com / +12125551212)', ), 
                        address = wink_sdk_inventory.models.simple_address_non_authenticated_entity.SimpleAddress_Non_Authenticated_Entity(
                            address1 = '234', 
                            address2 = 'Pebble #5001', 
                            state = 'CA', 
                            postal_code = '90210', 
                            county = 'Alameda county', 
                            city = '0', 
                            country_code = '0', 
                            country = 'United States', 
                            full_address = '11', ), 
                        commissionable = True, 
                        name = 'Archery lesson', 
                        proximity_code = '1', 
                        sort = 1, 
                        min_age_appropriate_code = '1', 
                        bookable = True, 
                        active = True, 
                        disability_features = [
                            ''
                            ], 
                        security_features = [
                            ''
                            ], 
                        socials = [
                            wink_sdk_inventory.models.social_non_authenticated_entity.Social_Non_Authenticated_Entity(
                                type = 'FACEBOOK', 
                                location = '', )
                            ], 
                        price_point = 'THREE', 
                        recognition_list = [
                            wink_sdk_inventory.models.travel_inventory_recognition_non_authenticated_entity.TravelInventoryRecognition_Non_Authenticated_Entity(
                                identifier = 'recognition-1', 
                                category = 'AWARD', 
                                type = 'PERCENT_RATING', 
                                provider = 'Michelin', 
                                rating = 8.5, 
                                max_rating = 10, 
                                date = '2020-10-24', 
                                official_appointment_ind = True, 
                                rating_symbol = '*', )
                            ], 
                        max_occupancy = 2, 
                        min_occupancy = 1, 
                        quantity = 40, 
                        non_smoking = True, 
                        bedroom_configuration_list = [
                            wink_sdk_inventory.models.bedroom_configuration_non_authenticated_entity.BedroomConfiguration_Non_Authenticated_Entity(
                                identifier = '0', 
                                name = '0', 
                                bedroom_list = [
                                    wink_sdk_inventory.models.bedroom_non_authenticated_entity.Bedroom_Non_Authenticated_Entity(
                                        type = 'MASTER', 
                                        bed_list = [
                                            wink_sdk_inventory.models.bed_non_authenticated_entity.Bed_Non_Authenticated_Entity(
                                                bed_type_code = '1', 
                                                quantity = 10, )
                                            ], )
                                    ], )
                            ], 
                        size = 55, 
                        max_adult_occupancy = 1, 
                        max_child_occupancy = 0, 
                        bathroom_count = 0, 
                        living_room_count = 0, 
                        max_rollaways = 0, 
                        room_category = '1', 
                        floor = '', 
                        room_location_code = '1', 
                        room_view_code = '1', 
                        composite = False, 
                        composite_count = 2, 
                        room_classification_code = '1', 
                        room_architecture_code = '1', 
                        room_gender = 'Unknown', 
                        shared_room_ind = False, 
                        max_cribs = 1, 
                        amenities = [
                            ''
                            ], 
                        included_adult_occupancy = 2, 
                        included_child_occupancy = 0, ), 
                    price = wink_sdk_inventory.models.room_configuration_price_non_authenticated_entity.RoomConfigurationPrice_Non_Authenticated_Entity(
                        channel_inventory_identifier = '', 
                        list = [
                            wink_sdk_inventory.models.localized_transactional_travel_inventory_non_authenticated_entity.LocalizedTransactionalTravelInventory_Non_Authenticated_Entity(
                                identifier = 'travel-blocking-1', 
                                name = '1', 
                                descriptions = [
                                    wink_sdk_inventory.models.simple_description_non_authenticated_entity.SimpleDescription_Non_Authenticated_Entity(
                                        name = 'An example title', 
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
                                    ], 
                                pricing_type = 'PER_STAY', 
                                price = wink_sdk_inventory.models.localized_price_non_authenticated_entity.LocalizedPrice_Non_Authenticated_Entity(
                                    source_to_user_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    source_to_internal_currency_quote = wink_sdk_inventory.models.quote_lightweight_non_authenticated_entity.QuoteLightweight_Non_Authenticated_Entity(
                                        source = '0', 
                                        target = '0', 
                                        exchange_rate = 1.337, 
                                        timestamp = 56, ), 
                                    user_specified_currency_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
                                        amount = 1.337, 
                                        currency = '0', ), 
                                    source_base_total = wink_sdk_inventory.models.custom_monetary_amount.CustomMonetaryAmount(
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
                                min_pax = 2, 
                                max_pax = 10, 
                                offer_details = [
                                    wink_sdk_inventory.models.localized_description_non_authenticated_entity.LocalizedDescription_Non_Authenticated_Entity(
                                        description = 'This is a longer description in the specified language.', 
                                        language = 'en', )
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
                        rate_plan = wink_sdk_inventory.models.room_configuration_price_rate_plan_non_authenticated_entity.RoomConfigurationPriceRatePlan_Non_Authenticated_Entity(
                            identifier = '0', 
                            name = 'BAR 1', 
                            breakfast = False, 
                            brunch = False, 
                            lunch = False, 
                            dinner = False, 
                            all_inclusive = False, 
                            all_inclusive_plus_alcohol = False, 
                            early_check_in_charge = null, 
                            late_check_out_charge = null, 
                            cancellation_policy = wink_sdk_inventory.models.cancellation_policy_lightweight_non_authenticated_entity.CancellationPolicyLightweight_Non_Authenticated_Entity(
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
                            cancellation_policy_exceptions = wink_sdk_inventory.models.cancellation_policy_exceptions_non_authenticated_entity.CancellationPolicyExceptions_Non_Authenticated_Entity(
                                list = [
                                    wink_sdk_inventory.models.cancellation_policy_exception_non_authenticated_entity.CancellationPolicyException_Non_Authenticated_Entity(
                                        cancellation_policy_identifier = '0', 
                                        cancellation_policy = wink_sdk_inventory.models.cancellation_policy_lightweight_non_authenticated_entity.CancellationPolicyLightweight_Non_Authenticated_Entity(
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
                        price = wink_sdk_inventory.models.stay_rate_non_authenticated_entity.StayRate_Non_Authenticated_Entity(
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
                        extra_charges = wink_sdk_inventory.models.extra_charges_non_authenticated_entity.ExtraCharges_Non_Authenticated_Entity(
                            items = [
                                wink_sdk_inventory.models.extra_charge_non_authenticated_entity.ExtraCharge_Non_Authenticated_Entity(
                                    rate_plan_level_fee = wink_sdk_inventory.models.rate_plan_level_fee_non_authenticated_entity.RatePlanLevelFee_Non_Authenticated_Entity(
                                        descriptions = [
                                            wink_sdk_inventory.models.localized_description_non_authenticated_entity.LocalizedDescription_Non_Authenticated_Entity(
                                                description = 'This is a longer description in the specified language.', 
                                                language = 'en', )
                                            ], 
                                        fixed_amount = , 
                                        type = 'PER_DAY', ), 
                                    unit_price = wink_sdk_inventory.models.localized_price_non_authenticated_entity.LocalizedPrice_Non_Authenticated_Entity(
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
                        configuration = wink_sdk_inventory.models.room_configuration_non_authenticated_entity.RoomConfiguration_Non_Authenticated_Entity(
                            adults = 2, 
                            children = [
                                wink_sdk_inventory.models.child_non_authenticated_entity.Child_Non_Authenticated_Entity(
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
                    available = True, )
            )
        else:
            return PropertyInventoryResponseNonAuthenticatedEntity(
        )
        """

    def testPropertyInventoryResponseNonAuthenticatedEntity(self):
        """Test PropertyInventoryResponseNonAuthenticatedEntity"""
        # inst_req_only = self.make_instance(include_optional=False)
        # inst_req_and_optional = self.make_instance(include_optional=True)

if __name__ == '__main__':
    unittest.main()
