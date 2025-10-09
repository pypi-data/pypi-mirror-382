from oneroster_api import Users

building_map = {
    "A3700.1": "A3700.1",
    "A3700.2": "A3700.2",
    "A3700.3": "A3700.3",
    "A3700.4": "A3700.1",
}


def build_teacher_data(
    users_list: list[Users], gam_user_data: list[dict]
) -> list[dict]:
    teachers = [
        {
            "School_id": get_building_id(gam_user_data, teacher.email),
            "Teacher_id": teacher.identifier,
            "Teacher_number": teacher.sourced_id,
            "State_id": teacher.state_id,
            "First_name": teacher.first_name,
            "Last_name": teacher.last_name,
            "Teacher_email": teacher.email.lower(),
            "Username": teacher.email.split("@")[0].lower(),
        }
        for teacher in users_list
        if teacher.role == "teacher" and teacher.email
    ]
    return [
        teacher
        for teacher in teachers
        if teacher["School_id"] and teacher["School_id"].strip()
    ]


def get_building_id(user_list: list[dict], email: str) -> str | None:
    for user in user_list:
        if user["primaryEmail"].lower().strip() == email.lower().strip():
            if user["locations.0.buildingId"] in building_map.keys():
                return building_map[user["locations.0.buildingId"]]

    return None
