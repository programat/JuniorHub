from django.db import models
from django.contrib.auth.models import User


class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    company = models.CharField(max_length=255)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    source = models.CharField(max_length=50)


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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
