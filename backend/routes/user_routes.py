import os
from werkzeug.utils import secure_filename
from flask import Blueprint, request, jsonify
from models import db, Application

user_bp = Blueprint('user_bp', __name__)

UPLOAD_FOLDER_CV = 'uploads/cv'
UPLOAD_FOLDER_MOTIVATION = 'uploads/motivation'
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

    if not all([file_cv, file_motivation]):
        return jsonify({'error': 'Files missing'}), 400

    cv_filename = secure_filename(file_cv.filename)
    motivation_filename = secure_filename(file_motivation.filename)

    cv_path = os.path.join(UPLOAD_FOLDER_CV, cv_filename)
    motivation_path = os.path.join(UPLOAD_FOLDER_MOTIVATION, motivation_filename)

    file_cv.save(cv_path)
    file_motivation.save(motivation_path)

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

    db.session.add(application)
    db.session.commit()

    return jsonify({'message': 'Application submitted successfully'}), 201
