const sqlite3 = require('sqlite3').verbose();

function openDatabase(filename = ':memory:') {
    return new Promise((resolve, reject) => {
        const database = new sqlite3.Database(filename, error => {
            if (error) {
                reject(error);
                return;
            }

            resolve(database);
        });
    });
}

function closeDatabase(database) {
    return new Promise((resolve, reject) => {
        database.close(error => error ? reject(error) : resolve());
    });
}

module.exports = { openDatabase, closeDatabase };
