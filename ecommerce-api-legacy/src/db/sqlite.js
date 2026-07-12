function run(database, sql, parameters = []) {
    return new Promise((resolve, reject) => {
        database.run(sql, parameters, function onRun(error) {
            if (error) {
                reject(error);
                return;
            }

            resolve({ lastID: this.lastID, changes: this.changes });
        });
    });
}

function get(database, sql, parameters = []) {
    return new Promise((resolve, reject) => {
        database.get(sql, parameters, (error, row) => {
            if (error) {
                reject(error);
                return;
            }

            resolve(row);
        });
    });
}

function all(database, sql, parameters = []) {
    return new Promise((resolve, reject) => {
        database.all(sql, parameters, (error, rows) => {
            if (error) {
                reject(error);
                return;
            }

            resolve(rows);
        });
    });
}

function execute(database, sql) {
    return new Promise((resolve, reject) => {
        database.exec(sql, error => error ? reject(error) : resolve());
    });
}

async function withTransaction(database, operation) {
    await execute(database, 'BEGIN IMMEDIATE TRANSACTION');

    try {
        const result = await operation();
        await execute(database, 'COMMIT');
        return result;
    } catch (error) {
        try {
            await execute(database, 'ROLLBACK');
        } catch (rollbackError) {
            error.rollbackError = rollbackError;
        }

        throw error;
    }
}

module.exports = { run, get, all, execute, withTransaction };
