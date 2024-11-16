from flask import Flask, render_template, request, redirect, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import random

load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


#Databasees
class PatientInfo(db.Model):
    __tablename__ = "patient_info"
    id = db.Column(db.Integer, primary_key=True)
    patient_no = db.Column(db.String(10), unique=True, nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    other_names = db.Column(db.String(100), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    relative = db.Column(db.String(100), nullable=False)
    relative_contact = db.Column(db.Text(11), nullable=False)
    referralinfo = db.relationship("ReferralInfo", back_populates="patient_referred")


class ReferralInfo(db.Model):
    __tablename__ = "referral_info"
    id = db.Column(db.Integer, primary_key=True)
    referral_no = db.Column(db.String(6), nullable=False)
    referral_date = db.Column(db.Date, nullable=False)

    patient_id = db.Column(db.Integer, db.ForeignKey("patient_info.id"))
    patient_referred = db.relationship("PatientInfo", back_populates="referralinfo")

    referred_from = db.Column(db.String(200), nullable=False, default="University Hospital, KNUST")
    referral_time = db.Column(db.String(15), nullable=False)
    departure_time = db.Column(db.String(15), nullable=False)

    # vitals
    temperature = db.Column(db.Float, nullable=False)
    pulse = db.Column(db.Integer, nullable=False)
    resp_rate = db.Column(db.Integer, nullable=True)
    bp_sys = db.Column(db.Integer, nullable=False)
    bp_dias = db.Column(db.Integer, nullable=False)
    weight = db.Column(db.Float, nullable=True)
    tews = db.Column(db.Integer, nullable=False)

    # mos entry

    diagnosis = db.Column(db.String(100), nullable=False)
    referral_comment = db.Column(db.String(250), nullable=False)
    mo = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()

today = datetime.today().date()
date_format = '%Y-%m-%d'

referral_no = str(random.randint(0, 99999)).zfill(5)

@app.route('/')
def home():
    return render_template('index.html', today=today.strftime(F'%d-%b-%Y'), referral_no=referral_no)


def ref_no_gen():
    global referral_no
    referral_no = str(random.randint(0, 99999)).zfill(5)


def save_patientinfo():
    """Collects Patient Info from form and saves to the database."""
    patient_reg_no = request.form["patient-reg-no"]

    surname = request.form["surname"]
    oname = request.form["other-names"]
    sex = request.form["sex"]
    dob = request.form['dob']
    age = request.form['age']
    relative = request.form["contact-person"]
    relative_contact = request.form["contact-number"]

    patient = PatientInfo()
    patient.patient_no = patient_reg_no
    patient.last_name = surname
    patient.other_names = oname
    patient.sex = sex
    patient.dob = datetime.strptime(dob, date_format).date()
    patient.age = age
    patient.relative = relative
    patient.relative_contact = relative_contact

    db.session.add(patient)
    db.session.commit()


def save_referralinfo():
    """Collects Referral specific Info from form and saves to the database."""
    patient_reg_no = request.form["patient-reg-no"]

    referral_date = today
    facility_referred = request.form["facility-referred"]
    time_referred = request.form["time-referred"]
    departure_time = request.form["departure-time"]

    temperature = float(request.form["temperature"])
    pulse = int(request.form["pulse"])
    resp_rate = int(request.form["respiratory-rate"])
    bp_sys = int(request.form["systolic"])
    bp_dias = int(request.form["diastolic"])
    weight = float(request.form["weight"])
    tews = int(request.form["tewsCode"])

    # complaints = request.form["complaints"]
    diagnosis = request.form['diagnosis']
    referral_comment = request.form['referral-comments']
    mo = request.form['officer-name']

    referral = ReferralInfo()
    referral.patient_referred = PatientInfo.query.filter_by(patient_no=patient_reg_no).first()
    referral.referral_date = referral_date
    referral.referral_no = referral_no
    referral.referral_time = time_referred
    referral.departure_time = departure_time
    referral.temperature = temperature
    referral.pulse = pulse
    referral.resp_rate = resp_rate
    referral.bp_sys = bp_sys
    referral.bp_dias = bp_dias
    referral.weight = weight
    referral.tews = tews
    # referral.patient_complaints = complaints
    referral.diagnosis = diagnosis
    referral.referral_comment = referral_comment
    if facility_referred:
        referral.referred_from = facility_referred
    referral.mo = mo

    db.session.add(referral)
    db.session.commit()


@app.route('/api/search-patients', methods=['GET'])
def search_patients():
    query = request.args.get('query', '')

    if len(query) < 3:
        return jsonify([])

    # Search for patients where patient_no contains the query
    patients = PatientInfo.query.filter(
        PatientInfo.patient_no.ilike(f'%{query}%')
    ).all()

    # Format the results
    results = []
    for patient in patients:
        results.append({
            'registrationNumber': patient.patient_no,
            'surname': patient.last_name,
            'otherNames': patient.other_names,
            'sex': patient.sex,
            'dateOfBirth': patient.dob.strftime('%Y-%m-%d'),
            'age': patient.age,
            'contactPerson': patient.relative,
            'contactNumber': patient.relative_contact
        })

    return jsonify(results)


@app.route('/log', methods=['POST', 'GET'])
def log():
    patient_reg_no = request.form["patient-reg-no"]
    if request.method == "POST":
        if PatientInfo.query.filter_by(patient_no=patient_reg_no).first():
            save_referralinfo()
        else:
            save_patientinfo()
            save_referralinfo()
        ref_no_gen()
        return redirect('/')


if __name__ == "__main__":
    app.run(debug=True)
