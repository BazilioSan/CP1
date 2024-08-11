from src.utils import reading_file_from_excel
from src.views import views
from src.services import investment_bank
from src.reports import spent_by_category
import datetime
import pandas as pd

if __name__ == "__main__":
    date = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")
    transactions_list = reading_file_from_excel("operations.xls")
    transactions_df = pd.DataFrame(transactions_list)

    print(views(date, transactions_df))
    print("\n###################\n")

    print(investment_bank("2021-10", transactions_list.to_dict(orient="records"), 100))
    print("\n###################\n")

    print((spent_by_category(transactions_df, "Фастфуд", "2021-10-25")).head())
