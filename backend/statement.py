import io
import pdfplumber

from decimal import Decimal
from datetime import datetime

from schema.Expense import ExpenseCreate
from schema.Income import IncomeCreate


def classify_expense(description: str) -> str:
    description = description.lower()

    if any(word in description for word in [
        "swiggy",
        "zomato",
        "blinkit",
        "restaurant",
        "hotel",
        "food"
    ]):
        return "food"

    if any(word in description for word in [
        "uber",
        "ola",
        "rapido",
        "railway",
        "irctc"
    ]):
        return "transport"

    if "rent" in description:
        return "rent"

    return "others"


def classify_income(description: str) -> str:
    description = description.lower()

    if "salary" in description:
        return "salary"

    if "freelance" in description:
        return "freelance"

    if "business" in description:
        return "business"

    return "others"


def extract_title(description: str) -> str:
    description = description.strip()

    parts = description.split("/")

    if len(parts) >= 3:
        return parts[2].strip().title()

    return description[:50]


def parse_date(value: str):
    return datetime.strptime(
        value.strip(),
        "%d %b %Y"
    ).date()


def parse_amount(value: str | None):
    if not value:
        return None

    value = value.replace(",", "").strip()

    if not value:
        return None

    return Decimal(value)


def parse_statement(file_content: bytes):

    transactions = []

    with pdfplumber.open(io.BytesIO(file_content)) as pdf:

        for page in pdf.pages:

            tables = page.extract_tables()

            for table in tables:

                for row in table:

                    if not row or len(row) < 8:
                        continue

                    # Expected:
                    # #, Date, Description, Chq/Ref No.,
                    # Withdrawal, Deposit, Balance

                    number = row[0]
                    date = row[1]
                    description = row[2]
                    withdrawal = row[3]
                    deposit = row[4]

                    # Ignore headers
                    if not number or not number.strip().isdigit():
                        continue

                    if not date or not description:
                        continue

                    try:
                        transaction_date = parse_date(date)
                    except ValueError:
                        continue

                    withdrawal_amount = parse_amount(withdrawal)
                    deposit_amount = parse_amount(deposit)

                    # -------------------------
                    # EXPENSE
                    # -------------------------

                    if withdrawal_amount is not None:

                        expense = ExpenseCreate(
                            title=extract_title(description),
                            amount=withdrawal_amount,
                            category=classify_expense(description),
                            description=description,
                            expense_date=transaction_date
                        )

                        transactions.append({
                            "type": "expense",
                            "data": expense
                        })

                    # -------------------------
                    # INCOME
                    # -------------------------

                    elif deposit_amount is not None:

                        income = IncomeCreate(
                            title=extract_title(description),
                            amount=deposit_amount,
                            category=classify_income(description),
                            description=description,
                            income_date=transaction_date
                        )

                        transactions.append({
                            "type": "income",
                            "data": income
                        })

    return transactions



