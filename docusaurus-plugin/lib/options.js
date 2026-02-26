"use strict";
/**
 * Plugin options validation using Joi.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.validateOptions = validateOptions;
const utils_validation_1 = require("@docusaurus/utils-validation");
const optionsSchema = utils_validation_1.Joi.object({
    apiUrl: utils_validation_1.Joi.string().uri().optional(),
    position: utils_validation_1.Joi.string().valid('bottom-right', 'bottom-left').optional(),
    defaultOpen: utils_validation_1.Joi.boolean().optional(),
    excludePages: utils_validation_1.Joi.array().items(utils_validation_1.Joi.string()).optional(),
});
function validateOptions({ validate, options, }) {
    return validate(optionsSchema, options);
}
//# sourceMappingURL=options.js.map