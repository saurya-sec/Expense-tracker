from fastapi import FastAPI , Depends , HTTPException, status
from psycopg import Connection
from schema.Expense import ExpenseCreate,ExpenseResponse ,ExpenseUpdate
from schema.Income import IncomeCreate,IncomeResponse,IncomeUpdate
from database import get_db

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Health Check
# -------------------------
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

# -------------------------
# Root
# -------------------------
@app.get("/")
def root():
    return{
        "message":"expense tracker API is running"
    }

# -------------------------
# CREATE Expense
# -------------------------

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


# -------------------------
# RETRIEVE EXPENSES 
# -------------------------

@app.get(
    "/expenses",
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

@app.get(
    "/expenses/{Expense_id}",
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

@app.put(
    "/expenses/{Expense_id}",
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

@app.delete(
    "/expenses/{Expense_id}",
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




# -------------------------
# Health Check
# -------------------------

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

# -------------------------
# Root
# -------------------------

@app.get("/")
def root():
    return {
        "message": "income tracker API is running"
        }

# -------------------------
# CREATE income
# -------------------------

@app.post(
        "/income",
        response_model=IncomeResponse,
        )
def create_income(
    income: IncomeCreate,
    db: Connection = Depends(get_db),
    ):
    with db.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO income (
            title,
            amount,
            category,
            description,
            income_date)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING
            id,
            title,
            amount,
            category,
            description,
            income_date,
            created_at,
            updated_at
            """,
            (
                income.title,
                income.amount,
                income.category,
                income.description,
                income.income_date,
                ),
                )
        row = cursor.fetchone()
        return IncomeResponse(
            id=row[0],
            title=row[1],
            amount=row[2],
            category=row[3],
            description=row[4],
            income_date=row[5],
            created_at=row[6],
            updated_at=row[7],
            )

# -------------------------
# RETRIEVE INCOME
# -------------------------
@app.get(
"/income",
response_model=list[IncomeResponse],
)
def retrieve_income(
    db: Connection = Depends(get_db),):
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
            ORDER BY id
            """

            )
        rows = cursor.fetchall()
        return [
            IncomeResponse(
                id=row[0],
                title=row[1],
                amount=row[2],
                category=row[3],
                description=row[4],
                income_date=row[5],
                created_at=row[6],
                updated_at=row[7],
                )
                for row in rows
                ]

# -------------------------
# GET for ONE ID
# -------------------------



@app.get(
        "/income/{income_id}",
        response_model=IncomeResponse,
        )
def for_single_id(
    income_id: int,
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
                income_date,
                created_at,
                updated_at
            FROM income
            WHERE id = %s
            """,
            (income_id,),
            )
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ID not found",
                )
        return IncomeResponse(
                id=row[0],
                title=row[1],
                amount=row[2],
                category=row[3],
                description=row[4],
                income_date=row[5],
                created_at=row[6],updated_at=row[7],
                )

# -------------------------
#  UPDATE income
# -------------------------


@app.put("/income/{income_id}",
         response_model=IncomeResponse,)
def update_income(
    income_id: int,
    income: IncomeUpdate,
    db: Connection = Depends(get_db),):
    with db.cursor() as cursor:
        cursor.execute(
            """
            UPDATE income
            SET
                title = %s,
                amount = %s,
                category = %s,
                income_date = %s,
                description = %s,
            updated_at = NOW()
            WHERE id = %s
            RETURNING
            id,
            title,
            amount,
            category,
            description,
            income_date,
            created_at,
            updated_at
            """,
            (
                income.title,
                income.amount,
                income.category,
                income.income_date,
                income.description,
                income_id,
            ),
            )
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ID not found",
                )
        return IncomeResponse(
            id=row[0],
            title=row[1],
            amount=row[2],
            category=row[3],
            description=row[4],
            income_date=row[5],
            created_at=row[6],
            updated_at=row[7],
            )

# -------------------------
# DELETE Income
# -------------------------


@app.delete(
        "/income/{income_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        )
def delete_income(
    income_id: int,
    db: Connection = Depends(get_db),
    ):
    with db.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM income
            WHERE id = %s
            RETURNING id
            """,
            (income_id,),
            )
        row = cursor.fetchone()
        if row is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="ID not found",
                )
                


