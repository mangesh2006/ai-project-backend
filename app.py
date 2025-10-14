from app import create_app
from flask_cors import CORS

app = create_app()

app.route("/")
def hello():
    return "Hello"

if __name__ == "__main__":
    app.run(debug=True)
