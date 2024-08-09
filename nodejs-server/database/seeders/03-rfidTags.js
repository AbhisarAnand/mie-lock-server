const sequelize = require('../database');  // Make sure the path to your Sequelize setup is correct
const RfidTags = require('../models/rfidTags');  // Adjust the path to your RfidTags model as necessary
const Master = require('../models/master');  // Needed to ensure the Master table is loaded and synced

async function seed() {
    await sequelize.sync({ force: false });  // Sync the database without dropping data

    // Ensure that there are some Masters available
    const masters = await Master.findAll();
    if (masters.length === 0) {
        console.error('No master records found. Please seed Masters first.');
        return;
    }

    const rfidTagsData = [
        { ID: masters[0].ID, RFIDUID: '1234567890abcdef' },
        { ID: masters[1].ID, RFIDUID: 'abcdef1234567890' }
    ];

    try {
        const rfidTags = await RfidTags.bulkCreate(rfidTagsData);
        console.log('RFID Tags seeded successfully.');
        console.log(rfidTags);  // Optional: Log the inserted objects
    } catch (error) {
        console.error('Failed to seed RFID Tags:', error);
    } finally {
        await sequelize.close();  // Close the database connection to prevent leaks
    }
}

seed();