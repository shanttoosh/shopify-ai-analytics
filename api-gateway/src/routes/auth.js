const express = require('express');
const crypto = require('crypto');
const axios = require('axios');
const StoreModel = require('../models/store');

const router = express.Router();

/**
 * GET /auth/shopify
 * Initiate Shopify OAuth flow
 */
router.get('/', (req, res) => {
    const { shop } = req.query;

    if (!shop) {
        return res.status(400).json({ error: 'Missing shop parameter' });
    }

    // Validate shop domain
    const shopDomain = shop.replace(/^https?:\/\//, '').replace(/\/$/, '');
    if (!shopDomain.endsWith('.myshopify.com')) {
        return res.status(400).json({ error: 'Invalid shop domain' });
    }

    // Generate state for CSRF protection
    const state = crypto.randomBytes(16).toString('hex');
    req.session.oauth_state = state;
    req.session.shop = shopDomain;

    const apiKey = process.env.SHOPIFY_API_KEY;
    const scopes = process.env.SHOPIFY_SCOPES;
    const redirectUri = process.env.SHOPIFY_CALLBACK_URL;

    const authUrl = `https://${shopDomain}/admin/oauth/authorize?` +
        `client_id=${apiKey}&` +
        `scope=${scopes}&` +
        `redirect_uri=${redirectUri}&` +
        `state=${state}`;

    res.redirect(authUrl);
});

/**
 * GET /auth/shopify/callback
 * Handle Shopify OAuth callback
 */
router.get('/callback', async (req, res) => {
    const { code, state, shop } = req.query;

    // Verify state to prevent CSRF
    if (state !== req.session.oauth_state) {
        return res.status(403).json({ error: 'Invalid state parameter' });
    }

    if (!code || !shop) {
        return res.status(400).json({ error: 'Missing required parameters' });
    }

    try {
        // Exchange code for access token
        const tokenUrl = `https://${shop}/admin/oauth/access_token`;
        const response = await axios.post(tokenUrl, {
            client_id: process.env.SHOPIFY_API_KEY,
            client_secret: process.env.SHOPIFY_API_SECRET,
            code
        });

        const accessToken = response.data.access_token;

        // Store the access token (encrypted)
        StoreModel.createOrUpdate({
            shop_domain: shop,
            access_token: accessToken
        });

        // Clean up session
        delete req.session.oauth_state;
        delete req.session.shop;

        res.json({
            success: true,
            message: 'Successfully authenticated with Shopify!',
            store: shop
        });

    } catch (error) {
        console.error('OAuth error:', error.message);
        res.status(500).json({
            error: 'Failed to complete OAuth flow',
            details: error.response?.data || error.message
        });
    }
});

module.exports = router;
