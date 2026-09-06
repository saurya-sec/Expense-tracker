from pydantic import BaseModel,Field
from decimal import Decimal
from datetime import date, datetime
from typing import Literal


class ExpenseCreate(BaseModel):
    title: str
    amount: Decimal
    category: Literal["food", "transport", "rent"]=Field(examples=["food","transport","rent"])
    description: str | None = None
    expense_date: date

class ExpenseResponse(BaseModel): 
    id: int 
    title: str 
    amount: Decimal 
    category: Literal["food", "transport", "rent"]=Field(examples=["food","transport","rent"])
    description: str | None = None 
    expense_date: date 
    created_at: datetime 
    updated_at: datetime

class ExpenseUpdate(BaseModel):
    title: str | None = None
    amount: Decimal | None = None
    category: Literal["food", "transport", "rent"]=Field(examples=["food","transport","rent"])
    expense_date: date | None = None
    description: str | None = None
