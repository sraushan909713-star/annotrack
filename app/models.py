# WHAT: Defines our two database tables, Batch and Scene.
# WHY:  We work with Python objects. SQLAlchemy turns them into SQL for us.

from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db


def utc_now():
    return datetime.now(timezone.utc)


class Batch(db.Model):
    __tablename__ = "batches"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    scenario = db.Column(db.String(50), nullable=False)
    target_scenes = db.Column(db.Integer, nullable=False, default=0)
    status = db.Column(db.String(20), nullable=False, default="open")
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    # one batch has many scenes; deleting a batch also deletes its scenes
    scenes = db.relationship("Scene", back_populates="batch", cascade="all, delete-orphan")

    # rules checked by the database itself, as a last line of defence
    __table_args__ = (
        db.CheckConstraint("target_scenes >= 0", name="ck_batch_target_nonneg"),
        db.CheckConstraint("status IN ('open', 'in_review', 'done')", name="ck_batch_status"),
    )


class Scene(db.Model):
    __tablename__ = "scenes"

    id = db.Column(db.Integer, primary_key=True)
    # links each scene to its batch; index makes "scenes of batch X" queries fast
    batch_id = db.Column(db.Integer, db.ForeignKey("batches.id", ondelete="CASCADE"),
                         nullable=False, index=True)
    scene_ref = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(20), nullable=False, default="pending")
    label_count = db.Column(db.Integer, nullable=False, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    batch = db.relationship("Batch", back_populates="scenes")

    __table_args__ = (
        db.CheckConstraint("label_count >= 0", name="ck_scene_labels_nonneg"),
        db.CheckConstraint("status IN ('pending', 'annotated', 'approved', 'rejected')",
                           name="ck_scene_status"),
    )


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)  # never the real password
    role = db.Column(db.String(20), nullable=False, default="annotator")
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    __table_args__ = (
        db.CheckConstraint("role IN ('annotator', 'reviewer')", name="ck_user_role"),
    )

    # turns "secret123" into a one-way hash before saving
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    # hashes the login attempt the same way and compares the two
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)