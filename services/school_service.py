from __future__ import annotations

from database.school_repository import SchoolRepository
from models.entities import School


class SchoolService:
    def __init__(self, repository: SchoolRepository | None = None) -> None:
        self.repository = repository or SchoolRepository()

    def list_schools(self) -> list[School]:
        return self.repository.list_schools()

    def create_school(self, name: str) -> School:
        self._validate_name(name)
        return self.repository.create_school(name)

    def get_or_create_school(self, name: str) -> School:
        self._validate_name(name)
        existing = self.repository.find_by_name(name)
        if existing is not None:
            return existing
        return self.repository.create_school(name)

    def update_school(self, school_id: int, name: str) -> None:
        self._validate_name(name)
        self.repository.update_school(school_id, name)

    def delete_school(self, school_id: int) -> None:
        self.repository.delete_school(school_id)

    @staticmethod
    def _validate_name(name: str) -> None:
        if not name.strip():
            raise ValueError("El nombre de la escuela es obligatorio.")
