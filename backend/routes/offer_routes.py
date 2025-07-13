# cSpell:disable
from flask import Blueprint,request, jsonify
from models import db,Offer

offer_bp = Blueprint('offer_bp', __name__)

# GET toutes les offres
@offer_bp.route('/offres', methods=['GET'])
def get_offres():
    offres = Offer.query.all()
    return jsonify([o.serialize() for o in offres]), 200

# POST nouvelle offre
@offer_bp.route('/offres', methods=['POST'])
def create_offre():
    data = request.json
    offre = Offer(titre=data['titre'], description=data['description'])
    db.session.add(offre)
    db.session.commit()
    return jsonify({"message": "Offre ajoutée"}), 201

# PUT modifier offre
@offer_bp.route('/offres/<int:id>', methods=['PUT'])
def update_offre(id):
    data = request.json
    offre = Offer.query.get(id)
    if not offre:
        return jsonify({"error": "Offre non trouvée"}), 404
    offre.titre = data.get('titre', offre.titre)
    offre.description = data.get('description', offre.description)
    db.session.commit()
    return jsonify({"message": "Offre modifiée"}), 200

# DELETE offre
@offer_bp.route('/offres/<int:id>', methods=['DELETE'])
def delete_offre(id):
    offre = Offer.query.get(id)
    if not offre:
        return jsonify({"error": "Offre non trouvée"}), 404
    db.session.delete(offre)
    db.session.commit()
    return jsonify({"message": "Offre supprimée"}), 200
