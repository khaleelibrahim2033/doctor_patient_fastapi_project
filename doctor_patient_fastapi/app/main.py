from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, doctors, patients

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Doctor-Patient Management API",
    description="End-to-end FastAPI backend with JWT authentication, RBAC, doctors, patients, and assignments.",
    version="1.0.0",
)

app.include_router(auth.router)
app.include_router(doctors.router)
app.include_router(patients.router)

@app.get("/", tags=["Health"])
def root():
    return {"message": "Doctor-Patient Management API is running"}
