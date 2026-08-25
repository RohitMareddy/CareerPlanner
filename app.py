import os
from groq import Groq
from dotenv import load_dotenv

from datetime import datetime, timedelta

from flask import Flask, render_template, redirect, url_for, request, flash,jsonify 
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from sqlalchemy import inspect, text

from models import db, User, StudentProfile, AcademicDetails, StudentSkill, Availability ,MentorChatMessage
load_dotenv()
groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("WARNING: GROQ_API_KEY is not configured.")
groq_client = Groq(
    api_key=GROQ_API_KEY
) if GROQ_API_KEY else None
app = Flask(__name__)
app.config["SECRET_KEY"] = "career-planner-development-key-change-later"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///career_planner.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


# ==========================================================
# DATABASE
# ==========================================================

def initialize_database():
    db.create_all()
    inspector = inspect(db.engine)

    if "student_profile" not in inspector.get_table_names():
        return

    columns = {c["name"] for c in inspector.get_columns("student_profile")}
    with db.engine.begin() as connection:
        if "career_goal" not in columns:
            connection.execute(text(
                "ALTER TABLE student_profile ADD COLUMN career_goal VARCHAR(200)"
            ))
        if "career_goal_description" not in columns:
            connection.execute(text(
                "ALTER TABLE student_profile ADD COLUMN career_goal_description TEXT"
            ))


with app.app_context():
    initialize_database()


# ==========================================================
# RESOURCES
# ==========================================================

YOUTUBE_RESOURCES = {
    "C": {
        "title": "C Programming Tutorial for Beginners",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/watch?v=KJgsSFOSQv0",
        "description": "Build strong C programming fundamentals."
    },
    "C++": {
        "title": "C++ Programming Course",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/results?search_query=freecodecamp+c%2B%2B+full+course",
        "description": "Learn modern C++ syntax, OOP and problem solving."
    },
    "Python": {
        "title": "Learn Python - Full Course for Beginners",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/watch?v=rfscVS0vtbw",
        "description": "Master Python fundamentals and problem solving."
    },
    "Java": {
        "title": "Java Full Course",
        "channel": "Bro Code",
        "url": "https://www.youtube.com/watch?v=xTtL8E4LzTQ",
        "description": "Learn Java fundamentals and object-oriented programming."
    },
    "SQL": {
        "title": "SQL Tutorial - Full Database Course for Beginners",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/watch?v=HXV3zeQKqGY",
        "description": "Learn queries, joins, CRUD and database fundamentals."
    },
    "HTML": {
        "title": "HTML Full Course",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/results?search_query=freecodecamp+html+full+course",
        "description": "Build clean web pages with semantic HTML."
    },
    "CSS": {
        "title": "CSS Full Course",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/results?search_query=freecodecamp+css+full+course",
        "description": "Learn layouts, responsive design and modern CSS."
    },
    "JavaScript": {
        "title": "JavaScript Projects and Web Development",
        "channel": "Traversy Media",
        "url": "https://www.youtube.com/watch?v=JkeyKeK3V24",
        "description": "Practice JavaScript through practical projects."
    },
    "React": {
        "title": "React JS Full Course",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/watch?v=bMknfKXIFA8",
        "description": "Learn React fundamentals and component-based development."
    },
    "Git": {
        "title": "Git and GitHub for Beginners",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/watch?v=RGOj5yH7evk",
        "description": "Learn version control and a practical GitHub workflow."
    },
    "Flask": {
        "title": "Flask Python Web Development",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/results?search_query=freecodecamp+flask+python",
        "description": "Build web applications with Python and Flask."
    },
    "Android Development": {
        "title": "Android Development for Beginners",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/results?search_query=freecodecamp+android+development",
        "description": "Start building Android applications and understand the fundamentals."
    },
    "Data Analysis": {
        "title": "Python Data Analysis",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/results?search_query=freecodecamp+python+data+analysis+pandas",
        "description": "Learn practical data analysis with Python and pandas."
    },
    "Machine Learning": {
        "title": "Machine Learning Course",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/results?search_query=freecodecamp+machine+learning+course",
        "description": "Build a foundation in machine learning concepts and practice."
    },
    "DSA": {
        "title": "Data Structures and Algorithms",
        "channel": "freeCodeCamp.org",
        "url": "https://www.youtube.com/results?search_query=freecodecamp+data+structures+algorithms",
        "description": "Practice the data structures and algorithms needed for interviews."
    }
}


