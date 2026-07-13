const { all } = require('../db/sqlite');

const FINANCIAL_REPORT_QUERY = `
    SELECT
        c.id AS course_id,
        c.title AS course,
        e.id AS enrollment_id,
        u.name AS student,
        p.amount AS amount,
        p.status AS payment_status
    FROM courses c
    LEFT JOIN enrollments e ON e.course_id = c.id
    LEFT JOIN users u ON u.id = e.user_id
    LEFT JOIN payments p ON p.enrollment_id = e.id
    ORDER BY c.id, e.id
`;

class ReportRepository {
    constructor(database) {
        this.database = database;
    }

    getFinancialRows() {
        return all(this.database, FINANCIAL_REPORT_QUERY);
    }
}

module.exports = ReportRepository;
