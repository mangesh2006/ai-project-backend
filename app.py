from app import create_app
from flask_cors import CORS

app = create_app()
CORS(
    app,
    origins=["https://mystudysaathi.vercel.app/"],
    supports_credentials=True,
    allow_headers=["Content-Type", "Authorization"],
    methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"]
)

if __name__ == "__main__":
    app.run(debug=True)