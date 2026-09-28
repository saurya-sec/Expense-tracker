import io
import re

from decimal import Decimal, InvalidOperation
from datetime import datetime, date

import pandas as pd
import pdfplumber

from schema.Expense import ExpenseCreate
from schema.Income import IncomeCreate


# ============================================================
# CATEGORY CLASSIFICATION
# ============================================================

def classify_expense(description: str) -> str:
    description = str(description).lower().strip()

    if any(word in description for word in [
        "swiggy",
        "zomato",
        "blinkit",
        "restaurant",
        "hotel",
        "food",
        "dominos",
        "pizza",
        "mcdonald",
        "starbucks",
        "cafe",
    ]):
        return "food"

    if any(word in description for word in [
        "uber",
        "ola",
        "rapido",
        "railway",
        "irctc",
        "metro",
        "transport",
        "bus",
        "taxi",
    ]):
        return "transport"

    if any(word in description for word in [
        "rent",
        "housing",
    ]):
        return "rent"

    return "others"


def classify_income(description: str) -> str:
    description = str(description).lower().strip()

    if any(word in description for word in [
        "salary",
        "payroll",
        "salary credit",
    ]):
        return "salary"

    if any(word in description for word in [
        "freelance",
        "freelancer",
    ]):
        return "freelance"

    if any(word in description for word in [
        "business",
        "sales",
        "invoice",
    ]):
        return "business"

    return "others"


# ============================================================
# TITLE EXTRACTION
# ============================================================

def extract_title(description: str) -> str:
    """
    Creates a readable title from an eSewa/bank transaction description.
    """

    if not description:
        return "Transaction"

    description = str(description).strip()

    # Remove excessive whitespace
    description = re.sub(r"\s+", " ", description)

    # eSewa descriptions don't necessarily contain "/"
    # so keep the complete description.
    title = description

    # Remove common transaction identifiers
    title = re.sub(
        r"\b(?:upi|imps|neft|rtgs|txn|transaction|ref|reference)\b",
        "",
        title,
        flags=re.IGNORECASE,
    )

    title = re.sub(r"\s+", " ", title).strip()

    if not title:
        title = "Transaction"

    return title[:50].title()


# ============================================================
# DATE PARSING
# ============================================================

def parse_date(value):
    """
    Supports:
    - datetime
    - date
    - pandas Timestamp
    - common string date formats
    """

    if value is None:
        return None

    if pd.isna(value):
        return None

    if isinstance(value, datetime):
        return value.date()

    if isinstance(value, date):
        return value

    value = str(value).strip()

    if not value:
        return None

    formats = [
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M:%S.%f",
        "%d %b %Y",
        "%d %B %Y",
        "%d-%m-%Y",
        "%d/%m/%Y",
        "%d-%m-%y",
        "%d/%m/%y",
        "%Y-%m-%d",
        "%d %b %y",
        "%d %B %y",
    ]

    for fmt in formats:
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    # Final fallback
    try:
        parsed = pd.to_datetime(value, dayfirst=True)
        return parsed.date()
    except (ValueError, TypeError):
        return None


# ============================================================
# AMOUNT PARSING
# ============================================================

def parse_amount(value):
    """
    Converts eSewa/bank statement amounts into Decimal.
    """

    if value is None:
        return None

    if pd.isna(value):
        return None

    if isinstance(value, Decimal):
        return value

    if isinstance(value, (float, int)):
        return Decimal(str(value))

    value = str(value).strip()

    if not value:
        return None

    if value.lower() in {
        "nan",
        "none",
        "null",
        "-",
        "--",
    }:
        return None

    # Remove commas and currency symbols
    value = value.replace(",", "")
    value = value.replace("₹", "")
    value = value.replace("$", "")
    value = value.replace("€", "")
    value = value.replace("£", "")

    # Remove DR / CR
    value = re.sub(
        r"\s*(DR|CR)\s*$",
        "",
        value,
        flags=re.IGNORECASE,
    )

    value = value.strip()

    # Accounting format: (500.00)
    if value.startswith("(") and value.endswith(")"):
        value = "-" + value[1:-1]

    try:
        return Decimal(value)
    except (InvalidOperation, ValueError):
        return None


