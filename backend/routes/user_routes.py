import os
from werkzeug.utils import secure_filename
from flask import send_from_directory, Blueprint, request, jsonify, send_file, abort
from models import db, Application, User, Stagiaire

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

@user_bp.route('/user/<int:user_id>/candidatures', methods=['GET'])
def get_user_candidatures(user_id):
    try:
        # Récupérer les candidatures de l'utilisateur avec les informations du stagiaire si accepté
        candidatures = db.session.query(Application).filter_by(user_id=user_id).all()
        
        result = []
        for app in candidatures:
            candidature_data = app.serialize()
            
            # Si la candidature est acceptée, récupérer les infos du stagiaire
            if app.statut == 'accepté':
                stagiaire = db.session.query(Stagiaire).filter_by(application_id=app.id).first()
                if stagiaire:
                    candidature_data.update({
                        'sujet': stagiaire.sujet,
                        'encadrant': stagiaire.encadrant,
                        'attestation_filename': stagiaire.attestation_filename
                    })
            
            result.append(candidature_data)
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_profile(user_id):
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Utilisateur non trouvé'}), 404
        return jsonify(user.serialize()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/user/<int:stagiaire_id>/attestation')
def get_attestation(stagiaire_id):
    # Récupère le stagiaire et son fichier d'attestation
    stagiaire = db.session.query(Stagiaire).filter_by(id=stagiaire_id).first()
    if not stagiaire or not stagiaire.attestation_filename:
        return abort(404, description="Attestation not found")

    file_path = os.path.join('uploads', 'attestations', stagiaire.attestation_filename)
    if not os.path.exists(file_path):
        return abort(404, description="Attestation file not found on server")

    return send_file(file_path, mimetype='application/pdf', as_attachment=True,
                     download_name='attestation.pdf')

@user_bp.route('/user/attestation/<int:stagiaire_id>', methods=['GET'])
def download_attestation(stagiaire_id):
    # Alternative endpoint pour le téléchargement
    stagiaire = db.session.query(Stagiaire).filter_by(id=stagiaire_id).first()
    if not stagiaire or not stagiaire.attestation_filename:
        return abort(404)

    file_path = os.path.join('uploads', 'attestations', stagiaire.attestation_filename)
    if not os.path.exists(file_path):
        return abort(404)

    return send_file(file_path, mimetype='application/pdf', as_attachment=True,
                     download_name='attestation.pdf')

@user_bp.route('/user/<int:user_id>/stagiaires', methods=['GET'])
def get_user_stagiaires(user_id):
    # Récupérer tous les stagiaires liés aux candidatures de cet utilisateur
    stagiaires = db.session.query(Stagiaire).join(Application).filter(Application.user_id == user_id).all()
    stagiaires_list = [
        {
            'id': s.id,
            'application_id': s.application_id,
            'encadrant': s.encadrant,
            'sujet': s.sujet,
            'attestation_filename': s.attestation_filename
        }
        for s in stagiaires
    ]
    return jsonify({'stagiaires': stagiaires_list})

@user_bp.route('/user/stagiaire/<int:stagiaire_id>', methods=['GET'])
def get_stagiaire_by_id(stagiaire_id):
    stagiaire = db.session.query(Stagiaire).filter_by(id=stagiaire_id).first()
    if not stagiaire:
        return jsonify({'error': 'Stagiaire not found'}), 404
    
    return jsonify(stagiaire.serialize()), 200
