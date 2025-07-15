from flask import Blueprint, request, jsonify
from models import db, Offer
from datetime import datetime

offer_bp = Blueprint('offer_bp', __name__)

@offer_bp.route('/offres', methods=['GET'])
def get_offres():
    try:
        offres = Offer.query.all()
        return jsonify([o.serialize() for o in offres]), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch offers"}), 500

@offer_bp.route('/offres', methods=['POST'])
def create_offre():
    try:
        data = request.json
        if not data or not data.get('titre') or not data.get('description'):
            return jsonify({"error": "Fields 'titre' and 'description' are required"}), 400

        offre = Offer(
            titre=data['titre'],
            description=data['description'],
            nb_souhaitee=data.get('nb_souhaitee', 1),
            competences=data.get('competences'),
            duree=data.get('duree'),
            date_debut=data.get('date_debut'),
            date_fin=data.get('date_fin')
        )
        db.session.add(offre)
        db.session.commit()
        return jsonify({"message": "Offer created successfully", "id": offre.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to create offer"}), 500

@offer_bp.route('/offres/<int:id>', methods=['PUT'])
def update_offre(id):
    try:
        data = request.json
        offre = Offer.query.get(id)
        if not offre:
            return jsonify({"error": "Offer not found"}), 404

        offre.titre = data.get('titre', offre.titre)
        offre.description = data.get('description', offre.description)
        offre.nb_souhaitee = data.get('nb_souhaitee', offre.nb_souhaitee)
        offre.competences = data.get('competences', offre.competences)
        offre.duree = data.get('duree', offre.duree)
        offre.date_debut = data.get('date_debut', offre.date_debut)
        offre.date_fin = data.get('date_fin', offre.date_fin)

        db.session.commit()
        return jsonify({"message": "Offer updated successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update offer"}), 500

@offer_bp.route('/offres/<int:id>', methods=['DELETE'])
def delete_offre(id):
    try:
        offre = Offer.query.get(id)
        if not offre:
            return jsonify({"error": "Offer not found"}), 404

        db.session.delete(offre)
        db.session.commit()
        return jsonify({"message": "Offer deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to delete offer"}), 500