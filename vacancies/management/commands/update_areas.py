from django.core.management.base import BaseCommand
from vacancies.models import Area
from vacancies.hhapi import HhApiClient


class Command(BaseCommand):
    help = 'Updates areas from HH.ru API'

    def handle(self, *args, **options):
        api_client = HhApiClient()
        areas_data = api_client.get_areas()

        def create_areas(areas, parent=None):
            for area_data in areas:
                area, created = Area.objects.get_or_create(code=area_data['id'],
                                                           defaults={'name': area_data['name'], 'parent': parent})
                create_areas(area_data.get('areas', []), parent=area)

        create_areas(areas_data)

        self.stdout.write(self.style.SUCCESS('Areas updated successfully'))