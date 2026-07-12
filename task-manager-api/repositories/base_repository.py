from database import db


class BaseRepository:
    @staticmethod
    def add(entity):
        db.session.add(entity)
        return entity

    @staticmethod
    def delete(entity):
        db.session.delete(entity)

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def rollback():
        db.session.rollback()

