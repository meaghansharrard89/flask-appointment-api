from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData
from sqlalchemy.orm import validates
from sqlalchemy.ext.associationproxy import association_proxy
from sqlalchemy_serializer import SerializerMixin
import string, datetime

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    }
)
db = SQLAlchemy(metadata=metadata)


class Patient(db.Model, SerializerMixin):
    __tablename__ = "patient_table"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # Relationships

    appointments = db.relationship(
        "Appointment", back_populates="patient", cascade="all, delete-orphan"
    )
    doctors = association_proxy("appointments", "doctor")

    # Serialization rules

    serialize_rules = ("-appointments.patient",)


class Appointment(db.Model, SerializerMixin):
    __tablename__ = "appointment_table"

    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String, nullable=False)

    # Foreign keys

    doctor_id = db.Column(db.Integer, db.ForeignKey("doctor_table.id"), nullable=False)
    patient_id = db.Column(
        db.Integer, db.ForeignKey("patient_table.id"), nullable=False
    )

    # Relationships

    patient = db.relationship("Patient", back_populates="appointments")
    doctor = db.relationship("Doctor", back_populates="appointments")

    # Serialization rules

    serialize_rules = (
        "-patient.appointments",
        "-doctor.appointments",
    )

    # Validation

    @validates("day")
    def validate_day(self, key, value):
        if value not in self.day_choices:
            raise ValueError("Invalid day. Must be between Monday and Friday.")
        return value


class Doctor(db.Model, SerializerMixin):
    __tablename__ = "doctor_table"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    specialty = db.Column(db.String, nullable=False)

    # Relationships

    appointments = db.relationship(
        "Appointment", back_populates="doctor", cascade="all, delete-orphan"
    )
    patients = association_proxy("appointments", "patient")

    # Serialization rules

    serialize_rules = ("-appointments.doctor",)

    # Validation

    @validates("name")
    def validate_name(self, key, value):
        if not value.startswith("Dr."):
            raise ValueError("Doctor's name must start with 'Dr.'")
        return value
