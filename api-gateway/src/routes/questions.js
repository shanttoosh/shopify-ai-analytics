const express = require('express');
const { body, validationResult } = require('express-validator');
const PythonAIClient = require('../services/pythonAIClient');
const StoreModel = require('../models/store');
const QueryLogModel = require('../models/queryLog');
const conversationMemory = require('../services/conversationMemory');
const crypto = require('crypto');

const router = express.Router();
const pythonClient = new PythonAIClient();

/**
 * POST /api/v1/questions
 * Analyze a natural language question about store data
 */
router.post('/',
    // Validation
    [
        body('store_id').isString().notEmpty().withMessage('store_id is required'),
        body('question').isString().notEmpty().withMessage('question is required')
    ],
    async (req, res, next) => {
        try {
            // Check validation errors
            const errors = validationResult(req);
            if (!errors.isEmpty()) {
                return res.status(400).json({ errors: errors.array() });
            }

            const { store_id, question, session_id } = req.body;
            const startTime = Date.now();

            // Create or get session ID for conversation tracking
            const sessionId = session_id || crypto.randomUUID();
            conversationMemory.createSession(sessionId);

            // Get conversation context for follow-up questions
            const context = conversationMemory.getContext(sessionId);

            // Get store access token from database
            let accessToken = null;
            if (process.env.USE_MOCK_DATA !== 'true') {
                const store = StoreModel.getByDomain(store_id);
                if (!store) {
                    return res.status(404).json({
                        error: 'Store not found. Please authenticate first via /auth/shopify'
                    });
                }
                accessToken = store.access_token;
            }

            // Forward to Python AI service with context
            console.log(`📤 Forwarding question to AI service: "${question}"`);
            console.log(`🔄 Session ID: ${sessionId}, Context: ${context ? 'Yes' : 'No'}`);

            const aiResponse = await pythonClient.analyze({
                store_id,
                question,
                access_token: accessToken,
                context: context // Pass conversation history
            });

            const executionTime = ((Date.now() - startTime) / 1000).toFixed(2);

            // Save to conversation memory
            conversationMemory.addInteraction(sessionId, question, aiResponse.answer);

            // Optional: Log the query
            if (process.env.ENABLE_QUERY_LOGS === 'true') {
                QueryLogModel.create({
                    store_id,
                    question,
                    generated_query: aiResponse.shopify_query || null,
                    response: JSON.stringify(aiResponse),
                    confidence: aiResponse.confidence
                });
            }

            // Return formatted response with session info
            res.json({
                answer: aiResponse.answer,
                confidence: aiResponse.confidence,
                shopify_query: aiResponse.shopify_query,
                reasoning: aiResponse.reasoning,
                session_id: sessionId,
                metadata: {
                    execution_time: `${executionTime}s`,
                    conversation_turns: conversationMemory.getHistory(sessionId).length,
                    has_context: !!context,
                    ...(aiResponse.metadata || {})
                }
            });

        } catch (error) {
            console.error('❌ Error processing question:', error.message);

            if (error.response) {
                // Python service returned an error
                return res.status(error.response.status || 500).json({
                    error: error.response.data?.detail || 'AI service error',
                    message: 'Failed to process your question. Please try again.'
                });
            }

            next(error);
        }
    }
);

module.exports = router;
