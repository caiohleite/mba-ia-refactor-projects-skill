const { get, run } = require('../db/sqlite');

class UserRepository {
    constructor(database) {
        this.database = database;
    }

    findByEmail(email) {
        return get(this.database, 'SELECT id, name, email FROM users WHERE email = ?', [email]);
    }

    async create({ name, email, passwordHash }) {
        const result = await run(
            this.database,
            'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
            [name, email, passwordHash]
        );

        return { id: result.lastID, name, email };
    }

    deleteById(id) {
        return run(this.database, 'DELETE FROM users WHERE id = ?', [id]);
    }
}

module.exports = UserRepository;
