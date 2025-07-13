# cSpell:disable
from flask import Blueprint, jsonify, request
from models import User, Application, Rapport,db
from datetime import datetime
from flask import send_from_directory

admin_bp = Blueprint('admin', __name__)

# Liste des comptes créés
@admin_bp.route('/comptes', methods=['GET'])
def get_comptes():
    users = User.query.all()
    return jsonify([u.serialize() for u in users]), 200

# Voir toutes les candidatures
@admin_bp.route('/candidatures', methods=['GET'])
def get_all_candidatures():
    applications = Application.query.all()
    result = []
    for app in applications:
        result.append({
            "id": app.id,
            "user_id": app.user_id,
            "offre_id": app.offer_id,
            "statut": app.statut
        })
    return jsonify(result), 200

# Changer statut (accepter ou refuser)
@admin_bp.route('/candidature/<int:id>/statut', methods=['PUT'])
def update_statut(id):
    data = request.json
    statut = data.get("statut")
    entretien_date = data.get("date_entretien")
    entretien_lieu = data.get("lieu_entretien")

    app = Application.query.get(id)
    if not app:
        return jsonify({"error": "Candidature non trouvée"}), 404

    app.statut = statut
    if statut == "accepté":
        app.date_entretien = entretien_date
        app.lieu_entretien = entretien_lieu

    db.session.commit()
    return jsonify({"message": "Statut mis à jour"}), 200

# Ajouter commentaire sur rapport
@admin_bp.route('/rapport/<int:user_id>/commentaire', methods=['POST'])
def ajouter_commentaire(user_id):
    data = request.json
    commentaire = data.get("commentaire")

    rapport = Rapport.query.filter_by(user_id=user_id).first()
    if not rapport:
        return jsonify({"error": "Rapport non trouvé"}), 404

    rapport.commentaire = commentaire
    db.session.commit()
    return jsonify({"message": "Commentaire ajouté"}), 200
@admin_bp.route('/download/cv/<filename>', methods=['GET'])
def download_cv(filename):
    return send_from_directory('uploads/cv', filename, as_attachment=True)

@admin_bp.route('/download/motivation/<filename>', methods=['GET'])
def download_motivation(filename):
    return send_from_directory('uploads/motivation', filename, as_attachment=True)

