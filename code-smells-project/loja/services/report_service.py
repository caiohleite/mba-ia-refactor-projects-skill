from loja.repositories.report_repository import ReportRepository


DISCOUNT_TIERS = (
    (10_000, 0.10),
    (5_000, 0.05),
    (1_000, 0.02),
)


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
        for minimum_revenue, discount_rate in DISCOUNT_TIERS:
            if revenue > minimum_revenue:
                return revenue * discount_rate
        return 0