def get_weekly_learning_skills(profile, skills):
    selected = {skill.skill_name: skill.skill_level for skill in skills}
    goal = (profile.career_goal or "").lower()

    if any(word in goal for word in [
        "data scientist", "machine learning", "artificial intelligence",
        "ai engineer", "data analyst", "aiml"
    ]):
        priority = ["Python", "SQL", "Data Analysis", "Machine Learning", "Git"]
    elif any(word in goal for word in [
        "software developer", "software engineer", "backend", "developer"
    ]):
        priority = ["Java", "Python", "DSA", "SQL", "Git"]
    elif any(word in goal for word in [
        "web developer", "frontend", "full stack"
    ]):
        priority = ["HTML", "CSS", "JavaScript", "React", "Git"]
    elif any(word in goal for word in ["android", "mobile app"]):
        priority = ["Java", "Android Development", "Git", "SQL"]
    else:
        priority = list(selected.keys())

    weekly = []
    for name in priority:
        if name in selected and selected[name].lower() not in {"advanced", "expert"}:
            weekly.append(name)

    for name, level in selected.items():
        if len(weekly) >= 3:
            break
        if name not in weekly and level.lower() not in {"advanced", "expert"}:
            weekly.append(name)

    if len(weekly) < 3:
        for name in priority:
            if name not in weekly and name in YOUTUBE_RESOURCES:
                weekly.append(name)
            if len(weekly) >= 3:
                break

    return weekly[:3]


def resource_links(skills):
    result = []
    for skill in skills:
        data = YOUTUBE_RESOURCES.get(skill.skill_name)
        if data:
            result.append({"skill": skill.skill_name, **data})
    return result


# ==========================================================
# INTERNSHIPS
# ==========================================================

def internship_links():
    return [
        {
            "name": "Google Students & Internships",
            "type": "Official student opportunities",
            "url": "https://www.google.com/about/careers/applications/students/",
            "description": "Google's official student and internship portal."
        },
        {
            "name": "Microsoft Early in Profession",
            "type": "Official student opportunities",
            "url": "https://careers.microsoft.com/v2/global/en/students?qcountry=India",
            "description": "Microsoft's student, internship and early-career portal."
        },
        {
            "name": "Amazon Student Internships",
            "type": "Official student opportunities",
            "url": "https://www.amazon.jobs/content/en/career-programs/university/internships-for-students/",
            "description": "Amazon's official university internship portal."
        },
        {
            "name": "LinkedIn Jobs",
            "type": "Job and internship search",
            "url": "https://www.linkedin.com/jobs/",
            "description": "Search for current internships and entry-level opportunities."
        }
    ]


# ==========================================================
# SCHEDULE + ROADMAP
# ==========================================================

def parse_time(value):
    return datetime.strptime(value, "%H:%M")


def format_time(value):
    return value.strftime("%I:%M %p").lstrip("0")


