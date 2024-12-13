from flask import Flask, render_template, request, redirect, jsonify
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func
from http import HTTPStatus
from dotenv import load_dotenv
import os
import random
from typing import Optional
from dataclasses import dataclass
from http import HTTPStatus
from flask.logging import create_logger
import logging
from werkzeug.middleware.proxy_fix import ProxyFix

load_dotenv()
db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Config
    app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE")
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

    logger = create_logger(app)
    logger.setLevel(logging.INFO)

    db.init_app(app)

    return app


app = create_app()


# Database Models with type hints
@dataclass
class PatientInfo(db.Model):
    __tablename__ = "patient_info"
    id: int = db.Column(db.Integer, primary_key=True)
    patient_no: str = db.Column(db.String(10), unique=True, nullable=False, index=True)
    last_name: str = db.Column(db.String(100), nullable=False)
    other_names: str = db.Column(db.String(100), nullable=False)
    sex: str = db.Column(db.String(10), nullable=False)
    age: int = db.Column(db.Integer, nullable=False)
    dob: datetime = db.Column(db.Date, nullable=False)
    relative: str = db.Column(db.String(100), nullable=False)
    relative_contact: str = db.Column(db.String(11), nullable=False)
    referralinfo = db.relationship("ReferralInfo", back_populates="patient_referred", cascade="all, delete-orphan")


@dataclass
class Doctors(db.Model):
    __tablename__ = "doctors"
    id: int = db.Column(db.Integer, primary_key=True)
    name: str = db.Column(db.String(150), unique=True, nullable=False, index=True)
    referralinfo = db.relationship("ReferralInfo", back_populates="mo")


@dataclass
class ReferralInfo(db.Model):
    __tablename__ = "referral_info"
    id: int = db.Column(db.Integer, primary_key=True)
    referral_no: str = db.Column(db.String(6), nullable=False, index=True)
    referral_date: datetime = db.Column(db.Date, nullable=False)
    patient_id: int = db.Column(db.Integer, db.ForeignKey("patient_info.id"))
    patient_referred = db.relationship("PatientInfo", back_populates="referralinfo")
    mo_id: int = db.Column(db.Integer, db.ForeignKey("doctors.id"))
    mo = db.relationship("Doctors", back_populates="referralinfo")
    referred_from: str = db.Column(db.String(200), nullable=False, default="University Hospital, KNUST")
    referral_time: str = db.Column(db.String(15), nullable=False)
    departure_time: str = db.Column(db.String(15), nullable=False)
    temperature: float = db.Column(db.Float, nullable=False)
    pulse: int = db.Column(db.Integer, nullable=False)
    resp_rate: Optional[int] = db.Column(db.Integer, nullable=True)
    bp_sys: int = db.Column(db.Integer, nullable=False)
    bp_dias: int = db.Column(db.Integer, nullable=False)
    weight: Optional[float] = db.Column(db.Float, nullable=True)
    tews: int = db.Column(db.Integer, nullable=False)
    diagnosis: str = db.Column(db.String(100), nullable=False)
    referral_comment: str = db.Column(db.String(250), nullable=False)


today = datetime.today().date()
date_format = '%Y-%m-%d'
referral_no = str(random.randint(0, 99999)).zfill(5)


@app.route('/')
def home():
    """Serves Hompage"""
    try:
        doctors = Doctors.query.all()
        today_str = datetime.today().strftime('%d-%b-%Y')
        return render_template('index.html',
                               today=today_str,
                               referral_no=referral_no,
                               doctors=doctors)
    except Exception as e:
        app.logger.error(f"Error in home route: {str(e)}")
        return "An error occurred", HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/api/search-patients')
def search_patients():
    """Provides JS with DB info"""
    try:
        query = request.args.get('query', '')
        if len(query) < 3:
            return jsonify([])

        patients = PatientInfo.query.filter(
            PatientInfo.patient_no.ilike(f'%{query}%')
        ).limit(10).all()  # Limit results for performance

        return jsonify([{
            'registrationNumber': p.patient_no,
            'surname': p.last_name,
            'otherNames': p.other_names,
            'sex': p.sex,
            'dateOfBirth': p.dob.strftime('%Y-%m-%d'),
            'age': p.age,
            'contactPerson': p.relative,
            'contactNumber': p.relative_contact
        } for p in patients])
    except Exception as e:
        app.logger.error(f"Error in search_patients: {str(e)}")
        return jsonify({'error': 'Search failed'}), HTTPStatus.INTERNAL_SERVER_ERROR


def ref_no_gen():
    """Generates random referral no."""
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
    mo = request.form.get('officer-name')

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
    referral.mo = Doctors.query.filter_by(name=mo).first()

    db.session.add(referral)
    db.session.commit()


