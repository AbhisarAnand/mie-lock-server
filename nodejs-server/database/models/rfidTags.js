const { DataTypes } = require('sequelize');
const sequelize = require('../database');  // Ensure this path is correct
const Master = require('./master');  // Importing the Master model to link RFID tags to users

const RfidTags = sequelize.define('RfidTags', {
    RID: {
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
    RFIDUID: {
        type: DataTypes.STRING,
        allowNull: false
    }
}, {
    timestamps: false
});

// Relationship
RfidTags.belongsTo(Master, {
    foreignKey: 'ID',
    as: 'Master'
});

module.exports = RfidTags;