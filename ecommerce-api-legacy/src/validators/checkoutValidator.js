const AppError = require('../errors/AppError');

const EMAIL_PATTERN = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const CARD_PATTERN = /^\d{12,19}$/;

function invalidPayload() {
    return new AppError('Bad Request', 400, 'INVALID_CHECKOUT_PAYLOAD');
}

function validateCheckoutPayload(payload) {
    if (!payload || typeof payload !== 'object') {
        throw invalidPayload();
    }

    const name = typeof payload.usr === 'string' ? payload.usr.trim() : '';
    const email = typeof payload.eml === 'string' ? payload.eml.trim() : '';
    const password = typeof payload.pwd === 'string' ? payload.pwd : '';
    const courseId = Number(payload.c_id);
    const card = typeof payload.card === 'string' ? payload.card.replace(/\s/g, '') : '';

    if (
        !name ||
        !EMAIL_PATTERN.test(email) ||
        !password ||
        !Number.isInteger(courseId) ||
        courseId <= 0 ||
        !CARD_PATTERN.test(card)
    ) {
        throw invalidPayload();
    }

    return { name, email, password, courseId, card };
}

module.exports = { validateCheckoutPayload };
