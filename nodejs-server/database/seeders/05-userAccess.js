const sequelize = require('../database');  // Make sure the path to your Sequelize setup is correct
const UserAccess = require('../models/userAccess');  // Adjust the path to your UserAccess model as necessary
const Master = require('../models/master');  // Needed to ensure the Master table is loaded and synced
const Lock = require('../models/lock');  // Needed to ensure the Lock table is loaded and synced

async function seed() {
    await sequelize.sync({ force: false });  // Sync the database without dropping data

    // Ensure that there are some Masters and Locks available
    const masters = await Master.findAll();
    const locks = await Lock.findAll();
    if (masters.length === 0 || locks.length === 0) {
        console.error('No master or lock records found. Please seed Masters and Locks first.');
        return;
    }

    const userAccessData = [
        { ID: masters[0].ID, LockID: locks[0].LockID },
        { ID: masters[1].ID, LockID: locks[1].LockID }
    ];

    try {
        const userAccess = await UserAccess.bulkCreate(userAccessData);
        console.log('User Access seeded successfully.');
        console.log(userAccess);  // Optional: Log the inserted objects
    } catch (error) {
        console.error('Failed to seed User Access:', error);
    } finally {
        await sequelize.close();  // Close the database connection to prevent leaks
    }
}

seed();