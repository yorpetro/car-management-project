from pydantic import BaseModel, Field


class GaragesIn(BaseModel):
    name: str
    location: str
    city: str
    capacity: int


class GaragesOut(BaseModel):
    garage_id: int = Field(alias="id")
    name: str
    location: str
    city: str
    capacity: int

    class Config:
        populate_by_name = True


class CarsIn(BaseModel):
    make: str
    model: str
    productionYear: int
    licensePlate: str
    garageIds: list


class CarsOut(BaseModel):
    car_id: int = Field(alias="id")
    make: str
    model: str
    production_year: int = Field(alias="productionYear")
    license_plate: str = Field(alias="licensePlate")
    garages: list[GaragesOut]

    class Config:
        populate_by_name = True
