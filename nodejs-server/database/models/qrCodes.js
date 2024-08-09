const { DataTypes } = require('sequelize');
const sequelize = require('../database');  // Ensure this path is correct
const Master = require('./master');  // Importing the Master model

const QrCodes = sequelize.define('QrCodes', {
    QID: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    ID: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: Master,  // Link to Master table
            key: 'ID'
        }
    },
    QRUID: {
        type: DataTypes.STRING,
        allowNull: false
    },
    ExpiryDate: {
        type: DataTypes.DATE,
        allowNull: false
    }
}, {
    timestamps: false
});

// Relationship
QrCodes.belongsTo(Master, {
    foreignKey: 'ID',
    as: 'Master'
});

module.exports = QrCodes;