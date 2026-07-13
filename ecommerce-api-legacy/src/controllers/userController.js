const AppError = require('../errors/AppError');

class UserController {
    constructor(userService) {
        this.userService = userService;
        this.delete = this.delete.bind(this);
    }

    async delete(req, res, next) {
        try {
            const userId = Number(req.params.id);

            if (!Number.isInteger(userId) || userId <= 0) {
                throw new AppError('Bad Request', 400, 'INVALID_USER_ID');
            }

            const message = await this.userService.delete(userId);
            return res.status(200).send(message);
        } catch (error) {
            return next(error);
        }
    }
}

module.exports = UserController;
