# WHAT: Endpoints to add scenes to a batch and list a batch's scenes.
# WHY:  Scenes are the actual work items, and each one belongs to a batch.

from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.errors import error
from app.extensions import db
from app.models import Batch, Scene
from app.schemas import SCENE_STATUSES, scene_schema, scenes_schema

scenes_bp = Blueprint("scenes", __name__, url_prefix="/api/batches")


@scenes_bp.post("/<int:batch_id>/scenes")
@jwt_required()
def create_scene(batch_id):
    batch = db.get_or_404(Batch, batch_id, description="batch not found")

    # business rule (stays in the route, because it depends on the batch's state)
    if batch.status == "done":
        return error("cannot add scenes to a batch that is done", 409)

    data = scene_schema.load(request.get_json(silent=True) or {})
    scene = Scene(batch_id=batch.id, **data)
    db.session.add(scene)
    db.session.commit()
    return jsonify(scene_schema.dump(scene)), 201


@scenes_bp.get("/<int:batch_id>/scenes")
@jwt_required()
def list_scenes(batch_id):
    db.get_or_404(Batch, batch_id, description="batch not found")
    query = db.select(Scene).where(Scene.batch_id == batch_id).order_by(Scene.id)
    status = request.args.get("status")
    if status:
        if status not in SCENE_STATUSES:
            return error(f"status must be one of {SCENE_STATUSES}", 400)
        query = query.where(Scene.status == status)
    scenes = db.session.scalars(query).all()
    return jsonify(scenes_schema.dump(scenes)), 200
