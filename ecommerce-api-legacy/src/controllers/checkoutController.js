const { validateCheckoutPayload } = require('../validators/checkoutValidator');

class CheckoutController {
    constructor(checkoutService) {
        this.checkoutService = checkoutService;
        this.create = this.create.bind(this);
    }

    async create(req, res, next) {
        try {
            const checkoutInput = validateCheckoutPayload(req.body);
            const result = await this.checkoutService.checkout(checkoutInput);
            return res.status(200).json(result);
        } catch (error) {
            return next(error);
        }
    }
}

module.exports = CheckoutController;
