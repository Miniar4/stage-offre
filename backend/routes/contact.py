from flask import Blueprint, request, jsonify
from models import db, Contact

contact_bp = Blueprint('contact_bp', __name__)

@contact_bp.route('/contact', methods=['POST'])
def envoyer_contact():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    message = data.get('message')

    contact = Contact(name=name, email=email, message=message)
    db.session.add(contact)
    db.session.commit()
    return jsonify({'message': 'Message reçu'}), 200

@contact_bp.route('/admin/contacts', methods=['GET'])
def lister_contacts():
    contacts = Contact.query.all()
    result = [{
        'id': c.id,
        'name': c.name,
        'email': c.email,
        'message': c.message
    } for c in contacts]
    return jsonify(result)
