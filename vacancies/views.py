import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from .models import Vacancy, VacancyDetail, Bookmark
from .hhapi import HhApiClient


def index(request):
    return render(request, 'vacancies/index.html')


def search_vacancies(request):
    if request.method == 'POST':
        query = request.POST.get('query', '')
        area_name = request.POST.get('area')
        experience = request.POST.get('experience')

        # Формируем параметры для запроса
        params = {
            'page': 0,
            'per_page': 100
        }
        if query:
            params['text'] = query
        if area_name:
            if not area_name.isdigit():
                api_client = HhApiClient()
                area_id = api_client.find_area(area_name)
                if area_id:
                    params['area'] = area_id
            else:
                params['area'] = area_name
        if experience:
            params['experience'] = experience

        # Выполняем поиск вакансий через API HH.ru
        api_client = HhApiClient()
        try:
            vacancies = api_client.search_vacancies(**params)
        except requests.exceptions.HTTPError as e:
            return HttpResponse(f'Error: {e}', status=400)

        # Передаем вакансии в шаблон для отображения
        context = {'vacancies': vacancies['items']}
        return render(request, 'vacancies/search_results.html', context)

    return render(request, 'vacancies/search_form.html')


def add_to_bookmarks(request, vacancy_id):
    api_client = HhApiClient()
    vacancy_data = api_client.get_vacancy(vacancy_id)

    if request.method == 'POST':
        # Временно используем фиксированный id пользователя
        user_id = 1

        # Сохраняем информацию о вакансии в базу данных
        vacancy, created = Vacancy.objects.get_or_create(
            url=vacancy_data['alternate_url'],
            defaults={
                'title': vacancy_data['name'],
                'description': vacancy_data.get('description', ''),
                'company': vacancy_data['employer']['name'],
                'source': 'hh.ru'
            }
        )
        if created:
            # Сохраняем дополнительную информацию о вакансии
            salary = vacancy_data.get('salary', {})
            salary_from = salary.get('from')
            salary_to = salary.get('to')
            currency = salary.get('currency')

            area = vacancy_data.get('area', {})
            city = area.get('name', '')

            experience = vacancy_data.get('experience', {})
            experience_name = experience.get('name', '')

            employment = vacancy_data.get('employment', {})
            employment_type = employment.get('name', '')

            schedule = vacancy_data.get('schedule', {})
            schedule_name = schedule.get('name', '')

            key_skills = vacancy_data.get('key_skills', [])
            skills = ', '.join(skill.get('name', '') for skill in key_skills)

            VacancyDetail.objects.create(
                vacancy=vacancy,
                salary_from=salary_from,
                salary_to=salary_to,
                currency=currency,
                city=city,
                experience=experience_name,
                employment_type=employment_type,
                schedule=schedule_name,
                skills=skills,
                source_id=vacancy_data.get('id')
            )

        # Проверяем, есть ли уже эта вакансия в закладках у пользователя
        bookmark, created = Bookmark.objects.get_or_create(user_id=user_id, vacancy=vacancy)

        return redirect('bookmarks')

    return redirect('vacancy_detail', vacancy_id=vacancy_id)


def vacancy_detail(request, vacancy_id):
    api_client = HhApiClient()
    vacancy = api_client.get_vacancy(vacancy_id)
    return render(request, 'vacancies/vacancy_detail.html', {'vacancy': vacancy})


# @login_required
def bookmarks(request):
    # Временно используем фиксированный id пользователя
    user_id = 1
    bookmarks = Bookmark.objects.filter(user_id=user_id)
    return render(request, 'vacancies/bookmarks.html', {'bookmarks': bookmarks})
