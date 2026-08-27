from fastapi import FastAPI

app = FastAPI()



@app.get("/")
def root():
    return{
        "message":"expense tracker API is running"
    }