def build_schedule(availability, subjects):
    """
    Build a personalized 7-day timetable.

    Every day contains:
    - College / Classes
    - Academic study sessions
    - Exactly one Other Skills session

    The Other Skills session links to the Resources section
    of the dashboard.
    """

    if not availability:
        return {}

    subjects = [
        s.strip()
        for s in subjects
        if s and s.strip()
    ]

    if not subjects:
        subjects = ["Focused Study"]

    try:
        study_start = parse_time(availability.study_start)
        study_end = parse_time(availability.study_end)

        college_start = availability.college_start
        college_end = availability.college_end

        study_hours = int(
            availability.study_hours or 1
        )

    except (TypeError, ValueError):
        return {}

    if study_end <= study_start:
        return {}

    available_minutes = (
        study_end - study_start
    ).seconds // 60

    target_minutes = min(
        study_hours * 60,
        available_minutes
    )

    # We reserve one session for learning skills
    # outside the student's academic subjects.
    OTHER_SKILLS_MINUTES = 45

    if target_minutes <= OTHER_SKILLS_MINUTES:
        other_skills_minutes = max(
            30,
            target_minutes
        )
        academic_minutes = max(
            0,
            target_minutes - other_skills_minutes
        )
    else:
        other_skills_minutes = OTHER_SKILLS_MINUTES
        academic_minutes = (
            target_minutes - other_skills_minutes
        )

    # Split the academic study time across subjects.
    subject_count = len(subjects)

    academic_block_minutes = max(
        30,
        academic_minutes // subject_count
    ) if academic_minutes else 0

    days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    weekly_schedule = {}

    # Subject rotation makes the timetable less repetitive.
    for day_index, day in enumerate(days):

        slots = []

        # --------------------------------------------------
        # COLLEGE
        # --------------------------------------------------

        slots.append({
            "time": (
                f"{college_start} – "
                f"{college_end}"
            ),
            "title": "College / Classes",
            "kind": "college"
        })

        # --------------------------------------------------
        # ACADEMIC STUDY
        # --------------------------------------------------

        cursor = study_start

        if academic_minutes > 0:

            used_minutes = 0
            subject_index = (
                day_index % subject_count
            )

            while (
                cursor < study_end
                and used_minutes < academic_minutes
            ):

                remaining = (
                    academic_minutes
                    - used_minutes
                )

                minutes = min(
                    academic_block_minutes,
                    remaining
                )

                start = cursor

                end = min(
                    study_end,
                    cursor + timedelta(
                        minutes=minutes
                    )
                )

                if end <= start:
                    break

                slots.append({
                    "time": (
                        f"{format_time(start)}"
                        f" – "
                        f"{format_time(end)}"
                    ),
                    "title": subjects[
                        subject_index % subject_count
                    ],
                    "kind": "study"
                })

                used_minutes += (
                    end - start
                ).seconds // 60

                subject_index += 1

                # Short break between sessions.
                cursor = (
                    end
                    + timedelta(minutes=10)
                )

        # --------------------------------------------------
        # OTHER SKILLS
        # --------------------------------------------------

        # Put the skill-learning session at the end
        # of the available study period.

        other_end = study_end

        other_start = (
            other_end
            - timedelta(
                minutes=other_skills_minutes
            )
        )

        slots.append({
            "time": (
                f"{format_time(other_start)}"
                f" – "
                f"{format_time(other_end)}"
            ),
            "title": "Other Skills",
            "kind": "skills",
            "description": (
                "Learn skills related to your "
                "career goal and placement preparation."
            ),
            "resource_url": (
                "/dashboard?view=resources"
            )
        })

        weekly_schedule[day] = slots

    return weekly_schedule

def skill_needs(skills):
    return [
        skill.skill_name for skill in skills
        if skill.skill_level in {"Beginner", "Basic"}
    ]


def calculate_progress(profile, skills, availability):
    points = {"Beginner": 25, "Basic": 40, "Intermediate": 65, "Advanced": 90, "Expert": 100}
    skill_score = (
        sum(points.get(s.skill_level, 25) for s in skills) / len(skills)
        if skills else 0
    )
    completed = sum([
        bool(profile),
        bool(profile and profile.academic_details),
        bool(profile and profile.career_goal),
        bool(skills),
        bool(availability)
    ])
    completion_score = completed * 20
    return min(100, round(skill_score * 0.65 + completion_score * 0.35))


