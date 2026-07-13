from exceptions import ForbiddenError, NotFoundError
from models.category import Category
from repositories.category_repository import CategoryRepository
from schemas.validators import validate_category_payload


class CategoryService:
    def __init__(self, category_repository=CategoryRepository):
        self.categories = category_repository

    def list_categories(self):
        return self.categories.list_with_task_counts()

    def create_category(self, payload, actor):
        self._ensure_admin(actor)
        category = Category(**validate_category_payload(payload))
        self.categories.add(category)
        self._commit()
        return category

    def update_category(self, category_id, payload, actor):
        self._ensure_admin(actor)
        category = self._get(category_id)
        for field, value in validate_category_payload(payload, partial=True).items():
            setattr(category, field, value)
        self._commit()
        return category

    def delete_category(self, category_id, actor):
        self._ensure_admin(actor)
        category = self._get(category_id)
        self.categories.delete(category)
        self._commit()

    def _get(self, category_id):
        category = self.categories.get(category_id)
        if not category:
            raise NotFoundError("Categoria não encontrada")
        return category

    @staticmethod
    def _ensure_admin(actor):
        if not actor or actor.role != "admin":
            raise ForbiddenError()

    def _commit(self):
        try:
            self.categories.commit()
        except Exception:
            self.categories.rollback()
            raise

