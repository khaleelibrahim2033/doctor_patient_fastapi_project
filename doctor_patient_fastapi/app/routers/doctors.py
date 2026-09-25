from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth import get_current_user, require_admin
from app.database import get_db
from app.models import Doctor, Patient, User
from app.schemas import DoctorCreate, DoctorResponse, DoctorUpdate, PatientResponse

router = APIRouter(prefix="/doctors", tags=["Doctors"])


@router.post("", response_model=DoctorResponse, status_code=status.HTTP_201_CREATED)
def create_doctor(
    payload: DoctorCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    if db.query(Doctor).filter(Doctor.email == str(payload.email)).first():
        raise HTTPException(status_code=400, detail="Doctor email already exists")

    doctor = Doctor(
        name=payload.name,
        specialization=payload.specialization,
        email=str(payload.email),
    )
    db.add(doctor)
    db.commit()
    db.refresh(doctor)
    return doctor


@router.get("", response_model=list[DoctorResponse])
def list_doctors(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    specialization: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    query = db.query(Doctor)

    if specialization:
        query = query.filter(Doctor.specialization.ilike(f"%{specialization}%"))

    return query.offset(skip).limit(limit).all()


@router.get("/{doctor_id}", response_model=DoctorResponse)
def get_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return doctor


@router.put("/{doctor_id}", response_model=DoctorResponse)
def update_doctor(
    doctor_id: int,
    payload: DoctorUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    if payload.email is not None:
        existing = (
            db.query(Doctor)
            .filter(Doctor.email == str(payload.email), Doctor.id != doctor_id)
            .first()
        )
        if existing:
            raise HTTPException(status_code=400, detail="Doctor email already exists")

    for field, value in payload.model_dump(exclude_unset=True).items():
        if field == "email" and value is not None:
            value = str(value)
        setattr(doctor, field, value)

    db.commit()
    db.refresh(doctor)
    return doctor


@router.delete("/{doctor_id}", response_model=DoctorResponse)
def delete_doctor(
    doctor_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # Soft delete: record remains in the database.
    doctor.is_active = False
    db.commit()
    db.refresh(doctor)
    return doctor


@router.post("/{doctor_id}/patients/{patient_id}", response_model=PatientResponse)
def assign_patient(
    doctor_id: int,
    patient_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(require_admin),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    patient = db.query(Patient).filter(Patient.id == patient_id).first()

    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    if not doctor.is_active:
        raise HTTPException(status_code=400, detail="Cannot assign patient to inactive doctor")
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    if patient not in doctor.patients:
        doctor.patients.append(patient)
        db.commit()

    return patient


@router.get("/{doctor_id}/patients", response_model=list[PatientResponse])
def get_doctor_patients(
    doctor_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    doctor = db.query(Doctor).filter(Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    # A doctor can only access the patients assigned to their own doctor record.
    if current_user.role == "doctor":
        linked_doctor = db.query(Doctor).filter(Doctor.email == current_user.email).first()
        if not linked_doctor or linked_doctor.id != doctor_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Doctors can only view their own assigned patients",
            )

    return doctor.patients
