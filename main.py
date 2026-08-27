from fastapi import FastAPI , Depends
from psycopg import Connection

from database import get_db

app = FastAPI()





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
