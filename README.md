# doctor_patient_fastapi_project
## 1. Setup Instructions

### Prerequisites

Make sure the following are installed:

* Python 3.9+
* pip
* Git (optional)
* Docker (optional)

### Step 1: Clone or Extract the Project

If using Git:

```bash
git clone <repository-url>
cd doctor_patient_fastapi
```

Or extract the submitted ZIP file and open the project folder.

### Step 2: Create a Virtual Environment

#### Windows

```powershell
python -m venv .venv
```

Activate the environment:

```powershell
.venv\Scripts\Activate.ps1
```

#### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the project root.

```env
DATABASE_URL=sqlite:///./doctor_patient.db
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Step 5: Start the Application

```bash
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

### Step 6: Open Swagger Documentation

Open the following URL in a browser:

```text
http://127.0.0.1:8000/docs
```

Swagger provides an interactive interface for testing all APIs.

---

## 2. Environment Configuration

The application uses environment variables through a `.env` file.

### Environment Variables

| Variable                      | Description                        | Example                         |
| ----------------------------- | ---------------------------------- | ------------------------------- |
| `DATABASE_URL`                | Database connection URL            | `sqlite:///./doctor_patient.db` |
| `SECRET_KEY`                  | Secret key used to sign JWT tokens | `your-secret-key`               |
| `ALGORITHM`                   | JWT signing algorithm              | `HS256`                         |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT expiration time in minutes     | `60`                            |

### Example `.env`

```env
DATABASE_URL=sqlite:///./doctor_patient.db
SECRET_KEY=replace-with-a-long-random-secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### Security

The `.env` file contains sensitive configuration and should not be committed to GitHub.

The project provides `.env.example` as a template.

---

## 3. How Authentication Works

The application uses **JWT-based authentication**.

### Authentication Flow

```text
User
  │
  ▼
POST /auth/register
  │
  ▼
User Account Created
  │
  ▼
POST /auth/login
  │
  ▼
Username + Password Verified
  │
  ▼
JWT Access Token Generated
  │
  ▼
Client Receives Token
  │
  ▼
Authorization: Bearer <token>
  │
  ▼
Protected API
```

### Step 1: Register

Use:

```http
POST /auth/register
```

Example:

```json
{
  "username": "admin",
  "email": "admin@example.com",
  "password": "admin123",
  "role": "admin"
}
```

A doctor account can also be registered:

```json
{
  "username": "doctor1",
  "email": "doctor1@example.com",
  "password": "doctor123",
  "role": "doctor"
}
```

The password is hashed before it is stored in the database.

---

### Step 2: Login

Use:

```http
POST /auth/login
```

Request:

```json
{
  "username": "admin",
  "password": "admin123"
}
```

Successful login returns:

```json
{
  "access_token": "eyJ...",
  "token_type": "bearer"
}
```

---

### Step 3: Use the JWT Token

Copy the returned `access_token`.

In Swagger:

1. Click **Authorize**.
2. Enter:

```text
Bearer <access_token>
```

3. Click **Authorize**.
4. Click **Close**.

Swagger will then send the JWT token with protected API requests.

---

### Step 4: Authorization

The JWT contains information about the authenticated user, including the user's role.

The application checks the role before allowing protected operations.

### Admin

Admin can:

```text
Create Doctor
Update Doctor
Delete Doctor
Create Patient
View Patients
Assign Patient
```

### Doctor

Doctor can:

```text
View Doctors
View Assigned Patients
View Their Own Patient List
```

A doctor cannot manage doctors or access another doctor's patients.

---

## 4. API Flow Overview

The complete application flow is:

```text
                    ┌───────────────┐
                    │     User      │
                    └───────┬───────┘
                            │
                            ▼
                 ┌───────────────────┐
                 │ Register / Login   │
                 │ /auth/register    │
                 │ /auth/login       │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │   JWT Token       │
                 └─────────┬─────────┘
                           │
                           ▼
                 ┌───────────────────┐
                 │ Authentication    │
                 │ & Authorization   │
                 └─────────┬─────────┘
                           │
                  ┌────────┴────────┐
                  │                 │
                  ▼                 ▼
             ┌──────────┐      ┌──────────┐
             │  Admin   │      │  Doctor  │
             └────┬─────┘      └────┬─────┘
                  │                 │
        ┌─────────┼─────────┐       │
        ▼         ▼         ▼       ▼
     Doctors   Patients  Assignment  Own
                                      Patients
        │         │         │
        └─────────┴─────────┘
                  │
                  ▼
           ┌──────────────┐
           │  SQLite DB   │
           └──────────────┘
```

### Main API Flow

```text
1. Register user
       ↓
2. Login
       ↓
3. Receive JWT token
       ↓
4. Authorize Swagger
       ↓
5. Create Doctor
       ↓
6. Create Patient
       ↓
7. Assign Patient to Doctor
       ↓
8. Doctor logs in
       ↓
9. Doctor views assigned patients
       ↓
10. Authorization prevents access to
    another doctor's patients
```

### API Endpoint Flow

#### Authentication

```text
POST /auth/register
POST /auth/login
```

#### Doctors

```text
POST   /doctors
GET    /doctors
GET    /doctors/{doctor_id}
PUT    /doctors/{doctor_id}
DELETE /doctors/{doctor_id}
```

#### Patients

```text
POST /patients
GET  /patients
GET  /patients/{patient_id}
```

#### Doctor–Patient Assignment

```text
POST /doctors/{doctor_id}/patients/{patient_id}

GET /doctors/{doctor_id}/patients
```

### Example Business Flow

```text
Admin
 │
 ├── Creates Doctor
 │       │
 │       └── Dr. John
 │
 ├── Creates Patient
 │       │
 │       └── Sufiyan
 │
 └── Assigns Patient
         │
         ▼
     Dr. John
         │
         └── Sufiyan
```

After assignment, when Dr. John logs in:

```text
GET /doctors/{doctor_id}/patients
```

returns only the patients assigned to Dr. John.

This ensures that doctors cannot access patients belonging to another doctor.
