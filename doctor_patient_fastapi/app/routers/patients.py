from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Patient, User, Doctor
from app.schemas import PaginatedPatients, PatientCreate, PatientResponse

router = APIRouter(prefix="/patients", tags=["Patients"])


@router.post("", response_model=PatientResponse, status_code=status.HTTP_201_CREATED)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    patient = Patient(
        name=payload.name,
        age=payload.age,
        phone=payload.phone,
    )
    db.add(patient)
    db.commit()
    db.refresh(patient)
    return patient


@router.get("", response_model=PaginatedPatients)
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    name: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    query = db.query(Patient)

    # Admin can view all patients. A doctor can view only assigned patients.
    if current_user.role == "doctor":
        doctor = db.query(Doctor).filter(Doctor.email == current_user.email).first()
        if not doctor:
            raise HTTPException(
                status_code=403,
                detail="Doctor profile not found",
            )
        query = query.filter(Patient.doctors.any(Doctor.id == doctor.id))

    if name:
        query = query.filter(Patient.name.ilike(f"%{name}%"))

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items,
    }


@router.get("/{patient_id}", response_model=PatientResponse)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if current_user.role == "doctor":
        doctor = db.query(Doctor).filter(Doctor.email == current_user.email).first()
        if not doctor or doctor not in patient.doctors:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only view your assigned patients",
            )

    return patient
