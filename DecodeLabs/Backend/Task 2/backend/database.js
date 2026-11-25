const { Sequelize, DataTypes } = require('sequelize');
const path = require('path');

// Initialize SQLite database connection
const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: path.join(__dirname, 'database.sqlite'),
  logging: false // Disable logging for cleaner console
});

// Define the User model
const User = sequelize.define('User', {
  name: {
    type: DataTypes.STRING,
    allowNull: false,
    validate: {
      notEmpty: true
    }
  },
  email: {
    type: DataTypes.STRING,
    allowNull: false,
    unique: {
      msg: 'Email address must be unique.'
    },
    validate: {
      isEmail: true,
      notEmpty: true
    }
  },
  role: {
    type: DataTypes.STRING,
    allowNull: true,
    defaultValue: 'User'
  }
});

// Sync database (creates table if it doesn't exist)
sequelize.sync()
  .then(() => console.log('Database & tables synced'))
  .catch(err => console.error('Error syncing database:', err));

module.exports = { sequelize, User };
