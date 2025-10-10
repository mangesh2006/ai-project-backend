from app import db
from datetime import datetime

class Summary(db.Model):
    __tablename__ = "summaries"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    pdf_name = db.Column(db.String(100), nullable=False)
    summary = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, email, pdf_name, summary):
        self.email = email
        self.pdf_name = pdf_name
        self.summary = summary