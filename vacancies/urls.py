from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('internships/', views.get_tinkoff_internships, name='internships'),
    path('search/', views.search_vacancies, name='search_vacancies'),
    path('bookmarks/', views.bookmarks, name='bookmarks'),
    path('bookmarks/<int:vacancy_id>/', views.bookmark_detail, name='bookmark_detail'),
    path('bookmarks/<int:vacancy_id>/delete/', views.delete_bookmark, name='delete_bookmark'),
    path('bookmarks/update/', views.update_bookmarks, name='update_bookmarks'),
    path('vacancy/<int:vacancy_id>/', views.vacancy_detail, name='vacancy_detail'),
    path('vacancy/<int:vacancy_id>/bookmark/', views.add_to_bookmarks, name='add_to_bookmarks'),
]
