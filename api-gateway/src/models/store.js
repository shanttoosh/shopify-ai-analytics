const Database = require('better-sqlite3');
const CryptoJS = require('crypto-js');
const path = require('path');

// Initialize database
const dbPath = process.env.DATABASE_URL?.replace('sqlite:', '') || './dev.db';
const db = new Database(dbPath);

// Create stores table
db.exec(`
  CREATE TABLE IF NOT EXISTS stores (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_domain TEXT UNIQUE NOT NULL,
    access_token TEXT NOT NULL,
    installed_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

const ENCRYPTION_KEY = process.env.SESSION_SECRET || 'dev-secret-change-me';

class StoreModel {
    /**
     * Encrypt sensitive data
     */
    static encrypt(text) {
        return CryptoJS.AES.encrypt(text, ENCRYPTION_KEY).toString();
    }

    /**
     * Decrypt sensitive data
     */
    static decrypt(ciphertext) {
        const bytes = CryptoJS.AES.decrypt(ciphertext, ENCRYPTION_KEY);
        return bytes.toString(CryptoJS.enc.Utf8);
    }

    /**
     * Create or update a store
     */
    static createOrUpdate({ shop_domain, access_token }) {
        const encryptedToken = this.encrypt(access_token);

        const stmt = db.prepare(`
      INSERT INTO stores (shop_domain, access_token)
      VALUES (?, ?)
      ON CONFLICT(shop_domain) 
      DO UPDATE SET access_token = ?, installed_at = CURRENT_TIMESTAMP
    `);

        return stmt.run(shop_domain, encryptedToken, encryptedToken);
    }

    /**
     * Get store by domain
     */
    static getByDomain(shop_domain) {
        const stmt = db.prepare('SELECT * FROM stores WHERE shop_domain = ?');
        const store = stmt.get(shop_domain);

        if (store) {
            store.access_token = this.decrypt(store.access_token);
        }

        return store;
    }

    /**
     * Get all stores
     */
    static getAll() {
        const stmt = db.prepare('SELECT * FROM stores');
        return stmt.all().map(store => ({
            ...store,
            access_token: this.decrypt(store.access_token)
        }));
    }

    /**
     * Delete a store
     */
    static delete(shop_domain) {
        const stmt = db.prepare('DELETE FROM stores WHERE shop_domain = ?');
        return stmt.run(shop_domain);
    }
}

module.exports = StoreModel;
