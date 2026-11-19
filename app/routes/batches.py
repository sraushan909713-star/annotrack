# WHAT: Endpoints to create, list, read, update and delete batches.
# WHY:  Batch is the main resource. Scenes belong to a batch.

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Batch

# every route in this file starts with /api/batches
batches_bp = Blueprint("batches", __name__, url_prefix="/api/batches")

BATCH_STATUSES = {"open", "in_review", "done"}


def error(message, code):
    return jsonify(error=message), code


@batches_bp.get("")
def list_batches():
    query = db.select(Batch).order_by(Batch.id)
    status = request.args.get("status")  # reads ?status=open from the URL
    if status:
        if status not in BATCH_STATUSES:
            return error(f"status must be one of {sorted(BATCH_STATUSES)}", 400)
        query = query.where(Batch.status == status)
    batches = db.session.scalars(query).all()
    return jsonify([b.to_dict() for b in batches]), 200


@batches_bp.post("")
def create_batch():
    data = request.get_json(silent=True) or {}  # bad or missing JSON becomes {}
    name = data.get("name")
    scenario = data.get("scenario")
    target = data.get("target_scenes", 0)

    # simple checks for now; Marshmallow replaces these on Day 2
    if not name or not scenario:
        return error("name and scenario are required", 400)
    if not isinstance(target, int) or target < 0:
        return error("target_scenes must be an integer >= 0", 400)

    batch = Batch(name=name, scenario=scenario, target_scenes=target)
    db.session.add(batch)
    try:
        db.session.commit()
    except IntegrityError:  # the database rejected a duplicate name
        db.session.rollback()
        return error(f"batch '{name}' already exists", 409)
    return jsonify(batch.to_dict()), 201


@batches_bp.get("/<int:batch_id>")
def get_batch(batch_id):
    batch = db.get_or_404(Batch, batch_id)  # returns 404 if the id doesn't exist
    return jsonify(batch.to_dict()), 200


@batches_bp.patch("/<int:batch_id>")
def update_batch(batch_id):
    batch = db.get_or_404(Batch, batch_id)
    data = request.get_json(silent=True) or {}

    allowed = {"name", "scenario", "target_scenes", "status"}
    unknown = set(data) - allowed
    if unknown:
        return error(f"unknown fields: {sorted(unknown)}", 400)
    if "status" in data and data["status"] not in BATCH_STATUSES:
        return error(f"status must be one of {sorted(BATCH_STATUSES)}", 400)
    if "target_scenes" in data and (not isinstance(data["target_scenes"], int) or data["target_scenes"] < 0):
        return error("target_scenes must be an integer >= 0", 400)

    # PATCH = change only the fields that were sent
    for field, value in data.items():
        setattr(batch, field, value)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return error("a batch with that name already exists", 409)
    return jsonify(batch.to_dict()), 200


@batches_bp.delete("/<int:batch_id>")
def delete_batch(batch_id):
    batch = db.get_or_404(Batch, batch_id)
    db.session.delete(batch)  # its scenes are deleted too (cascade)
    db.session.commit()
    return "", 204  # 204 = success with an empty body