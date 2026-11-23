from enum import StrEnum


class Role(StrEnum):
    """The three roles from the spec.

    admin    — manages users and (later) risk rules for their own org
    reviewer — reviews extractions and job assessments
    engineer — uploads documents, asks questions, creates assessments
    """

    ADMIN = "admin"
    REVIEWER = "reviewer"
    ENGINEER = "engineer"
