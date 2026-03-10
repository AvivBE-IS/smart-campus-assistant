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

    # 2. Create 10 Departments (Data in Hebrew)
    departments = [
        Department(name="מדע הנתונים"),
        Department(name="ביולוגיה חישובית"),
        Department(name="הנדסת תעשייה וניהול"),
        Department(name="מדעי המחשב"),
        Department(name="הנדסת תוכנה"),
        Department(name="הנדסת חשמל"),
        Department(name="הנדסת מכונות"),
        Department(name="מתמטיקה"),
        Department(name="פיזיקה"),
        Department(name="כימיה")
    ]
    session.add_all(departments)
    session.commit()

    # 3. Create 10 Lecturers
    lecturers = [
        Lecturer(first_name="יוסי", last_name="כהן", seniority=15, rank="פרופסור", office_location="בניין 37, חדר 101", department_id=departments[0].id),
        Lecturer(first_name="דנה", last_name="לוי", seniority=8, rank="ד''ר", office_location="בניין 90, חדר 202", department_id=departments[1].id),
        Lecturer(first_name="רון", last_name="גולן", seniority=20, rank="פרופסור", office_location="בניין 72, חדר 303", department_id=departments[2].id),
        Lecturer(first_name="מיכל", last_name="שפירא", seniority=5, rank="ד''ר", office_location="בניין 37, חדר 404", department_id=departments[3].id),
        Lecturer(first_name="אלי", last_name="אברהם", seniority=12, rank="פרופסור", office_location="בניין 55, חדר 111", department_id=departments[4].id),
        Lecturer(first_name="תמר", last_name="פרידמן", seniority=3, rank="מרצה", office_location="בניין 90, חדר 212", department_id=departments[5].id),
        Lecturer(first_name="אורן", last_name="כץ", seniority=18, rank="פרופסור", office_location="בניין 72, חדר 313", department_id=departments[6].id),
        Lecturer(first_name="יעל", last_name="בר", seniority=7, rank="ד''ר", office_location="בניין 37, חדר 414", department_id=departments[7].id),
        Lecturer(first_name="גיא", last_name="פלד", seniority=10, rank="ד''ר", office_location="בניין 55, חדר 121", department_id=departments[8].id),
        Lecturer(first_name="נועה", last_name="איתן", seniority=2, rank="עוזרת הוראה", office_location="בניין 90, חדר 222", department_id=departments[9].id)
    ]
    session.add_all(lecturers)
    session.commit()

    # 4. Create 10 Students
    students = [
        Student(first_name="אביב", last_name="בן גוריון", residence="באר שבע", year=3, email="aviv@post.bgu.ac.il", phone="050-1111111", department_id=departments[0].id),
        Student(first_name="אליה", last_name="פלאי", residence="באר שבע", year=2, email="eliya@post.bgu.ac.il", phone="054-2222222", department_id=departments[1].id),
        Student(first_name="בועז", last_name="בנאי", residence="תל אביב", year=1, email="boaz@post.bgu.ac.il", phone="052-3333333", department_id=departments[2].id),
        Student(first_name="גל", last_name="כהן", residence="אשקלון", year=4, email="gal@post.bgu.ac.il", phone="053-4444444", department_id=departments[3].id),
        Student(first_name="דינה", last_name="נסיך", residence="באר שבע", year=3, email="dina@post.bgu.ac.il", phone="050-5555555", department_id=departments[4].id),
        Student(first_name="חווה", last_name="פולסטרי", residence="מעונות", year=2, email="hava@post.bgu.ac.il", phone="054-6666666", department_id=departments[5].id),
        Student(first_name="פרנק", last_name="קאסל", residence="נתיבות", year=1, email="frank@post.bgu.ac.il", phone="052-7777777", department_id=departments[6].id),
        Student(first_name="גרייס", last_name="הופר", residence="באר שבע", year=4, email="grace@post.bgu.ac.il", phone="053-8888888", department_id=departments[7].id),
        Student(first_name="היידי", last_name="קלום", residence="עומר", year=3, email="heidi@post.bgu.ac.il", phone="050-9999999", department_id=departments[8].id),
        Student(first_name="איוון", last_name="דראגו", residence="מעונות", year=2, email="ivan@post.bgu.ac.il", phone="054-0000000", department_id=departments[9].id)
    ]
    session.add_all(students)
    session.commit()

    # 5. Create 10 Courses
    courses = [
        Course(name="רגרסיה לינארית", credits=Decimal('3.50'), extra_fee=Decimal('50.00'), department_id=departments[0].id),
        Course(name="למידת מכונה", credits=Decimal('4.00'), extra_fee=Decimal('0.00'), department_id=departments[0].id),
        Course(name="שפת אסמבלי", credits=Decimal('3.00'), extra_fee=Decimal('20.00'), department_id=departments[3].id),
        Course(name="תכנות בפייתון", credits=Decimal('2.50'), extra_fee=Decimal('0.00'), department_id=departments[3].id),
        Course(name="C++ ו-Windows API", credits=Decimal('4.50'), extra_fee=Decimal('100.00'), department_id=departments[4].id),
        Course(name="חדו''א ב", credits=Decimal('5.00'), extra_fee=Decimal('0.00'), department_id=departments[7].id),
        Course(name="אלגברה א", credits=Decimal('5.00'), extra_fee=Decimal('0.00'), department_id=departments[7].id),
        Course(name="מערכות הפעלה", credits=Decimal('4.00'), extra_fee=Decimal('0.00'), department_id=departments[3].id),
        Course(name="הסתברות וסטטיסטיקה", credits=Decimal('3.50'), extra_fee=Decimal('0.00'), department_id=departments[2].id),
        Course(name="פיתוח פול-סטאק", credits=Decimal('3.00'), extra_fee=Decimal('45.00'), department_id=departments[4].id)
    ]
    session.add_all(courses)
    session.commit()

    # 6. Create 10 Groups (with a deliberate exam conflict on 2026-02-06)
    groups = [
        Group(course_id=courses[0].id, group_number=101, day_of_week=DayOfWeek.THURSDAY, start_time=time(14, 0), end_time=time(16, 0), type=GroupType.LECTURE, building="בניין 90", room_number="201", max_capacity=50, exam_date_a=date(2026, 2, 6), exam_date_b=date(2026, 3, 5)),
        Group(course_id=courses[1].id, group_number=202, day_of_week=DayOfWeek.MONDAY, start_time=time(10, 0), end_time=time(12, 0), type=GroupType.LECTURE, building="בניין 72", room_number="105", max_capacity=40, exam_date_a=date(2026, 2, 6), exam_date_b=date(2026, 3, 8)), # Conflict!
        Group(course_id=courses[2].id, group_number=303, day_of_week=DayOfWeek.TUESDAY, start_time=time(8, 0), end_time=time(10, 0), type=GroupType.LECTURE, building="בניין 37", room_number="301", max_capacity=30, exam_date_a=date(2026, 2, 15), exam_date_b=date(2026, 3, 10)),
        Group(course_id=courses[3].id, group_number=404, day_of_week=DayOfWeek.WEDNESDAY, start_time=time(16, 0), end_time=time(18, 0), type=GroupType.TUTORIAL, building="בניין 55", room_number="112", max_capacity=25, exam_date_a=date(2026, 2, 18), exam_date_b=date(2026, 3, 12)),
        Group(course_id=courses[4].id, group_number=505, day_of_week=DayOfWeek.SUNDAY, start_time=time(12, 0), end_time=time(14, 0), type=GroupType.LECTURE, building="בניין 90", room_number="404", max_capacity=45, exam_date_a=date(2026, 2, 20), exam_date_b=date(2026, 3, 15)),
        Group(course_id=courses[5].id, group_number=606, day_of_week=DayOfWeek.MONDAY, start_time=time(14, 0), end_time=time(17, 0), type=GroupType.LECTURE, building="בניין 72", room_number="200", max_capacity=80, exam_date_a=date(2026, 2, 22), exam_date_b=date(2026, 3, 18)),
        Group(course_id=courses[6].id, group_number=707, day_of_week=DayOfWeek.THURSDAY, start_time=time(8, 0), end_time=time(11, 0), type=GroupType.LECTURE, building="בניין 37", room_number="100", max_capacity=90, exam_date_a=date(2026, 2, 25), exam_date_b=date(2026, 3, 20)),
        Group(course_id=courses[7].id, group_number=808, day_of_week=DayOfWeek.TUESDAY, start_time=time(12, 0), end_time=time(14, 0), type=GroupType.LECTURE, building="בניין 55", room_number="333", max_capacity=60, exam_date_a=date(2026, 2, 28), exam_date_b=date(2026, 3, 22)),
        Group(course_id=courses[8].id, group_number=909, day_of_week=DayOfWeek.WEDNESDAY, start_time=time(10, 0), end_time=time(12, 0), type=GroupType.LECTURE, building="בניין 90", room_number="111", max_capacity=55, exam_date_a=date(2026, 3, 1), exam_date_b=date(2026, 3, 25)),
        Group(course_id=courses[9].id, group_number=1010, day_of_week=DayOfWeek.SUNDAY, start_time=time(16, 0), end_time=time(19, 0), type=GroupType.LECTURE, building="בניין 72", room_number="401", max_capacity=35, exam_date_a=date(2026, 3, 3), exam_date_b=date(2026, 3, 28))
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

    print("Database seeded successfully with Hebrew test data.")
    print(f"Created {session.query(Department).count()} departments, {session.query(Student).count()} students, {session.query(Lecturer).count()} lecturers, {session.query(Course).count()} courses, {session.query(Group).count()} groups, and {session.query(Enrollment).count()} enrollments.")
    session.close()

if __name__ == "__main__":
    seed_data()