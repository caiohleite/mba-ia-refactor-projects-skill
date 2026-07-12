const express = require('express');
const createCheckoutRoutes = require('./routes/checkoutRoutes');
const createAdminRoutes = require('./routes/adminRoutes');
const createUserRoutes = require('./routes/userRoutes');
const errorHandler = require('./middlewares/errorHandler');

function createApp({
    checkoutController,
    financialReportController,
    userController,
    adminAuth
}) {
    const app = express();

    app.use(express.json());
    app.use(createCheckoutRoutes(checkoutController));
    app.use(createAdminRoutes(financialReportController, adminAuth));
    app.use(createUserRoutes(userController, adminAuth));
    app.use(errorHandler);

    return app;
}

module.exports = createApp;
