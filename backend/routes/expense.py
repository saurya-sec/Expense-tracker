from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import Connection
from schema.Expense import ExpenseCreate,ExpenseResponse,ExpenseUpdate
from database import get_db


router = APIRouter(
    prefix="/expenses",
    tags=["Expenses"]
)


# -------------------------
# CREATE Expense
# -------------------------

@router.post(
    "", response_model=ExpenseResponse,
)

def create_expense (
    expense : ExpenseCreate,
    db: Connection = Depends (get_db),
):
    with db.cursor() as cursor :
        cursor.execute(
            """
            INSERT INTO expenses (
                title,
                amount,
                category,
                description,
                expense_date
            )
            VALUES (%s,%s,%s,%s,%s)
            RETURNING
                id,
                title, 
                amount, 
                category,
                description,
                expense_date, 
                created_at,
                updated_at
            """,
            (
                expense.title,
                expense.amount,
                expense.category,
                expense.description,
                expense.expense_date,
            ),

            )
        row = cursor.fetchone()

    return ExpenseResponse(
        id=row[0],
        title=row[1],
        amount=row[2],
        category=row[3],
        description=row[4],
        expense_date=row[5],
        created_at=row[6],
        updated_at=row[7],
    )


# -------------------------
# RETRIEVE EXPENSES 
# -------------------------

@router.get(
    "",
    response_model=list[ExpenseResponse],
)
def Retrive_Expense(
    db: Connection = Depends(get_db),
):

    with db.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                id,
                title, 
                amount, 
                category,
                description,
                expense_date, 
                created_at,
                updated_at
            FROM expenses
            ORDER BY id
            """
        )

        rows = cursor.fetchall()

    return [
        ExpenseResponse(
            id=row[0],
            title=row[1],
            amount=row[2],
            category=row[3],
            description=row[4],
            expense_date=row[5],
            created_at=row[6],
            updated_at=row[7],
        )
        for row in rows
    ]


# -------------------------
# GET FOR ONE ID
# -------------------------

@router.get(
    "/{Expense_id}",
    response_model=ExpenseResponse,
)
def For_single_id(
    Expense_id: int,
    db: Connection = Depends(get_db),
):

    with db.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                id,
                title, 
                amount, 
                category,
                description,
                expense_date, 
                created_at,
                updated_at
            FROM expenses
            WHERE id = %s
            """,
            (Expense_id,),
        )

        row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="elle",
        )

    return ExpenseResponse(
       id=row[0],
       title=row[1],
       amount=row[2],
       category=row[3],
       description=row[4],
       expense_date=row[5],
       created_at=row[6],
       updated_at=row[7],
    )




# -------------------------
# UPDATE Expenses
# -------------------------

@router.put(
    "/{Expense_id}",
    response_model=ExpenseResponse,
)
def update_Expense(
    Expense_id: int,
    expense: ExpenseUpdate,
    db: Connection = Depends(get_db),
):

    with db.cursor() as cursor:

        cursor.execute(
            """
            UPDATE expenses
            SET
                title = %s,
                amount = %s,
                category = %s,
                expense_date = %s,
                description = %s,
                updated_at = NOW()
            WHERE id = %s
            RETURNING
                id,
                title, 
                amount, 
                category,
                description,
                expense_date, 
                created_at,
                updated_at
            """,
            (
                expense.title,
                expense.amount,
                expense.category,
                expense.expense_date,
                expense.description,
                Expense_id,
            ),
        )

        row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ID not found",
        )

    return ExpenseResponse(
       id=row[0],
       title=row[1],
       amount=row[2],
       category=row[3],
       description=row[4],
       expense_date=row[5],
       created_at=row[6],
       updated_at=row[7],
    )


# -------------------------
# DELETE Expense
# -------------------------

@router.delete(
    "/{Expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_expense(
    Expense_id: int,
    db: Connection = Depends(get_db),
):

    with db.cursor() as cursor:

        cursor.execute(
            """
            DELETE FROM expenses
            WHERE id = %s
            RETURNING id
            """,
            (Expense_id,),
        )

        row = cursor.fetchone()

    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ID not found",
        )


