# vacancies/management/commands/delete_unused_vacancies.py
from django.core.management.base import BaseCommand
from vacancies.models import Vacancy, Bookmark


class Command(BaseCommand):
    help = 'Удаляет вакансии, которые не связаны ни с одной закладкой'

    def handle(self, *args, **options):
        # Получаем все вакансии, у которых нет связанных закладок
        unused_vacancies = Vacancy.objects.exclude(id__in=Bookmark.objects.values('vacancy_id'))

        # Удаляем неиспользуемые вакансии
        deleted_count = unused_vacancies.count()
        unused_vacancies.delete()

        self.stdout.write(self.style.SUCCESS(f'Удалено {deleted_count} неиспользуемых вакансий'))
