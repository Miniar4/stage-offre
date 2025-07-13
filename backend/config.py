# cSpell:disable
class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'votre_secret_key_ici'
    JWT_SECRET_KEY = 'cle_jwt_super_secrete'
