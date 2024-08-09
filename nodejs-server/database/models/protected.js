const { DataTypes } = require('sequelize');
const sequelize = require('../database');  // Ensure this path is correct
const Verification = require('./verification');  // Importing the Verification model

const Protected = sequelize.define('Protected', {
    PID: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    VID: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: Verification,
            key: 'VID'
        }
    },
    Password: {
        type: DataTypes.STRING,
        allowNull: false
    }
}, {
    timestamps: false
});

// Relationship
Protected.belongsTo(Verification, {
    foreignKey: 'VID',
    as: 'Verification'
});

module.exports = Protected;