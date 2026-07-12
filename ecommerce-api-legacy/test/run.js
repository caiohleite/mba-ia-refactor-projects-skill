const assert = require('assert');
const fs = require('fs');
const http = require('http');
const path = require('path');
const { once } = require('events');
const { getConfig } = require('../src/config');
const passwordService = require('../src/services/passwordService');
const { startServer } = require('../src/server');
const { closeDatabase } = require('../src/db/connection');

function request(port, method, requestPath, { body, headers = {} } = {}) {
    return new Promise((resolve, reject) => {
        const data = body ? JSON.stringify(body) : null;
        const requestHeaders = { ...headers };

        if (data) {
            requestHeaders['content-type'] = 'application/json';
            requestHeaders['content-length'] = Buffer.byteLength(data);
        }

        const clientRequest = http.request({
            hostname: '127.0.0.1',
            port,
            method,
            path: requestPath,
            headers: requestHeaders
        }, response => {
            let responseBody = '';
            response.on('data', chunk => { responseBody += chunk; });
            response.on('end', () => resolve({
                statusCode: response.statusCode,
                body: responseBody,
                json: () => JSON.parse(responseBody)
            }));
        });

        clientRequest.on('error', reject);
        if (data) clientRequest.write(data);
        clientRequest.end();
    });
}

async function closeRuntime(runtime) {
    if (runtime.server.listening) {
        await new Promise(resolve => runtime.server.close(resolve));
    }

    await closeDatabase(runtime.database);
}

async function withRuntime(env, operation) {
    const runtime = await startServer({ env });

    try {
        if (!runtime.server.listening) {
            await once(runtime.server, 'listening');
        }

        await operation(runtime.server.address().port);
    } finally {
        await closeRuntime(runtime);
    }
}

function assertArchitecture() {
    const sourceRoot = path.join(__dirname, '..', 'src');
    const readTree = directory => fs.readdirSync(directory, { withFileTypes: true }).flatMap(entry => {
        const target = path.join(directory, entry.name);
        return entry.isDirectory() ? readTree(target) : [target];
    });
    const sourceFiles = readTree(sourceRoot).filter(file => file.endsWith('.js'));
    const allSource = sourceFiles.map(file => fs.readFileSync(file, 'utf8')).join('\n');
    const routeAndControllerFiles = sourceFiles.filter(file =>
        file.includes(`${path.sep}routes${path.sep}`) ||
        file.includes(`${path.sep}controllers${path.sep}`)
    );

    assert.strictEqual(fs.existsSync(path.join(sourceRoot, 'AppManager.js')), false);
    assert.strictEqual(fs.existsSync(path.join(sourceRoot, 'utils.js')), false);
    assert.doesNotMatch(allSource, /senha_super_secreta|pk_live_|admin_master|globalCache|badCrypto/);

    for (const file of routeAndControllerFiles) {
        assert.doesNotMatch(fs.readFileSync(file, 'utf8'), /\b(SELECT|INSERT|UPDATE|DELETE)\b/);
    }
}

async function run() {
    const config = getConfig({ PORT: '0' });
    assert.strictEqual(config.port, 0);
    assert.strictEqual(config.adminApiKey, null);

    const passwordHash = await passwordService.hashPassword('senha-forte');
    assert.match(passwordHash, /^scrypt\$[a-f0-9]+\$[a-f0-9]+$/);
    assert.strictEqual(await passwordService.verifyPassword('senha-forte', passwordHash), true);
    assert.strictEqual(await passwordService.verifyPassword('incorreta', passwordHash), false);

    const adminKey = 'test-admin-key';
    await withRuntime({ PORT: '0', ADMIN_API_KEY: adminKey }, async port => {
        let response = await request(port, 'POST', '/api/checkout', { body: {} });
        assert.strictEqual(response.statusCode, 400);
        assert.strictEqual(response.json().code, 'INVALID_CHECKOUT_PAYLOAD');

        response = await request(port, 'POST', '/api/checkout', { body: {
            usr: 'Recusado',
            eml: 'recusado@test.local',
            pwd: 'senha',
            c_id: 1,
            card: '5111111111111111'
        } });
        assert.strictEqual(response.statusCode, 400);
        assert.strictEqual(response.json().code, 'PAYMENT_DENIED');

        response = await request(port, 'POST', '/api/checkout', { body: {
            usr: 'Inexistente',
            eml: 'inexistente@test.local',
            pwd: 'senha',
            c_id: 999,
            card: '4111111111111111'
        } });
        assert.strictEqual(response.statusCode, 404);

        response = await request(port, 'POST', '/api/checkout', { body: {
            usr: 'Guilherme',
            eml: 'gui@test.local',
            pwd: 'senhaforte',
            c_id: 2,
            card: '4111111111111111'
        } });
        assert.strictEqual(response.statusCode, 200);
        assert.strictEqual(response.json().msg, 'Sucesso');

        response = await request(port, 'GET', '/api/admin/financial-report');
        assert.strictEqual(response.statusCode, 401);

        response = await request(port, 'GET', '/api/admin/financial-report', {
            headers: { 'x-admin-api-key': adminKey }
        });
        assert.strictEqual(response.statusCode, 200);
        let report = response.json();
        assert.deepStrictEqual(report.map(item => item.revenue), [997, 497]);

        response = await request(port, 'DELETE', '/api/users/2');
        assert.strictEqual(response.statusCode, 401);

        response = await request(port, 'DELETE', '/api/users/2', {
            headers: { 'x-admin-api-key': adminKey }
        });
        assert.strictEqual(response.statusCode, 200);
        assert.strictEqual(response.body, 'Usuário deletado.');

        response = await request(port, 'GET', '/api/admin/financial-report', {
            headers: { 'x-admin-api-key': adminKey }
        });
        report = response.json();
        assert.strictEqual(report[1].revenue, 0);
        assert.deepStrictEqual(report[1].students, []);
    });

    await withRuntime({ PORT: '0' }, async port => {
        const response = await request(port, 'GET', '/api/admin/financial-report');
        assert.strictEqual(response.statusCode, 503);
        assert.strictEqual(response.json().code, 'ADMIN_AUTH_NOT_CONFIGURED');
    });

    assertArchitecture();
    console.log('PASS: regressão funcional, segurança e arquitetura MVC');
}

run().catch(error => {
    console.error(error);
    process.exitCode = 1;
});
