const express = require('express');
const router = express.Router();
const conversationMemory = require('../services/conversationMemory');
const shopifyCache = require('../services/cache');
const QueryLog = require('../models/queryLog');

// GET /metrics/dashboard - Metrics dashboard
router.get('/dashboard', async (req, res) => {
    try {
        // Get query statistics
        const totalQueries = await QueryLog.count();
        const recentQueries = await QueryLog.findRecent(20);

        // Get cache statistics
        const cacheStats = shopifyCache.getStats();

        // Get conversation statistics
        const conversationStats = conversationMemory.getStats();

        // Calculate metrics
        const stats = {
            overview: {
                totalQueries,
                activeSessions: conversationStats.activeSessions,
                cacheSize: cacheStats.size,
                cacheTTL: cacheStats.ttlMinutes
            },
            recentQueries: recentQueries.map(q => ({
                question: q.question,
                storeId: q.store_id,
                timestamp: q.created_at,
                responseTime: q.response ? JSON.parse(q.response).metadata?.execution_time : null
            })),
            sessions: conversationStats.sessions,
            cache: {
                entries: cacheStats.size,
                ttl: `${cacheStats.ttlMinutes} minutes`
            }
        };

        res.json(stats);
    } catch (error) {
        console.error('Error fetching metrics:', error);
        res.status(500).json({ error: 'Failed to fetch metrics' });
    }
});

// GET /metrics/stats - Simple stats endpoint
router.get('/stats', async (req, res) => {
    try {
        const stats = {
            queries: {
                total: await QueryLog.count(),
                last24h: await QueryLog.countLast24Hours()
            },
            cache: shopifyCache.getStats(),
            conversations: conversationMemory.getStats()
        };

        res.json(stats);
    } catch (error) {
        res.status(500).json({ error: 'Failed to fetch stats' });
    }
});

// POST /metrics/cache/clear - Clear cache
router.post('/cache/clear', (req, res) => {
    const { storeId } = req.body;
    shopifyCache.clear(storeId);
    res.json({ message: 'Cache cleared', storeId: storeId || 'all' });
});

module.exports = router;
