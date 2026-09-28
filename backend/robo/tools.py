from langchain_core.tools import tool

from database import get_db


@tool
def get_income() -> list[dict]:
    """
    Get all income records from the database.

    Use this tool whenever the user asks about income,
    earnings, salary, or income history.
    """

    db = next(get_db())

    with db.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                title,
                amount,
                category,
                description,
                income_date,
                created_at,
                updated_at
            FROM income
            ORDER BY income_date DESC
            """
        )

        rows = cursor.fetchall()

    db.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "amount": str(row[2]),
            "category": row[3],
            "description": row[4],
            "income_date": str(row[5]),
            "created_at": str(row[6]),
            "updated_at": str(row[7]),
        }
        for row in rows
    ]


tools = [get_income]