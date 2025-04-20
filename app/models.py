from sqlalchemy import DateTime, func
from db import db

class Politica(db.Model):
    __tablename__ = 'politicas'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(80), nullable=False)
    descricao = db.Column(db.String(200), nullable=False)
    data_criacao = db.Column(DateTime(timezone=True), server_default=func.now())