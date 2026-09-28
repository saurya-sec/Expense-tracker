from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from psycopg import Connection

from database import get_db
from statement import parse_statement


router = APIRouter(
    prefix="/statement",
    tags=["Statement"],
)


@router.post("/upload")
async def upload_statement(
    file: UploadFile = File(...),
    db: Connection = Depends(get_db),
):

    if not file.filename.lower().endswith(".xls"):
        raise HTTPException(
            status_code=400,
            detail="Only excel files are supported",
        )

    content = await file.read()

    try:
        transactions = parse_statement(content)

        created_expenses = 0
        created_income = 0

        with db.cursor() as cursor:

            for transaction in transactions:

                transaction_type = transaction["type"]
                data = transaction["data"]

                # -------------------------
                # EXPENSE
                # -------------------------

                if transaction_type == "expense":

                    cursor.execute(
                        """
                        INSERT INTO expenses (
                            title,
                            amount,
                            category,
                            description,
                            expense_date
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            data.title,
                            data.amount,
                            data.category,
                            data.description,
                            data.expense_date,
                        ),
                    )

                    created_expenses += 1

                # -------------------------
                # INCOME
                # -------------------------

                elif transaction_type == "income":

                    cursor.execute(
                        """
                        INSERT INTO income (
                            title,
                            amount,
                            category,
                            description,
                            income_date
                        )
                        VALUES (%s, %s, %s, %s, %s)
                        """,
                        (
                            data.title,
                            data.amount,
                            data.category,
                            data.description,
                            data.income_date,
                        ),
                    )

                    created_income += 1

        db.commit()

        return {
            "message": "Statement imported successfully",
            "total_transactions": len(transactions),
            "expenses_created": created_expenses,
            "income_created": created_income,
        }

    except Exception as e:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Failed to import statement: {str(e)}",
        )