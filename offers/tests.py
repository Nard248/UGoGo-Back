# offers/tests.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Flight, UserFlight, Offer
from users.models import Users
from locations.models import Country, City, Airport
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from items.models.items import ItemCategory

# class OffersAPITestCase(APITestCase):
#     def setUp(self):
#         # Create test user
#         self.user = Users.objects.create_user(
#             email='testuser@example.com',
#             password='testpassword',
#             first_name='Test',
#             last_name='User'
#         )
#         self.courier = Users.objects.create_user(
#             email='courier@example.com',
#             password='courierpassword',
#             first_name='Courier',
#             last_name='Example'
#         )
#
#         # Obtain JWT token for authentication
#         refresh = RefreshToken.for_user(self.user)
#         self.access_token = str(refresh.access_token)
#         self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.access_token)
#
#         # Create Country
#         self.country = Country.objects.create(
#             country_code='AM',
#             country_abbr='ARM',
#             country_name='Armenia'
#         )
#
#         # Create City
#         self.city = City.objects.create(
#             country=self.country,
#             city_code='YE',
#             city_abbr='YE',
#             city_name='Yerevan',
#             timezone='Asia/Yerevan'
#         )
#
#         # Create Airports
#         self.airport_origin = Airport.objects.create(
#             city=self.city,
#             airport_code='EVN',
#             airport_name='Zvartnots International Airport'
#         )
#         self.airport_destination = Airport.objects.create(
#             city=self.city,
#             airport_code='LDN',
#             airport_name='London International Airport'
#         )
#
#         # Create Flight
#         self.flight = Flight.objects.create(
#             publisher='airline',
#             from_airport=self.airport_origin,
#             to_airport=self.airport_destination,
#             departure_datetime=timezone.now() + timedelta(days=1),
#             arrival_datetime=timezone.now() + timedelta(days=1, hours=5)
#         )
#
#         # Create UserFlight
#         self.user_flight = UserFlight.objects.create(
#             flight=self.flight,
#             user=self.user
#         )
#
#         # Create Offer
#         self.offer = Offer.objects.create(
#             user_flight=self.user_flight,
#             courier=self.courier,
#             status='available',
#             price=150.00,
#             available_weight=20.0,
#             available_space=2.0
#         )
#
#     def test_list_flights(self):
#         url = reverse('flight-list-create')
#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 1)
#         flight = response.data['results'][0]
#         self.assertEqual(flight['id'], self.flight.id)
#         self.assertEqual(flight['publisher'], 'airline')
#         self.assertEqual(flight['from_airport']['airport_code'], 'EVN')
#         self.assertEqual(flight['to_airport']['airport_code'], 'LDN')
#
#     def test_create_flight(self):
#         url = reverse('flight-list-create')
#         data = {
#             'publisher': 'custom',
#             'from_airport_id': self.airport_origin.id,
#             'to_airport_id': self.airport_destination.id,
#             'departure_datetime': (timezone.now() + timedelta(days=2)).isoformat(),
#             'arrival_datetime': (timezone.now() + timedelta(days=2, hours=6)).isoformat()
#         }
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Flight.objects.count(), 2)
#         new_flight = Flight.objects.get(id=response.data['id'])
#         self.assertEqual(new_flight.publisher, 'custom')
#
#     def test_retrieve_flight_detail(self):
#         url = reverse('flight-detail', kwargs={'pk': self.flight.id})
#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         flight = response.data
#         self.assertEqual(flight['id'], self.flight.id)
#         self.assertEqual(flight['from_airport']['airport_code'], 'EVN')
#         self.assertEqual(flight['to_airport']['airport_code'], 'LDN')
#
#     def test_update_flight(self):
#         url = reverse('flight-detail', kwargs={'pk': self.flight.id})
#         data = {
#             'publisher': 'airline',
#             'from_airport_id': self.airport_origin.id,
#             'to_airport_id': self.airport_destination.id,
#             'departure_datetime': (timezone.now() + timedelta(days=3)).isoformat(),
#             'arrival_datetime': (timezone.now() + timedelta(days=3, hours=5)).isoformat()
#         }
#         response = self.client.put(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.flight.refresh_from_db()
#         self.assertEqual(self.flight.departure_datetime.date(), (timezone.now() + timedelta(days=3)).date())
#
#     def test_partial_update_flight(self):
#         url = reverse('flight-detail', kwargs={'pk': self.flight.id})
#         data = {
#             'publisher': 'airline'
#         }
#         response = self.client.patch(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.flight.refresh_from_db()
#         self.assertEqual(self.flight.publisher, 'airline')
#
#     def test_delete_flight(self):
#         url = reverse('flight-detail', kwargs={'pk': self.flight.id})
#         response = self.client.delete(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
#         self.assertEqual(Flight.objects.count(), 0)
#
#     def test_search_flights(self):
#         url = reverse('flight-search')
#         params = {
#             'origin': 'Yerevan',
#             'destination': 'London',
#             'departure_date_from': (timezone.now() + timedelta(days=1)).date(),
#             'departure_date_to': (timezone.now() + timedelta(days=2)).date(),
#             'min_weight': 10,
#             'max_weight': 30,
#             'min_price': 100,
#             'max_price': 200,
#             'ordering': 'price'
#         }
#         response = self.client.get(url, params, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertEqual(len(response.data['results']), 1)
#         offer = response.data['results'][0]
#         self.assertEqual(offer['id'], self.offer.id)
#         self.assertEqual(offer['price'], '150.00')
#
#     def test_search_flights_invalid_params(self):
#         url = reverse('flight-search')
#         params = {
#             'origin': 'Yerevan',
#             'departure_date_from': 'invalid-date',
#             'min_weight': 'abc',
#             'max_price': 'xyz'
#         }
#         response = self.client.get(url, params, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#
#     def test_retrieve_offer_detail(self):
#         url = reverse('offer-detail', kwargs={'pk': self.offer.id})
#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         offer = response.data
#         self.assertEqual(offer['id'], self.offer.id)
#         self.assertEqual(offer['price'], '150.00')
#         self.assertEqual(offer['courier']['email'], 'courier@example.com')
#
#     def test_list_offers(self):
#         """
#         Test listing all offers.
#         """
#         url = reverse('offer-list-create')
#         response = self.client.get(url, format='json')
#         self.assertEqual(response.status_code, status.HTTP_200_OK)
#         self.assertIsInstance(response.data['results'], list)
#
#     def test_create_offer(self):
#         """
#         Test creating a new offer.
#         """
#         url = reverse('offer-list-create')
#         data = {
#             'user_flight_id': self.user_flight.id,
#             'courier_id': self.courier.id,
#             'status': 'available',
#             'price': '200.00',
#             'available_weight': '25.0',
#             'available_space': '3.0'
#         }
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)
#         self.assertEqual(Offer.objects.count(), 2)
#         new_offer = Offer.objects.get(id=response.data['id'])
#         self.assertEqual(new_offer.price, 200.00)
#         self.assertEqual(new_offer.available_weight, 25.0)
#         self.assertEqual(new_offer.available_space, 3.0)
#
#     def test_create_offer_invalid_data(self):
#         """
#         Test creating an offer with invalid data.
#         """
#         url = reverse('offer-list-create')
#         data = {
#             'user_flight_id': self.user_flight.id,
#             'courier_id': self.courier.id,
#             'status': 'invalid_status',  # Invalid status
#             'price': 'invalid_price',  # Invalid price
#         }
#         response = self.client.post(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('status', response.data)
#         self.assertIn('price', response.data)
#
#     def test_partial_update_flight_invalid_field(self):
#         url = reverse('flight-detail', kwargs={'pk': self.flight.id})
#         data = {
#             'status': 'cancelled'  # Invalid field
#         }
#         response = self.client.patch(url, data, format='json')
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         self.assertIn('unexpected_fields', response.data)


