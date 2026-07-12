const { withTransaction } = require('../db/sqlite');

class TransactionManager {
    constructor(database) {
        this.database = database;
    }

    run(operation) {
        return withTransaction(this.database, operation);
    }
}

module.exports = TransactionManager;