@app.route('/log', methods=['POST', 'GET'])
def log():
    """Saves info from form to DB"""
    patient_reg_no = request.form["patient-reg-no"]
    if request.method == "POST":
        if PatientInfo.query.filter_by(patient_no=patient_reg_no).first():
            save_referralinfo()
        else:
            save_patientinfo()
            save_referralinfo()
        ref_no_gen()
        return redirect('/')


@app.route('/search')
def search_page():
    """Serves search.html"""
    return render_template('search.html')


@app.route('/api/search-referrals/registration/<path:reg_no>')
def search_referrals_by_registration(reg_no):
    """P"""
    try:
        # URL decode the registration number if needed
        import urllib.parse
        reg_no = urllib.parse.unquote(reg_no)

        # print(f"Searching for referrals with registration number: {reg_no}")

        patient = PatientInfo.query.filter_by(patient_no=reg_no).first()

        if not patient:
            # print(f"No patient found with registration number: {reg_no}")
            return jsonify({'error': 'No patient found with this registration number'}), 404

        referrals = ReferralInfo.query.filter_by(patient_id=patient.id) \
            .order_by(ReferralInfo.referral_date.desc()) \
            .all()

        # print(f"Found {len(referrals)} referrals")
        referral_list = []
        for referral in referrals:
            referral_dict = {
                'id': referral.id,
                'referral_date': referral.referral_date.isoformat(),
                'patient_referred': {
                    'patient_no': patient.patient_no,
                    'last_name': patient.last_name,
                    'other_names': patient.other_names
                },
                'diagnosis': referral.diagnosis,
                'referral_comment': referral.referral_comment
            }
            referral_list.append(referral_dict)

        return jsonify(referral_list)
    except Exception as e:
        print(f"Error in search_referrals_by_registration: {str(e)}")  # Debug print
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


@app.route('/api/search-referrals/date/<date>')
def search_referrals_by_date(date):
    try:
        search_date = datetime.strptime(date, '%Y-%m-%d').date()
        referrals = ReferralInfo.query.filter(
            func.date(ReferralInfo.referral_date) == search_date
        ).order_by(ReferralInfo.referral_time.desc()).all()

        referral_list = []
        for referral in referrals:
            patient = referral.patient_referred
            referral_dict = {
                'id': referral.id,
                'referral_date': referral.referral_date.isoformat(),
                'patient_referred': {
                    'patient_no': patient.patient_no,
                    'last_name': patient.last_name,
                    'other_names': patient.other_names
                },
                'diagnosis': referral.diagnosis,
                'referral_comment': referral.referral_comment
            }
            referral_list.append(referral_dict)

        return jsonify(referral_list)
    except Exception as e:
        print(f"Error in search_referrals_by_date: {str(e)}")
        return jsonify({'error': f'Search failed: {str(e)}'}), 500


@app.route('/api/referral/<int:referral_id>')
def get_referral_details(referral_id):
    try:
        referral = ReferralInfo.query.get_or_404(referral_id)
        patient = referral.patient_referred
        mo = referral.mo

        referral_dict = {
            'id': referral.id,
            'referral_no': referral.referral_no,
            'referral_date': referral.referral_date.isoformat(),
            'referral_time': referral.referral_time,
            'departure_time': referral.departure_time,
            'patient_referred': {
                'patient_no': patient.patient_no,
                'last_name': patient.last_name,
                'other_names': patient.other_names,
                'sex': patient.sex,
                'age': patient.age
            },
            'temperature': referral.temperature,
            'pulse': referral.pulse,
            'resp_rate': referral.resp_rate,
            'bp_sys': referral.bp_sys,
            'bp_dias': referral.bp_dias,
            'weight': referral.weight,
            'tews': referral.tews,
            'diagnosis': referral.diagnosis,
            'referral_comment': referral.referral_comment,
            'mo': {
                'name': mo.name
            }
        }

        return jsonify(referral_dict)
    except Exception as e:
        app.logger.error(f"Error in get_referral_details: {str(e)}")
        return jsonify({'error': 'Failed to fetch referral details'}), HTTPStatus.INTERNAL_SERVER_ERROR


@app.route('/api/search-clients')
def search_clients():
    try:
        query = request.args.get('query', '').strip()
        if len(query) < 3:
            return jsonify([])

        patients = PatientInfo.query.filter(
            or_(
                PatientInfo.patient_no.ilike(f'%{query}%'),
                PatientInfo.last_name.ilike(f'%{query}%'),
                PatientInfo.other_names.ilike(f'%{query}%')
            )
        ).limit(10).all()

        patient_list = [
            {
                'registrationNumber': patient.patient_no,
                'name': f"{patient.last_name} {patient.other_names}"
            } for patient in patients
        ]

        return jsonify(patient_list)
    except Exception as e:
        app.logger.error(f"Error in search_patients: {str(e)}")
        return jsonify({'error': 'Failed to fetch patient suggestions'}), HTTPStatus.INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=False)

######################https://github.com/r3tr0t3ch########################