class MultiCategoryOfferCreationTest(APITestCase):
    def setUp(self):
        self.user = Users.objects.create_user(
            email='courier@example.com',
            password='password123'
        )
        token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + str(token.access_token))

        # Basic location data
        self.country = Country.objects.create(
            country_code='US',
            country_abbr='USA',
            country_name='United States'
        )
        self.city = City.objects.create(
            country=self.country,
            city_code='NYC',
            city_abbr='NY',
            city_name='New York',
            timezone='America/New_York'
        )
        self.airport_jfk = Airport.objects.create(
            city=self.city,
            airport_code='JFK',
            airport_name='John F Kennedy Intl'
        )
        self.airport_lax = Airport.objects.create(
            city=self.city,
            airport_code='LAX',
            airport_name='Los Angeles Intl'
        )

        # some categories
        self.cat1 = ItemCategory.objects.create(name="Electronics", description="Phones, laptops")
        self.cat2 = ItemCategory.objects.create(name="LargeItems", description="Big stuff")

        self.url = reverse('offer-create')  # 'create_offer/'

    def test_multi_category_offer_creation(self):
        payload = {
            "flight_number": "FL123",
            "from_airport_id": self.airport_jfk.id,
            "to_airport_id": self.airport_lax.id,
            "departure_datetime": (timezone.now() + timedelta(days=2)).isoformat(),
            "arrival_datetime": (timezone.now() + timedelta(days=2, hours=5)).isoformat(),
            "flight_details": "Testing flight details",
            "publisher": "airline",

            "category_ids": [self.cat1.id, self.cat2.id],
            "allow_fragile": True,  # This should automatically add or create a "Fragile" category
            "available_dimensions": "100x50x50",
            "available_weight": "25.00",
            "available_space": "2.0",
            "price": "150.00",
            "notes": "Handle with care, multi-cat test"
        }

        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED, response.data)
        self.assertIn("offer_id", response.data)
        offer_id = response.data["offer_id"]

        offer = Offer.objects.get(pk=offer_id)
        # Check categories
        cat_names = set(offer.categories.values_list('name', flat=True))
        self.assertTrue("Electronics" in cat_names)
        self.assertTrue("LargeItems" in cat_names)
        # If you auto-add "Fragile" category, check that
        self.assertTrue("Fragile" in cat_names)

    def test_invalid_categories(self):
        # One valid, one invalid
        payload = {
            "flight_number": "FL123",
            "from_airport_id": self.airport_jfk.id,
            "to_airport_id": self.airport_lax.id,
            "departure_datetime": (timezone.now() + timedelta(days=2)).isoformat(),
            "arrival_datetime": (timezone.now() + timedelta(days=2, hours=5)).isoformat(),
            "available_weight": "20.00",
            "available_space": "1.0",
            "price": "99.99",
            "category_ids": [self.cat1.id, 9999]  # 9999 doesn't exist
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('category_ids', response.data)


    def test_no_categories_but_fragile(self):
        payload = {
            "flight_number": "FL123",
            "from_airport_id": self.airport_jfk.id,
            "to_airport_id": self.airport_lax.id,
            "departure_datetime": (timezone.now() + timedelta(days=2)).isoformat(),
            "arrival_datetime": (timezone.now() + timedelta(days=2, hours=5)).isoformat(),
            "available_weight": "10.00",
            "available_space": "0.5",
            "price": "50.00",
            "allow_fragile": True
        }
        response = self.client.post(self.url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        offer_id = response.data["offer_id"]
        offer = Offer.objects.get(pk=offer_id)
        cat_names = set(offer.categories.values_list('name', flat=True))
        self.assertIn("Fragile", cat_names)  # auto-added