# ============================================================
# CREATE EXPENSE
# ============================================================

def create_expense(
    description: str,
    amount: Decimal,
    transaction_date: date,
):
    return ExpenseCreate(
        title=extract_title(description),
        amount=amount,
        category=classify_expense(description),
        description=description,
        expense_date=transaction_date,
    )


# ============================================================
# CREATE INCOME
# ============================================================

def create_income(
    description: str,
    amount: Decimal,
    transaction_date: date,
):
    return IncomeCreate(
        title=extract_title(description),
        amount=amount,
        category=classify_income(description),
        description=description,
        income_date=transaction_date,
    )


# ============================================================
# PDF STATEMENT
# ============================================================

def parse_pdf_statement(file_content: bytes):
    transactions = []

    try:
        pdf = pdfplumber.open(io.BytesIO(file_content))
    except Exception as e:
        raise ValueError(
            f"Unable to read PDF statement: {str(e)}"
        )

    with pdf:
        for page in pdf.pages:

            try:
                tables = page.extract_tables()
            except Exception:
                continue

            for table in tables:

                if not table:
                    continue

                for row in table:

                    if not row or len(row) < 6:
                        continue

                    number = row[0]
                    transaction_date_value = row[1]
                    description = row[2]
                    withdrawal = row[4]
                    deposit = row[5]

                    if number is None:
                        continue

                    if not str(number).strip().isdigit():
                        continue

                    if not transaction_date_value or not description:
                        continue

                    description = str(description).strip()

                    transaction_date = parse_date(
                        transaction_date_value
                    )

                    if transaction_date is None:
                        continue

                    withdrawal_amount = parse_amount(withdrawal)
                    deposit_amount = parse_amount(deposit)

                    # EXPENSE
                    if (
                        withdrawal_amount is not None
                        and withdrawal_amount > 0
                    ):
                        expense = create_expense(
                            description=description,
                            amount=withdrawal_amount,
                            transaction_date=transaction_date,
                        )

                        transactions.append({
                            "type": "expense",
                            "data": expense,
                        })

                    # INCOME
                    elif (
                        deposit_amount is not None
                        and deposit_amount > 0
                    ):
                        income = create_income(
                            description=description,
                            amount=deposit_amount,
                            transaction_date=transaction_date,
                        )

                        transactions.append({
                            "type": "income",
                            "data": income,
                        })

    return transactions


# ============================================================
# EXCEL / XLS / XLSX STATEMENT
# ============================================================

