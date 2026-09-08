from fastapi import APIRouter, Depends, HTTPException, status
from psycopg import Connection
from schema.Income import IncomeCreate,IncomeResponse,IncomeUpdate
from database import get_db


router = APIRouter(
    prefix="/income",
    tags=["Income"]
)



# -------------------------
# CREATE income
# -------------------------

@router.post(
        "",
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
@router.get(
"",
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



@router.get(
        "/{income_id}",
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


@router.put("/{income_id}",
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


@router.delete(
        "/{income_id}",
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
                


