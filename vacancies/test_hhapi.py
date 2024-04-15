from hhapi import HhApiClient

client = HhApiClient()
data = client.search_vacancies(text='Python', area=1, experience='between1And3')

print(data)