const Database = require('better-sqlite3');
const path = require('path');

const dbPath = process.env.DATABASE_URL?.replace('sqlite:', '') || './dev.db';
const db = new Database(dbPath);

// Create query_logs table
db.exec(`
  CREATE TABLE IF NOT EXISTS query_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    store_id TEXT NOT NULL,
    question TEXT NOT NULL,
    generated_query TEXT,
    response TEXT,
    confidence TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  )
`);

class QueryLogModel {
  /**
   * Create a new query log
   */
  static create({ store_id, question, generated_query, response, confidence }) {
    const stmt = db.prepare(`
      INSERT INTO query_logs (store_id, question, generated_query, response, confidence)
      VALUES (?, ?, ?, ?, ?)
    `);

    return stmt.run(store_id, question, generated_query, response, confidence);
  }

  /**
   * Get all logs for a store
   */
  static getByStore(store_id, limit = 50) {
    const stmt = db.prepare(`
      SELECT * FROM query_logs 
      WHERE store_id = ? 
      ORDER BY created_at DESC 
      LIMIT ?
    `);

    return stmt.all(store_id, limit);
  }

  /**
   * Get all logs
   */
  static getAll(limit = 100) {
    const stmt = db.prepare(`
      SELECT * FROM query_logs 
      ORDER BY created_at DESC 
      LIMIT ?
    `);

    return stmt.all(limit);
  }

  /**
   * Count total queries
   */
  static count() {
    const stmt = db.prepare('SELECT COUNT(*) as count FROM query_logs');
    return stmt.get().count;
  }

  /**
    * Count queries in last 24 hours
    */
  static countLast24Hours() {
    const stmt = db.prepare(`
      SELECT COUNT(*) as count FROM query_logs 
      WHERE created_at >= datetime('now', '-1 day')
    `);
    return stmt.get().count;
  }

  /**
   * Get recent queries
   */
  static findRecent(limit = 20) {
    const stmt = db.prepare(`
      SELECT * FROM query_logs 
      ORDER BY created_at DESC 
      LIMIT ?
    `);
    return stmt.all(limit);
  }
}

module.exports = QueryLogModel;
