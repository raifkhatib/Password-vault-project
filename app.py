from flask import Flask

app = Flask(__name__)


@app.route("/")
def home():
    return """
    <h1>Password Vault</h1>
    <p>The Flask application is running successfully.</p>
    """


if __name__ == "__main__":
    app.run(debug=True)