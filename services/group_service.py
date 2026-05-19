from __future__ import annotations

from models.entities import Group

from database.group_repository import GroupRepository


class GroupService:
    def __init__(self, repository: GroupRepository | None = None) -> None:
        self.repository = repository or GroupRepository()

    def list_groups(self) -> list[Group]:
        return self.repository.list_groups()

    def create_group(
        self,
        name: str,
        school_id: int | None,
        subject_name: str,
        school_year: str,
        grade_level: str,
        group_section: str,
        passing_grade: float,
    ) -> Group:
        name = self._normalize_group_name(name)
        grade_level = Group.normalize_grade_level(grade_level)
        group_section = group_section.strip().upper()
        self._validate_name(name)
        self._validate_passing_grade(passing_grade)
        return self.repository.create_group(
            Group(
                id=None,
                name=name,
                school_id=school_id,
                subject_name=subject_name,
                school_year=school_year,
                grade_level=grade_level,
                group_section=group_section,
                passing_grade=passing_grade,
            )
        )

    def find_matching_group(
        self,
        *,
        school_id: int | None,
        grade_level: str,
        group_section: str,
        school_year: str = "",
    ) -> Group | None:
        if not grade_level.strip() or not group_section.strip():
            return None
        normalized_grade = Group.normalize_grade_level(grade_level)
        normalized_section = group_section.strip().upper()
        normalized_year = school_year.strip().lower()
        for group in self.list_groups():
            if group.school_id != school_id:
                continue
            if Group.normalize_grade_level(group.grade_level) != normalized_grade:
                continue
            if group.group_section.strip().upper() != normalized_section:
                continue
            if normalized_year and group.school_year.strip().lower() != normalized_year:
                continue
            return group
        return None

    def update_group(
        self,
        group_id: int,
        name: str,
        school_id: int | None,
        subject_name: str,
        school_year: str,
        grade_level: str,
        group_section: str,
        passing_grade: float,
    ) -> None:
        name = self._normalize_group_name(name)
        grade_level = Group.normalize_grade_level(grade_level)
        group_section = group_section.strip().upper()
        self._validate_name(name)
        self._validate_passing_grade(passing_grade)
        self.repository.update_group(
            Group(
                id=group_id,
                name=name,
                school_id=school_id,
                subject_name=subject_name,
                school_year=school_year,
                grade_level=grade_level,
                group_section=group_section,
                passing_grade=passing_grade,
            )
        )

    def delete_group(self, group_id: int) -> None:
        self.repository.delete_group(group_id)

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name or not name.strip():
            raise ValueError("El nombre del grupo es obligatorio.")

    @staticmethod
    def _validate_passing_grade(passing_grade: float) -> None:
        if passing_grade < 0 or passing_grade > 100:
            raise ValueError("El minimo aprobatorio debe estar entre 0 y 100.")

    @staticmethod
    def _normalize_group_name(name: str) -> str:
        parts = [part.strip() for part in name.split("-", 1)]
        if len(parts) == 2:
            return f"{Group.normalize_grade_level(parts[0])}-{parts[1].upper()}"
        return name.strip()
