"""
Lockbook Backend
Contributors:
	:: H. Kamran [@hkamran80] (author)
Version: 1.0.0
Last Updated: 2020-07-02, @hkamran80
"""

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_httpauth import HTTPBasicAuth
import flask_cors
import hashlib
import base64
import json
import os

app = Flask(__name__, static_folder="../dist", static_url_path="/")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", None)
app.secret_key = os.urandom(24)

flask_cors.CORS(app)
authentication = HTTPBasicAuth()
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
    entry_date_id = db.Column(db.Integer())
    user_id = db.Column(db.Integer())

    def __init__(self, entry, entry_date, entry_date_id, user_id):
        self.entry = entry
        self.entry_date = entry_date
        self.entry_date_id = entry_date_id
        self.user_id = user_id

    def __repr__(self):
        return f"<Entry {self.entry_date} - {self.entry_date_id}>"


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
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    public_pem_64 = base64.b64encode(str(public_key).splitlines()[0].encode("utf-8"))
    return (private_pem_64, public_pem_64)


def create_account(email: str, password: str):
    public_key, private_key = generate_keys()

    sha512_hash = hashlib.sha512()
    sha512_hash.update(password.encode("utf-8"))
    hashed_password = sha512_hash.hexdigest()

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


# TODO: Figure out why the function either throws a ValueError or a "TypeError: from_buffer() cannot return the address of a unicode object" when it's loading the public key
def create_entry(email: str, user_id: int, date: str, entry: str, entry_date_count: int):
    _public_key = UsersModel.query.filter_by(email=email).first_or_404().public_key
    if not _public_key:
        return {"error": "Unable to retrieve public key from database"}
    
    decoded_public_key = base64.b64decode(_public_key)
    certificate_filename = f"certificate-{user_id}-public.pem"
    with open(certificate_filename, "wb") as tmp_certificate:
        tmp_certificate.write(decoded_public_key)
        print("Temporary certificate written")

    # TODO: Remove debug print statements once no longer needed
    with open(certificate_filename, "rb") as key_file:
        print("Loading temporary certificate...")
        print("="*20, key_file.read(), "="*20)
        public_key = serialization.load_pem_public_key(key_file.read(), backend=default_backend())
        print("Loaded...removing temporary public certificate")
        os.remove(certificate_filename)

    print("="*20, public_key, "="*20)

    public_key = serialization.load_pem_public_key(public_key, backend=default_backend())
    encrypted_entry = public_key.encrypt(
        entry,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    new_entry = EntriesModel(
        entry=encrypted_entry,
        entry_date=date,
        entry_date_id=entry_date_count,
        user_id=user_id,
    )
    db.session.add(new_entry)
    db.session.commit()

    return {
        "message": f"Successfully created entry '{new_entry.date} - {new_entry.entry_date_id}'"
    }


# TODO: Simplify function
@authentication.verify_password
def verify_password(email, password):
    users = UsersModel.query.all()
    credentials = [(user.email, user.password) for user in users]
    emails = [credential[0] for credential in credentials]
    hashes = [credential[1] for credential in credentials]

    sha512_hash = hashlib.sha512()
    sha512_hash.update(password.encode("utf-8"))
    hashed_password = sha512_hash.hexdigest()

    if email in emails and hashes[emails.index(email)] == hashed_password:
        return True
    else:
        return False


@app.errorhandler(501)
def error_not_implemented(description):
    if description:
        return jsonify(description), 501
    else:
        return {"error": "Not implemented"}, 501

@app.errorhandler(400)
def error_bad_request(description):
    if description:
        return jsonify(description), 400
    else:
        return {"error": "Bad request"}, 400


@app.route("/")
def index():
    return app.send_static_file("index.html")


# TODO: Remove prior to deployment
@app.route("/api/v1/account/list", methods=["GET"])
def tmp__api_account_list():
    users = UsersModel.query.all()
    print(users)
    results = [
        {
            "email": user.email,
            "password_hash": user.password,
        }
        for user in users
    ]

    return {"result_count": len(results), "users": results}


@app.route("/api/v1/entries", methods=["GET", "POST", "UPDATE", "DELETE"])
@authentication.login_required
def api_entries():
    if request.method == "GET":
        _user_id = (
            UsersModel.query.filter_by(email=authentication.current_user())
            .first_or_404()
            .id
        )
        entries = EntriesModel.query.filter_by(user_id=_user_id).all()
        results = [
            {
                "entry": entry.entry,
                "entry_date": entry.entry_date,
                "date_entry_count": entry.entry_date_id,
                "user_id": entry.user_id
            } for entry in entries 
        ]
        return json.dumps(results)
    elif request.method == "POST":
        if request.is_json:
            req_data = request.get_json()
            if not req_data["date"] or not req_data["entry"]:
                abort(400, {"error": "Required values were not provided"})

            user_id = (
                UsersModel.query.filter_by(email=authentication.current_user())
                .first_or_404()
                .id
            )
            date_entry_count = len(
                [
                    entry
                    for entry in EntriesModel.query.filter_by(
                        entry_date=req_data["date"], user_id=user_id
                    ).all()
                ]
            )

            creation = create_entry(
                authentication.current_user(), user_id, req_data["date"], req_data["entry"], date_entry_count
            )
            return creation
        else:
            return {"error": "Request payload is not in the JSON format"}
    else:
        abort(501)


@app.route("/api/v1/account", methods=["POST"])
def api_account__register():
    if request.is_json:
        req_data = request.get_json()
        if not req_data["email"] or not req_data["password"]:
            abort(400, {"error": "Required values were not provided"})

        creation = create_account(
            email=req_data["email"], password=req_data["password"]
        )

        return creation
    else:
        return {"error": "Request payload is not in the JSON format"}


@app.route("/api/v1/account", methods=["GET", "UPDATE"])
@authentication.login_required
def api_account():
    abort(501)


if __name__ == "__main__":
    development = {"state": True, "host": "0.0.0.0", "port": 8081}
    app.run(
        host=development["host"], port=development["port"], debug=development["state"]
    )
