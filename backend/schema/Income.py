from pydantic import BaseModel, Field
from decimal import Decimal
from datetime import date, datetime
from typing import Literal

class IncomeCreate(BaseModel):
    title: str
    amount: Decimal
    category: Literal["salary", "business", "freelance"] = Field(examples=["salary", "business", "freelance"])
    description: str | None = None
    income_date: date

class IncomeResponse(BaseModel):
    id: int
    title: str
    amount: Decimal
    category: Literal["salary", "business", "freelance"] = Field(examples=["salary", "business", "freelance"])
    description: str | None = None
    income_date: date
    created_at: datetime
    updated_at: datetime

class IncomeUpdate(BaseModel):
    title: str | None = None
    amount: Decimal | None = None
    category: Literal["salary", "business", "freelance"] = Field(examples=["salary", "business", "freelance"])
    income_date: date | None = None 
    description: str | None = None
