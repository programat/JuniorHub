import json

import grpc
import requests
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect

from .grpc_client import get_internships
from .models import Vacancy, VacancyDetail, Bookmark
from data_providers.data_provider_services import DataProviderFactory, HhDataProvider


def index(request):
    return render(request, 'vacancies/index.html')


def page_not_found(request, exception=None):
    return render(request, '404.html', status=404)


# TODO: удалить старый метод old_search_vacancies
def old_search_vacancies(request):
    user = request.user
    query = request.GET.get('query', 'Тинькофф')
    area_name = request.GET.get('area', user.location if user.is_authenticated else '')
    experience = request.GET.get('experience', '')
    sources = request.GET.getlist('source', ['hh', 'tinkoff'])

    page = int(request.GET.get('page', 1))
    per_page = 20

    params = {
        'page': page,
        'per_page': per_page
    }

    vacancies_by_source = {}
    internships = []

    for source in sources:
        api_client = DataProviderFactory.create_data_provider(source)

        if query:
            params['text'] = query
        if area_name:
            if not area_name.isdigit():
                try:
                    area_id = api_client.find_area(area_name)
                    if area_id:
                        params['area'] = area_id
                except NotImplementedError:
                    pass
            else:
                params['area'] = area_name
        if experience:
            params['experience'] = experience

        text = params.pop('text', '')
        try:
            vacancies = api_client.get_vacancies(text, **params)
            vacancies_by_source[source] = vacancies
            if source == 'tinkoff':
                internships = vacancies
        except requests.exceptions.HTTPError as e:
            return HttpResponse(f'Error: {e}', status=400)

    total_pages = max(len(vacancies) // per_page for vacancies in vacancies_by_source.values())
    page_range = range(1, total_pages + 1)

    if total_pages > 7:
        if page <= 4:
            page_range = range(1, 6)
        elif page >= total_pages - 3:
            page_range = range(total_pages - 4, total_pages + 1)
        else:
            page_range = range(page - 2, page + 3)

    context = {
        'vacancies_by_source': vacancies_by_source,
        'internships': internships,
        'page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'per_page': per_page,
        'query': query,
        'area_name': area_name,
        'experience': experience
    }
    return render(request, 'vacancies/search_results.html', context)


def search_vacancies(request):
    user = request.user
    query = request.GET.get('query', 'Тинькофф')
    area_name = request.GET.get('area', user.location if user.is_authenticated else '')
    experience = request.GET.get('experience', '')
    sources = request.GET.getlist('source', ['hh', 'tinkoff'])

    page = int(request.GET.get('page', 1))
    per_page = 20

    params = {
        'page': page,
        'per_page': per_page
    }

    vacancies_by_source = {}
    internships = []

    for source in sources:
        data_provider = DataProviderFactory.create_data_provider(source)

        if query:
            params['text'] = query
        if area_name and isinstance(data_provider, HhDataProvider):
            if not area_name.isdigit():
                try:
                    area_id = data_provider.find_area(area_name)
                    if area_id:
                        params['area'] = area_id
                except NotImplementedError:
                    pass
            else:
                params['area'] = area_name
        if experience:
            params['experience'] = experience

        text = params.pop('text', '')
        try:
            vacancies = data_provider.get_vacancies(text, **params)
            vacancies_by_source[source] = vacancies
            if source == 'tinkoff':
                internships = vacancies
        except requests.exceptions.HTTPError as e:
            return HttpResponse(f'Error: {e}', status=400)

    total_pages = sum(len(vacancies) // per_page for vacancies in vacancies_by_source.values())
    page_range = range(1, total_pages + 1)

    if total_pages > 7:
        if page <= 4:
            page_range = range(1, 6)
        elif page >= total_pages - 3:
            page_range = range(total_pages - 4, total_pages + 1)
        else:
            page_range = range(page - 2, page + 3)

    context = {
        'vacancies_by_source': vacancies_by_source,
        'internships': internships,
        'page': page,
        'total_pages': total_pages,
        'page_range': page_range,
        'per_page': per_page,
        'query': query,
        'area_name': area_name,
        'experience': experience
    }
    return render(request, 'vacancies/search_results.html', context)


# TODO: удалить старый метод old_add_to_bookmarks
def old_add_to_bookmarks(request, vacancy_id):
    source = request.GET.get('source', 'hh')
    api_client = DataProviderFactory.create_api_client(source)
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


def add_to_bookmarks(request, vacancy_id):
    source = request.GET.get('source', 'hh')
    data_provider = DataProviderFactory.create_data_provider(source)
    vacancy_data = data_provider.get_vacancy_details(vacancy_id)

    if request.method == 'POST':
        user = request.user

        # Сохраняем информацию о вакансии в базу данных
        vacancy, created = Vacancy.objects.get_or_create(
            url=vacancy_data['alternate_url'],
            defaults={
                'title': vacancy_data['name'],
                'description': vacancy_data.get('description', ''),
                'company': vacancy_data['employer']['name'],
                'source': source
            }
        )
        if created:
            data_provider.save_vacancy_details(vacancy_id, vacancy_data)

        # Проверяем, есть ли уже эта вакансия в закладках у пользователя
        bookmark, created = Bookmark.objects.get_or_create(user=user, vacancy=vacancy)

        return redirect('bookmarks')

    return redirect('vacancy_detail', vacancy_id=vacancy_id)


def vacancy_detail(request, vacancy_id):
    source = request.GET.get('source', 'hh')
    data_provider = DataProviderFactory.create_data_provider(source)
    vacancy = data_provider.get_vacancy_details(vacancy_id)
    return render(request, 'vacancies/vacancy_detail.html', {'vacancy': vacancy})


def bookmark_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy.objects.prefetch_related('details'), pk=vacancy_id)
    return render(request, 'vacancies/bookmark_detail.html', {'vacancy': vacancy})


# TODO: удалить старый метод old_update_bookmarks
@login_required
def old_update_bookmarks(request):
    source = request.GET.get('source', 'hh')
    api_client = DataProviderFactory.create_api_client(source)
    bookmarks = request.user.bookmarks.all()
    for bookmark in bookmarks:
        vacancy = bookmark.vacancy
        vacancy_id = vacancy.url.split('/')[-1]
        vacancy_data = api_client.get_vacancy(vacancy_id)

        # Обновляем данные вакансии и сохраняем изменения
        vacancy.title = vacancy_data['name']
        vacancy.company = vacancy_data['employer']['name']
        vacancy.description = vacancy_data['description']
        vacancy.save()

        # Обновляем или создаем объект VacancyDetail
        vacancy_detail, created = VacancyDetail.objects.get_or_create(vacancy=vacancy)

        # Обновляем данные VacancyDetail и сохраняем изменения
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
def update_bookmarks(request):
    source = request.GET.get('source', 'hh')
    data_provider = DataProviderFactory.create_data_provider(source)
    bookmarks = request.user.bookmarks.all()
    for bookmark in bookmarks:
        vacancy = bookmark.vacancy
        vacancy_id = vacancy.url.split('/')[-1]
        vacancy_data = data_provider.get_vacancy_details(vacancy_id)

        # Обновляем данные вакансии и сохраняем изменения
        vacancy.title = vacancy_data['name']
        vacancy.company = vacancy_data['employer']['name']
        vacancy.description = vacancy_data['description']
        vacancy.save()

        # Обновляем или создаем объект VacancyDetail
        data_provider.save_vacancy_details(vacancy_id, vacancy_data)

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


def get_tinkoff_internships(request):
    parser_url = 'http://127.0.0.1:5000/internships'
    try:
        response = requests.get(parser_url)
        # Ensure the response content is decoded properly
        vacancies = response.json()
    except requests.RequestException as e:
        # Handle request errors
        return JsonResponse({'error': 'Request failed', 'details': str(e)}, status=500)
    except ValueError as e:
        # Handle JSON decoding errors
        return JsonResponse({'error': 'Failed to parse JSON', 'details': str(e)}, status=500)

    # Return the decoded JSON as a response
    return JsonResponse(vacancies, safe=False)


def internships_view(request):
    try:
        categories = get_internships()
        internships_data = []
        for category in categories:
            positions = []
            for position in category.positions:
                positions.append({
                    'title': position.title,
                    'description': position.description,
                    'status': position.status,
                    'link': position.link,
                    'area': position.area
                })
            internships_data.append({
                'category': category.category,
                'positions': positions
            })
        return JsonResponse({'internships': internships_data})
    except grpc.RpcError as e:
        return JsonResponse({'error': f'gRPC error: {e.details()}'}, status=500)
