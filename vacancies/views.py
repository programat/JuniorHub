from django.shortcuts import render
from .models import Vacancy
from .hhapi import HhApiClient

def index(request):
    return render(request, 'vacancies/index.html')

def search_vacancies(request):
    if request.method == 'POST':
        # Получаем данные из формы поиска
        query = request.POST.get('query')
        area = request.POST.get('area')
        experience = request.POST.get('experience')

        # Выполняем поиск вакансий через API HH.ru
        api_client = HhApiClient()
        vacancies = api_client.search_vacancies(query, area, experience)

        # Сохраняем полученные вакансии в базу данных
        for vacancy_data in vacancies['items']:
            vacancy = Vacancy(
                title=vacancy_data['name'],
                description=vacancy_data['description'],
                company=vacancy_data['employer']['name'],
                url=vacancy_data['alternate_url'],
                source='hh.ru'
            )
            vacancy.save()

        # Передаем вакансии в шаблон для отображения
        context = {'vacancies': vacancies['items']}
        return render(request, 'vacancies/search_results.html', context)

    return render(request, 'vacancies/search_form.html')