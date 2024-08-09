const sequelize = require('../database');  // Ensure the path to your Sequelize setup is correct
const Verification = require('../models/verification');  // Adjust the path to your Verification model
const Master = require('../models/master');  // Needed to ensure the Master table is loaded and synced

async function seed() {
    await sequelize.sync({ force: false });  // Sync the database without dropping data

    // Ensure that there are some Masters available
    const masters = await Master.findAll();
    if (masters.length === 0) {
        console.error('No master records found. Please seed Masters first.');
        return;
    }

    const verificationData = [
        { ID: masters[0].ID, EmailID: 'john.doe@example.com', Username: 'john_doe', Question1ID: 1, Question1Answer: 'Fluffy', Question2ID: 2, Question2Answer: 'Ford', Question3ID: 3, Question3Answer: 'Springfield' },
        { ID: masters[1].ID, EmailID: 'jane.doe@example.com', Username: 'jane_doe', Question1ID: 1, Question1Answer: 'Sparky', Question2ID: 2, Question2Answer: 'Toyota', Question3ID: 3, Question3Answer: 'Atlanta' }
    ];

    try {
        const verifications = await Verification.bulkCreate(verificationData);
        console.log('Verification records seeded successfully.');
        console.log(verifications);  // Optional: Log the inserted objects
    } catch (error) {
        console.error('Failed to seed Verification records:', error);
    } finally {
        await sequelize.close();  // Close the database connection to prevent leaks
    }
}

seed();
