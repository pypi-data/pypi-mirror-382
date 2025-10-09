"""Init."""

from pathlib import Path
import csv
from .academic_sessions import AcademicSessions
from .classes import Classes
from .client import set_credentials
from .courses import Courses
from .demographics import Demographics
from .enrollments import Enrollments
from .users import Users

__all__ = [
    "AcademicSessions",
    "Classes",
    "Courses",
    "Demographics",
    "Enrollments",
    "Users",
    "set_credentials",
]


def import_oneroster_data() -> dict:
    """Uses api to import all oneroster data."""
    return {
        "users": Users.retrieve_all(),
        "academic_sessions": AcademicSessions.retrieve_all(),
        "classes": Classes.retrieve_all(),
        "demographics": Demographics.retrieve_all(),
        "courses": Courses.retrieve_all(),
        "enrollments": Enrollments.retrieve_all()
    }

def download_oneroster_data(oneroster_data: dict, export_path: Path = Path()) -> None:
    for filename, data in oneroster_data.items():
        filepath = export_path/f"{filename}.csv"
        data_dict = [item.__dict__ for item in data]
        print(data_dict)
        headers = data_dict[0].keys()
        with open(filepath, "w", encoding="utf8") as file:
            writer = csv.DictWriter(file, headers)
            writer.writeheader()
            writer.writerows(data)
