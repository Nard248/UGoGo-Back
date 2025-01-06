# locations/tests.py

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Country, City, Airport, CityPolicy
from users.models import Users


class LocationAPITestCase(APITestCase):
    def setUp(self):
        # Create a test user
        self.user = Users.objects.create_user(
            email='testuser@example.com',
            password='testpassword',
            first_name='Test',
            last_name='User'
        )

        # Obtain JWT token
        token_url = reverse('token_obtain_pair')  # Ensure this name matches your URLs
        response = self.client.post(token_url, {
            'email': 'testuser@example.com',
            'password': 'testpassword'
        }, format='json')

        # Extract tokens
        self.assertEqual(response.status_code, status.HTTP_200_OK, "Token obtain failed during setup.")
        self.access_token = response.data['access']
        self.refresh_token = response.data['refresh']

        # Set Authorization header for future requests
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        # Initial data for Country
        self.country_data = {
            'country_code': 'US',
            'country_abbr': 'USA',
            'country_name': 'United States'
        }
        self.country = Country.objects.create(**self.country_data)

        # Initial data for City
        self.city_data = {
            'country': self.country,
            'city_code': 'NYC',
            'city_abbr': 'NY',
            'city_name': 'New York',
            'timezone': 'America/New_York'
        }
        self.city = City.objects.create(**self.city_data)

        # Initial data for Airport
        self.airport_data = {
            'city': self.city,
            'airport_code': 'JFK',
            'airport_name': 'John F. Kennedy International Airport'
        }
        self.airport = Airport.objects.create(**self.airport_data)

        # Initial data for CityPolicy
        self.policy_data = {
            'city': self.city,
            'policy_type': 'allowed_categories',
            'policy_status': 'active',
            'policy_description': 'Allowed categories include electronics and clothing.'
        }
        self.city_policy = CityPolicy.objects.create(**self.policy_data)


