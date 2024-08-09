const { DataTypes } = require('sequelize');
const sequelize = require('../database');  // Ensure this path is correct

const Lock = sequelize.define('Lock', {
    LockID: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    LockMacAddr: {
        type: DataTypes.STRING,
        allowNull: false
    }
}, {
    timestamps: false
});

module.exports = Lock;