from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def inicio():
    return {"message": "App funcionando coretamente !"}
