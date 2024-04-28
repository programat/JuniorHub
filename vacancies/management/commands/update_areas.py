from django.core.management.base import BaseCommand
from vacancies.models import Area
from api.api_clients import ApiClientFactory

class Command(BaseCommand):
    help = 'Updates areas from API'

    def handle(self, *args, **options):
        source = options.get('source', 'hh')  # Получаем источник данных из аргументов команды
        api_client = ApiClientFactory.create_api_client(source)

        try:
            areas_data = api_client.get_areas()
        except NotImplementedError:
            self.stdout.write(self.style.WARNING('Получение списка регионов не поддерживается для выбранного API'))
            return

        def create_areas(areas, parent=None):
            for area_data in areas:
                area, created = Area.objects.get_or_create(code=area_data['id'],
                                                           defaults={'name': area_data['name'], 'parent': parent})
                create_areas(area_data.get('areas', []), parent=area)

        create_areas(areas_data)

        self.stdout.write(self.style.SUCCESS('Areas updated successfully'))
