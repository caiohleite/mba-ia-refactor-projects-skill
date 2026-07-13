const { run } = require('../db/sqlite');

class AuditRepository {
    constructor(database) {
        this.database = database;
    }

    record(action) {
        return run(
            this.database,
            "INSERT INTO audit_logs (action, created_at) VALUES (?, datetime('now'))",
            [action]
        );
    }
}

module.exports = AuditRepository;
