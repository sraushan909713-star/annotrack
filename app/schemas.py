# WHAT: Rules for valid input (load) and the JSON shape of output (dump).
# WHY:  One place for validation, instead of if-checks repeated in every route.

from marshmallow import Schema, fields, validate

BATCH_STATUSES = ["open", "in_review", "done"]
SCENE_STATUSES = ["pending", "annotated", "approved", "rejected"]


class BatchSchema(Schema):
    # dump_only: shown in responses, but the client is not allowed to send it
    id = fields.Integer(dump_only=True)
    name = fields.String(required=True, validate=validate.Length(min=1, max=120))
    scenario = fields.String(required=True, validate=validate.Length(min=1, max=50))
    # strict=True rejects true/false and "5" (fixes Day 1 bug #1)
    target_scenes = fields.Integer(strict=True, load_default=0, validate=validate.Range(min=0))
    status = fields.String(load_default="open", validate=validate.OneOf(BATCH_STATUSES))
    created_at = fields.DateTime(dump_only=True)


class SceneSchema(Schema):
    id = fields.Integer(dump_only=True)
    batch_id = fields.Integer(dump_only=True)  # comes from the URL, not the body
    scene_ref = fields.String(required=True, validate=validate.Length(min=1, max=100))
    status = fields.String(load_default="pending", validate=validate.OneOf(SCENE_STATUSES))
    label_count = fields.Integer(strict=True, load_default=0, validate=validate.Range(min=0))
    notes = fields.String(allow_none=True)
    created_at = fields.DateTime(dump_only=True)


# one object for single items, one for lists
batch_schema = BatchSchema()
batches_schema = BatchSchema(many=True)
scene_schema = SceneSchema()
scenes_schema = SceneSchema(many=True) 


ROLES = ["annotator", "reviewer"]


class RegisterSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=80))
    # load_only: accepted in requests, never sent back in responses
    password = fields.String(required=True, load_only=True, validate=validate.Length(min=8))
    role = fields.String(load_default="annotator", validate=validate.OneOf(ROLES))


class LoginSchema(Schema):
    username = fields.String(required=True)
    password = fields.String(required=True, load_only=True)


# what we send back about a user (no password field at all)
class UserSchema(Schema):
    id = fields.Integer(dump_only=True)
    username = fields.String(dump_only=True)
    role = fields.String(dump_only=True)
    created_at = fields.DateTime(dump_only=True)


register_schema = RegisterSchema()
login_schema = LoginSchema()
user_schema = UserSchema()
