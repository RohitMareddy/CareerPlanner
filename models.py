from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()


# ==========================================================
# USER
# ==========================================================

class User(UserMixin, db.Model):

    __tablename__ = "user"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    phone = db.Column(
        db.String(20),
        unique=True,
        nullable=False
    )

    password_hash = db.Column(
        db.String(256),
        nullable=False
    )

    def set_password(self, password):

        self.password_hash = generate_password_hash(
            password
        )

    def check_password(self, password):

        return check_password_hash(
            self.password_hash,
            password
        )


# ==========================================================
# STUDENT PROFILE
# ==========================================================

class StudentProfile(db.Model):

    __tablename__ = "student_profile"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        unique=True,
        nullable=False
    )

    full_name = db.Column(
        db.String(100),
        nullable=False
    )

    college = db.Column(
        db.String(200),
        nullable=False
    )

    degree = db.Column(
        db.String(100),
        nullable=False
    )

    branch = db.Column(
        db.String(150),
        nullable=False
    )

    career_goal = db.Column(
        db.String(200),
        nullable=True
    )

    career_goal_description = db.Column(
        db.Text,
        nullable=True
    )

    user = db.relationship(
        "User",
        backref=db.backref(
            "profile",
            uselist=False
        )
    )


# ==========================================================
# ACADEMIC DETAILS
# ==========================================================

class AcademicDetails(db.Model):

    __tablename__ = "academic_details"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    profile_id = db.Column(
        db.Integer,
        db.ForeignKey("student_profile.id"),
        unique=True,
        nullable=False
    )

    current_year = db.Column(
        db.String(20),
        nullable=False
    )

    current_semester = db.Column(
        db.String(20),
        nullable=False
    )

    graduation_year = db.Column(
        db.Integer,
        nullable=False
    )

    cgpa = db.Column(
        db.Float,
        nullable=True
    )

    subjects = db.Column(
        db.Text,
        nullable=False
    )

    academic_challenges = db.Column(
        db.Text,
        nullable=True
    )

    profile = db.relationship(
        "StudentProfile",
        backref=db.backref(
            "academic_details",
            uselist=False
        )
    )


# ==========================================================
# STUDENT SKILLS
# ==========================================================

class StudentSkill(db.Model):

    __tablename__ = "student_skill"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    profile_id = db.Column(
        db.Integer,
        db.ForeignKey("student_profile.id"),
        nullable=False
    )

    skill_name = db.Column(
        db.String(100),
        nullable=False
    )

    skill_level = db.Column(
        db.String(30),
        nullable=False
    )

    profile = db.relationship(
        "StudentProfile",
        backref=db.backref(
            "skills",
            lazy=True,
            cascade="all, delete-orphan"
        )
    )


# ==========================================================
# AVAILABILITY
# ==========================================================

class Availability(db.Model):

    __tablename__ = "availability"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    profile_id = db.Column(
        db.Integer,
        db.ForeignKey("student_profile.id"),
        unique=True,
        nullable=False
    )

    college_start = db.Column(
        db.String(10),
        nullable=False
    )

    college_end = db.Column(
        db.String(10),
        nullable=False
    )

    study_start = db.Column(
        db.String(10),
        nullable=False
    )

    study_end = db.Column(
        db.String(10),
        nullable=False
    )

    study_hours = db.Column(
        db.Integer,
        nullable=False
    )

    weekend_mode = db.Column(
        db.String(30),
        nullable=False
    )

    profile = db.relationship(
        "StudentProfile",
        backref=db.backref(
            "availability",
            uselist=False
        )
    )
class MentorChatMessage(db.Model):
    __tablename__ = "mentor_chat_messages"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        nullable=False,
        index=True
    )

    role = db.Column(
        db.String(20),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    def __repr__(self):
        return f"<MentorChatMessage {self.id} {self.role}>"