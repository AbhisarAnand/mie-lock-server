const sequelize = require('../database');  // Ensure the path to your Sequelize setup is correct
const Lock = require('../models/lock');  // Adjust the path to your Lock model as necessary

async function seed() {
    await sequelize.sync({ force: false });  // Sync the database without dropping data

    const locksData = [
        { LockMacAddr: 'AA:BB:CC:DD:EE:FF' },
        { LockMacAddr: '11:22:33:44:55:66' }
    ];

    try {
        const locks = await Lock.bulkCreate(locksData);
        console.log('Locks seeded successfully.');
        console.log(locks);  // Optional: Log the inserted objects
    } catch (error) {
        console.error('Failed to seed Locks:', error);
    } finally {
        await sequelize.close();  // Close the database connection to prevent leaks
    }
}

seed();