from flask import Flask, render_template, request, redirect, url_for, flash
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


class PatientInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    referral_no = db.Column(db.String(6), nullable=False)
    patient_no = db.Column(db.String(10), unique=True, nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    other_names = db.Column(db.String(100), nullable=False)
    sex = db.Column(db.String(10), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    dob = db.Column(db.Date, nullable=False)
    relative = db.Column(db.String(100), nullable=False)
    relative_contact = db.Column(db.Text(11), nullable=False)
    referred_from = db.Column(db.String(200), nullable=False, default="University Hospital, KNUST")
    referral_time = db.Column(db.String(15), nullable=False)
    departure_time = db.Column(db.String(15), nullable=False)

    # vitals
    temperature = db.Column(db.Float, nullable=False)
    pulse = db.Column(db.Integer, nullable=False)
    resp_rate = db.Column(db.Integer, nullable=True)
    bp = db.Column(db.String(7), nullable=False)
    weight = db.Column(db.Float, nullable=True)

    # mos entry
    patient_complaints = db.Column(db.String(250), nullable=False)
    diagnosis = db.Column(db.String(100), nullable=False)
    referral_comment = db.Column(db.String(250), nullable=False)
    mo = db.Column(db.String(100), nullable=False)
    # position = db.Column(db.String(100), nullable=False)
    # signature = db.Column(db.String(100), nullable=False)


with app.app_context():
    db.create_all()

today = datetime.today().date()
format = '%Y-%m-%d'
referral_no = str(random.randint(0, 99999)).zfill(5)


@app.route('/')
def home():
    return render_template('index.html', today=today.strftime(F'%d-%b-%Y'), referral_no=referral_no)


@app.route('/log', methods=['POST', 'GET'])
def log():
    # referral details
    patient_reg_no = request.form["patient-reg-no"]
    facility_referred = request.form["facility-referred"]
    time_referred = request.form["time-referred"]
    departure_time = request.form["departure-time"]

    # patient info
    surname = request.form["surname"]
    oname = request.form["other-names"]
    sex = request.form["sex"]
    dob = request.form['dob']
    age = request.form['age']
    relative = request.form["contact-person"]
    relative_contact = request.form["contact-number"]

    # examination findings
    # vitals
    temperature = request.form["temperature"]
    pulse = request.form["pulse"]
    resp_rate = request.form["respiratory-rate"]
    # divide sytolic/dystolic
    bp = request.form["bp"]
    weight = request.form["weight"]

    complaints = request.form["complaints"]
    diagnosis = request.form['diagnosis']
    referral_comment = request.form['referral-comments']
    mo = request.form['officer-name']
    # position = request.form['position']
    # signature = request.form['signature']

    if request.method == "POST":
        patient = PatientInfo()
        patient.patient_no = patient_reg_no
        patient.referral_no = referral_no
        patient.last_name = surname
        patient.other_names = oname
        patient.sex = sex
        patient.dob = datetime.strptime(dob, format).date()
        patient.age = age
        # patient.referred_from = facility_referred
        patient.referral_time = time_referred
        patient.departure_time = departure_time
        patient.relative = relative
        patient.relative_contact = relative_contact
        patient.temperature = temperature
        patient.pulse = pulse
        patient.resp_rate = resp_rate
        patient.bp = bp
        patient.weight = weight
        patient.patient_complaints = complaints
        patient.diagnosis = diagnosis
        patient.referral_comment = referral_comment
        patient.mo = mo
        # patient.position = position
        # patient.signature = signature

        db.session.add(patient)
        db.session.commit()
        print(type(patient.dob))
        return render_template('index.html', today=today.strftime(F'%d-%b-%Y'), referral_no=referral_no)


if __name__ == "__main__":
    app.run(debug=True)
