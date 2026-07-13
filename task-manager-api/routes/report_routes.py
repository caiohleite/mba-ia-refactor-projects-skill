from flask import Blueprint

from controllers.report_controller import ReportController
from middlewares.auth import authenticated, roles_required


report_bp = Blueprint("reports", __name__)


@report_bp.get("/reports/summary")
@roles_required("admin", "manager")
def summary_report():
    return ReportController.summary()


@report_bp.get("/reports/user/<int:user_id>")
@authenticated
def user_report(user_id):
    return ReportController.user_report(user_id)
