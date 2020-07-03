"""
Lockbook Backend
Contributors:
	:: H. Kamran [@hkamran80] (author)
Version: 1.0.0
Last Updated: 2020-07-02, @hkamran80
"""

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import flask_cors
import hashlib
import base64
import json
import os

app = Flask(__name__, static_folder="../dist", static_url_path="/")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", None)
app.secret_key = os.urandom(24)
flask_cors.CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


class UsersModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String())
    password = db.Column(db.String())
    public_key = db.Column(db.LargeBinary)
    private_key = db.Column(db.LargeBinary)
    access_tokens = db.Column(db.String())

    def __init__(self, email, password, public_key, private_key, access_tokens):
        self.email = email
        self.password = password
        self.public_key = public_key
        self.private_key = private_key
        self.access_tokens = access_tokens

    def __repr__(self):
        return f"<User {self.email}>"


class EntriesModel(db.Model):
    __tablename__ = "entries"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    entry = db.Column(db.String())
    entry_date = db.Column(db.String())
    user_id = db.Column(db.Integer())


def generate_keys():
    private_key = rsa.generate_private_key(
        public_exponent=65537, key_size=2048, backend=default_backend()
    )
    public_key = private_key.public_key()
    private_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    private_pem_64 = base64.b64encode(private_pem)
    public_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
		format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    public_pem_64 = base64.b64encode(str(public_key).splitlines()[0].encode("utf-8"))
    return (private_pem_64, public_pem_64)


def create_user(email: str, password: str):
    public_key, private_key = generate_keys()

    sha512 = hashlib.sha512()
    sha512.update(password.encode("utf-8"))
    hashed_password = sha512.hexdigest()

    new_user = UsersModel(
        email=email,
        password=hashed_password,
        public_key=public_key,
        private_key=private_key,
        access_tokens="",
    )
    db.session.add(new_user)
    db.session.commit()

    return {"message": f"Successfully created user '{new_user.email}'"}


def get_entries():
    return {}


@app.errorhandler(501)
def error_not_implemented(description):
    return "Not implemented", 501

@app.errorhandler(400)
def error_bad_request(description):
    if description:
        return description, 400
    else:
        return "Bad Request", 400

@app.route("/")
def index():
    return app.send_static_file("index.html")


# TODO: Remove prior to production
@app.route("/api/v1/user/list", methods=["GET"])
def tmp__api_user_list():
    users = UsersModel.query.all()
    results = [
        {
            "email": user.email,
            "password": user.password,
            "access_tokens": user.access_tokens,
        }
        for user in users
    ]

    return {"count": len(results), "users": results}


@app.route("/api/v1/user/register", methods=["POST"])
def api_user_register():
    if request.is_json:
        req_data = request.get_json()
        if not req_data["email"] or not req_data["password"]:
            abort(400, {"error": "Required values were not provided"})
    
        creation = create_user(email=req_data["email"], password=req_data["password"])

        return creation
    else:
        return {"error": "Request payload is not in the JSON format"}
 

@app.route("/api/v1/authorize", methods=["POST"])
def api_authorize():
    abort(501)


@app.route("/api/v1/entries", methods=["GET", "POST", "UPDATE", "DELETE"])
def api_entries():
    abort(501)


@app.route("/api/v1/account", methods=["GET", "UPDATE"])
def api_account():
    abort(501)


if __name__ == "__main__":
    development = {"state": True, "host": "0.0.0.0", "port": 8081}
    app.run(
        host=development["host"], port=development["port"], debug=development["state"]
    )
