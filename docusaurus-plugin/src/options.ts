/**
 * Plugin options validation using Joi.
 */

import { Joi } from '@docusaurus/utils-validation';
import type { OptionValidationContext } from '@docusaurus/types';
import type { PluginOptions } from './index';

const optionsSchema = Joi.object<PluginOptions>({
  apiUrl: Joi.string().uri().optional(),
  position: Joi.string().valid('bottom-right', 'bottom-left').optional(),
  defaultOpen: Joi.boolean().optional(),
  excludePages: Joi.array().items(Joi.string()).optional(),
});

export function validateOptions({
  validate,
  options,
}: OptionValidationContext<PluginOptions>): PluginOptions {
  return validate(optionsSchema, options);
}
