class FinancialReportService {
    constructor(reportRepository) {
        this.reportRepository = reportRepository;
    }

    async generate() {
        const rows = await this.reportRepository.getFinancialRows();
        const coursesById = new Map();

        for (const row of rows) {
            if (!coursesById.has(row.course_id)) {
                coursesById.set(row.course_id, {
                    course: row.course,
                    revenue: 0,
                    students: []
                });
            }

            if (!row.enrollment_id) {
                continue;
            }

            const course = coursesById.get(row.course_id);

            if (row.payment_status === 'PAID') {
                course.revenue += Number(row.amount);
            }

            course.students.push({
                student: row.student || 'Unknown',
                paid: row.amount === null ? 0 : Number(row.amount)
            });
        }

        return Array.from(coursesById.values());
    }
}

module.exports = FinancialReportService;
