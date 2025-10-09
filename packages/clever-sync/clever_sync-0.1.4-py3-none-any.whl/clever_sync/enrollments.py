from oneroster_api import Enrollments
from datetime import datetime, date


def build_enrollment_data(
    enrollments_list: list[Enrollments], sections_data: list[dict]
) -> list[dict]:
    return [
        {
            "School_id": get_school_id(sections_data, enrollment.class_id),
            "Section_id": enrollment.class_id,
            "Student_id": int(enrollment.user.split("S")[-1]),
        }
        for enrollment in enrollments_list
        if enrollment.role == "student" and verify_dates(enrollment)
    ]

def verify_dates(enrollment: Enrollments) -> bool:
    start_date = datetime.strptime(enrollment.begin_date, "%Y-%m-%d").date()
    end_date = datetime.strptime(enrollment.end_date, "%Y-%m-%d").date()
    today = date.today()
    # print(f"Start Date: {start_date}, End Date: {end_date}, Today: {today}, After Start: {start_date <= today}, Before End: {today <= end_date}")
    return (start_date <= today <= end_date)

def get_school_id(sections_data: list[dict], section_id: int) -> str | None:
    for section in sections_data:
        if section["Section_id"] == section_id:
            return section["School_id"]
    return None
