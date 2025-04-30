const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('messages.db');

db.serialize(() => {
  db.run(`
    CREATE TABLE IF NOT EXISTS messages (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      to_number TEXT,
      message TEXT,
      time_sent TEXT,
      status TEXT
    )
  `, (err) => {
    if (err) {
      console.error('❌ Table creation failed:', err.message);
    } else {
      console.log('📦 Connected to SQLite database.');
      console.log('🛠️ Table "messages" is ready.');
    }
  });
});

module.exports = db;
