from fastapi import FastAPI , Depends
from psycopg import Connection
from pydantic import BaseModel
from decimal import Decimal
from datetime import date, datetime

from database import get_db

app = FastAPI()

class ExpenseCreate(BaseModel):
    title: str
    amount: Decimal
    category: str
    description: str | None = None
    expense_date: date

class ExpenseResponse(BaseModel): 
    id: int 
    title: str 
    amount: Decimal 
    category: str
    description: str | None = None 
    expense_date: date 
    created_at: datetime 
    updated_at: datetime

@app.get("/health/db")
def check_database(db: Connection = Depends(get_db)):

    with db.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

    return {
        "status": "ok",
        "database": "connected",
        "test": result[0],
    }

@app.get("/")
def root():
    return{
        "message":"expense tracker API is running"
    }

@app.post(
    "/expenses", response_model=ExpenseResponse,
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