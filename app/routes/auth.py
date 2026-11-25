# WHAT: Register, log in (get a JWT token), and "who am I".
# WHY:  Every protected endpoint later needs to know who is calling and their role.

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError

from app.errors import error
from app.extensions import db
from app.models import User
from app.schemas import login_schema, register_schema, user_schema

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@auth_bp.post("/register")
def register():
    data = register_schema.load(request.get_json(silent=True) or {})
    user = User(username=data["username"], role=data["role"])
    user.set_password(data["password"])
    db.session.add(user)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("username already taken", 409)
    return jsonify(user_schema.dump(user)), 201


@auth_bp.post("/login")
def login():
    data = login_schema.load(request.get_json(silent=True) or {})
    user = db.session.scalar(db.select(User).where(User.username == data["username"]))

    # same message for "no such user" and "wrong password", so attackers can't discover usernames
    if user is None or not user.check_password(data["password"]):
        return error("invalid username or password", 401)

    # identity = who this is (must be a string); the role travels inside the token
    token = create_access_token(identity=str(user.id), additional_claims={"role": user.role})
    return jsonify(access_token=token), 200


@auth_bp.get("/me")
@jwt_required()  # no valid token -> 401, and this function never runs
def me():
    user = db.get_or_404(User, int(get_jwt_identity()), description="user not found")
    return jsonify(user_schema.dump(user)), 200