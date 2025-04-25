/**
 * Routes for the LLM API
 */

import { Router } from 'express';
import { LLMController } from '../controllers/llm-controller';

/**
 * Create and configure LLM routes
 * 
 * @param llmController LLM controller instance
 * @returns Configured router
 */
export const createLLMRoutes = (llmController: LLMController): Router => {
  const router = Router();

  /**
   * @api {get} /providers Get all available providers
   * @apiName GetProviders
   * @apiGroup LLM
   * @apiSuccess {Boolean} success Indicates if the request was successful
   * @apiSuccess {Object} data Response data
   * @apiSuccess {String[]} data.providers List of available provider names
   */
  router.get('/providers', llmController.getProviders);

  /**
   * @api {get} /providers/:provider/models Get available models for a provider
   * @apiName GetModels
   * @apiGroup LLM
   * @apiParam {String} provider Provider name
   * @apiSuccess {Boolean} success Indicates if the request was successful
   * @apiSuccess {Object} data Response data
   * @apiSuccess {String} data.provider Provider name
   * @apiSuccess {String[]} data.models List of model names
   */
  router.get('/providers/:provider/models', llmController.getModels);

  /**
   * @api {post} /completions/:provider Generate a completion
   * @apiName GenerateCompletion
   * @apiGroup LLM
   * @apiParam {String} provider Provider name
   * @apiBody {String} prompt Input text
   * @apiBody {String} [model] Model to use
   * @apiBody {Number} [temperature=0.7] Temperature
   * @apiBody {Number} [maxTokens=1000] Maximum tokens
   * @apiBody {Number} [topP=1.0] Top P
   * @apiBody {String[]} [stopSequences] Stop sequences
   * @apiSuccess {Boolean} success Indicates if the request was successful
   * @apiSuccess {Object} data Response data (CompletionResponse)
   */
  router.post('/completions/:provider', llmController.generateCompletion);

  /**
   * @api {post} /completions/:provider/stream Stream a completion
   * @apiName StreamCompletion
   * @apiGroup LLM
   * @apiParam {String} provider Provider name
   * @apiBody {String} prompt Input text
   * @apiBody {String} [model] Model to use
   * @apiBody {Number} [temperature=0.7] Temperature
   * @apiBody {Number} [maxTokens=1000] Maximum tokens
   * @apiBody {Number} [topP=1.0] Top P
   * @apiBody {String[]} [stopSequences] Stop sequences
   * @apiSuccess {String} data SSE data stream
   */
  router.get('/completions/:provider/stream', llmController.streamCompletion);

  /**
   * @api {post} /completions/compare Compare completions across providers
   * @apiName CompareCompletions
   * @apiGroup LLM
   * @apiBody {String} prompt Input text
   * @apiBody {String[]} [providers] Providers to use (defaults to all)
   * @apiBody {String} [model] Model to use
   * @apiBody {Number} [temperature=0.7] Temperature
   * @apiBody {Number} [maxTokens=1000] Maximum tokens
   * @apiBody {Number} [topP=1.0] Top P
   * @apiBody {String[]} [stopSequences] Stop sequences
   * @apiSuccess {Boolean} success Indicates if the request was successful
   * @apiSuccess {Object} data Response data
   * @apiSuccess {String} data.prompt Input prompt
   * @apiSuccess {Object} data.comparisons Provider completions
   */
  router.post('/completions/compare', llmController.compareCompletions);

  /**
   * @api {get} /usage Get usage statistics
   * @apiName GetUsageStats
   * @apiGroup LLM
   * @apiSuccess {Boolean} success Indicates if the request was successful
   * @apiSuccess {Object} data Response data
   * @apiSuccess {Object} data.stats Usage statistics by provider
   */
  router.get('/usage', llmController.getUsageStats);

  return router;
};
