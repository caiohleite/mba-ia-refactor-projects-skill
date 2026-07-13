const express = require('express');

function createAdminRoutes(financialReportController, adminAuth) {
    const router = express.Router();
    router.get('/api/admin/financial-report', adminAuth, financialReportController.show);
    return router;
}

module.exports = createAdminRoutes;
