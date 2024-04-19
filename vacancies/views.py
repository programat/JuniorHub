import requests
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from .models import Vacancy, VacancyDetail, Bookmark
from .hhapi import HhApiClient


def index(request):
    return render(request, 'vacancies/index.html')


def search_vacancies(request):
    if request.method == 'POST' or request.GET:
        query = request.POST.get('query', '')
        area_name = request.POST.get('area')
        experience = request.POST.get('experience')

        page = int(request.GET.get('page', 1))
        per_page = 20

        params = {
            'page': page,
            'per_page': per_page
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
        text = params.pop('text', '')
        try:
            vacancies = api_client.search_vacancies(text, **params)
        except requests.exceptions.HTTPError as e:
            return HttpResponse(f'Error: {e}', status=400)

        total_pages = vacancies['pages']
        page_range = range(1, total_pages + 1)

        if total_pages > 7:
            if page <= 4:
                page_range = range(1, 6)
            elif page >= total_pages - 3:
                page_range = range(total_pages - 4, total_pages + 1)
            else:
                page_range = range(page - 2, page + 3)

        context = {
            'vacancies': vacancies['items'],
            'page': page,
            'total_pages': total_pages,
            'page_range': page_range,
            'per_page': per_page
        }
        return render(request, 'vacancies/search_results.html', context)

    return render(request, 'vacancies/search_form.html')


def add_to_bookmarks(request, vacancy_id):
    api_client = HhApiClient()
    vacancy_data = api_client.get_vacancy(vacancy_id)

    if request.method == 'POST':
        user = request.user

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
            # Попытка сохранить детали вакансии (перешел к другому варианту)
            # salary_from = vacancy_data.get('salary', {}).get('from', None),
            # salary_to = vacancy_data.get('salary', {}).get('to', None),
            # currency = vacancy_data.get('salary', {}).get('currency', ''),

            # Сохраняем дополнительную информацию о вакансии
            salary = vacancy_data.get('salary', {})
            print(salary)
            if salary is not None:
                salary_from = salary.get('from', '')
                salary_to = salary.get('to', '')
                currency = salary.get('currency', '')
            else:
                salary_from = None
                salary_to = None
                currency = ''

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
        bookmark, created = Bookmark.objects.get_or_create(user=user, vacancy=vacancy)

        return redirect('bookmarks')

    return redirect('vacancy_detail', vacancy_id=vacancy_id)


def vacancy_detail(request, vacancy_id):
    api_client = HhApiClient()
    vacancy = api_client.get_vacancy(vacancy_id)
    return render(request, 'vacancies/vacancy_detail.html', {'vacancy': vacancy})


def bookmark_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy.objects.prefetch_related('details'), pk=vacancy_id)
    return render(request, 'vacancies/bookmark_detail.html', {'vacancy': vacancy})


def update_bookmarks(request):
    api_client = HhApiClient()
    for vacancy in Vacancy.objects.all():
        vacancy_id = vacancy.url.split('/')[-1]
        vacancy_data = api_client.get_vacancy(vacancy_id)

        vacancy.title = vacancy_data['name']
        vacancy.company = vacancy_data['employer']['name']
        vacancy.description = vacancy_data['description']
        vacancy.save()

        # Получаем или создаем объект VacancyDetail, связанный с текущей вакансией
        vacancy_detail, created = VacancyDetail.objects.get_or_create(vacancy=vacancy)

        salary = vacancy_data.get('salary')
        vacancy_detail.city = vacancy_data.get('area', {}).get('name', '')
        vacancy_detail.salary_from = salary['from'] if salary else None
        vacancy_detail.salary_to = salary['to'] if salary else None
        vacancy_detail.currency = salary['currency'] if salary else ''
        vacancy_detail.experience = vacancy_data.get('experience', {}).get('name', '')
        vacancy_detail.employment_type = vacancy_data.get('employment', {}).get('name', '')
        vacancy_detail.schedule = vacancy_data.get('schedule', {}).get('name', '')
        vacancy_detail.skills = ', '.join([skill['name'] for skill in vacancy_data.get('key_skills', [])])
        vacancy_detail.save()

    return redirect('bookmarks')


@login_required
def delete_bookmark(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
    request.user.bookmarks.filter(vacancy=vacancy).delete()
    return redirect('bookmarks')

@login_required
def bookmarks(request):
    bookmarks = request.user.bookmarks.all()
    return render(request, 'vacancies/bookmarks.html', {'bookmarks': bookmarks})
