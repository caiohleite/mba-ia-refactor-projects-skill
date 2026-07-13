const crypto = require('crypto');
const AppError = require('../errors/AppError');

function safeEquals(left, right) {
    const leftBuffer = Buffer.from(String(left));
    const rightBuffer = Buffer.from(String(right));

    return leftBuffer.length === rightBuffer.length &&
        crypto.timingSafeEqual(leftBuffer, rightBuffer);
}

function createAdminAuth({ adminApiKey }) {
    return function adminAuth(req, res, next) {
        if (!adminApiKey) {
            return next(new AppError(
                'Autenticação administrativa não configurada',
                503,
                'ADMIN_AUTH_NOT_CONFIGURED'
            ));
        }

        const providedKey = req.get('x-admin-api-key');

        if (!providedKey || !safeEquals(providedKey, adminApiKey)) {
            return next(new AppError('Não autorizado', 401, 'UNAUTHORIZED'));
        }

        return next();
    };
}

module.exports = { createAdminAuth };
