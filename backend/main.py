from fastapi import FastAPI , Depends , HTTPException, status
from psycopg import Connection
from schema.Expense import ExpenseCreate,ExpenseResponse ,ExpenseUpdate
from schema.Income import IncomeCreate,IncomeResponse,IncomeUpdate
from database import get_db
from routes import income,expense
app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://expense-tracker-frontend-saurya1.vercel.app/","https://expense-tracker-frontend-git-main-saurya1.vercel.app/","https://expense-tracker-frontend-e7mwn09o0-saurya1.vercel.app/"

    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)





app.include_router(income.router)
app.include_router(expense.router)

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
