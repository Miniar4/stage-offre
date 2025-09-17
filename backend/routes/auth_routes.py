# cSpell:disable
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from models import db, User
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import cross_origin
from datetime import datetime


auth_bp = Blueprint('auth_bp', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    nom = data.get('nom')
    password = data.get('password')
    role = data.get('role', 'stagiaire')  
    age = data.get('age')
    date_of_birth = data.get('dateOfBirth')
    phone = data.get('phone')
    address = data.get('address')
    university = data.get('university')
    education = data.get('education')
    skills = data.get('skills')

    if not email or not password or not nom:
        return jsonify({"error": "Données manquantes"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email déjà utilisé"}), 400

    user = User(
            nom=nom, 
            email=email,
            role=role, 
            age=age,
            phone=phone,
            address=address,
            university=university,
            education=education,
            skills=skills)
    if date_of_birth:
        try:
            user.date_of_birth = datetime.strptime(date_of_birth, '%Y-%m-%d').date()
        except ValueError:
            pass
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "Inscription réussie"}), 201

@auth_bp.route('/login', methods=['POST'])
@cross_origin(origin='http://localhost:4200', supports_credentials=True)
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Données manquantes"}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "Email ou mot de passe invalide"}), 401

    access_token = create_access_token(identity={"id": user.id, "role": user.role})
    return jsonify({"access_token": access_token, "user": {"id": user.id, "nom": user.nom, "email": user.email, "role": user.role}}), 200
