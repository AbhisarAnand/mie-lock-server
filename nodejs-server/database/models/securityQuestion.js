const { DataTypes } = require('sequelize');
const sequelize = require('../database');  // Ensure this path is correct

const SecurityQuestion = sequelize.define('SecurityQuestion', {
    QuestionID: {
        type: DataTypes.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    Question: {
        type: DataTypes.STRING,
        allowNull: false
    }
}, {
    timestamps: false
});

module.exports = SecurityQuestion;