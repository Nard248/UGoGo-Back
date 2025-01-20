from django.core.management.base import BaseCommand
import csv
from locations.models import Country, City, Airport

class Command(BaseCommand):
    help = "Import airport data from a CSV file"

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        file_path = kwargs['file_path']
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                airport_id, airport_name, city_name, country_name, airport_code, city_code, latitude, longitude, elevation, utc_offset, daylight_saving, timezone, airport_type, source = row

                country, created = Country.objects.get_or_create(
                    country_name=country_name,
                    defaults={
                        'country_code': country_name[:3].upper(),
                        'country_abbr': country_name[:3].upper()
                    }
                )

                city, created = City.objects.get_or_create(
                    city_name=city_name,
                    country=country,
                    defaults={
                        'city_code': city_code if city_code else None,
                        'city_abbr': city_name[:3].upper(),
                        'timezone': timezone,
                    }
                )

                Airport.objects.get_or_create(
                    city=city,
                    airport_code=airport_code,
                    defaults={
                        'airport_name': airport_name,
                    }
                )

        self.stdout.write(self.style.SUCCESS("Data import completed successfully."))