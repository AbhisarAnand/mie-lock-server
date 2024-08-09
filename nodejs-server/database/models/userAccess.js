const { DataTypes } = require('sequelize');
const sequelize = require('../database');  // Ensure this path is correct
const Master = require('./master');  // Importing the Master model
const Lock = require('./lock');  // Importing the Lock model

const UserAccess = sequelize.define('UserAccess', {
    AccessID: {
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
UserAccess.belongsTo(Master, {
    foreignKey: 'ID',
    as: 'Master'
});
UserAccess.belongsTo(Lock, {
    foreignKey: 'LockID',
    as: 'Lock'
});

module.exports = UserAccess;