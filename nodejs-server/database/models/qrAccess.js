const { DataTypes } = require('sequelize');
const sequelize = require('../database');  // Ensure this path is correct
const QrCodes = require('./qrCodes');  // Importing the QR Codes model
const Lock = require('./lock');  // Importing the Lock model

const QrAccess = sequelize.define('QrAccess', {
    QrAccessID: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    QID: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: QrCodes,  // Link to QR Codes table
            key: 'QID'
        }
    },
    LockID: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: Lock,  // Link to Lock table
            key: 'LockID'
        }
    }
}, {
    timestamps: false
});

// Relationships
QrAccess.belongsTo(QrCodes, {
    foreignKey: 'QID',
    as: 'QrCode'
});
QrAccess.belongsTo(Lock, {
    foreignKey: 'LockID',
    as: 'Lock'
});

module.exports = QrAccess;