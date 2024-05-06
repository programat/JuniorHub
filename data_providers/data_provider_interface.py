from abc import ABC, abstractmethod


class VacancyDataProvider(ABC):
    @abstractmethod
    def get_vacancies(self, **kwargs):
        pass

    @abstractmethod
    def get_vacancy_details(self, vacancy_id):
        pass

    @abstractmethod
    def save_vacancies(self, vacancies):
        pass

    @abstractmethod
    def save_vacancy_details(self, vacancy_id, details):
        pass
