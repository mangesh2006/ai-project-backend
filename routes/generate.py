from app import db
from flask import Blueprint, request, jsonify
import tempfile
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.document_loaders import PyMuPDFLoader
from langchain.chains.summarize import load_summarize_chain
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
import os
from dotenv import load_dotenv
from models.summaries import Summary
import json
from flask_cors import CORS

load_dotenv()

gen_bp = Blueprint("generate", __name__)

CORS(gen_bp, origins=["https://mystudysaathi.vercel.app"])

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

@gen_bp.route("/generate-quiz", methods=["POST"])
def generate_quiz():
    if "file" not in request.files:
        return jsonify({"error": "Please provide a PDF file"}), 400

    pdf = request.files["file"]

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.save(tmp.name)
        pdf_path = tmp.name

    try:
        loader = PyMuPDFLoader(pdf_path)
        document = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        docs = splitter.split_documents(document)

        selected_text = " ".join([doc.page_content for doc in docs[:3]])

        llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

        prompt = PromptTemplate(
            input_variables=["content"],
            template=(
                "You are a helpful quiz generator. Based on the text below, "
                "create 10 multiple-choice questions (MCQs). "
                "Return your response strictly in pure JSON format like this:\n"
                "[{{\"question\": \"...\", \"options\": [\"A\", \"B\", \"C\", \"D\"], \"answer\": \"A\"}}]\n\n"
                "Text:\n{content}"
            ),
        )

        chain = prompt | llm

        response = chain.invoke({"content": selected_text})
        text_output = response.content.strip()

        import re
        import json

        clean_text = re.sub(r"```(?:json)?", "", text_output).strip()

        match = re.search(r"\[.*\]", clean_text, re.DOTALL)
        if match:
            clean_text = match.group(0)
        else:
            return jsonify({"error": "No valid JSON found in LLM output"}), 500

        quiz_json = json.loads(clean_text)

        return jsonify({"quiz": quiz_json})

    except Exception as e:
        print("❌ Error generating quiz:", e)
        return jsonify({"error": str(e)}), 500

    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)


@gen_bp.route("/submit-quiz", methods=["POST"])
def submit_quiz():
    try:
        data = request.get_json()  
        quiz = data["quiz"]
        user_answers = data["answers"]

        score = 0
        for i, q in enumerate(quiz):
            if i < len(user_answers) and user_answers[i] == q["answer"]:
                score += 1

        return jsonify({"score": score, "total": len(quiz)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

