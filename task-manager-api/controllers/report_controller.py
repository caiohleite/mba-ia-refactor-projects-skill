from flask import g, jsonify

from services.report_service import ReportService


class ReportController:
    service = ReportService()

    @classmethod
    def summary(cls):
        return jsonify(cls.service.summary(g.current_user)), 200

    @classmethod
    def user_report(cls, user_id):
        return jsonify(cls.service.user_report(user_id, g.current_user)), 200
