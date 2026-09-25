# Doctor-Patient Management API

A complete FastAPI backend assignment implementing:

- JWT authentication
- Role-based authorization
- Admin and Doctor roles
- Doctor management
- Patient management
- Doctor-patient assignment
- SQLAlchemy + SQLite persistence
- Pydantic validation
- Soft delete for doctors
- Pagination and filtering
- Pytest test setup
- Docker support
- Environment-based configuration

## 1. Project Structure

```text
doctor_patient_fastapi/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── auth.py
│   └── routers/
│       ├── __init__.py
│       ├── auth.py
│       ├── doctors.py
│       └── patients.py
│
├── tests/
│   ├── __init__.py
│   └── test_api.py
│
├── .env.example
├── .gitignore
├── Dockerfile
├── requirements.txt
└── README.md
```

## 2. Assumptions

1. SQLite is used because it is explicitly allowed by the assignment.
2. A registered user can have either `admin` or `doctor` role.
3. A doctor application user is linked to a Doctor record using the same email address.
4. Admin users can create, update, soft-delete and assign doctors/patients.
5. Authenticated users can create patients because the assignment does not restrict `POST /patients` to Admin only.
6. Doctors can read only their assigned patients.
7. Admin users can read all doctors and patients.
8. Deleting a doctor is implemented as a soft delete by setting `is_active=false`.
9. The database tables are automatically created at application startup. For a larger production system, Alembic migrations are recommended.
10. JWT access tokens expire according to `ACCESS_TOKEN_EXPIRE_MINUTES`.

## 3. Setup

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Run:

```bash
uvicorn app.main:app --reload
```

Open Swagger:

```text
http://127.0.0.1:8000/docs
```

## 4. Authentication Flow

### Step 1: Register

`POST /auth/register`

Example Admin:

```json
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "admin123",
  "role": "admin"
}
```

Example Doctor user:

```json
{
  "username": "doctor1",
  "email": "doctor1@example.com",
  "password": "doctor123",
  "role": "doctor"
}
```

### Step 2: Login

`POST /auth/login`

```json
{
  "username": "admin",
  "password": "admin123"
}
```

The API returns a JWT:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

In Swagger, click **Authorize** and enter:

```text
Bearer <access_token>
```

The JWT contains the user ID, username, role and expiry.

## 5. Authorization Rules

| API area | Admin | Doctor |
|---|---:|---:|
| Register/Login | Yes | Yes |
| Create Doctor | Yes | No |
| List Doctors | Yes | Yes |
| Get Doctor | Yes | Yes |
| Update Doctor | Yes | No |
| Delete Doctor | Yes | No |
| Create Patient | Yes | Yes |
| List Patients | All | Assigned only |
| Get Patient | All | Assigned only |
| Assign Patient | Yes | No |
| Get Doctor's Patients | Yes | Own doctor only |

## 6. Doctor APIs

### Create doctor

`POST /doctors`

Admin only.

```json
{
  "name": "Dr. John Smith",
  "specialization": "Cardiology",
  "email": "doctor1@example.com"
}
```

### List doctors

`GET /doctors`

Optional:

```text
GET /doctors?skip=0&limit=20&specialization=cardio
```

### Get doctor

`GET /doctors/{doctor_id}`

### Update doctor

`PUT /doctors/{doctor_id}`

### Soft delete doctor

`DELETE /doctors/{doctor_id}`

The row is not physically removed. `is_active` becomes `false`.

## 7. Patient APIs

### Create patient

`POST /patients`

```json
{
  "name": "Sufiyan",
  "age": 22,
  "phone": "9876543210"
}
```

Validation:

- age must be greater than 0
- phone must contain 10-15 digits

### List patients

`GET /patients`

Pagination:

```text
GET /patients?skip=0&limit=10
```

Filtering:

```text
GET /patients?name=sufi
```

Doctors automatically receive only patients assigned to their doctor profile.

### Get patient

`GET /patients/{patient_id}`

Doctors receive `403 Forbidden` when the patient is not assigned to them.

## 8. Doctor-Patient Assignment

Admin assigns a patient:

`POST /doctors/{doctor_id}/patients/{patient_id}`

Example:

```text
POST /doctors/1/patients/1
```

Get assigned patients:

`GET /doctors/{doctor_id}/patients`

A doctor can only request their own doctor ID. Access to another doctor's patient list returns `403 Forbidden`.

## 9. Validation and Errors

Examples:

- Duplicate email -> `400 Bad Request`
- Invalid JWT -> `401 Unauthorized`
- Missing/invalid authentication -> `401 Unauthorized`
- Doctor trying to perform an Admin action -> `403 Forbidden`
- Doctor requesting another doctor's patients -> `403 Forbidden`
- Missing doctor/patient -> `404 Not Found`
- Invalid age -> `422 Unprocessable Entity`
- Invalid phone -> `422 Unprocessable Entity`

## 10. Recommended API Testing Order

1. Register Admin.
2. Login as Admin.
3. Copy the JWT.
4. Authorize Swagger with the JWT.
5. Create a Doctor.
6. Register a Doctor user using the same email as the Doctor record.
7. Create a Patient.
8. Assign the Patient to the Doctor.
9. Login as the Doctor.
10. Authorize Swagger with the Doctor token.
11. Call `GET /patients` and verify only assigned patients are returned.
12. Try to access another doctor's patients and verify `403`.
13. Login as Admin again.
14. Test doctor update.
15. Test doctor soft delete.
16. Test invalid phone and age validation.
17. Test duplicate doctor email.
18. Test an invalid/expired JWT.

## 11. Running Tests

```bash
pytest
```

## 12. Docker

Build:

```bash
docker build -t doctor-patient-api .
```

Run:

```bash
docker run -p 8000:8000 doctor-patient-api
```

Then open:

```text
http://127.0.0.1:8000/docs
```

## 13. Production Improvements

For production deployment, the following can be added:

- PostgreSQL
- Alembic migrations
- Redis-based rate limiting
- Refresh tokens
- Email verification
- Password reset
- Structured logging
- Centralized exception handlers
- Docker Compose
- CI/CD pipeline
- HTTPS
- Secret manager
- More comprehensive unit/integration tests

## 14. Submission Checklist

- [x] FastAPI
- [x] Pydantic
- [x] SQLAlchemy
- [x] SQLite
- [x] JWT authentication
- [x] Register API
- [x] Login API
- [x] Admin role
- [x] Doctor role
- [x] Doctor CRUD
- [x] Soft delete
- [x] Patient APIs
- [x] Doctor-patient assignment
- [x] Validation
- [x] HTTPException error handling
- [x] Routers
- [x] Models
- [x] Schemas
- [x] Auth module
- [x] Database layer
- [x] Environment configuration
- [x] Pagination
- [x] Filtering
- [x] Pytest setup
- [x] Dockerfile
- [x] README
