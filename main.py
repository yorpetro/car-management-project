from fastapi import FastAPI
from routes import car_router
app = FastAPI()

app.include_router(car_router, tags=["Cars"])
@app.get("/")
def root():
    return {
        "message": "Welcome to car-management-backend api, "
                   "Go to /docs to see the swagger documentation :)"
    }
