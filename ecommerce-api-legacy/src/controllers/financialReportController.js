class FinancialReportController {
    constructor(financialReportService) {
        this.financialReportService = financialReportService;
        this.show = this.show.bind(this);
    }

    async show(req, res, next) {
        try {
            const report = await this.financialReportService.generate();
            return res.status(200).json(report);
        } catch (error) {
            return next(error);
        }
    }
}

module.exports = FinancialReportController;
