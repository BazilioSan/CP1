import datetime
import json
import logging
import os
import re
from functools import wraps
from typing import Any, Callable, Dict, List

import pandas as pd

from config import REPORTS_LOGS, ROOT_DIR

logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler(REPORTS_LOGS, mode="w")
file_formatter = logging.Formatter("%(asctime)s - %(filename)s - %(funcName)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)


def log(filename: str = "log_file.json") -> Any:
    """Декоратор принимает функцию. Проводит запись результата (pd.DataFrame) её работы в json-файл.
    Возвращает результат самой функции."""
    logger.info("Декоратор начал свою работу.")

    def wrapper(func: Callable) -> Any:
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:
            logger.info("Декоратор получает результат работы декорируемой функции.")
            result = func(*args, **kwargs)
            logger.info("Декоратор записывает полученный результат в файл.")
            with open(os.path.join(ROOT_DIR, filename), "w", encoding="utf-8") as file:
                json.dump(result.to_dict(orient="records"), file, ensure_ascii=False, indent=4)
            logger.info("Декоратор успешно завершил свою работу.")
            return result

        return inner

    return wrapper


def filtered_by_category(category: str, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Функция принимает список транзакций (словарей) и категорию.
    Возвращает список транзакций (словарей), отфильтрованных по заданной категории."""
    logger.info("Функция начала свою работу.")
    pattern = rf"{category}"
    logger.info("Функция обрабатывает полученные данные.")
    filtered_list = [
        transaction
        for transaction in transactions
        if re.findall(pattern, transaction["Категория"], flags=re.IGNORECASE)
    ]
    logger.info("Функция успешно завершила свою работу.")
    return filtered_list


def filtered_by_date(transactions: List[Dict], date: str = "") -> List[Dict[str, Any]]:
    """Функция принимает список транзакций (словарей) и дату.
    Возвращает список транзакций (словарей), отобранных за период в 3 месяца от заданной даты,
    если дата не передана, то от настоящего числа."""
    logger.info("Функция начала свою работу.")
    time_start = datetime.time(hour=00, minute=00, second=00)
    time_end = datetime.time(hour=23, minute=59, second=59)
    if not date:
        end_date = datetime.datetime.today()
        start_date = end_date - datetime.timedelta(weeks=12)
    if date:
        end_date = datetime.datetime.strptime(date, "%Y-%m-%d")
        start_date = end_date - datetime.timedelta(weeks=12)
    filtered_list = []
    logger.info("Функция обрабатывает полученные данные.")
    for transaction in transactions:
        transaction_date = datetime.datetime.strptime(transaction["Дата операции"], "%d.%m.%Y %H:%M:%S")
        if (
            datetime.datetime.combine(start_date, time_start)
            <= transaction_date
            <= datetime.datetime.combine(end_date, time_end)
        ):
            filtered_list.append(transaction)
    logger.info("Функция успешно завершила свою работу.")
    return filtered_list


@log()
def spent_by_category(transactions: pd.DataFrame, category: str, date: str = "") -> pd.DataFrame:
    """Функция принимает транзакции (pd.DataFrame), чистит от пустых значений в колонке 'Категория'.
    Подготовленные данные передаёт для дальнейшей обработки своим подфункциям.
    Возвращает pd.DataFrame транзакций, отобранных за определённый период по определённой категории."""
    logger.info("Функция начала свою работу.")
    not_null_category = transactions.loc[transactions["Категория"].notnull()]
    logger.info("Функция проводит очистку от пустых значений в Категориях")
    transaction_list = not_null_category.to_dict(orient="records")
    logger.info("Функция передаёт очищенные данные для обработки своим подфункциям.")
    filtered_by_date_list = filtered_by_date(transaction_list, date)
    filtered_by_category_list = filtered_by_category(category, filtered_by_date_list)
    result = pd.DataFrame(filtered_by_category_list)
    logger.info("Функция успешно завершила свою работу.")
    return result


data_from_excel = pd.DataFrame(
    [
        {"Дата операции": "01.10.2023 17:53:24", "Сумма операции": -152, "Категория": "Фастфуд"},
        {"Дата операции": "07.10.2023 17:53:24", "Сумма операции": -47.85, "Категория": "Каршеринг"},
        {"Дата операции": "15.10.2023 17:53:24", "Сумма операции": -10385, "Категория": "Фастфуд"},
        {"Дата операции": "07.10.2023 17:53:24", "Сумма операции": -101, "Категория": "Супермаркет"},
        {"Дата операции": "17.10.2023 17:53:24", "Сумма операции": -52, "Категория": "Супермаркет"},
        {"Дата операции": "27.10.2023 17:53:24", "Сумма операции": -887.65, "Категория": "Детские товары"},
        {"Дата операции": "01.10.2023 17:53:24", "Сумма операции": -152, "Категория": "Фастфуд"},
        {"Дата операции": "07.10.2023 17:53:24", "Сумма операции": -47.85, "Категория": "Каршеринг"},
        {"Дата операции": "15.10.2023 17:53:24", "Сумма операции": -10385, "Категория": "Фастфуд"},
        {"Дата операции": "07.10.2023 17:53:24", "Сумма операции": -101, "Категория": "Супермаркет"},
        {"Дата операции": "17.10.2023 17:53:24", "Сумма операции": -52, "Категория": "Супермаркет"},
        {"Дата операции": "27.10.2023 17:53:24", "Сумма операции": -887.65, "Категория": "Детские товары"},
    ]
)


if __name__ == "__main__":
    print(spent_by_category(data_from_excel, "Фастфуд", "2023-10-15"))
