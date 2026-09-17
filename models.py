from datetime import date, datetime
from decimal import Decimal

from database import db


def _serialize(value):
    """Convert DB values to JSON-safe types."""
    if value is None:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, bool):
        return value
    return value


class Farmer(db.Model):
    __tablename__ = "farmers"

    owner_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(15), unique=True)
    village = db.Column(db.String(100))
    mandal = db.Column(db.String(100))
    district = db.Column(db.String(100))
    state = db.Column(db.String(100), default="Telangana")
    address = db.Column(db.Text)
    created_at = db.Column(db.DateTime)

    animals = db.relationship("Animal", back_populates="farmer", lazy="dynamic")

    def to_dict(self):
        return {
            "owner_id": self.owner_id,
            "full_name": self.full_name,
            "mobile": self.mobile,
            "village": self.village,
            "mandal": self.mandal,
            "district": self.district,
            "state": self.state,
            "address": self.address,
            "created_at": _serialize(self.created_at),
        }


class Animal(db.Model):
    __tablename__ = "animals"

    animal_id = db.Column(db.String(20), primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("farmers.owner_id"), nullable=False)
    animal_name = db.Column(db.String(50))
    species = db.Column(
        db.Enum("Cow", "Buffalo", "Goat", "Sheep", "Poultry"),
        nullable=False,
    )
    breed = db.Column(db.String(50))
    gender = db.Column(db.Enum("Male", "Female"))
    age = db.Column(db.Integer)
    weight = db.Column(db.Numeric(5, 2))
    color = db.Column(db.String(30))
    registration_date = db.Column(db.Date)
    status = db.Column(
        db.Enum("Healthy", "Under Treatment", "Recovered"),
        default="Healthy",
    )

    farmer = db.relationship("Farmer", back_populates="animals")
    vaccinations = db.relationship("Vaccination", back_populates="animal", lazy="dynamic")
    health_records = db.relationship("HealthRecord", back_populates="animal", lazy="dynamic")
    lab_reports = db.relationship("LabReport", back_populates="animal", lazy="dynamic")
    complaints = db.relationship("Complaint", back_populates="animal", lazy="dynamic")

    def to_dict(self, include_owner=False):
        data = {
            "animal_id": self.animal_id,
            "owner_id": self.owner_id,
            "animal_name": self.animal_name,
            "species": self.species,
            "breed": self.breed,
            "gender": self.gender,
            "age": self.age,
            "weight": _serialize(self.weight),
            "color": self.color,
            "registration_date": _serialize(self.registration_date),
            "status": self.status,
        }
        if include_owner and self.farmer:
            data["owner"] = self.farmer.to_dict()
        return data


class Vaccination(db.Model):
    __tablename__ = "vaccinations"

    vaccine_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    animal_id = db.Column(db.String(20), db.ForeignKey("animals.animal_id"), nullable=False)
    vaccine_name = db.Column(db.String(100))
    vaccination_date = db.Column(db.Date)
    next_due_date = db.Column(db.Date)
    vaccinated_by = db.Column(db.String(100))

    animal = db.relationship("Animal", back_populates="vaccinations")

    def to_dict(self):
        return {
            "vaccine_id": self.vaccine_id,
            "animal_id": self.animal_id,
            "vaccine_name": self.vaccine_name,
            "vaccination_date": _serialize(self.vaccination_date),
            "next_due_date": _serialize(self.next_due_date),
            "vaccinated_by": self.vaccinated_by,
        }


class HealthRecord(db.Model):
    __tablename__ = "health_records"

    record_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    animal_id = db.Column(db.String(20), db.ForeignKey("animals.animal_id"), nullable=False)
    disease = db.Column(db.String(100))
    severity = db.Column(db.Enum("Low", "Medium", "High"))
    symptoms = db.Column(db.Text)
    treatment = db.Column(db.Text)
    doctor_name = db.Column(db.String(100))
    visit_date = db.Column(db.Date)
    recovered = db.Column(db.Boolean, default=False)

    animal = db.relationship("Animal", back_populates="health_records")

    def to_dict(self):
        return {
            "record_id": self.record_id,
            "animal_id": self.animal_id,
            "disease": self.disease,
            "severity": self.severity,
            "symptoms": self.symptoms,
            "treatment": self.treatment,
            "doctor_name": self.doctor_name,
            "visit_date": _serialize(self.visit_date),
            "recovered": _serialize(self.recovered),
        }


class LabReport(db.Model):
    __tablename__ = "lab_reports"

    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    animal_id = db.Column(db.String(20), db.ForeignKey("animals.animal_id"), nullable=False)
    test_type = db.Column(db.String(100))
    result = db.Column(db.String(100))
    remarks = db.Column(db.Text)
    report_date = db.Column(db.Date)

    animal = db.relationship("Animal", back_populates="lab_reports")

    def to_dict(self):
        return {
            "report_id": self.report_id,
            "animal_id": self.animal_id,
            "test_type": self.test_type,
            "result": self.result,
            "remarks": self.remarks,
            "report_date": _serialize(self.report_date),
        }


class Complaint(db.Model):
    __tablename__ = "complaints"

    complaint_id = db.Column(db.String(20), primary_key=True)
    animal_id = db.Column(db.String(20), db.ForeignKey("animals.animal_id"), nullable=False)
    vet_id = db.Column(db.String(10), db.ForeignKey("vets.vet_id"))
    complaint_date = db.Column(db.Date)
    symptoms = db.Column(db.Text)
    ai_prediction = db.Column(db.String(100))
    confidence = db.Column(db.Numeric(5, 2))
    priority = db.Column(db.Enum("Low", "Medium", "High"))
    status = db.Column(
        db.Enum(
            "Submitted",
            "Vet Assigned",
            "Sample Collected",
            "Lab Testing",
            "Recovered",
        ),
        default="Submitted",
    )

    animal = db.relationship("Animal", back_populates="complaints")
    vet = db.relationship("Vet", back_populates="complaints")

    def to_dict(self, include_animal=False):
        data = {
            "complaint_id": self.complaint_id,
            "animal_id": self.animal_id,
            "vet_id": self.vet_id,
            "complaint_date": _serialize(self.complaint_date),
            "symptoms": self.symptoms,
            "ai_prediction": self.ai_prediction,
            "confidence": _serialize(self.confidence),
            "priority": self.priority,
            "status": self.status,
        }
        if include_animal and self.animal:
            data["animal"] = self.animal.to_dict()
        return data


class Vet(db.Model):
    __tablename__ = "vets"

    vet_id = db.Column(db.String(10), primary_key=True)
    vet_name = db.Column(db.String(100))
    hospital = db.Column(db.String(150))
    district = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    email = db.Column(db.String(100))

    complaints = db.relationship("Complaint", back_populates="vet", lazy="dynamic")

    def to_dict(self):
        return {
            "vet_id": self.vet_id,
            "vet_name": self.vet_name,
            "hospital": self.hospital,
            "district": self.district,
            "phone": self.phone,
            "email": self.email,
        }
