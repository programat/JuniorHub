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
        area_id = request.POST.get('area')
        experience = request.POST.get('experience')

        # Формируем параметры для запроса
        params = {
            'page': 0,
            'per_page': 100
        }
        if query:
            params['text'] = query
        if area_id:
            params['area'] = area_id
        if experience:
            params['experience'] = experience

        # Выполняем поиск вакансий через API HH.ru
        api_client = HhApiClient()
        try:
            vacancies = api_client.search_vacancies(**params)
        except requests.exceptions.HTTPError as e:
            return HttpResponse(f'Error: {e}', status=400)

        # Сохраняем полученные вакансии в базу данных
        for vacancy_data in vacancies['items']:
            vacancy = Vacancy(
                title=vacancy_data['name'],
                description=vacancy_data.get('description', ''),
                company=vacancy_data['employer']['name'],
                url=vacancy_data['alternate_url'],
                source='hh.ru'
            )
            vacancy.save()

        # Передаем вакансии в шаблон для отображения
        context = {'vacancies': vacancies['items']}
        return render(request, 'vacancies/search_results.html', context)

    return render(request, 'vacancies/search_form.html')


def add_to_bookmarks(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id)

    if request.method == 'POST':
        # Получаем текущего пользователя
        user = request.user

        # Проверяем, есть ли уже эта вакансия в закладках у пользователя
        bookmark, created = Bookmark.objects.get_or_create(user=user, vacancy=vacancy)

        # Если вакансии не было в закладках, сохраняем ее в базу данных
        if created:
            vacancy.save_with_details()

        return redirect('bookmarks')

    return redirect('vacancy_detail', vacancy_id=vacancy_id)


def vacancy_detail(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, pk=vacancy_id)
    return render(request, 'vacancies/vacancy_detail.html', {'vacancy': vacancy})


@login_required
def bookmarks(request):
    bookmarks = Bookmark.objects.filter(user=request.user)
    return render(request, 'vacancies/bookmarks.html', {'bookmarks': bookmarks})
