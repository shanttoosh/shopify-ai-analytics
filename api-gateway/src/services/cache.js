// Simple in-memory cache for Shopify API responses
class ShopifyCache {
    constructor(ttlMinutes = 5) {
        this.cache = new Map();
        this.ttl = ttlMinutes * 60 * 1000; // Convert to milliseconds
    }

    generateKey(storeId, endpoint, params = {}) {
        return `${storeId}:${endpoint}:${JSON.stringify(params)}`;
    }

    get(storeId, endpoint, params = {}) {
        const key = this.generateKey(storeId, endpoint, params);
        const cached = this.cache.get(key);

        if (!cached) return null;

        // Check if expired
        if (Date.now() - cached.timestamp > this.ttl) {
            this.cache.delete(key);
            return null;
        }

        console.log(`🎯 Cache HIT: ${key}`);
        return cached.data;
    }

    set(storeId, endpoint, params = {}, data) {
        const key = this.generateKey(storeId, endpoint, params);
        this.cache.set(key, {
            data,
            timestamp: Date.now()
        });
        console.log(`💾 Cache SET: ${key}`);
    }

    clear(storeId = null) {
        if (storeId) {
            // Clear only for specific store
            for (const key of this.cache.keys()) {
                if (key.startsWith(`${storeId}:`)) {
                    this.cache.delete(key);
                }
            }
        } else {
            // Clear all
            this.cache.clear();
        }
    }

    getStats() {
        return {
            size: this.cache.size,
            ttlMinutes: this.ttl / 60000,
            keys: Array.from(this.cache.keys())
        };
    }
}

// Singleton instance
const shopifyCache = new ShopifyCache(5); // 5 minute TTL

module.exports = shopifyCache;
