const { get } = require('../db/sqlite');

class CourseRepository {
    constructor(database) {
        this.database = database;
    }

    findActiveById(id) {
        return get(
            this.database,
            'SELECT id, title, price FROM courses WHERE id = ? AND active = 1',
            [id]
        );
    }
}

module.exports = CourseRepository;
