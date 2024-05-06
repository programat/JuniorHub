from django.core.management.base import BaseCommand

from data_providers.data_provider_services import TinkoffDataProvider
from vacancies.models import Vacancy, VacancyDetail
from vacancies.grpc_client import get_internships


class Command(BaseCommand):
    help = 'Populate database with internships from Tinkoff service'

    def handle(self, *args, **options):
        internships = get_internships()
        data_provider = TinkoffDataProvider()
        data_provider.save_vacancies(internships)
        self.stdout.write(self.style.SUCCESS('Successfully populated internships'))

