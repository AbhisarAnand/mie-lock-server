const { DataTypes } = require('sequelize');
const sequelize = require('../database');  // Ensure this path is correct
const RfidTags = require('./rfidTags');  // Importing the RFID Tags model
const Lock = require('./lock');  // Importing the Lock model

const RfidAccess = sequelize.define('RfidAccess', {
    RFIDAccessID: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    RID: {
        type: DataTypes.INTEGER,
        allowNull: false,
        references: {
            model: RfidTags,  // Link to RFID Tags table
            key: 'RID'
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
RfidAccess.belongsTo(RfidTags, {
    foreignKey: 'RID',
    as: 'RfidTag'
});
RfidAccess.belongsTo(Lock, {
    foreignKey: 'LockID',
    as: 'Lock'
});

module.exports = RfidAccess;