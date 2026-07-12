const createApp = require('./app');
const { getConfig } = require('./config');
const { openDatabase, closeDatabase } = require('./db/connection');
const { initializeDatabase } = require('./db/initialize');
const UserRepository = require('./repositories/userRepository');
const CourseRepository = require('./repositories/courseRepository');
const EnrollmentRepository = require('./repositories/enrollmentRepository');
const PaymentRepository = require('./repositories/paymentRepository');
const AuditRepository = require('./repositories/auditRepository');
const ReportRepository = require('./repositories/reportRepository');
const TransactionManager = require('./repositories/transactionManager');
const passwordService = require('./services/passwordService');
const CheckoutService = require('./services/checkoutService');
const FinancialReportService = require('./services/financialReportService');
const UserService = require('./services/userService');
const CheckoutController = require('./controllers/checkoutController');
const FinancialReportController = require('./controllers/financialReportController');
const UserController = require('./controllers/userController');
const { createAdminAuth } = require('./middlewares/adminAuth');

async function buildApplication({ env = process.env } = {}) {
    const config = getConfig(env);
    const database = await openDatabase();

    try {
        const seedPasswordHash = await passwordService.createUnusablePassword();
        await initializeDatabase(database, { seedPasswordHash });

        const userRepository = new UserRepository(database);
        const checkoutService = new CheckoutService({
            userRepository,
            courseRepository: new CourseRepository(database),
            enrollmentRepository: new EnrollmentRepository(database),
            paymentRepository: new PaymentRepository(database),
            auditRepository: new AuditRepository(database),
            transactionManager: new TransactionManager(database),
            hashPassword: passwordService.hashPassword
        });

        const app = createApp({
            checkoutController: new CheckoutController(checkoutService),
            financialReportController: new FinancialReportController(
                new FinancialReportService(new ReportRepository(database))
            ),
            userController: new UserController(new UserService(userRepository)),
            adminAuth: createAdminAuth(config)
        });

        return { app, database, config };
    } catch (error) {
        await closeDatabase(database);
        throw error;
    }
}

async function startServer(options) {
    const application = await buildApplication(options);
    const server = application.app.listen(application.config.port);
    return { ...application, server };
}

if (require.main === module) {
    startServer()
        .then(({ config }) => {
            console.log(`LMS API rodando na porta ${config.port}.`);
        })
        .catch(() => {
            console.error('[STARTUP] Não foi possível iniciar a aplicação.');
            process.exitCode = 1;
        });
}

module.exports = { buildApplication, startServer };
