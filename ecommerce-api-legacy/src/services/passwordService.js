const crypto = require('crypto');
const { promisify } = require('util');

const scrypt = promisify(crypto.scrypt);
const KEY_LENGTH = 64;

async function hashPassword(password) {
    if (typeof password !== 'string' || password.length === 0) {
        throw new TypeError('A senha deve ser uma string não vazia');
    }

    const salt = crypto.randomBytes(16).toString('hex');
    const derivedKey = await scrypt(password, salt, KEY_LENGTH);
    return `scrypt$${salt}$${derivedKey.toString('hex')}`;
}

async function createUnusablePassword() {
    const randomPassword = crypto.randomBytes(32).toString('hex');
    return hashPassword(randomPassword);
}

async function verifyPassword(password, encodedPassword) {
    const [algorithm, salt, encodedKey] = String(encodedPassword).split('$');

    if (algorithm !== 'scrypt' || !salt || !encodedKey) {
        return false;
    }

    const storedKey = Buffer.from(encodedKey, 'hex');
    const derivedKey = await scrypt(password, salt, storedKey.length);

    return storedKey.length === derivedKey.length && crypto.timingSafeEqual(storedKey, derivedKey);
}

module.exports = { hashPassword, createUnusablePassword, verifyPassword };
