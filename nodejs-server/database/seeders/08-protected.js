const sequelize = require('../database');  // Ensure the path to your Sequelize setup is correct
const Protected = require('../models/protected');  // Adjust the path to your Protected model
const Verification = require('../models/verification');  // Ensure the Verification model is loaded

async function seed() {
    await sequelize.sync({ force: false });  // Sync the database without dropping data

    // Ensure that there are some Verification records available
    const verifications = await Verification.findAll();
    if (verifications.length === 0) {
        console.error('No verification records found. Please seed Verifications first.');
        return;
    }

    const protectedData = [
        { VID: verifications[0].VID, Password: 'encryptedPassword123' },
        { VID: verifications[1].VID, Password: 'encryptedPassword456' }
    ];

    try {
        const protectedRecords = await Protected.bulkCreate(protectedData);
        console.log('Protected records seeded successfully.');
        console.log(protectedRecords);  // Optional: Log the inserted objects
    } catch (error) {
        console.error('Failed to seed Protected records:', error);
    } finally {
        await sequelize.close();  // Close the database connection to prevent leaks
    }
}

seed();