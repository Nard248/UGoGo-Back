# items/tests.py
from decimal import Decimal

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient, APIRequestFactory
from .models import Item
from .models.request import Request
from offers.models import Flight, UserFlight, Offer
from users.models import Users
from locations.models import Country, City, Airport
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from datetime import timedelta
from .serializers import RequestSerializer, ItemSerializer
from django.test import RequestFactory


class ItemsAPITestCase(APITestCase):
    def setUp(self):
        # Initialize the API client and request factory
        self.client = APIClient()
        self.factory = RequestFactory()

        # Create test users
        self.sender = Users.objects.create_user(
            email='sender@example.com',
            password='senderpassword',
            first_name='Sender',
            last_name='Example'
        )
        self.courier = Users.objects.create_user(
            email='courier@example.com',
            password='courierpassword',
            first_name='Courier',
            last_name='Example'
        )

        # Obtain JWT tokens for authentication
        self.sender_refresh = RefreshToken.for_user(self.sender)
        self.sender_access = str(self.sender_refresh.access_token)

        self.courier_refresh = RefreshToken.for_user(self.courier)
        self.courier_access = str(self.courier_refresh.access_token)

        # Create Country
        self.country = Country.objects.create(
            country_code='AM',
            country_abbr='ARM',
            country_name='Armenia'
        )

        # Create City
        self.city = City.objects.create(
            country=self.country,
            city_code='YE',
            city_abbr='YE',
            city_name='Yerevan',
            timezone='Asia/Yerevan'
        )

        # Create Airports
        self.airport_origin = Airport.objects.create(
            city=self.city,
            airport_code='EVN',
            airport_name='Zvartnots International Airport'
        )
        self.airport_destination = Airport.objects.create(
            city=self.city,
            airport_code='LDN',
            airport_name='London International Airport'
        )

        # Create Flight
        self.flight = Flight.objects.create(
            publisher='airline',
            from_airport=self.airport_origin,
            to_airport=self.airport_destination,
            departure_datetime=timezone.now() + timedelta(days=1),
            arrival_datetime=timezone.now() + timedelta(days=1, hours=5)
        )

        # Create UserFlight
        self.user_flight = UserFlight.objects.create(
            flight=self.flight,
            user=self.courier  # Courier owns the flight
        )

        # Create Offer
        self.offer = Offer.objects.create(
            user_flight=self.user_flight,
            courier=self.courier,
            status='available',
            price=150.00,  # Consider using Decimal for price fields
            available_weight=2.5,  # in kilograms
            available_space=5000.0,  # in cubic centimeters (e.g., 100000 cm³ = 100 liters)
            notes='No fragile items.'
        )

        # Create an Item owned by the sender
        self.item = Item.objects.create(
            user=self.sender,
            name='Laptop',
            description='A 15-inch laptop with accessories.',
            weight=3.5,
            dimensions='40x30x5'  # cm
        )

        # Create a Request linked to the item and offer
        self.request = Request.objects.create(
            item=self.item,
            offer=self.offer,
            user=self.sender,
            suggested_price=100.00,
            status='pending',
            comments='Handle with care.'
        )

    # -------------------------------
    # Item Tests
    # -------------------------------

    def test_list_items_authenticated_user(self):
        """
        Test that an authenticated user can list their own items.
        """
        url = reverse('item-list-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Assuming pagination is enabled, access 'results'
        self.assertEqual(len(response.data.get('results', [])), 1)
        item = response.data['results'][0]
        self.assertEqual(item['name'], 'Laptop')

    def test_list_items_unauthenticated_user(self):
        """
        Test that unauthenticated users cannot list items.
        """
        url = reverse('item-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_item_authenticated_user(self):
        """
        Test that an authenticated user can create an item.
        """
        url = reverse('item-list-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'name': 'Smartphone',
            'description': 'Latest model smartphone.',
            'weight': 0.2,
            'dimensions': '15x7x0.8'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Item.objects.count(), 2)
        new_item = Item.objects.get(id=response.data['id'])
        self.assertEqual(new_item.name, 'Smartphone')
        self.assertEqual(new_item.user, self.sender)

    def test_create_item_invalid_data(self):
        """
        Test creating an item with invalid data.
        """
        url = reverse('item-list-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'name': '',
            'description': 'No name provided.',
            'weight': -1.0,
            'dimensions': 'invalid-format'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('name', response.data)
        self.assertIn('weight', response.data)
        self.assertIn('dimensions', response.data)

    def test_delete_item_owner(self):
        """
        Test that the owner can delete their own item.
        """
        url = reverse('item-destroy', kwargs={'pk': self.item.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Item.objects.count(), 0)

    def test_delete_item_not_owner(self):
        """
        Test that a user cannot delete someone else's item.
        """
        # Create another item owned by the courier
        other_item = Item.objects.create(
            user=self.courier,
            name='Tablet',
            description='A 10-inch tablet.',
            weight=0.5,
            dimensions='25x15x0.7'
        )
        url = reverse('item-destroy', kwargs={'pk': other_item.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # -------------------------------
    # Request Tests
    # -------------------------------

    def test_create_request_authenticated_sender(self):
        """
        Test that an authenticated sender can create a request.
        """
        url = reverse('request-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'item_id': self.item.id,  # Added item_id
            'offer_id': self.offer.id,  # Added offer_id
            'suggested_price': 120.00,
            'comments': 'Urgent delivery.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)  # Test should pass now
        self.assertEqual(Request.objects.count(), 2)
        new_request = Request.objects.get(id=response.data['id'])
        self.assertEqual(new_request.suggested_price, 120.00)
        self.assertEqual(new_request.user, self.sender)
        self.assertEqual(new_request.status, 'pending')

    def test_create_request_valid_data(self):
        """
        Test that an authenticated sender can create a request with valid data.
        """
        url = reverse('request-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'item_id': self.item.id,  # Added item_id
            'offer_id': self.offer.id,  # Added offer_id
            'suggested_price': 120.00,
            'comments': 'Urgent delivery.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) # Test should pass now
        self.assertEqual(Request.objects.count(), 2)
        new_request = Request.objects.get(id=response.data['id'])
        self.assertEqual(new_request.suggested_price, 120.00)
        self.assertEqual(new_request.user, self.sender)
        self.assertEqual(new_request.status, 'pending')


    def test_create_request_unauthenticated_sender(self):
        """
        Test that unauthenticated users cannot create requests.
        """
        url = reverse('request-create')
        data = {
            'item_id': self.item.id,
            'offer_id': self.offer.id,
            'suggested_price': 120.00,
            'comments': 'Urgent delivery.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_request_invalid_offer(self):
        """
        Test creating a request with a non-existent or unavailable offer.
        """
        url = reverse('request-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'item_id': self.item.id,
            'offer_id': 999,  # Assuming this offer does not exist
            'suggested_price': 120.00,
            'comments': 'Urgent delivery.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('offer_id', response.data)

    def test_create_request_invalid_offer_status(self):
        """
        Test that the RequestSerializer rejects requests with offers that are not available.
        """
        # Change offer status to 'unavailable'
        self.offer.status = 'unavailable'
        self.offer.save()
        url = reverse('request-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'item_id': self.item.id,
            'offer_id': self.offer.id,
            'suggested_price': 120.00,
            'comments': 'Offer is unavailable.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('offer_id', response.data)

    def test_create_request_item_not_owned(self):
        """
        Test that a user cannot create a request for an item they do not own.
        """
        # Create an item owned by the courier
        other_item = Item.objects.create(
            user=self.courier,
            name='Headphones',
            description='Noise-cancelling headphones.',
            weight=0.3,
            dimensions='20x15x5'
        )
        url = reverse('request-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'item_id': other_item.id,  # Item not owned by the sender
            'offer_id': self.offer.id,
            'suggested_price': 80.00,
            'comments': 'Handle with care.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', response.data)

    def test_create_request_without_comments(self):
        """
        Test creating a request without providing comments.
        """
        url = reverse('request-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'item_id': self.item.id,
            'offer_id': self.offer.id,
            'suggested_price': 90.00,
            # 'comments' is omitted
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Request.objects.count(), 2)
        new_request = Request.objects.get(id=response.data['id'])
        self.assertEqual(new_request.comments, '')  # Assuming blank comments are allowed

    def test_create_request_zero_suggested_price(self):
        """
        Test creating a request with a suggested price of zero.
        """
        url = reverse('request-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'item_id': self.item.id,
            'offer_id': self.offer.id,
            'suggested_price': 0.00,
            'comments': 'Zero price test.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('suggested_price', response.data)

    def test_create_request_negative_suggested_price(self):
        """
        Test creating a request with a negative suggested price.
        """
        url = reverse('request-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'item_id': self.item.id,
            'offer_id': self.offer.id,
            'suggested_price': -50.00,
            'comments': 'Negative price test.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('suggested_price', response.data)

    def test_create_request_with_invalid_dimensions(self):
        """
        Test that the RequestSerializer raises an error for invalid item dimensions.
        """
        invalid_item = Item.objects.create(
            user=self.sender,
            name='Box',
            description='A large box.',
            weight=10.0,
            dimensions='invalid_dimensions'
        )
        url = reverse('request-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'item_id': invalid_item.id,
            'offer_id': self.offer.id,
            'suggested_price': 50.00,
            'comments': 'Handle with care.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dimensions', response.data) # Changed from non_field_errors

    def test_create_request_exceeds_weight_capacity(self):
        """
        Test creating a request that exceeds the offer's available weight.
        """
        # Set available_weight to 4.0 (existing request uses 3.5)
        self.offer.available_weight = 4.0
        self.offer.save()

        # Create a new item that would exceed the weight
        heavy_item = Item.objects.create(
            user=self.sender,
            name='Heavy Equipment',
            description='A very heavy item.',
            weight=2.0,  # Total weight would be 3.5 + 2.0 = 5.5 > 4.0
            dimensions='50x40x10'
        )

        url = reverse('request-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'item_id': heavy_item.id,
            'offer_id': self.offer.id,
            'suggested_price': 200.00,
            'comments': 'This should exceed weight capacity.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('weight', response.data)
        self.assertEqual(Request.objects.count(), 1)  # No new request created

    def test_create_request_exceeds_space_capacity(self):
        """
        Test creating a request that exceeds the offer's available space.
        """
        # Set available_space to 6000.0 (existing request uses 40x30x5=6000 cm³)
        self.offer.available_space = 6000.0
        self.offer.save()

        # Create a new item that would exceed the space
        large_item = Item.objects.create(
            user=self.sender,
            name='Large Box',
            description='A very large item.',
            weight=2.0,
            dimensions='100x100x100'  # Volume = 1,000,000 cm³
        )

        url = reverse('request-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'item_id': large_item.id,
            'offer_id': self.offer.id,
            'suggested_price': 500.00,
            'comments': 'This should exceed space capacity.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dimensions', response.data)
        self.assertEqual(Request.objects.count(), 1)  # No new request created

    def test_create_request_exact_capacity_weight(self):
        """
        Test creating a request that exactly matches the offer's available weight.
        """
        # Update offer
        self.offer.available_weight = self.item.weight
        self.offer.available_space = Decimal('6000') # Exact space needed
        self.offer.save()

        url = reverse('request-create')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'item_id': self.item.id,
            'offer_id': self.offer.id,
            'suggested_price': 100.00,
            'comments': 'Exact weight test.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED) # Test should pass now
        self.assertEqual(Request.objects.count(), 2)
        new_request = Request.objects.get(id=response.data['id'])
        self.assertEqual(new_request.status, 'pending')

    def test_update_request_status_as_courier(self):
        """
        Test that the courier can update the status of a request.
        """
        url = reverse('request-update-status', kwargs={'pk': self.request.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.courier_access)
        data = {
            'status': 'accepted'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'accepted')


    def test_update_request_status_as_non_courier(self):
        """
        Test that a user who is not the courier cannot update the request status.
        """
        url = reverse('request-update-status', kwargs={'pk': self.request.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        data = {
            'status': 'accepted'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'pending')  # Status remains unchanged

    def test_update_request_status_to_invalid_value(self):
        """
        Test updating a request status to an invalid value.
        """
        url = reverse('request-update-status', kwargs={'pk': self.request.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.courier_access)  # Update credentials
        data = {
            'status': 'invalid_status',
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('status', response.data)  # Check for 'status' key
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'pending')  # Status remains unchanged

    def test_update_request_status_to_accepted(self):
        """
        Test updating a request status to 'accepted'.
        """
        url = reverse('request-update-status', kwargs={'pk': self.request.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.courier_access)
        data = {
            'status': 'accepted'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.request.refresh_from_db()
        self.assertEqual(self.request.status, 'accepted')

    def test_update_request_status_as_unauthenticated_user(self):
        """
        Test that unauthenticated users cannot update the request status.
        """
        url = reverse('request-update-status', kwargs={'pk': self.request.id})
        self.client.credentials()  # Remove authentication
        data = {
            'status': 'accepted'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_request_owner(self):
        """
        Test that the owner can delete their own request.
        """
        url = reverse('request-destroy', kwargs={'pk': self.request.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Request.objects.count(), 0)

    def test_delete_request_not_owner(self):
        """
        Test that a user cannot delete someone else's request.
        """
        # Create a request by another sender
        other_sender = Users.objects.create_user(
            email='othersender@example.com',
            password='otherpassword',
            first_name='Other',
            last_name='Sender'
        )
        other_item = Item.objects.create(
            user=other_sender,
            name='Camera',
            description='Digital SLR camera.',
            weight=1.0,
            dimensions='25x20x15'
        )
        other_request = Request.objects.create(
            item=other_item,
            offer=self.offer,
            user=other_sender,
            suggested_price=200.00,
            status='pending',
            comments='Please deliver safely.'
        )

        url = reverse('request-destroy', kwargs={'pk': other_request.id})
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.sender_access)
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_request_as_unauthenticated_user(self):
        """
        Test that unauthenticated users cannot delete requests.
        """
        url = reverse('request-destroy', kwargs={'pk': self.request.id})
        self.client.credentials()  # Remove authentication
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SerializerTests(APITestCase):
    def setUp(self):
        # Initialize the request factory
        self.factory = APIRequestFactory()

        # Create test user
        self.sender = Users.objects.create_user(
            email='sender@example.com',
            password='senderpassword',
            first_name='Sender',
            last_name='Example'
        )

        # Create Country
        self.country = Country.objects.create(
            country_code='AM',
            country_abbr='ARM',
            country_name='Armenia'
        )

        # Create City
        self.city = City.objects.create(
            country=self.country,
            city_code='YE',
            city_abbr='YE',
            city_name='Yerevan',
            timezone='Asia/Yerevan'
        )

        # Create Airports
        self.airport_origin = Airport.objects.create(
            city=self.city,
            airport_code='EVN',
            airport_name='Zvartnots International Airport'
        )
        self.airport_destination = Airport.objects.create(
            city=self.city,
            airport_code='LDN',
            airport_name='London International Airport'
        )

        # Create Flight
        self.flight = Flight.objects.create(
            publisher='airline',
            from_airport=self.airport_origin,
            to_airport=self.airport_destination,
            departure_datetime=timezone.now() + timedelta(days=1),
            arrival_datetime=timezone.now() + timedelta(days=1, hours=5)
        )

        # Create UserFlight
        self.user_flight = UserFlight.objects.create(
            flight=self.flight,
            user=self.sender
        )

        # Create Offer
        self.offer = Offer.objects.create(
            user_flight=self.user_flight,
            courier=self.sender,
            status='available',
            price=150.00,
            available_weight=50.0,
            available_space=100000.0,
            notes='No fragile items.'
        )

        # Create an Item owned by the sender
        self.item = Item.objects.create(
            user=self.sender,
            name='Laptop',
            description='A 15-inch laptop with accessories.',
            weight=3.5,
            dimensions='40x30x5'
        )

        # Create a dummy request for serializer context
        self.dummy_request = self.factory.post('/dummy-url/')
        self.dummy_request.user = self.sender

    # -------------------------------
    # Serializer Tests
    # -------------------------------

    def test_item_serializer_valid_data(self):
        """
        Test that the ItemSerializer validates correct data.
        """
        data = {
            'name': 'Smartphone',
            'description': 'Latest model smartphone.',
            'weight': 0.2,
            'dimensions': '15x7x0.8'
        }
        serializer = ItemSerializer(data=data, context={'request': self.dummy_request})
        self.assertTrue(serializer.is_valid())
        item = serializer.save()
        self.assertEqual(item.name, 'Smartphone')

    def test_item_serializer_invalid_weight(self):
        """
        Test that the ItemSerializer rejects non-positive weight.
        """
        data = {
            'name': 'Smartphone',
            'description': 'Latest model smartphone.',
            'weight': -0.5,
            'dimensions': '15x7x0.8'
        }
        serializer = ItemSerializer(data=data, context={'request': self.dummy_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('weight', serializer.errors)

    def test_item_serializer_invalid_dimensions(self):
        """
        Test that the ItemSerializer rejects invalid dimensions format.
        """
        data = {
            'name': 'Smartphone',
            'description': 'Latest model smartphone.',
            'weight': 0.2,
            'dimensions': '15-7-0.8'  # Invalid separator
        }
        serializer = ItemSerializer(data=data, context={'request': self.dummy_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('dimensions', serializer.errors)

    def test_request_serializer_valid_data(self):
        """
        Test that the RequestSerializer validates correct data.
        """
        data = {
            'item_id': self.item.id,
            'offer_id': self.offer.id,
            'suggested_price': 100.00,
            'comments': 'Handle with care.'
        }
        serializer = RequestSerializer(data=data, context={'request': self.dummy_request})
        self.assertTrue(serializer.is_valid())
        request_instance = serializer.save()
        self.assertEqual(request_instance.suggested_price, 100.00)
        self.assertEqual(request_instance.user, self.sender)

    def test_request_serializer_invalid_item_user(self):
        """
        Test that the RequestSerializer rejects requests where the item does not belong to the user.
        """
        other_user = Users.objects.create_user(
            email='other@example.com',
            password='otherpassword',
            first_name='Other',
            last_name='User'
        )
        other_item = Item.objects.create(
            user=other_user,
            name='Tablet',
            description='A 10-inch tablet.',
            weight=0.5,
            dimensions='25x15x0.7'
        )
        data = {
            'item_id': other_item.id,
            'offer_id': self.offer.id,
            'suggested_price': 80.00,
            'comments': "Attempting to request someone else's item."
        }
        serializer = RequestSerializer(data=data, context={'request': self.dummy_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('non_field_errors', serializer.errors)  # Expect 'non_field_errors'

    def test_request_serializer_invalid_offer_status(self):
        """
        Test that the RequestSerializer rejects requests with offers that are not available.
        """
        # Change offer status to 'unavailable'
        self.offer.status = 'unavailable'
        self.offer.save()
        data = {
            'item_id': self.item.id,
            'offer_id': self.offer.id,
            'suggested_price': 100.00,
            'comments': 'Offer is unavailable.'
        }
        serializer = RequestSerializer(data=data, context={'request': self.dummy_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('offer_id', serializer.errors)

    def test_request_serializer_exceeds_capacity(self):
        """
        Test that the RequestSerializer rejects requests that exceed offer's capacity.
        """
        # Set offer's available weight and space to be exactly the item's weight and space
        self.offer.available_weight = self.item.weight
        self.offer.available_space = 6000.0  # 40x30x5=6000 cm³
        self.offer.save()

        # Attempt to create another request which would exceed capacity
        new_item = Item.objects.create(
            user=self.sender,
            name='Box',
            description='A large box.',
            weight=1.0,
            dimensions='50x50x50'  # 125000 cm³
        )
        data = {
            'item_id': new_item.id,
            'offer_id': self.offer.id,
            'suggested_price': 150.00,
            'comments': 'Exceeds capacity.'
        }
        serializer = RequestSerializer(data=data, context={'request': self.dummy_request})
        self.assertFalse(serializer.is_valid())
        self.assertTrue('weight' in serializer.errors or 'dimensions' in serializer.errors)  # Check for either error

    def test_request_serializer_missing_fields(self):
        """
        Test that the RequestSerializer rejects requests missing required fields.
        """
        data = {
            # 'item_id' is missing
            'offer_id': self.offer.id,
            'suggested_price': 100.00,
            'comments': 'Missing item field.'
        }
        serializer = RequestSerializer(data=data, context={'request': self.dummy_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('item_id', serializer.errors)

        data = {
            'item_id': self.item.id,
            # 'offer_id' is missing
            'suggested_price': 100.00,
            'comments': 'Missing offer field.'
        }
        serializer = RequestSerializer(data=data, context={'request': self.dummy_request})
        self.assertFalse(serializer.is_valid())
        self.assertIn('offer_id', serializer.errors)
