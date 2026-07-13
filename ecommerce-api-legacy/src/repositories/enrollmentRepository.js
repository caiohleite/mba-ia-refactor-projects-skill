const { run } = require('../db/sqlite');

class EnrollmentRepository {
    constructor(database) {
        this.database = database;
    }

    async create({ userId, courseId }) {
        const result = await run(
            this.database,
            'INSERT INTO enrollments (user_id, course_id) VALUES (?, ?)',
            [userId, courseId]
        );

        return { id: result.lastID, userId, courseId };
    }
}

module.exports = EnrollmentRepository;
