const { DataTypes } = require('sequelize');
const sequelize = require('../database');  // Ensure this path is correct
const Master = require('./master');  // Importing the Master model

const Verification = sequelize.define('Verification', {
    VID: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    ID: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: Master,  // This links to the Master table
            key: 'ID'
        }
    },
    EmailID: {
        type: DataTypes.STRING,
        allowNull: false
    },
    Username: {
        type: DataTypes.STRING,
        allowNull: false
    },
    Question1ID: {
        type: DataTypes.INTEGER,
        allowNull: false
    },
    Question1Answer: {
        type: DataTypes.STRING,
        allowNull: false
    },
    Question2ID: {
        type: DataTypes.INTEGER,
        allowNull: false
    },
    Question2Answer: {
        type: DataTypes.STRING,
        allowNull: false
    },
    Question3ID: {
        type: DataTypes.INTEGER,
        allowNull: false
    },
    Question3Answer: {
        type: DataTypes.STRING,
        allowNull: false
    }
}, {
    timestamps: false
});

// Relationship
Verification.belongsTo(Master, {
    foreignKey: 'ID',
    as: 'Master'  // This alias is optional but helps with readability
});

module.exports = Verification;