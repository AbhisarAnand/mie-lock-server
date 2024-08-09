const sequelize = require('../database');  // Make sure the path to your Sequelize setup is correct
const QrAccess = require('../models/qrAccess');  // Adjust the path to your QrAccess model as necessary
const QrCodes = require('../models/qrCodes');  // Ensure the QR Codes model is loaded
const Lock = require('../models/lock');  // Ensure the Lock model is loaded

async function seed() {
    await sequelize.sync({ force: false });  // Sync the database without dropping data

    // Ensure that there are some QR Codes and Locks available
    const qrCodes = await QrCodes.findAll();
    const locks = await Lock.findAll();
    if (qrCodes.length === 0 || locks.length === 0) {
        console.error('No QR codes or lock records found. Please seed QR Codes and Locks first.');
        return;
    }

    const qrAccessData = [
        { QID: qrCodes[0].QID, LockID: locks[0].LockID },
        { QID: qrCodes[1].QID, LockID: locks[1].LockID }
    ];

    try {
        const qrAccess = await QrAccess.bulkCreate(qrAccessData);
        console.log('QR Access seeded successfully.');
        console.log(qrAccess);  // Optional: Log the inserted objects
    } catch (error) {
        console.error('Failed to seed QR Access:', error);
    } finally {
        await sequelize.close();  // Close the database connection to prevent leaks
    }
}

seed();