def parse_excel_statement(file_content: bytes):
    """
    Parses eSewa Excel statements.

    Expected transaction columns:

        Reference Code
        Date Time
        Description
        Dr.
        Cr.
        Status
        Balance (NPR)
        Channel
    """

    transactions = []

    excel_file = io.BytesIO(file_content)

    try:
        # sheet_name=None reads all sheets
        sheets = pd.read_excel(
            excel_file,
            sheet_name=None,
            header=None,
        )

    except Exception as e:
        raise ValueError(
            f"Unable to read Excel statement: {str(e)}"
        )

    for sheet_name, raw_df in sheets.items():

        if raw_df.empty:
            continue

        header_row = None

        # ====================================================
        # FIND eSewa TRANSACTION HEADER
        # ====================================================

        for index, row in raw_df.iterrows():

            values = {
                str(value).strip().lower()
                for value in row.tolist()
                if pd.notna(value)
            }

            required_headers = {
                "reference code",
                "date time",
                "description",
                "dr.",
                "cr.",
                "status",
            }

            if required_headers.issubset(values):
                header_row = index
                break

        if header_row is None:
            continue

        # ====================================================
        # BUILD DATAFRAME
        # ====================================================

        headers = raw_df.iloc[header_row].tolist()

        df = raw_df.iloc[header_row + 1:].copy()
        df.columns = headers

        # ====================================================
        # MAP COLUMNS
        # ====================================================

        column_map = {}

        for column in df.columns:

            if pd.isna(column):
                continue

            normalized = str(column).strip().lower()

            if normalized == "reference code":
                column_map["reference_code"] = column

            elif normalized == "date time":
                column_map["date_time"] = column

            elif normalized == "description":
                column_map["description"] = column

            elif normalized == "dr.":
                column_map["debit"] = column

            elif normalized == "cr.":
                column_map["credit"] = column

            elif normalized == "status":
                column_map["status"] = column

            elif normalized == "balance (npr)":
                column_map["balance"] = column

            elif normalized == "channel":
                column_map["channel"] = column

        required_columns = [
            "date_time",
            "description",
            "debit",
            "credit",
            "status",
        ]

        if not all(
            column in column_map
            for column in required_columns
        ):
            continue

        # ====================================================
        # PROCESS TRANSACTIONS
        # ====================================================

        for _, row in df.iterrows():

            description = row.get(
                column_map["description"]
            )

            date_time = row.get(
                column_map["date_time"]
            )

            debit = row.get(
                column_map["debit"]
            )

            credit = row.get(
                column_map["credit"]
            )

            status = row.get(
                column_map["status"]
            )

            # ------------------------------------------------
            # IGNORE EMPTY ROWS
            # ------------------------------------------------

            if pd.isna(description) and pd.isna(date_time):
                continue

            # ------------------------------------------------
            # IGNORE SUMMARY ROWS
            # ------------------------------------------------

            description_text = (
                str(description).strip().lower()
                if pd.notna(description)
                else ""
            )

            if description_text in {
                "total",
                "pending",
                "complete",
                "canceled",
                "cancelled",
                "time out",
                "timeout",
            }:
                continue

            # ------------------------------------------------
            # STATUS
            # ------------------------------------------------

            if pd.notna(status):

                status_value = (
                    str(status)
                    .strip()
                    .upper()
                )

                # Only import completed transactions
                if status_value != "COMPLETE":
                    continue

            # ------------------------------------------------
            # REQUIRED VALUES
            # ------------------------------------------------

            if pd.isna(description):
                continue

            if pd.isna(date_time):
                continue

            description = str(description).strip()

            if not description:
                continue

            # ------------------------------------------------
            # DATE
            # ------------------------------------------------

            transaction_date = parse_date(date_time)

            if transaction_date is None:
                continue

            # ------------------------------------------------
            # AMOUNTS
            # ------------------------------------------------

            debit_amount = parse_amount(debit)
            credit_amount = parse_amount(credit)

            # ------------------------------------------------
            # EXPENSE
            # ------------------------------------------------

            if (
                debit_amount is not None
                and debit_amount > 0
            ):

                expense = create_expense(
                    description=description,
                    amount=debit_amount,
                    transaction_date=transaction_date,
                )

                transactions.append({
                    "type": "expense",
                    "data": expense,
                })

            # ------------------------------------------------
            # INCOME
            # ------------------------------------------------

            elif (
                credit_amount is not None
                and credit_amount > 0
            ):

                income = create_income(
                    description=description,
                    amount=credit_amount,
                    transaction_date=transaction_date,
                )

                transactions.append({
                    "type": "income",
                    "data": income,
                })

    return transactions


# ============================================================
# MAIN STATEMENT PARSER
# ============================================================

def parse_statement(
    file_content: bytes,
    filename: str | None = None,
):
    """
    Parse a bank/eSewa statement.

    Supported formats:
        PDF
        XLS
        XLSX

    Returns:
        [
            {
                "type": "expense",
                "data": ExpenseCreate(...)
            },
            {
                "type": "income",
                "data": IncomeCreate(...)
            }
        ]
    """

    if not filename:
        raise ValueError(
            "Filename is required to determine "
            "the statement format"
        )

    filename = filename.lower().strip()

    if filename.endswith(".pdf"):
        return parse_pdf_statement(file_content)

    if (
        filename.endswith(".xls")
        or filename.endswith(".xlsx")
    ):
        return parse_excel_statement(file_content)

    raise ValueError(
        "Unsupported file format. "
        "Only PDF, XLS and XLSX files are supported."
    )