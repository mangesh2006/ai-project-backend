from app import db
from flask import Blueprint, request, jsonify
import tempfile
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
from dotenv import load_dotenv
from models.summaries import Summary
import json

load_dotenv()

gen_bp = Blueprint("generate", __name__)

@gen_bp.route("/generate-summary", methods=["POST"])
def generate_summary():
    json_file = request.form.get("json")
    if not "file" in request.files:
        return jsonify({"error": "Please provide pdf file"})
    
    pdf = request.files["file"]
    data = json.loads(json_file)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.save(tmp.name)
        pdf_path = tmp.name

    loader = PyMuPDFLoader(pdf_path)
    document = loader.load()

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = splitter.split_documents(document)

    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
    chain = load_summarize_chain(llm, chain_type="map_reduce")

    summary = chain.run(docs)

    new_summary = Summary(email=data["email"], pdf_name=pdf.filename, summary=summary)
    db.session.add(new_summary)
    db.session.commit()

    os.remove(pdf_path)

    return jsonify({"summary": summary}), 200