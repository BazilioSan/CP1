import pytest
import json

from src.services import date_sorting, investment_bank, limit_payment


@pytest.mark.parametrize("limit, summa, expected", [(100, -97, -100), (50, 173.4, 200), (10, 236.75, 240)])
def test_limit_payment(limit, summa, expected):
    assert limit_payment(limit, summa) == expected


data_for_test = [
    {"Дата операции": "01.10.2021 17:53:24"},
    {"Дата операции": "07.10.2022 17:53:24"},
    {"Дата операции": "15.10.2022 17:53:24"},
    {"Дата операции": "07.10.2022 17:53:24"},
    {"Дата операции": "17.10.2021 17:53:24"},
    {"Дата операции": "27.10.2022 17:53:24"},
]

expected_for_test_1 = [{"Дата операции": "01.10.2021 17:53:24"}, {"Дата операции": "17.10.2021 17:53:24"}]

expected_for_test_2 = [
    {"Дата операции": "07.10.2022 17:53:24"},
    {"Дата операции": "15.10.2022 17:53:24"},
    {"Дата операции": "07.10.2022 17:53:24"},
    {"Дата операции": "27.10.2022 17:53:24"},
]


@pytest.mark.parametrize(
    "month, transaction, expected",
    [
        ("2021-10", data_for_test, expected_for_test_1),
        ("2022-10", data_for_test, expected_for_test_2),
        ("2023-10", data_for_test, []),
    ],
)
def test_date_sorting(month, transaction, expected):
    assert date_sorting(month, transaction) == expected


data_for_test_1 = [
    {"Дата операции": "01.10.2021 17:53:24", "Сумма операции": -152},
    {"Дата операции": "07.10.2022 17:53:24", "Сумма операции": -47.85},
    {"Дата операции": "15.10.2022 17:53:24", "Сумма операции": -10385},
    {"Дата операции": "07.10.2022 17:53:24", "Сумма операции": -101},
    {"Дата операции": "17.10.2021 17:53:24", "Сумма операции": -52},
    {"Дата операции": "27.10.2022 17:53:24", "Сумма операции": -887.65},
]


@pytest.mark.parametrize(
    "month, transaction, limit, expected",
    [
        ("2021-10", data_for_test_1, 100, 96.0),
        ("2021-10", data_for_test_1, 10, 16.0),
        ("2021-10", data_for_test_1, 50, 96.0),
        ("2023-10", data_for_test_1, 100, 0.0),
        ("2022-10", data_for_test_1, 50, 78.5),
    ],
)
def test_investment_bank(month, transaction, limit, expected):
    result = investment_bank(month, transaction, limit)
    result_to_assert = json.loads(result)
    assert result_to_assert == expected
