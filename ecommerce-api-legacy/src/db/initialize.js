const { execute, run, withTransaction } = require('./sqlite');

const SCHEMA = `
    PRAGMA foreign_keys = ON;

    CREATE TABLE users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        pass TEXT NOT NULL
    );

    CREATE TABLE courses (
        id INTEGER PRIMARY KEY,
        title TEXT NOT NULL,
        price REAL NOT NULL,
        active INTEGER NOT NULL DEFAULT 1
    );

    CREATE TABLE enrollments (
        id INTEGER PRIMARY KEY,
        user_id INTEGER NOT NULL,
        course_id INTEGER NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (course_id) REFERENCES courses(id) ON DELETE RESTRICT
    );

    CREATE TABLE payments (
        id INTEGER PRIMARY KEY,
        enrollment_id INTEGER NOT NULL,
        amount REAL NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (enrollment_id) REFERENCES enrollments(id) ON DELETE CASCADE
    );

    CREATE TABLE audit_logs (
        id INTEGER PRIMARY KEY,
        action TEXT NOT NULL,
        created_at DATETIME NOT NULL
    );
`;

async function initializeDatabase(database, { seedPasswordHash }) {
    if (!seedPasswordHash) {
        throw new Error('seedPasswordHash é obrigatório');
    }

    await execute(database, SCHEMA);

    await withTransaction(database, async () => {
        const user = await run(
            database,
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            ['Leonan', 'leonan@fullcycle.com.br', seedPasswordHash]
        );

        await run(
            database,
            'INSERT INTO courses (title, price, active) VALUES (?, ?, ?), (?, ?, ?)',
            ['Clean Architecture', 997.00, 1, 'Docker', 497.00, 1]
        );

        const enrollment = await run(
            database,
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [user.lastID, 1]
        );

        await run(
            database,
            'INSERT INTO payments (enrollment_id, amount, status) VALUES (?, ?, ?)',
            [enrollment.lastID, 997.00, 'PAID']
        );
    });
}

module.exports = { initializeDatabase };
