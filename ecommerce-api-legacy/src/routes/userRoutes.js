const express = require('express');

function createUserRoutes(userController, adminAuth) {
    const router = express.Router();
    router.delete('/api/users/:id', adminAuth, userController.delete);
    return router;
}

module.exports = createUserRoutes;
