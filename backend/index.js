// index.js
const express = require('express');
const sqlite3 = require('sqlite3').verbose();
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = 5000;

// Middleware
app.use(cors());
app.use(bodyParser.json());

// Connect to SQLite DB
const db = new sqlite3.Database('./messages.db', (err) => {
  if (err) {
    return console.error('❌ DB Connection Error:', err.message);
  }
  console.log('📦 Connected to SQLite database.');
});

// Create table if it doesn't exist
const createTableQuery = `
  CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    message TEXT,
    time TEXT
  )
`;
db.run(createTableQuery, (err) => {
  if (err) {
    return console.error('❌ Error creating table:', err.message);
  }
  console.log('🛠️ Table "messages" is ready.');
});

// API to receive and log a message
app.post('/log-message', (req, res) => {
  const { leadId, message, time } = req.body;

  const insertQuery = `INSERT INTO messages (lead_id, message, time) VALUES (?, ?, ?)`;
  db.run(insertQuery, [leadId, message, time], function (err) {
    if (err) {
      console.error('❌ DB Error logging message:', err.message);
      return res.status(500).json({ success: false, error: err.message });
    }
    res.status(200).json({ success: true, messageId: this.lastID });
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`🚀 Server running on port ${PORT}`);
});
