from django.core.management.base import BaseCommand
from vacancies.models import Vacancy, VacancyDetail
from vacancies.grpc_client import get_internships


class Command(BaseCommand):
    help = 'Populate database with internships from Tinkoff service'

    def handle(self, *args, **options):
        internships = get_internships()
        for category in internships:
            for position in category.positions:
                vacancy, created = Vacancy.objects.update_or_create(
                    url=position.link,
                    defaults={
                        'title': position.title,
                        'description': position.description,
                        'company': 'Тинькофф',
                        'source': 'tinkoff'
                    }
                )
                VacancyDetail.objects.update_or_create(
                    vacancy=vacancy,
                    defaults={
                        'city': position.area,
                        'status': 'active' if position.status == 'Набор открыт' else 'closed'
                    }
                )
        self.stdout.write(self.style.SUCCESS('Successfully populated internships'))
