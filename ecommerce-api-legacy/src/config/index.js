function parsePort(value) {
    const port = Number(value || 3000);

    if (!Number.isInteger(port) || port < 0 || port > 65535) {
        throw new Error('PORT deve ser um número inteiro entre 0 e 65535');
    }

    return port;
}

function getConfig(env = process.env) {
    return Object.freeze({
        port: parsePort(env.PORT),
        adminApiKey: env.ADMIN_API_KEY || null
    });
}

module.exports = { getConfig };
