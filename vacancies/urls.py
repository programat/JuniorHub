from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search_vacancies, name='search_vacancies'),
    path('vacancy/<int:vacancy_id>/', views.vacancy_detail, name='vacancy_detail'),
    path('vacancy/<int:vacancy_id>/bookmark/', views.add_to_bookmarks, name='add_to_bookmarks'),
]
