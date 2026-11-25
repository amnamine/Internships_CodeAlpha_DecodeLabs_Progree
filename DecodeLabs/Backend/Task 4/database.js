const sqlite3 = require('sqlite3').verbose();
const path = require('path');

// Connect to SQLite database (or create it if it doesn't exist)
const dbPath = path.join(__dirname, 'database.sqlite');
const db = new sqlite3.Database(dbPath, (err) => {
    if (err) {
        console.error('Error connecting to the database:', err.message);
    } else {
        console.log('Connected to the SQLite database.');
        
        // Create the search_history table if it doesn't exist
        db.run(`
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        `, (err) => {
            if (err) {
                console.error('Error creating table:', err.message);
            } else {
                console.log('Table "search_history" is ready.');
            }
        });
    }
});

// Function to log a search query
function logSearch(city) {
    const query = 'INSERT INTO search_history (city) VALUES (?)';
    db.run(query, [city], function(err) {
        if (err) {
            console.error('Error inserting into database:', err.message);
        } else {
            console.log(`Logged search for: ${city} (ID: ${this.lastID})`);
        }
    });
}

// Function to get recent searches
function getRecentSearches(limit = 5) {
    return new Promise((resolve, reject) => {
        const query = 'SELECT DISTINCT city FROM search_history ORDER BY timestamp DESC LIMIT ?';
        db.all(query, [limit], (err, rows) => {
            if (err) {
                reject(err);
            } else {
                resolve(rows.map(row => row.city));
            }
        });
    });
}

module.exports = {
    logSearch,
    getRecentSearches
};
