const sequelize = require('../database');  // Make sure the path to your Sequelize setup is correct
const RfidAccess = require('../models/rfidAccess');  // Adjust the path to your RfidAccess model as necessary
const RfidTags = require('../models/rfidTags');  // Ensure the RFID Tags model is loaded
const Lock = require('../models/lock');  // Ensure the Lock model is loaded

async function seed() {
    await sequelize.sync({ force: false });  // Sync the database without dropping data

    // Ensure that there are some RFID Tags and Locks available
    const rfidTags = await RfidTags.findAll();
    const locks = await Lock.findAll();
    if (rfidTags.length === 0 || locks.length === 0) {
        console.error('No RFID tags or lock records found. Please seed RFID Tags and Locks first.');
        return;
    }

    const rfidAccessData = [
        { RID: rfidTags[0].RID, LockID: locks[0].LockID },
        { RID: rfidTags[1].RID, LockID: locks[1].LockID }
    ];

    try {
        const rfidAccess = await RfidAccess.bulkCreate(rfidAccessData);
        console.log('RFID Access seeded successfully.');
        console.log(rfidAccess);  // Optional: Log the inserted objects
    } catch (error) {
        console.error('Failed to seed RFID Access:', error);
    } finally {
        await sequelize.close();  // Close the database connection to prevent leaks
    }
}

seed();
