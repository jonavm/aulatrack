from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import re


@dataclass(slots=True)
class Group:
    id: Optional[int]
    name: str
    school_id: Optional[int] = None
    school_name: str = ""
    subject_name: str = ""
    school_year: str = ""
    grade_level: str = ""
    group_section: str = ""
    passing_grade: float = 60.0
    student_count: int = 0

    @property
    def display_name(self) -> str:
        if self.grade_level and self.group_section:
            return f"{self.formatted_grade_level}-{self.formatted_group_section}"
        return self.name

    @property
    def qualified_display_name(self) -> str:
        school_name = " ".join(self.school_name.strip().split())
        if school_name:
            return f"{self.display_name} · {school_name}"
        return self.display_name

    @property
    def formatted_grade_level(self) -> str:
        return self.normalize_grade_level(self.grade_level)

    @property
    def formatted_group_section(self) -> str:
        return self.group_section.strip().upper()

    @staticmethod
    def normalize_grade_level(value: str) -> str:
        text = " ".join(value.strip().split())
        if not text:
            return ""
        text = re.sub(r"(?i)(\d+)\s*[o°]$", r"\1º", text)
        return text


@dataclass(slots=True)
class School:
    id: Optional[int]
    name: str


@dataclass(slots=True)
class Student:
    id: Optional[int]
    group_id: int
    first_name: str
    last_name: str
    student_code: str = ""
    is_active: bool = True
    notes: str = ""

    @property
    def full_name(self) -> str:
        return self.roster_name

    @property
    def natural_name(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()

    @property
    def roster_name(self) -> str:
        paternal, maternal = self._split_last_names(self.last_name)
        given_names = " ".join(self.first_name.strip().split())
        if paternal and maternal:
            return f"{paternal} {maternal} {given_names}".strip()
        if paternal:
            return f"{paternal} {given_names}".strip()
        return given_names

    @staticmethod
    def _split_last_names(value: str) -> tuple[str, str]:
        text = " ".join(value.strip().split())
        if not text:
            return "", ""
        if "/" in text:
            parts = [part.strip() for part in text.split("/") if part.strip()]
            if len(parts) >= 2:
                return parts[0], " / ".join(parts[1:])
        parts = text.split()
        if len(parts) == 1:
            return parts[0], ""
        if len(parts) == 2:
            return parts[0], parts[1]
        return text, ""


@dataclass(slots=True)
class EvaluationCategory:
    id: Optional[int]
    group_id: int
    name: str
    weight_percent: float
    period_number: int = 1
    category_mode: str = "normal"
    deduction_base_score: float = 100.0
    is_active: bool = True
    sort_order: int = 0
    is_custom: bool = False
    activity_count: int = 0


@dataclass(slots=True)
class Activity:
    id: Optional[int]
    category_id: int
    name: str
    max_score: float = 100.0
    due_date: Optional[str] = None
    applies_to_risk: bool = True
    sort_order: int = 0
    category_name: str = ""


@dataclass(slots=True)
class GradeEntry:
    id: Optional[int]
    activity_id: int
    student_id: int
    score: Optional[float] = None
    status: str = "pending"
    comment: str = ""


@dataclass(slots=True)
class AttendanceSession:
    id: Optional[int]
    group_id: int
    session_date: str
    note: str = ""


@dataclass(slots=True)
class AttendanceRecord:
    id: Optional[int]
    session_id: int
    student_id: int
    status: str = "present"
    comment: str = ""


@dataclass(slots=True)
class StudentAdjustment:
    id: Optional[int]
    group_id: int
    student_id: int
    points: float = 0.0
    note: str = ""


@dataclass(slots=True)
class StudentCategoryDeductionEntry:
    id: Optional[int]
    category_id: int
    student_id: int
    points: float = 0.0
    note: str = ""
    created_at: str = ""
