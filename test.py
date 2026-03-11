import requests
from bs4 import BeautifulSoup

def save_html_request(url, file_name="page.html"):
    try:
        response = requests.get(url)
        response.raise_for_status()

        with open(file_name, 'w', encoding='utf-8') as f:
            f.write(response.text)

        print(f"HTML успешно сохранен в файл: {file_name}")
        print(f"Размер страницы: {len(response.text)} символов")

        return response.text

    except requests.exceptions.RequestException as e:

        print(f"Ошибка при запросе: {e}")

        return None

url = 'https://www.avito.ru/all/tovary_dlya_kompyutera/komplektuyuschie-ASgBAgICAUTGB~pm?d=1&s=104'
text = save_html_request(url, 'test.html')
print(text)
