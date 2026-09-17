# PashuRakshak AI — Flask Backend

REST API for the SIH project **PashuRakshak AI**, connected to the existing MySQL database `pashurakshak_ndlm`.

## Prerequisites

- Python 3.10+
- MySQL server with database `pashurakshak_ndlm` already created and populated

## Setup

1. **Navigate to the backend folder**

   ```bash
   cd backend
   ```

2. **Create a virtual environment (recommended)**

   ```bash
   python -m venv venv
   venv\Scripts\activate        # Windows
   # source venv/bin/activate   # macOS / Linux
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   Copy `.env.example` to `.env` and set your MySQL password:

   ```bash
   copy .env.example .env
   ```

   Edit `.env`:

   ```
   GEMINI_API_KEY=your_gemini_api_key
   GEMINI_MODEL=gemini-1.5-flash
   DB_HOST=localhost
   DB_PORT=3306
   DB_NAME=pashurakshak_ndlm
   DB_USER=root
   DB_PASSWORD=your_actual_password
   ```

5. **Run the server**

   ```bash
   python app.py
   ```

   API base URL: `http://localhost:5000`

   CORS is enabled for the React frontend at `http://localhost:5173`.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/login` | Login (farmer / vet / admin) |
| GET | `/api/farmers/<owner_id>` | Farmer profile |
| GET | `/api/farmers/<owner_id>/animals` | Farmer's animals |
| GET | `/api/animals/<animal_id>` | Animal profile |
| GET | `/api/animals/<animal_id>/vaccinations` | Vaccination history |
| GET | `/api/animals/<animal_id>/health` | Disease history |
| GET | `/api/animals/<animal_id>/labreports` | Lab reports |
| POST | `/api/complaints` | Submit complaint |
| GET | `/api/complaints` | List all complaints |
| GET | `/api/complaints/<complaint_id>` | Complaint details |
| PATCH | `/api/complaints/<complaint_id>/status` | Update status |
| POST | `/api/ai/analyze` | Predict disease and submit an AI complaint |
| GET | `/api/dashboard/summary` | Dashboard KPIs |
| GET | `/api/dashboard/species` | Animals by species |
| GET | `/api/dashboard/districts` | Farmers by district |

## Login Examples

**Farmer**

```json
POST /api/login
{ "owner_id": "OWN001", "role": "farmer" }
```

**Vet**

```json
POST /api/login
{ "owner_id": "VET001", "role": "vet" }
```

**Admin (demo)**

```json
POST /api/login
{ "owner_id": "ADMIN01", "role": "admin" }
```

## Complaint Status Flow

`Submitted` → `Vet Assigned` → `Sample Collected` → `Lab Testing` → `Recovered`

## Project Structure

```
backend/
├── app.py
├── database.py
├── config.py
├── models.py
├── routes/
│   ├── auth.py
│   ├── farmers.py
│   ├── animals.py
│   ├── complaints.py
│   └── dashboard.py
├── .env
├── .env.example
├── requirements.txt
└── README.md
```
