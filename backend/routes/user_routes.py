# backend/routes/user.py

import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask import Blueprint, request, jsonify
from models import db, Application

user_bp = Blueprint('user_bp', __name__)

UPLOAD_FOLDER_CV = 'uploads/cv'
UPLOAD_FOLDER_MOTIVATION = 'uploads/motivation'

# Créer les dossiers si non existants
os.makedirs(UPLOAD_FOLDER_CV, exist_ok=True)
os.makedirs(UPLOAD_FOLDER_MOTIVATION, exist_ok=True)

@user_bp.route('/<int:user_id>/apply-offer/<int:offer_id>', methods=['POST'])
def postuler_offre(user_id, offer_id):
    data = request.form

    name = data.get('name')
    email = data.get('email')
    university = data.get('university')
    education = data.get('education')
    duration = data.get('duration')
    motivation = data.get('motivation')

    file_cv = request.files.get('cv')
    file_motivation = request.files.get('motivationLetter')

    # Vérification des champs obligatoires
    if not all([name, email, university, education, duration, motivation]):
        return jsonify({'error': 'Tous les champs sont requis'}), 400

    if not file_cv or not file_motivation:
        return jsonify({'error': 'CV et lettre de motivation requis'}), 400

    # Sécuriser les noms de fichiers
    cv_filename = secure_filename(file_cv.filename)
    motivation_filename = secure_filename(file_motivation.filename)

    # Chemins de sauvegarde
    cv_path = os.path.join(UPLOAD_FOLDER_CV, cv_filename)
    motivation_path = os.path.join(UPLOAD_FOLDER_MOTIVATION, motivation_filename)

    # Sauvegarde des fichiers
    try:
        file_cv.save(cv_path)
        file_motivation.save(motivation_path)
    except Exception as e:
        return jsonify({'error': f'Échec de la sauvegarde des fichiers : {str(e)}'}), 500

    # Enregistrement en base de données
    application = Application(
        user_id=user_id,
        offer_id=offer_id,
        name=name,
        email=email,
        university=university,
        education=education,
        duration=duration,
        motivation=motivation,
        cv_filename=cv_filename,
        motivation_filename=motivation_filename,
        statut='en attente'
    )

    try:
        db.session.add(application)
        db.session.commit()
    except Exception as e:
        return jsonify({'error': f'Erreur base de données : {str(e)}'}), 500

    return jsonify({'message': 'Candidature soumise avec succès'}), 201


@user_bp.route('/users/<int:user_id>/attestation', methods=['GET'])
def get_attestation(user_id):
    user = User.query.get(user_id)
    if not user or not user.attestation_filename:
        return jsonify({'error': 'Aucune attestation'}), 404

    return send_from_directory('uploads/attestations', user.attestation_filename, as_attachment=True)
