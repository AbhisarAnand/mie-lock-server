const { Sequelize } = require('sequelize');

// Setting up the database connection
const sequelize = new Sequelize({
    dialect: 'sqlite',    // Specifies the DB engine
    storage: './database/database.sqlite', // Location of the database file
    logging: false // Disables logging; set to console.log for visibility
});

module.exports = sequelize;