class CountryTests(LocationAPITestCase):

    def test_create_country(self):
        url = reverse('country-list-create')
        data = {
            'country_code': 'CA',
            'country_abbr': 'CAN',
            'country_name': 'Canada'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Country.objects.count(), 2)
        self.assertEqual(Country.objects.get(id=response.data['id']).country_name, 'Canada')

    def test_create_country_duplicate_code(self):
        url = reverse('country-list-create')
        data = {
            'country_code': 'US',  # Duplicate code
            'country_abbr': 'USA2',
            'country_name': 'United States of America'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('country_code', response.data)

    def test_list_countries(self):
        url = reverse('country-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_country(self):
        url = reverse('country-detail', kwargs={'pk': self.country.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['country_name'], 'United States')

    def test_update_country(self):
        url = reverse('country-detail', kwargs={'pk': self.country.id})
        data = {
            'country_code': 'US',
            'country_abbr': 'USA',
            'country_name': 'USA'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.country.refresh_from_db()
        self.assertEqual(self.country.country_name, 'USA')

    def test_partial_update_country(self):
        url = reverse('country-detail', kwargs={'pk': self.country.id})
        data = {
            'country_name': 'United States of America'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.country.refresh_from_db()
        self.assertEqual(self.country.country_name, 'United States of America')

    def test_delete_country(self):
        url = reverse('country-detail', kwargs={'pk': self.country.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Country.objects.count(), 0)


class CityTests(LocationAPITestCase):

    def test_create_city(self):
        url = reverse('city-list-create')
        data = {
            'country_id': self.country.id,
            'city_code': 'LA',
            'city_abbr': 'LA',
            'city_name': 'Los Angeles',
            'timezone': 'America/Los_Angeles'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(City.objects.count(), 2)
        self.assertEqual(City.objects.get(id=response.data['id']).city_name, 'Los Angeles')

    def test_create_city_duplicate_name(self):
        url = reverse('city-list-create')
        data = {
            'country_id': self.country.id,
            'city_code': 'NYC2',
            'city_abbr': 'NY2',
            'city_name': 'New York',  # Duplicate name
            'timezone': 'America/New_York'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('city_name', response.data)

    def test_list_cities(self):
        url = reverse('city-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_city(self):
        url = reverse('city-detail', kwargs={'pk': self.city.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['city_name'], 'New York')

    def test_update_city(self):
        url = reverse('city-detail', kwargs={'pk': self.city.id})
        data = {
            'country_id': self.country.id,
            'city_code': 'NYC',
            'city_abbr': 'NY',
            'city_name': 'NYC',
            'timezone': 'America/New_York'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.city.refresh_from_db()
        self.assertEqual(self.city.city_name, 'NYC')

    def test_partial_update_city(self):
        url = reverse('city-detail', kwargs={'pk': self.city.id})
        data = {
            'timezone': 'America/Chicago'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.city.refresh_from_db()
        self.assertEqual(self.city.timezone, 'America/Chicago')

    def test_delete_city(self):
        url = reverse('city-detail', kwargs={'pk': self.city.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(City.objects.count(), 0)


class AirportTests(LocationAPITestCase):

    def test_create_airport(self):
        url = reverse('airport-list-create')
        data = {
            'city_id': self.city.id,
            'airport_code': 'LAX',
            'airport_name': 'Los Angeles International Airport'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Airport.objects.count(), 2)
        self.assertEqual(Airport.objects.get(id=response.data['id']).airport_name, 'Los Angeles International Airport')

    def test_create_airport_duplicate_code(self):
        url = reverse('airport-list-create')
        data = {
            'city_id': self.city.id,
            'airport_code': 'JFK',  # Duplicate code
            'airport_name': 'New JFK Airport'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('airport_code', response.data)

    def test_list_airports(self):
        url = reverse('airport-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_airport(self):
        url = reverse('airport-detail', kwargs={'pk': self.airport.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['airport_name'], 'John F. Kennedy International Airport')

    def test_update_airport(self):
        url = reverse('airport-detail', kwargs={'pk': self.airport.id})
        data = {
            'city_id': self.city.id,
            'airport_code': 'JFK',
            'airport_name': 'JFK Airport'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.airport.refresh_from_db()
        self.assertEqual(self.airport.airport_name, 'JFK Airport')

    def test_partial_update_airport(self):
        url = reverse('airport-detail', kwargs={'pk': self.airport.id})
        data = {
            'airport_name': 'JFK Intl Airport'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.airport.refresh_from_db()
        self.assertEqual(self.airport.airport_name, 'JFK Intl Airport')

    def test_delete_airport(self):
        url = reverse('airport-detail', kwargs={'pk': self.airport.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Airport.objects.count(), 0)


class CityPolicyTests(LocationAPITestCase):

    def test_create_city_policy(self):
        url = reverse('citypolicy-list-create')
        data = {
            'city_id': self.city.id,
            'policy_type': 'restricted_items',
            'policy_status': 'active',
            'policy_description': 'Restricted items include weapons and flammable materials.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CityPolicy.objects.count(), 2)
        self.assertEqual(CityPolicy.objects.get(id=response.data['id']).policy_type, 'restricted_items')

    def test_create_city_policy_invalid_type(self):
        url = reverse('citypolicy-list-create')
        data = {
            'city_id': self.city.id,
            'policy_type': 'invalid_type',  # Invalid choice
            'policy_status': 'active',
            'policy_description': 'Invalid policy type.'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('policy_type', response.data)

    def test_list_city_policies(self):
        url = reverse('citypolicy-list-create')
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_retrieve_city_policy(self):
        url = reverse('citypolicy-detail', kwargs={'pk': self.city_policy.id})
        response = self.client.get(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['policy_type'], 'allowed_categories')

    def test_update_city_policy(self):
        url = reverse('citypolicy-detail', kwargs={'pk': self.city_policy.id})
        data = {
            'city_id': self.city.id,
            'policy_type': 'allowed_categories',
            'policy_status': 'inactive',
            'policy_description': 'Updated policy description.'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.city_policy.refresh_from_db()
        self.assertEqual(self.city_policy.policy_status, 'inactive')

    def test_partial_update_city_policy(self):
        url = reverse('citypolicy-detail', kwargs={'pk': self.city_policy.id})
        data = {
            'policy_status': 'inactive'
        }
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.city_policy.refresh_from_db()
        self.assertEqual(self.city_policy.policy_status, 'inactive')

    def test_delete_city_policy(self):
        url = reverse('citypolicy-detail', kwargs={'pk': self.city_policy.id})
        response = self.client.delete(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(CityPolicy.objects.count(), 0)
