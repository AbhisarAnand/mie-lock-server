const sequelize = require('../database');  // Ensure the path to your Sequelize setup is correct
const SecurityQuestion = require('../models/securityQuestion');  // Adjust the path to your SecurityQuestion model

async function seed() {
    await sequelize.sync({ force: false });  // Sync the database without dropping data

    const securityQuestionsData = [
        { Question: 'What was the name of your first pet?' },
        { Question: 'What was the make and model of your first car?' },
        { Question: 'What was the name of the town where you were born?' },
        { Question: 'What was your favorite food as a child?' },
        { Question: 'In what city did your parents meet?' }
    ];

    try {
        const securityQuestions = await SecurityQuestion.bulkCreate(securityQuestionsData);
        console.log('Security Questions seeded successfully.');
        console.log(securityQuestions);  // Optional: Log the inserted objects
    } catch (error) {
        console.error('Failed to seed Security Questions:', error);
    } finally {
        await sequelize.close();  // Close the database connection to prevent leaks
    }
}

seed();
