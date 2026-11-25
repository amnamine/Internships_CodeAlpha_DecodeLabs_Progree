const sqlite3 = require('sqlite3').verbose();
const bcrypt = require('bcrypt');
const path = require('path');
const db = require('./database'); // Assuming database.js connects to database.sqlite

const usersToInject = [
    { username: 'admin', password: 'adminPassword123' },
    { username: 'amine', password: 'securePass2026' },
    { username: 'guest', password: 'guestAccess' }
];

async function seedDatabase() {
    console.log('Starting user injection...');
    
    for (const user of usersToInject) {
        try {
            const hashedPassword = await bcrypt.hash(user.password, 10);
            
            // Check if user already exists
            db.get('SELECT * FROM users WHERE username = ?', [user.username], (err, row) => {
                if (err) {
                    console.error('Error checking user:', err);
                    return;
                }
                
                if (row) {
                    console.log(`User '${user.username}' already exists.`);
                } else {
                    db.run('INSERT INTO users (username, password) VALUES (?, ?)', [user.username, hashedPassword], (err) => {
                        if (err) {
                            console.error(`Failed to inject user '${user.username}':`, err.message);
                        } else {
                            console.log(`Successfully injected user: '${user.username}'`);
                        }
                    });
                }
            });
        } catch (error) {
            console.error(`Error hashing password for ${user.username}:`, error);
        }
    }
}

// Wait a tiny bit for the db connection from database.js to initialize before querying
setTimeout(seedDatabase, 500);
