from fastapi import FastAPI , Depends
from psycopg import Connection
from database import get_db
from routes import income,expense,auth ,chatbot ,state ,statement

app = FastAPI()
from fastapi.middleware.cors import CORSMiddleware


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://expense-tracker-frontend-saurya1.vercel.app","https://expense-tracker-frontend-git-main-saurya1.vercel.app","https://expense-tracker-frontend-e7mwn09o0-saurya1.vercel.app"

    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(income.router)
app.include_router(expense.router)
app.include_router(auth.router)
app.include_router(chatbot.router)
app.include_router(state.router)
app.include_router(statement.router)


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
