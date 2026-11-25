# WHAT: Endpoints to create, list, read, update and delete batches.
# WHY:  Batch is the main resource. Scenes belong to a batch.

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.errors import error
from app.extensions import db
from app.models import Batch
from app.schemas import BATCH_STATUSES, batch_schema, batches_schema
from flask_jwt_extended import jwt_required
from app.decorators import role_required

batches_bp = Blueprint("batches", __name__, url_prefix="/api/batches")


@batches_bp.get("")
def list_batches():
    query = db.select(Batch).order_by(Batch.id)
    status = request.args.get("status")
    if status:
        if status not in BATCH_STATUSES:
            return error(f"status must be one of {BATCH_STATUSES}", 400)
        query = query.where(Batch.status == status)
    batches = db.session.scalars(query).all()
    return jsonify(batches_schema.dump(batches)), 200


@batches_bp.post("")
def create_batch():
    # load() checks the input; bad input raises ValidationError -> 400 (errors.py)
    data = batch_schema.load(request.get_json(silent=True) or {})
    batch = Batch(**data)
    db.session.add(batch)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error(f"batch '{data['name']}' already exists", 409)
    return jsonify(batch_schema.dump(batch)), 201


@batches_bp.get("/<int:batch_id>")
def get_batch(batch_id):
    batch = db.get_or_404(Batch, batch_id, description="batch not found")
    return jsonify(batch_schema.dump(batch)), 200


@batches_bp.patch("/<int:batch_id>")
def update_batch(batch_id):
    batch = db.get_or_404(Batch, batch_id, description="batch not found")
    # partial=True: no field is required, but every field that IS sent is checked
    data = batch_schema.load(request.get_json(silent=True) or {}, partial=True)
    for field, value in data.items():
        setattr(batch, field, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("a batch with that name already exists", 409)
    return jsonify(batch_schema.dump(batch)), 200


@batches_bp.delete("/<int:batch_id>")
def delete_batch(batch_id):
    batch = db.get_or_404(Batch, batch_id, description="batch not found")
    db.session.delete(batch)
    db.session.commit()
    return "", 204