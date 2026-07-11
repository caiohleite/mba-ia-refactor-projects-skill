from loja.services.report_service import ReportService


class ReportController:
    def __init__(self, service=None):
        self.service = service or ReportService()

    def sales_report(self):
        return {"dados": self.service.sales_report(), "sucesso": True}, 200
