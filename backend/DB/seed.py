import sys
import pathlib
# Add current directory to sys.path to ensure local imports work
sys.path.append(str(pathlib.Path(__file__).parent.resolve()))

from datetime import date, time
from decimal import Decimal
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Import models from the local models.py file
from models import (
    Base, Department, Student, Lecturer, Course, Group, Enrollment,
    GroupType, DayOfWeek, DATABASE_URL
)

def seed_data():
    engine = create_engine(DATABASE_URL)
    Session = sessionmaker(bind=engine)
    session = Session()

    # 1. Clean slate - drop all tables and recreate them
    print("Recreating database schema...")
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    # 2. Create 10 Departments
    departments = [
        Department(name="Data Science"),
        Department(name="Computational Biology"),
        Department(name="Industrial Engineering & Management"),
        Department(name="Computer Science"),
        Department(name="Software Engineering"),
        Department(name="Electrical Engineering"),
        Department(name="Mechanical Engineering"),
        Department(name="Mathematics"),
        Department(name="Physics"),
        Department(name="Chemistry")
    ]
    session.add_all(departments)
    session.commit()

    # 3. Create 10 Lecturers
    lecturers = [
        Lecturer(first_name="Yossi", last_name="Cohen", seniority=15, rank="Professor", office_location="Building 37, Room 101", department_id=departments[0].id),
        Lecturer(first_name="Dana", last_name="Levi", seniority=8, rank="Dr.", office_location="Building 90, Room 202", department_id=departments[1].id),
        Lecturer(first_name="Ron", last_name="Golan", seniority=20, rank="Professor", office_location="Building 72, Room 303", department_id=departments[2].id),
        Lecturer(first_name="Michal", last_name="Shapira", seniority=5, rank="Dr.", office_location="Building 37, Room 404", department_id=departments[3].id),
        Lecturer(first_name="Eli", last_name="Abraham", seniority=12, rank="Professor", office_location="Building 55, Room 111", department_id=departments[4].id),
        Lecturer(first_name="Tamar", last_name="Friedman", seniority=3, rank="Lecturer", office_location="Building 90, Room 212", department_id=departments[5].id),
        Lecturer(first_name="Oren", last_name="Katz", seniority=18, rank="Professor", office_location="Building 72, Room 313", department_id=departments[6].id),
        Lecturer(first_name="Yael", last_name="Bar", seniority=7, rank="Dr.", office_location="Building 37, Room 414", department_id=departments[7].id),
        Lecturer(first_name="Guy", last_name="Peled", seniority=10, rank="Dr.", office_location="Building 55, Room 121", department_id=departments[8].id),
        Lecturer(first_name="Noa", last_name="Eitan", seniority=2, rank="Teaching Assistant", office_location="Building 90, Room 222", department_id=departments[9].id)
    ]
    session.add_all(lecturers)
    session.commit()

    # 4. Create 10 Students
    students = [
        Student(first_name="Aviv", last_name="Ben-Gurion", residence="Beer Sheva", year=3, email="aviv@post.bgu.ac.il", phone="050-1111111", department_id=departments[0].id),
        Student(first_name="Eliya", last_name="Palai", residence="Beer Sheva", year=2, email="eliya@post.bgu.ac.il", phone="054-2222222", department_id=departments[1].id),
        Student(first_name="Boaz", last_name="Banai", residence="Tel Aviv", year=1, email="boaz@post.bgu.ac.il", phone="052-3333333", department_id=departments[2].id),
        Student(first_name="Gal", last_name="Cohen", residence="Ashkelon", year=4, email="gal@post.bgu.ac.il", phone="053-4444444", department_id=departments[3].id),
        Student(first_name="Dina", last_name="Nasich", residence="Beer Sheva", year=3, email="dina@post.bgu.ac.il", phone="050-5555555", department_id=departments[4].id),
        Student(first_name="Hava", last_name="Polstri", residence="Dormitories", year=2, email="hava@post.bgu.ac.il", phone="054-6666666", department_id=departments[5].id),
        Student(first_name="Frank", last_name="Castle", residence="Netivot", year=1, email="frank@post.bgu.ac.il", phone="052-7777777", department_id=departments[6].id),
        Student(first_name="Grace", last_name="Hopper", residence="Beer Sheva", year=4, email="grace@post.bgu.ac.il", phone="053-8888888", department_id=departments[7].id),
        Student(first_name="Heidi", last_name="Klum", residence="Omer", year=3, email="heidi@post.bgu.ac.il", phone="050-9999999", department_id=departments[8].id),
        Student(first_name="Ivan", last_name="Drago", residence="Dormitories", year=2, email="ivan@post.bgu.ac.il", phone="054-0000000", department_id=departments[9].id)
    ]
    session.add_all(students)
    session.commit()

    # 5. Create 10 Courses
    courses = [
        Course(name="Linear Regression", credits=Decimal('3.50'), extra_fee=Decimal('50.00'), department_id=departments[0].id),
        Course(name="Machine Learning", credits=Decimal('4.00'), extra_fee=Decimal('0.00'), department_id=departments[0].id),
        Course(name="Assembly Language", credits=Decimal('3.00'), extra_fee=Decimal('20.00'), department_id=departments[3].id),
        Course(name="Python Programming", credits=Decimal('2.50'), extra_fee=Decimal('0.00'), department_id=departments[3].id),
        Course(name="C++ and Windows API", credits=Decimal('4.50'), extra_fee=Decimal('100.00'), department_id=departments[4].id),
        Course(name="Calculus B", credits=Decimal('5.00'), extra_fee=Decimal('0.00'), department_id=departments[7].id),
        Course(name="Algebra A", credits=Decimal('5.00'), extra_fee=Decimal('0.00'), department_id=departments[7].id),
        Course(name="Operating Systems", credits=Decimal('4.00'), extra_fee=Decimal('0.00'), department_id=departments[3].id),
        Course(name="Probability and Statistics", credits=Decimal('3.50'), extra_fee=Decimal('0.00'), department_id=departments[2].id),
        Course(name="Full-Stack Development", credits=Decimal('3.00'), extra_fee=Decimal('45.00'), department_id=departments[4].id)
    ]
    session.add_all(courses)
    session.commit()

    # 6. Create 10 Groups (with a deliberate exam conflict on 2026-02-06)
    groups = [
        Group(course_id=courses[0].id, group_number=101, day_of_week=DayOfWeek.THURSDAY, start_time=time(14, 0), end_time=time(16, 0), type=GroupType.LECTURE, building="Building 90", room_number="201", max_capacity=50, exam_date_a=date(2026, 2, 6), exam_date_b=date(2026, 3, 5)),
        Group(course_id=courses[1].id, group_number=202, day_of_week=DayOfWeek.MONDAY, start_time=time(10, 0), end_time=time(12, 0), type=GroupType.LECTURE, building="Building 72", room_number="105", max_capacity=40, exam_date_a=date(2026, 2, 6), exam_date_b=date(2026, 3, 8)), # Conflict!
        Group(course_id=courses[2].id, group_number=303, day_of_week=DayOfWeek.TUESDAY, start_time=time(8, 0), end_time=time(10, 0), type=GroupType.LECTURE, building="Building 37", room_number="301", max_capacity=30, exam_date_a=date(2026, 2, 15), exam_date_b=date(2026, 3, 10)),
        Group(course_id=courses[3].id, group_number=404, day_of_week=DayOfWeek.WEDNESDAY, start_time=time(16, 0), end_time=time(18, 0), type=GroupType.TUTORIAL, building="Building 55", room_number="112", max_capacity=25, exam_date_a=date(2026, 2, 18), exam_date_b=date(2026, 3, 12)),
        Group(course_id=courses[4].id, group_number=505, day_of_week=DayOfWeek.SUNDAY, start_time=time(12, 0), end_time=time(14, 0), type=GroupType.LECTURE, building="Building 90", room_number="404", max_capacity=45, exam_date_a=date(2026, 2, 20), exam_date_b=date(2026, 3, 15)),
        Group(course_id=courses[5].id, group_number=606, day_of_week=DayOfWeek.MONDAY, start_time=time(14, 0), end_time=time(17, 0), type=GroupType.LECTURE, building="Building 72", room_number="200", max_capacity=80, exam_date_a=date(2026, 2, 22), exam_date_b=date(2026, 3, 18)),
        Group(course_id=courses[6].id, group_number=707, day_of_week=DayOfWeek.THURSDAY, start_time=time(8, 0), end_time=time(11, 0), type=GroupType.LECTURE, building="Building 37", room_number="100", max_capacity=90, exam_date_a=date(2026, 2, 25), exam_date_b=date(2026, 3, 20)),
        Group(course_id=courses[7].id, group_number=808, day_of_week=DayOfWeek.TUESDAY, start_time=time(12, 0), end_time=time(14, 0), type=GroupType.LECTURE, building="Building 55", room_number="333", max_capacity=60, exam_date_a=date(2026, 2, 28), exam_date_b=date(2026, 3, 22)),
        Group(course_id=courses[8].id, group_number=909, day_of_week=DayOfWeek.WEDNESDAY, start_time=time(10, 0), end_time=time(12, 0), type=GroupType.LECTURE, building="Building 90", room_number="111", max_capacity=55, exam_date_a=date(2026, 3, 1), exam_date_b=date(2026, 3, 25)),
        Group(course_id=courses[9].id, group_number=1010, day_of_week=DayOfWeek.SUNDAY, start_time=time(16, 0), end_time=time(19, 0), type=GroupType.LECTURE, building="Building 72", room_number="401", max_capacity=35, exam_date_a=date(2026, 3, 3), exam_date_b=date(2026, 3, 28))
    ]
    session.add_all(groups)
    session.commit()

    # 7. Create Enrollments
    enrollments = [
        Enrollment(student_id=students[0].id, group_id=groups[0].id, grade=95), # Aviv in Linear Regression
        Enrollment(student_id=students[0].id, group_id=groups[1].id, grade=None), # Aviv in Machine Learning (Exam Conflict!)
        Enrollment(student_id=students[0].id, group_id=groups[3].id, grade=98), # Aviv in Python
        Enrollment(student_id=students[1].id, group_id=groups[5].id, grade=85), # Eliya in Calculus B
        Enrollment(student_id=students[1].id, group_id=groups[8].id, grade=88), # Eliya in Statistics
        Enrollment(student_id=students[2].id, group_id=groups[6].id, grade=75), # Boaz in Algebra A
        Enrollment(student_id=students[3].id, group_id=groups[2].id, grade=90), # Gal in Assembly
        Enrollment(student_id=students[3].id, group_id=groups[7].id, grade=92), # Gal in Operating Systems
        Enrollment(student_id=students[4].id, group_id=groups[4].id, grade=100),# Dina in C++
        Enrollment(student_id=students[4].id, group_id=groups[9].id, grade=96), # Dina in Full-Stack
        Enrollment(student_id=students[5].id, group_id=groups[5].id, grade=None),# Hava in Calculus B
        Enrollment(student_id=students[6].id, group_id=groups[6].id, grade=None) # Frank in Algebra A
    ]
    session.add_all(enrollments)
    session.commit()

    print("Database seeded successfully with English data.")
    print(f"Created {session.query(Department).count()} departments, {session.query(Student).count()} students, {session.query(Lecturer).count()} lecturers, {session.query(Course).count()} courses, {session.query(Group).count()} groups, and {session.query(Enrollment).count()} enrollments.")
    session.close()

if __name__ == "__main__":
    seed_data()