def build_roadmap(profile, skills):
    """
    Build a roadmap dynamically from the student's actual
    onboarding/profile data.

    Important:
    - Completing onboarding does NOT mean projects are completed.
    - Selecting skills does NOT mean those skills are mastered.
    - The roadmap progresses based on actual evidence.
    """

    # --------------------------------------------------
    # BASIC COMPLETION STATES
    # --------------------------------------------------

    profile_complete = bool(
        profile
        and profile.full_name
        and profile.college
        and profile.degree
        and profile.branch
    )

    academic_complete = bool(
        profile
        and profile.academic_details
    )

    career_complete = bool(
        profile
        and profile.career_goal
    )

    skills_complete = bool(skills)

    availability = Availability.query.filter_by(
        profile_id=profile.id
    ).first() if profile else None

    availability_complete = bool(availability)

    # --------------------------------------------------
    # SKILL READINESS
    # --------------------------------------------------

    level_points = {
        "Beginner": 25,
        "Basic": 40,
        "Intermediate": 65,
        "Advanced": 90,
        "Expert": 100
    }

    if skills:
        skill_score = round(
            sum(
                level_points.get(
                    skill.skill_level,
                    25
                )
                for skill in skills
            ) / len(skills)
        )
    else:
        skill_score = 0

    # --------------------------------------------------
    # STAGE COMPLETION
    # --------------------------------------------------

    foundation_complete = (
        profile_complete
        and academic_complete
    )

    core_skills_complete = (
        foundation_complete
        and career_complete
        and skills_complete
        and skill_score >= 65
    )

    projects_complete = False
    internships_complete = False
    job_ready_complete = False

    # --------------------------------------------------
    # DETERMINE CURRENT STAGE
    # --------------------------------------------------

    if not profile_complete:
        current_stage = "Foundation"

    elif not academic_complete:
        current_stage = "Foundation"

    elif not career_complete:
        current_stage = "Career Direction"

    elif not skills_complete:
        current_stage = "Core Skills"

    elif skill_score < 65:
        current_stage = "Core Skills"

    elif not availability_complete:
        current_stage = "Core Skills"

    else:
        current_stage = "Projects"

    # --------------------------------------------------
    # STAGE PERCENTAGES
    # --------------------------------------------------

    # Foundation
    foundation_steps = [
        profile_complete,
        academic_complete
    ]

    foundation_percentage = round(
        sum(foundation_steps)
        / len(foundation_steps)
        * 100
    )

    # Core Skills
    core_steps = [
        career_complete,
        skills_complete,
        availability_complete
    ]

    core_base_percentage = round(
        sum(core_steps)
        / len(core_steps)
        * 100
    )

    if skills_complete:
        core_percentage = round(
            (core_base_percentage * 0.5)
            + (skill_score * 0.5)
        )
    else:
        core_percentage = core_base_percentage

    # --------------------------------------------------
    # PROJECTS
    # --------------------------------------------------

    # We are NOT claiming projects are completed merely
    # because onboarding is complete.
    #
    # A future project-tracking system can replace this.
    projects_percentage = 0

    # --------------------------------------------------
    # INTERNSHIPS
    # --------------------------------------------------

    internships_percentage = 0

    # --------------------------------------------------
    # JOB READY
    # --------------------------------------------------

    job_ready_percentage = 0

    # --------------------------------------------------
    # BUILD ROADMAP
    # --------------------------------------------------

    roadmap = [
        {
            "number": "01",
            "title": "Foundation",
            "status": (
                "Completed"
                if foundation_percentage == 100
                else "In Progress"
            ),
            "percentage": foundation_percentage,
            "description":
                "Build a strong academic and programming foundation.",
            "action":
                "Complete your profile and academic information."
        },

        {
            "number": "02",
            "title": "Core Skills",
            "status": (
                "Completed"
                if core_skills_complete
                else (
                    "Current"
                    if current_stage == "Core Skills"
                    else "Upcoming"
                )
            ),
            "percentage": core_percentage,
            "description":
                "Develop the technical skills required for your target career.",
            "action":
                "Strengthen your selected skills and move toward intermediate level."
        },

        {
            "number": "03",
            "title": "Projects",
            "status": (
                "Completed"
                if projects_complete
                else (
                    "Current"
                    if current_stage == "Projects"
                    else "Upcoming"
                )
            ),
            "percentage": projects_percentage,
            "description":
                "Turn your knowledge into real projects that demonstrate your abilities.",
            "action":
                "Build practical projects related to your career goal."
        },

        {
            "number": "04",
            "title": "Internships",
            "status": (
                "Completed"
                if internships_complete
                else "Upcoming"
            ),
            "percentage": internships_percentage,
            "description":
                "Gain real-world experience through internships and practical opportunities.",
            "action":
                "Prepare your resume, GitHub profile and internship applications."
        },

        {
            "number": "05",
            "title": "Job Ready",
            "status": (
                "Completed"
                if job_ready_complete
                else "Upcoming"
            ),
            "percentage": job_ready_percentage,
            "description":
                "Prepare for technical interviews and professional software development.",
            "action":
                "Practice DSA, CS fundamentals, projects and interviews."
        }
    ]

    return roadmap

# ==========================================================
# AUTH
# ==========================================================

