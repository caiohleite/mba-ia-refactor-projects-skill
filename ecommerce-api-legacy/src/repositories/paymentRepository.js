const { run } = require('../db/sqlite');

class PaymentRepository {
    constructor(database) {
        this.database = database;
    }

    async create({ enrollmentId, amount, status }) {
        const result = await run(
            this.database,
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [enrollmentId, amount, status]
        );

        return { id: result.lastID, enrollmentId, amount, status };
    }
}

module.exports = PaymentRepository;
