const AppError = require('../errors/AppError');

const PAYMENT_STATUS = Object.freeze({
    PAID: 'PAID',
    DENIED: 'DENIED'
});

class CheckoutService {
    constructor({
        userRepository,
        courseRepository,
        enrollmentRepository,
        paymentRepository,
        auditRepository,
        transactionManager,
        hashPassword
    }) {
        this.userRepository = userRepository;
        this.courseRepository = courseRepository;
        this.enrollmentRepository = enrollmentRepository;
        this.paymentRepository = paymentRepository;
        this.auditRepository = auditRepository;
        this.transactionManager = transactionManager;
        this.hashPassword = hashPassword;
    }

    async checkout({ name, email, password, courseId, card }) {
        const course = await this.courseRepository.findActiveById(courseId);

        if (!course) {
            throw new AppError('Curso não encontrado', 404, 'COURSE_NOT_FOUND');
        }

        const paymentStatus = card.startsWith('4')
            ? PAYMENT_STATUS.PAID
            : PAYMENT_STATUS.DENIED;

        if (paymentStatus === PAYMENT_STATUS.DENIED) {
            throw new AppError('Pagamento recusado', 400, 'PAYMENT_DENIED');
        }

        return this.transactionManager.run(async () => {
            let user = await this.userRepository.findByEmail(email);

            if (!user) {
                user = await this.userRepository.create({
                    name,
                    email,
                    passwordHash: await this.hashPassword(password)
                });
            }

            const enrollment = await this.enrollmentRepository.create({
                userId: user.id,
                courseId: course.id
            });

            await this.paymentRepository.create({
                enrollmentId: enrollment.id,
                amount: course.price,
                status: paymentStatus
            });

            await this.auditRepository.record(`Checkout curso ${course.id} por ${user.id}`);

            return { msg: 'Sucesso', enrollment_id: enrollment.id };
        });
    }
}

module.exports = CheckoutService;
