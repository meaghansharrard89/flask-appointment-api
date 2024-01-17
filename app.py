#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restful import Api, Resource
import datetime
from models import db, Doctor, Patient, Appointment

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)


@app.get("/")
def index():
    return "doctor/patient"


class Doctors(Resource):
    def get_doctors():
        doctors = Doctor.query.all()
        return [d.to_dict(rules=["-appointments"]) for d in doctors], 200

    def post(self):
        data = request.get_json()
        doctor = Doctor()
        try:
            doctor.name = data.get("name")
            doctor.specialty = data.get("specialty")
            db.session.add(doctor)
            db.session.commit()
            return make_response(doctor.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Doctors, "/doctors")


class DoctorsById(Resource):
    def get_doctor_by_id(id):
        doctor = db.session.get(Doctor, id)
        if not doctor:
            return {"error": "not found"}, 404
        return (
            doctor.to_dict(
                rules=["-appointments.patient_id", "-appointments.doctor_id"]
            ),
            200,
        )


api.add_resource(DoctorsById, "/doctors/<int:id>")


class PatientsById(Resource):
    def get_patient_by_id(id):
        patient = db.session.get(Patient, id)
        if not patient:
            return {"error": "not found"}, 404
        patient_dict = patient.to_dict(rules=["-appointments"])
        doctor_dicts = [d.to_dict(rules=["-appointments"]) for d in patient.doctors]
        patient_dict["doctors"] = doctor_dicts
        return patient_dict, 200

    def patch_patient(id):
        try:
            data = request.json
            patient = db.session.get(Patient, id)
            if not patient:
                return {"error": "not found"}, 404
            for key in data:
                setattr(patient, key, data[key])
            db.session.add(patient)
            db.session.commit()
            return patient.to_dict(rules=["-appointments"])
        except Exception as e:
            return {"error": str(e)}, 404


api.add_resource(PatientsById, "/patients/<int:id>")


class Appointments(Resource):
    def post(self):
        data = request.get_json()
        appointment = Appointment()
        try:
            appointment.day = data.get("day")
            appointment.doctor_id = data.get("doctor_id")
            appointment.patient_id = data.get("patient_id")
            db.session.add(appointment)
            db.session.commit()
            return make_response(appointment.to_dict(), 201)
        except ValueError:
            return make_response({"errors": ["validation errors"]}, 400)


api.add_resource(Appointments, "/appointments")


if __name__ == "__main__":
    app.run(port=5555, debug=True)
