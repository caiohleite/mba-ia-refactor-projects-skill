const AppError = require('../errors/AppError');

function errorHandler(error, req, res, next) {
    if (res.headersSent) {
        return next(error);
    }

    if (error instanceof AppError) {
        return res.status(error.statusCode).json({
            error: error.message,
            code: error.code
        });
    }

    console.error('[ERROR] Falha interna não tratada');
    return res.status(500).json({
        error: 'Erro interno do servidor',
        code: 'INTERNAL_ERROR'
    });
}

module.exports = errorHandler;
