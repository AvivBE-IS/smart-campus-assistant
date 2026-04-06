"""
Infrastructure & Deployment:
This module isolates data persistence logic, ensuring that database models and schema definitions
are decoupled from the application logic. This separation supports clean architecture principles
and simplifies database migrations and management.

System Development:
By defining models here, we establish a clear contract for data structure, enabling
consistent interactions across the backend services.
"""
from datetime import datetime, timezone
import enum
import pathlib
from datetime import datetime
from decimal import Decimal
from sqlalchemy import (
    create_engine, Column, Integer, String, ForeignKey, 
    DECIMAL, Date, Time, Enum, Table, DateTime
)
from sqlalchemy.orm import declarative_base, relationship

# Define the database file path (SQLite) using pathlib for dynamic resolution
BASE_DIR = pathlib.Path(__file__).parent.resolve()
DB_FILE = BASE_DIR / 'smart_campus.db'
DATABASE_URL = f"sqlite:///{DB_FILE}"

Base = declarative_base()

# ---------------------------------------------------------
# Enums
# ---------------------------------------------------------

class GroupType(enum.Enum):
    LECTURE = "Lecture"
    TUTORIAL = "Tutorial"

class DayOfWeek(enum.Enum):
    SUNDAY = "Sunday"
    MONDAY = "Monday"
    TUESDAY = "Tuesday"
    WEDNESDAY = "Wednesday"
    THURSDAY = "Thursday"
    FRIDAY = "Friday"
    SATURDAY = "Saturday"

# ---------------------------------------------------------
# Association Tables
# ---------------------------------------------------------

# CoursePrerequisite: Self-referential many-to-many table
# Links a course to its required prerequisite courses.
course_prerequisites = Table(
    'course_prerequisites',
    Base.metadata,
    Column('course_id', Integer, ForeignKey('courses.id'), primary_key=True),
    Column('prerequisite_id', Integer, ForeignKey('courses.id'), primary_key=True)
)

# ---------------------------------------------------------
# Models
# ---------------------------------------------------------

class Department(Base):
    __tablename__ = 'departments'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True)

    # Relationships
    students = relationship("Student", back_populates="department")
    lecturers = relationship("Lecturer", back_populates="department")
    courses = relationship("Course", back_populates="department")

    def __repr__(self):
        return f"<Department(id={self.id}, name='{self.name}')>"


class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    residence = Column(String)
    year = Column(Integer)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))

    # Relationships
    department = relationship("Department", back_populates="students")
    enrollments = relationship("Enrollment", back_populates="student")


class Lecturer(Base):
    __tablename__ = 'lecturers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    seniority = Column(Integer)  # Years of experience
    rank = Column(String)        # e.g., Professor, Dr.
    office_location = Column(String)
    office_hours = Column(String)
    department_id = Column(Integer, ForeignKey('departments.id'))

    # Relationships
    department = relationship("Department", back_populates="lecturers")


class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    credits = Column(DECIMAL(10, 2), nullable=False)  # High precision
    extra_fee = Column(DECIMAL(10, 2), default=Decimal('0.00'))
    department_id = Column(Integer, ForeignKey('departments.id'))

    # Relationships
    department = relationship("Department", back_populates="courses")
    groups = relationship("Group", back_populates="course")

    # Self-referential relationship for prerequisites
    prerequisites = relationship(
        "Course",
        secondary=course_prerequisites,
        primaryjoin=(id == course_prerequisites.c.course_id),
        secondaryjoin=(id == course_prerequisites.c.prerequisite_id),
        backref="required_for_courses"
    )


class Group(Base):
    __tablename__ = 'groups'

    id = Column(Integer, primary_key=True, autoincrement=True)
    course_id = Column(Integer, ForeignKey('courses.id'), nullable=False)
    group_number = Column(Integer, nullable=False)
    day_of_week = Column(Enum(DayOfWeek), nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    type = Column(Enum(GroupType), nullable=False)
    building = Column(String)
    room_number = Column(String)
    max_capacity = Column(Integer)
    exam_date_a = Column(Date)
    exam_date_b = Column(Date)

    # Relationships
    course = relationship("Course", back_populates="groups")
    enrollments = relationship("Enrollment", back_populates="group")


class Enrollment(Base):
    """
    Association Object for Many-to-Many relationship between Student and Group.
    """
    __tablename__ = 'enrollments'

    student_id = Column(Integer, ForeignKey('students.id'), primary_key=True)
    group_id = Column(Integer, ForeignKey('groups.id'), primary_key=True)
    grade = Column(Integer, nullable=True)
    enrollment_date = Column(Date, default=datetime.now)

    # Relationships
    student = relationship("Student", back_populates="enrollments")
    group = relationship("Group", back_populates="enrollments")

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True) 
    password = Column(String, nullable=False) 
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    messages = relationship("Message", back_populates="owner")
    conversations = relationship("Conversation", back_populates="owner", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"


class Conversation(Base):
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    role = Column(String)
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="messages")
    conversation = relationship("Conversation", back_populates="messages")

if __name__ == "__main__":
    # Initialize the database if run as a script
    engine = create_engine(DATABASE_URL, echo=True)
    Base.metadata.create_all(engine)
    print(f"Database initialized at {DB_FILE}")