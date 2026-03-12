import requests
from bs4 import BeautifulSoup
import time
import re


def parse_avito_computer_parts_improved():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'ru-RU,ru;q=0.9,en;q=0.8',
        'Referer': 'https://www.avito.ru/'
    }

    url = "https://www.avito.ru/all/tovary_dlya_kompyutera/komplektuyuschie-ASgBAgICAUTGB~pm?d=1&s=104"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')

        items = soup.find_all('div', {'data-marker': 'item'})

        print(f"Найдено объявлений: {len(items)}")

        avito_lst = []

        for i, item in enumerate(items[:20], 1):  # Покажем первые 20
            try:
                # Название
                title_elem = item.find('a', {'data-marker': 'item-title'})
                title = title_elem.text.strip() if title_elem else "Нет названия"

                # Цена - ищем разными способами
                price = "Цена не указана"
                price_elem = item.find('span', {'data-marker': 'item-price'})
                if price_elem:
                    price = price_elem.text.strip()
                else:
                    # Альтернативный поиск цены
                    price_meta = item.find('meta', {'itemprop': 'price'})
                    if price_meta:
                        price = price_meta.get('content', '') + ' ₽'

                # Ссылка
                link = "https://www.avito.ru" + title_elem['href'] if title_elem else "Нет ссылки"

                # Описание - ищем по разным классам
                description = "Нет описания"
                desc_selectors = [
                    'div[class*="description"]',
                    'div[class*="text"]',
                    'p[class*="description"]'
                ]
                for selector in desc_selectors:
                    desc_elem = item.select_one(selector)
                    if desc_elem:
                        description = desc_elem.text.strip()
                        break

                # Местоположение
                location = "Местоположение не указано"
                location_elem = item.find('div', class_=lambda x: x and ('geo' in x or 'address' in x))
                if location_elem:
                    location = location_elem.text.strip()

                # Дата
                date = "Дата не указана"
                date_elem = item.find('div', class_=lambda x: x and 'date' in x)
                if date_elem:
                    date = date_elem.text.strip()

                print(f"\n{i}. {title}")
                print(f"   💰 {price}")
                print(f"   📍 {location}")
                print(f"   📅 {date}")
                if description != "Нет описания":
                    print(f"   📝 {description[:80]}...")
                print(f"   🔗 {link[:80]}...")  # Обрезаем длинную ссылку
                print("   " + "=" * 50)

                avito_lst.append(title)

            except Exception as e:
                print(f"Ошибка при парсинге объявления {i}: {e}")

        print(avito_lst)

    except requests.RequestException as e:
        print(f"Ошибка запроса: {e}")


# Запуск улучшенного парсера
parse_avito_computer_parts_improved()
