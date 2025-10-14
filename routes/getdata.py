from flask import Blueprint, request, jsonify
from models.summaries import Summary
from urllib.parse import unquote
from flask_cors import CORS, cross_origin

get_bp = Blueprint("get-bp", __name__)

CORS(get_bp, origins=["https://mystudysaathi.vercel.app"])

@get_bp.route("/get-summaries", methods=["POST"])
@cross_origin()
def getdata():
    data = request.get_json()
    email = data.get("email")

    summ = Summary.query.filter_by(email=email).all()

    if not summ:
        return jsonify({"message": "No summaries found."})
    
    summaries_list = [
        {
            "pdf_name": s.pdf_name,
            "summary": s.summary,
            "created_at": s.created_at
        }
        for s in summ
    ]

    return jsonify({"summaries": summaries_list})

@get_bp.route("/get-summary/<pdf_name>", methods=["GET"])
@cross_origin()
def get_summary(pdf_name):
    pdf_name = unquote(pdf_name)
    summ = Summary.query.filter_by(pdf_name=pdf_name).first()

    if not summ:
        return jsonify({"message": "No summaries found."}), 404

    return jsonify({"summary": summ.summary}), 200