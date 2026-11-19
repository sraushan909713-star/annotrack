# WHAT: Endpoints to add scenes to a batch and list a batch's scenes.
# WHY:  Scenes are the actual work items, and each one belongs to a batch.

from flask import Blueprint, jsonify, request

from app.errors import error
from app.extensions import db
from app.models import Batch, Scene

# URLs look like /api/batches/1/scenes, because scenes live inside a batch
scenes_bp = Blueprint("scenes", __name__, url_prefix="/api/batches")

SCENE_STATUSES = {"pending", "annotated", "approved", "rejected"}


@scenes_bp.post("/<int:batch_id>/scenes")
def create_scene(batch_id):
    batch = db.get_or_404(Batch, batch_id, description="batch not found")

    # business rule: a finished batch is locked
    if batch.status == "done":
        return error("cannot add scenes to a batch that is done", 409)

    data = request.get_json(silent=True) or {}
    scene_ref = data.get("scene_ref")
    status = data.get("status", "pending")
    label_count = data.get("label_count", 0)

    if not scene_ref:
        return error("scene_ref is required", 400)
    if status not in SCENE_STATUSES:
        return error(f"status must be one of {sorted(SCENE_STATUSES)}", 400)
    if not isinstance(label_count, int) or label_count < 0:
        return error("label_count must be an integer >= 0", 400)

    scene = Scene(batch_id=batch.id, scene_ref=scene_ref, status=status,
                  label_count=label_count, notes=data.get("notes"))
    db.session.add(scene)
    db.session.commit()
    return jsonify(scene.to_dict()), 201


@scenes_bp.get("/<int:batch_id>/scenes")
def list_scenes(batch_id):
    # 404 if the batch doesn't exist, instead of a misleading empty list
    db.get_or_404(Batch, batch_id, description="batch not found")

    query = db.select(Scene).where(Scene.batch_id == batch_id).order_by(Scene.id)
    status = request.args.get("status")
    if status:
        if status not in SCENE_STATUSES:
            return error(f"status must be one of {sorted(SCENE_STATUSES)}", 400)
        query = query.where(Scene.status == status)
    scenes = db.session.scalars(query).all()
    return jsonify([s.to_dict() for s in scenes]), 200