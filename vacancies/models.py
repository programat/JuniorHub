from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import User


class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.CharField(max_length=255)
    url = models.URLField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=50)

    def __str__(self):
        return self.title

    def save_with_details(self, api_client):
        # Сохраняем вакансию
        self.save()

        # Получаем детали вакансии из API
        vacancy_data = api_client.get_vacancy(self.url)

        # Сохраняем детали вакансии
        vacancy_detail, created = VacancyDetail.objects.get_or_create(vacancy=self)
        vacancy_detail.salary_from = vacancy_data['salary']['from']
        vacancy_detail.salary_to = vacancy_data['salary']['to']
        vacancy_detail.currency = vacancy_data['salary']['currency']
        vacancy_detail.city = vacancy_data['area']['name']
        vacancy_detail.experience = vacancy_data['experience']['name']
        vacancy_detail.employment_type = vacancy_data['employment']['name']
        vacancy_detail.schedule = vacancy_data['schedule']['name']
        vacancy_detail.skills = ', '.join(skill['name'] for skill in vacancy_data['key_skills'])
        vacancy_detail.source_id = vacancy_data['id']
        vacancy_detail.save()


class VacancyDetail(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='details')
    salary_from = models.IntegerField(null=True)
    salary_to = models.IntegerField(null=True)
    currency = models.CharField(max_length=10)
    city = models.CharField(max_length=50)
    experience = models.CharField(max_length=50)
    employment_type = models.CharField(max_length=50)
    schedule = models.CharField(max_length=50)
    skills = models.TextField()
    source_id = models.CharField(max_length=50)


class Bookmark(models.Model):
    # user_id = models.IntegerField()
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name='bookmarks')
    # user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.vacancy.title}"


class Area(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=50)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name
