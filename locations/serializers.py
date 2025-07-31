from rest_framework import serializers
from .models import Country, City, Airport, CityPolicy

class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = ['id', 'country_code', 'country_abbr', 'country_name']


class CitySerializer(serializers.ModelSerializer):
    country = CountrySerializer(read_only=True)
    country_id = serializers.PrimaryKeyRelatedField(queryset=Country.objects.all(), source='country', write_only=True)

    class Meta:
        model = City
        fields = ['id', 'country', 'country_id', 'city_code', 'city_abbr', 'city_name', 'timezone']


class AirportSerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), source='city', write_only=True)

    class Meta:
        model = Airport
        fields = ['id', 'city', 'city_id', 'airport_code', 'airport_name', 'airport_picture_url']


class CityPolicySerializer(serializers.ModelSerializer):
    city = CitySerializer(read_only=True)
    city_id = serializers.PrimaryKeyRelatedField(queryset=City.objects.all(), source='city', write_only=True)

    class Meta:
        model = CityPolicy
        fields = ['id', 'city', 'city_id', 'policy_type', 'policy_status', 'policy_description']
