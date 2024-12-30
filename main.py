from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import car_router

from routes.garages import garage_router

app = FastAPI()
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(car_router, tags=["Cars"])
app.include_router(garage_router, tags=["Garages"])
@app.get("/")
def root():
    return {
        "message": "Welcome to car-management-backend api, "
                   "Go to /docs to see the swagger documentation :)"
    }
