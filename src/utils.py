import datetime
import json
import os
import logging

from collections import defaultdict
from typing import Any, Dict, List, Tuple

import pandas as pd
import requests
from dotenv import load_dotenv

from config import DATA_DIR, ROOT_DIR, UTILS_LOGS

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)
file_handler = logging.FileHandler(UTILS_LOGS, mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def greetings(date_string: str) -> str:
    """Функция принимает время в строке в формате '%Y-%m-%d %H:%M:%S',
    возвращает приветствие в зависимости от времени суток."""
    logger.info(f"Старт функции с входными данными {date_string}")

    try:

        logger.info("Обработка входной строки.")

        date_object = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        time_for_greeting = date_object.time()
        greetings_dict = {
            "1": ("Доброе утро!", "05:00:01", "12:00:00"),
            "2": ("Добрый день!", "12:00:01", "17:00:00"),
            "3": ("Добрый вечер!", "17:00:01", "21:00:00"),
            "4": ("Доброй ночи!", "21:00:01", "00:00:00"),
            "5": ("Доброй ночи!", "00:00:01", "05:00:00"),
        }

        for greeting in greetings_dict:
            start, end = greetings_dict[greeting][1], greetings_dict[greeting][2]
            time_start = datetime.datetime.strptime(start, "%H:%M:%S").time()
            time_end = datetime.datetime.strptime(end, "%H:%M:%S").time()
            if time_start <= time_for_greeting <= time_end:
                logger.info(f"Функция успешно отработала с результатом: {greetings_dict[greeting][0]}.")
                return greetings_dict[greeting][0]

    except Exception:
        logger.error("Введены некорректные данные!")
        raise ValueError("Введены некорректные данные!")


# f = greetings("2025-12-06 20:42:30")
# print(f)

def reading_excel(file_name: str) -> List[Dict]:
    """Функция преобразования xls в DataFrame."""
    logger.info(f"Функция запущена с входым файлом {file_name}.")
    if file_name.endswith("xls") or file_name.endswith("xlsx"):
        logger.info("Функция начала обработку входного файла.")
        file_with_dir = os.path.join(DATA_DIR, file_name)
        transactions_df = pd.read_excel(file_with_dir)
        # result = transactions_df.to_dict(orient="records")
        logger.info("Функция успешно завершила свою работу.")
        # return result
        return transactions_df
    else:
        logger.error("Неподдерживаемый формат файла!")
        raise ValueError("Неподдерживаемый формат файла!")


def card_info(transactions: List[Dict]) -> List[Dict]:
    """Функция принимает список транзакций(словарей).
    Возвращает список словарей с информацией по каждой карте: последние 4 цифры номера карты,
    общая сумма расходов, кэшбек (1 рубль на каждые 100 рублей)."""
    logger.info("Функция начала свою работу.")
    unique_card_nums = list(set([transaction["Номер карты"] for transaction in transactions]))
    expenditure_by_card = defaultdict(int)
    logger.info("Функция обрабатывает данные транзакций.")
    for card_num in unique_card_nums:
        for transaction in transactions:
            if transaction["Номер карты"] == card_num:
                expenditure_by_card[card_num] += transaction["Сумма операции"]
    result_transaction_list = []
    logger.info("Функция формирует итоговый результат.")
    for item in expenditure_by_card:
        result_transaction_list.append(
            {
                "last_digits": item[1:],
                "total_spent": round(expenditure_by_card[item], 2),
                "cashback": round(expenditure_by_card[item] / 100, 2),
            }
        )
    logger.info("Функция успешно завершила свою работу.")
    return result_transaction_list


def top_five_transactions(transactions: List[Dict]) -> List[Dict]:
    """Функция принимает список транзакций(словарей).
    Возвращает список словарей с топ-пятью транзакциями по сумме операции."""
    logger.info("Функция начала свою работу.")
    sorted_transactions_list = sorted(transactions, key=lambda x: abs(x["Сумма операции"]))
    logger.info("Функция успешно завершила свою работу.")
    return sorted_transactions_list[-5:]


def json_loader(file_name: str = "user_settings.json") -> Tuple[Any, Any]:
    """Функция может принимать название json-файла пользовательских настроек
    (по-умолчанию задано 'user_settings.json'), который расположен в корне проекта.
    Обрабатывает json-файл пользовательских настроек.
    Возвращает кортеж списков валют и акций."""
    logger.info("Функция начала свою работу.")
    file_with_dir = os.path.join(ROOT_DIR, file_name)
    try:
        with open(file_with_dir, "r", encoding="utf-8") as file_in:
            data = json.load(file_in)
            logger.info("Функция успешно завершила свою работу.")
            return data["user_currencies"], data["user_stocks"]
    except Exception:
        logger.error("Возникла ошибка при обработке файла пользовательских настроек!")
        raise ValueError("Возникла ошибка при обработке файла пользовательских настроек!")


def currency_rates(users_currencies: List) -> List[Dict[str, Any]]:
    """Функция принимает список валют. Возвращает курс валют, полученный через API."""
    logger.info("Функция начала свою работу.")
    try:
        result_currency_list = []
        load_dotenv()
        api_key = os.getenv("API_KEY_CURRENCY")
        logger.info("Функция получает данные курсов валют.")
        for currency in users_currencies:
            url = f"https://api.apilayer.com/exchangerates_data/convert?to={"RUB"}&from={currency}&amount={1}"
            headers = {"apikey": api_key}
            response = requests.get(url, headers=headers, timeout=5, allow_redirects=False)
            result = response.json()
            logger.info(f"{result}")
            result_currency_list.append({"currency": currency, "rate": round(float(result["result"]), 2)})
        logger.info("Функция успешно завершила свою работу.")
        return result_currency_list
    except Exception:
        logger.error("При работе функции произошла ошибка!")
        raise Exception("При работе функции произошла ошибка!")


def stock_rates(users_stocks: List) -> List[Dict[str, Any]]:
    """Функция принимает список акций. Возвращает котировки, полученные через API."""
    logger.info("Функция начала свою работу.")
    try:
        result_stocks_list = []
        load_dotenv()
        api_key = os.getenv("API_KEY_STOCK")
        logger.info("Функция получает данные по котировкам.")
        for stock in users_stocks:
            url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={stock}&apikey={api_key}"
            response = requests.get(url, timeout=5, allow_redirects=False)
            result = response.json()
            logger.info(f"{result}")
            result_stocks_list.append({"stock": stock, "price": round(float(result["Global Quote"]["05. price"]), 2)})
        logger.info("Функция успешно завершила свою работу.")
        return result_stocks_list
    except Exception:
        logger.error("При работе функции произошла ошибка!")
        raise Exception("При работе функции произошла ошибка!")


if __name__ == "__main__":
    # print(stock_rates(['AAPL', 'AMZN', 'GOOGL']))
    print(greetings("2024-07-06 10:42:30"))
    data = reading_excel("operations.xls")
    print(card_info(data))
    print(
        card_info(
            [
                {
                    "Дата операции": "28.03.2018 09:24:15",
                    "Дата платежа": "29.03.2018",
                    "Номер карты": "*7197",
                    "Статус": "OK",
                    "Сумма операции": -150.0,
                    "Валюта операции": "RUB",
                    "Сумма платежа": -150.0,
                    "Валюта платежа": "RUB",
                    "Кэшбэк": "nan",
                    "Категория": "Связь",
                    "MCC": 4814.0,
                    "Описание": "МТС",
                    "Бонусы (включая кэшбэк)": 3,
                    "Округление на инвесткопилку": 0,
                    "Сумма операции с округлением": 150.0,
                },
                {
                    "Дата операции": "28.03.2018 08:23:56",
                    "Дата платежа": "30.03.2018",
                    "Номер карты": "*7197",
                    "Статус": "OK",
                    "Сумма операции": -197.7,
                    "Валюта операции": "RUB",
                    "Сумма платежа": -197.7,
                    "Валюта платежа": "RUB",
                    "Кэшбэк": "nan",
                    "Категория": "Супермаркеты",
                    "MCC": 5411.0,
                    "Описание": "Billa",
                    "Бонусы (включая кэшбэк)": 3,
                    "Округление на инвесткопилку": 0,
                    "Сумма операции с округлением": 197.7,
                },
            ]
        )
    )
    print(top_five_transactions(data))
    data_for_five = [
        {"Сумма операции": 1},
        {"Сумма операции": 9},
        {"Сумма операции": 4},
        {"Сумма операции": 31},
        {"Сумма операции": 11},
        {"Сумма операции": -17},
        {"Сумма операции": -100},
        {"Сумма операции": 5},
    ]
    print(top_five_transactions(data_for_five))
    print(json_loader())
    users_currs = json_loader()[0]
    print(currency_rates(["USD"]))