@app.route("/")
def home():
    return render_template("home.html")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        phone = request.form.get("phone", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not phone or not password:
            flash("Please fill in all fields.", "error")
            return redirect(url_for("signup"))
        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return redirect(url_for("signup"))
        if len(password) < 6:
            flash("Password must contain at least 6 characters.", "error")
            return redirect(url_for("signup"))
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "error")
            return redirect(url_for("signup"))
        if User.query.filter_by(phone=phone).first():
            flash("Phone number already registered.", "error")
            return redirect(url_for("signup"))

        user = User(username=username, phone=phone)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for("onboarding_profile"))

    return render_template("auth/signup.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for("dashboard"))
        flash("Invalid username or password.", "error")

    return render_template("auth/login.html")


# ==========================================================
# ONBOARDING
# ==========================================================

@app.route("/onboarding/profile", methods=["GET", "POST"])
@login_required
def onboarding_profile():
    if current_user.profile:
        return redirect(url_for("onboarding_academics"))

    if request.method == "POST":
        fields = {
            "full_name": request.form.get("full_name", "").strip(),
            "college": request.form.get("college", "").strip(),
            "degree": request.form.get("degree", "").strip(),
            "branch": request.form.get("branch", "").strip(),
        }
        if not all(fields.values()):
            flash("Please complete all the fields.", "error")
            return redirect(url_for("onboarding_profile"))

        db.session.add(StudentProfile(user_id=current_user.id, **fields))
        db.session.commit()
        return redirect(url_for("onboarding_academics"))

    return render_template("onboarding/profile.html")


@app.route("/onboarding/academics", methods=["GET", "POST"])
@login_required
def onboarding_academics():
    profile = current_user.profile
    if not profile:
        return redirect(url_for("onboarding_profile"))
    if profile.academic_details:
        return redirect(url_for("onboarding_career"))

    if request.method == "POST":
        current_year = request.form.get("current_year", "").strip()
        current_semester = request.form.get("current_semester", "").strip()
        graduation_year_value = request.form.get("graduation_year", "").strip()
        cgpa_value = request.form.get("cgpa", "").strip()
        subjects = request.form.get("subjects", "").strip()
        academic_challenges = request.form.get("academic_challenges", "").strip()

        if not all([current_year, current_semester, graduation_year_value, subjects]):
            flash("Please complete all required fields.", "error")
            return redirect(url_for("onboarding_academics"))

        try:
            graduation_year = int(graduation_year_value)
        except ValueError:
            flash("Please enter a valid graduation year.", "error")
            return redirect(url_for("onboarding_academics"))

        cgpa = None
        if cgpa_value:
            try:
                cgpa = float(cgpa_value)
            except ValueError:
                flash("Please enter a valid CGPA.", "error")
                return redirect(url_for("onboarding_academics"))
            if not 0 <= cgpa <= 10:
                flash("CGPA must be between 0 and 10.", "error")
                return redirect(url_for("onboarding_academics"))

        db.session.add(AcademicDetails(
            profile_id=profile.id,
            current_year=current_year,
            current_semester=current_semester,
            graduation_year=graduation_year,
            cgpa=cgpa,
            subjects=subjects,
            academic_challenges=academic_challenges
        ))
        db.session.commit()
        return redirect(url_for("onboarding_career"))

    return render_template("onboarding/academics.html")


@app.route("/onboarding/career", methods=["GET", "POST"])
@login_required
def onboarding_career():
    profile = current_user.profile
    if not profile:
        return redirect(url_for("onboarding_profile"))
    if not profile.academic_details:
        return redirect(url_for("onboarding_academics"))
    if profile.career_goal:
        return redirect(url_for("onboarding_skills"))

    if request.method == "POST":
        career_goal = request.form.get("career_goal", "").strip()
        description = request.form.get("career_goal_description", "").strip()
        if not career_goal:
            flash("Please choose or enter your career goal.", "error")
            return redirect(url_for("onboarding_career"))

        profile.career_goal = career_goal
        profile.career_goal_description = description
        db.session.commit()
        return redirect(url_for("onboarding_skills"))

    return render_template("onboarding/career.html")


@app.route("/onboarding/skills", methods=["GET", "POST"])
@login_required
def onboarding_skills():
    profile = current_user.profile
    if not profile:
        return redirect(url_for("onboarding_profile"))
    if not profile.academic_details:
        return redirect(url_for("onboarding_academics"))
    if not profile.career_goal:
        return redirect(url_for("onboarding_career"))

    if request.method == "POST":
        StudentSkill.query.filter_by(profile_id=profile.id).delete(synchronize_session=False)

        selected_skills = request.form.getlist("skills")
        default_level = request.form.get("level_default", "Beginner")
        valid_levels = {"Beginner", "Basic", "Intermediate", "Advanced", "Expert"}
        if default_level not in valid_levels:
            default_level = "Beginner"

        seen = set()
        for skill_name in selected_skills:
            skill_name = skill_name.strip()
            if not skill_name or skill_name in seen:
                continue
            seen.add(skill_name)
            level = request.form.get(f"level_{skill_name}", default_level)
            if level not in valid_levels:
                level = default_level
            db.session.add(StudentSkill(
                profile_id=profile.id,
                skill_name=skill_name,
                skill_level=level
            ))

        custom = request.form.get("custom_skills", "").strip()
        for skill_name in [x.strip() for x in custom.split(",") if x.strip()]:
            if skill_name.lower() in {x.lower() for x in seen}:
                continue
            seen.add(skill_name)
            db.session.add(StudentSkill(
                profile_id=profile.id,
                skill_name=skill_name,
                skill_level=default_level
            ))

        if not seen:
            flash("Please select at least one skill.", "error")
            db.session.rollback()
            return redirect(url_for("onboarding_skills"))

        db.session.commit()
        return redirect(url_for("onboarding_availability"))

    existing_skills = StudentSkill.query.filter_by(profile_id=profile.id).all()
    return render_template("onboarding/skills.html", existing_skills=existing_skills)


@app.route("/onboarding/availability", methods=["GET", "POST"])
@login_required
def onboarding_availability():
    profile = current_user.profile
    if not profile:
        return redirect(url_for("onboarding_profile"))
    if not profile.academic_details:
        return redirect(url_for("onboarding_academics"))
    if not profile.career_goal:
        return redirect(url_for("onboarding_career"))
    if StudentSkill.query.filter_by(profile_id=profile.id).count() == 0:
        return redirect(url_for("onboarding_skills"))

    availability = Availability.query.filter_by(profile_id=profile.id).first()

    if request.method == "POST":
        college_start = request.form.get("college_start", "").strip()
        college_end = request.form.get("college_end", "").strip()
        study_start = request.form.get("study_start", "").strip()
        study_end = request.form.get("study_end", "").strip()
        study_hours_value = request.form.get("study_hours", "").strip()
        weekend_mode = request.form.get("weekend_mode", "").strip()

        if not all([college_start, college_end, study_start, study_end, study_hours_value, weekend_mode]):
            flash("Please complete your availability.", "error")
            return redirect(url_for("onboarding_availability"))

        try:
            parse_time(college_start)
            parse_time(college_end)
            parse_time(study_start)
            parse_time(study_end)
            study_hours = int(study_hours_value)
        except (ValueError, TypeError):
            flash("Please enter valid time and study-hour values.", "error")
            return redirect(url_for("onboarding_availability"))

        if not 1 <= study_hours <= 6:
            flash("Study hours must be between 1 and 6.", "error")
            return redirect(url_for("onboarding_availability"))

        if availability is None:
            availability = Availability(profile_id=profile.id)
            db.session.add(availability)

        availability.college_start = college_start
        availability.college_end = college_end
        availability.study_start = study_start
        availability.study_end = study_end
        availability.study_hours = study_hours
        availability.weekend_mode = weekend_mode
        db.session.commit()
        return redirect(url_for("dashboard"))

    return render_template("onboarding/availability.html", availability=availability)


# ==========================================================
# DASHBOARD DATA
# ==========================================================

def dashboard_context(view):
    profile = current_user.profile
    skills = StudentSkill.query.filter_by(profile_id=profile.id).order_by(StudentSkill.skill_name.asc()).all()
    availability = Availability.query.filter_by(profile_id=profile.id).first()
    academic = profile.academic_details
    subjects = [s.strip() for s in (academic.subjects or "").split(",") if s.strip()]
    progress = calculate_progress(profile, skills, availability)
    roadmap = build_roadmap(profile, skills)
    weekly_names = get_weekly_learning_skills(profile, skills)
    weekly_resources = [YOUTUBE_RESOURCES[name] | {"skill": name} for name in weekly_names if name in YOUTUBE_RESOURCES]
    all_resources = resource_links(skills)
    if not all_resources:
        all_resources = weekly_resources

    schedule = build_schedule(availability, subjects)
    today_name = datetime.now().strftime("%A")
    today_schedule = schedule.get(today_name, []) if isinstance(schedule, dict) else schedule

    return {
        "user": current_user,
        "profile": profile,
        "academic": academic,
        "skills": skills,
        "availability": availability,
        "progress": progress,
        "roadmap": roadmap,
                "schedule": schedule,
        "today_schedule": today_schedule,
        "subjects": subjects,
        "weekly_skills": weekly_names,
        "weekly_resources": weekly_resources,
        "resources": all_resources,
        "opportunities": internship_links(),
        "view": view,
        "needs": skill_needs(skills),
        "achievements": build_achievements(profile, skills, availability),
    }


def build_achievements(profile, skills, availability):
    return [
        {
            "title": "Profile Complete",
            "description": "Your personal profile is complete.",
            "completed": bool(profile.full_name and profile.college and profile.degree and profile.branch),
            "icon": "◎"
        },
        {
            "title": "Academic Profile",
            "description": "Your academic information has been added.",
            "completed": bool(profile.academic_details),
            "icon": "▣"
        },
        {
            "title": "Career Direction",
            "description": "You have defined your target career.",
            "completed": bool(profile.career_goal),
            "icon": "⌁"
        },
        {
            "title": "Skill Profile",
            "description": f"{len(skills)} skills are mapped to your profile.",
            "completed": bool(skills),
            "icon": "◇"
        },
        {
            "title": "Schedule Ready",
            "description": "Your availability is ready for timetable generation.",
            "completed": bool(availability),
            "icon": "◷"
        },
        {
            "title": "5+ Skills",
            "description": f"{len(skills)} skills currently mapped.",
            "completed": len(skills) >= 5,
            "icon": "✦"
        }
    ]


def dashboard_guard():
    profile = current_user.profile
    if not profile:
        return redirect(url_for("onboarding_profile"))
    if not profile.academic_details:
        return redirect(url_for("onboarding_academics"))
    if not profile.career_goal:
        return redirect(url_for("onboarding_career"))
    if StudentSkill.query.filter_by(profile_id=profile.id).count() == 0:
        return redirect(url_for("onboarding_skills"))
    if not Availability.query.filter_by(profile_id=profile.id).first():
        return redirect(url_for("onboarding_availability"))
    return None


# ==========================================================
# SINGLE DASHBOARD ROUTER
# This is intentional: every dashboard page uses the same
# shell/template, so no sidebar link can hit a missing template.
# ==========================================================

VALID_VIEWS = {
    "dashboard", "profile", "roadmap", "schedule", "internships",
    "resources", "skills", "mentor", "achievements", "settings"
}


@app.route("/dashboard", defaults={"view": "dashboard"}, methods=["GET", "POST"])
@app.route("/dashboard/<view>", methods=["GET", "POST"])
@login_required
def dashboard(view):
    if view not in VALID_VIEWS:
        return redirect(url_for("dashboard"))

    guard = dashboard_guard()
    if guard:
        return guard

    if view == "settings" and request.method == "POST":
        profile = current_user.profile
        action = request.form.get("action", "")

        if action == "profile":
            for field in ["full_name", "college", "degree", "branch"]:
                value = request.form.get(field, "").strip()
                if not value:
                    flash("All profile fields are required.", "error")
                    return redirect(url_for("dashboard", view="settings"))
                setattr(profile, field, value)
            db.session.commit()
            flash("Profile updated successfully.", "success")

        elif action == "career":
            goal = request.form.get("career_goal", "").strip()
            if not goal:
                flash("Career goal cannot be empty.", "error")
                return redirect(url_for("dashboard", view="settings"))
            profile.career_goal = goal
            profile.career_goal_description = request.form.get("career_goal_description", "").strip()
            db.session.commit()
            flash("Career goal updated.", "success")

        elif action == "password":
            old_password = request.form.get("old_password", "")
            new_password = request.form.get("new_password", "")
            confirm_password = request.form.get("confirm_password", "")
            if not current_user.check_password(old_password):
                flash("Current password is incorrect.", "error")
            elif len(new_password) < 6:
                flash("New password must contain at least 6 characters.", "error")
            elif new_password != confirm_password:
                flash("New passwords do not match.", "error")
            else:
                current_user.set_password(new_password)
                db.session.commit()
                flash("Password updated successfully.", "success")

        return redirect(url_for("dashboard", view="settings"))

    context = dashboard_context(view)
    return render_template("dashboard/dashboard.html", **context)


# ==========================================================
# AI MENTOR CHAT API
# ==========================================================

@app.route("/api/ai-mentor/chat", methods=["POST"])
@login_required
def ai_mentor_chat():

    try:
        data = request.get_json(silent=True) or {}

        user_message = (data.get("message") or "").strip()

        if not user_message:
            return {
                "success": False,
                "error": "Please enter a message."
            }, 400

        # ==================================================
        # JARVIS CONVERSATION
        # ==================================================
        # Fresh conversation every time.
        # No previous chat history is loaded or sent to Groq.

        conversation = []

        # ==================================================
        # STUDENT INFORMATION
        # ==================================================

        profile = current_user.profile

        skills = StudentSkill.query.filter_by(
            profile_id=profile.id
        ).all()

        skill_names = [
            skill.skill_name
            for skill in skills
        ]

        # ==================================================
        # JARVIS SYSTEM PROMPT
        # ==================================================

        system_prompt = f"""
You are JARVIS, the personal AI career mentor inside Career Planner.

You are helping this student with their academic and career journey.

STUDENT INFORMATION:

Name: {profile.full_name}
College: {profile.college}
Degree: {profile.degree}
Branch: {profile.branch}
Career Goal: {profile.career_goal}

Skills:
{", ".join(skill_names) if skill_names else "No skills mapped yet."}

YOUR RESPONSIBILITIES:

1. Give practical and personalized career guidance.
2. Consider the student's existing skills and career goal.
3. Avoid generic advice when personalized advice is possible.
4. Help with programming, DSA, projects, internships,
   resumes, interviews and career planning.
5. If the student asks what they should do next,
   give clear actionable steps.
6. Keep answers understandable for a college student.
7. Do not pretend to have completed actions that you have not completed.
8. Your name is JARVIS.

RESPONSE STYLE:

- Be concise and directly answer the question.
- Usually give 1-4 short paragraphs or 3-6 bullet points.
- Do not repeat the user's question.
- Avoid unnecessary introductions and conclusions.
- Avoid unnecessary tables.
- Use bullets when they make the answer easier to understand.
- If the student asks for detailed, complete, full, or step-by-step
  guidance, provide more detail.
- Keep the response within approximately 500 tokens.
- Never intentionally produce a very long response.

IMPORTANT:

This is a fresh conversation.
Do NOT assume you remember previous conversations with the student.
Use only the student information provided above and the current message.

Answer naturally and conversationally.
"""

        conversation.append({
            "role": "system",
            "content": system_prompt
        })

        # ==================================================
        # CURRENT USER MESSAGE
        # ==================================================

        conversation.append({
            "role": "user",
            "content": user_message
        })

        # ==================================================
        # GROQ
        # ==================================================

        if groq_client is None:
            return {
                "success": False,
                "error": "Groq AI is not configured."
            }, 500

        completion = groq_client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=conversation,
            temperature=0.7,
            max_tokens=500
        )

        # ==================================================
        # GET JARVIS RESPONSE
        # ==================================================

        assistant_message = (
            completion.choices[0]
            .message
            .content
            .strip()
        )

        if not assistant_message:
            return {
                "success": False,
                "error": "JARVIS returned an empty response."
            }, 500

        # ==================================================
        # RETURN TO FRONTEND
        # ==================================================

        return {
            "success": True,
            "response": assistant_message
        }

    except Exception as e:

        print("\n===================================")
        print("JARVIS ERROR")
        print("===================================")
        print(repr(e))
        print("===================================\n")

        return {
            "success": False,
            "error": "I couldn't connect to JARVIS right now. Please try again."
        }, 500# ==========================================================
# LOGOUT
# ==========================================================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("home"))




# ==========================================================
# AI MENTOR
# ==========================================================

@app.route("/dashboard/ai-mentor")
@login_required
def dashboard_ai_mentor():

    # Make sure onboarding is complete
    profile = current_user.profile

    if not profile:
        return redirect(url_for("onboarding_profile"))

    if not profile.academic_details:
        return redirect(url_for("onboarding_academics"))

    if not profile.career_goal:
        return redirect(url_for("onboarding_career"))

    # Get student's skills
    skills = StudentSkill.query.filter_by(
        profile_id=profile.id
    ).all()

    if not skills:
        return redirect(url_for("onboarding_skills"))

    # Get skills that still need improvement
    needs = [
        skill.skill_name
        for skill in skills
        if skill.skill_level in ["Beginner", "Basic"]
    ]

    return render_template(
        "dashboard/ai_mentor.html",
        user=current_user,
        profile=profile,
        skills=skills,
        needs=needs
    )

if __name__ == "__main__":
    app.run(debug=True)