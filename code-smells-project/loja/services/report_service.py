from loja.repositories.report_repository import ReportRepository


class ReportService:
    def __init__(self, repository=None):
        self.repository = repository or ReportRepository()

    def sales_report(self):
        summary = self.repository.sales_summary()
        total_orders = summary["total_pedidos"]
        revenue = summary["faturamento"]
        discount = self._calculate_discount(revenue)
        return {
            "total_pedidos": total_orders,
            "faturamento_bruto": round(revenue, 2),
            "desconto_aplicavel": round(discount, 2),
            "faturamento_liquido": round(revenue - discount, 2),
            "pedidos_pendentes": summary["pendentes"],
            "pedidos_aprovados": summary["aprovados"],
            "pedidos_cancelados": summary["cancelados"],
            "ticket_medio": round(revenue / total_orders, 2) if total_orders else 0,
        }

    @staticmethod
    def _calculate_discount(revenue):
        if revenue > 10000:
            return revenue * 0.10
        if revenue > 5000:
            return revenue * 0.05
        if revenue > 1000:
            return revenue * 0.02
        return 0
