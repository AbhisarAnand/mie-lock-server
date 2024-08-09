const sequelize = require('../database');  // Make sure the path to your Sequelize setup is correct
const QrCodes = require('../models/qrCodes');  // Adjust the path to your QrCodes model as necessary
const Master = require('../models/master');  // Needed to ensure the Master table is loaded and synced

async function seed() {
    await sequelize.sync({ force: false });  // Sync the database without dropping data

    // Ensure that there are some Masters available
    const masters = await Master.findAll();
    if (masters.length === 0) {
        console.error('No master records found. Please seed Masters first.');
        return;
    }

    const qrCodesData = [
        { ID: masters[0].ID, QRUID: 'QR1234567890ABCD', ExpiryDate: new Date(Date.now() + 1000*60*60*24*30) }, // Expires in 30 days
        { ID: masters[1].ID, QRUID: 'QR0987654321DCBA', ExpiryDate: new Date(Date.now() + 1000*60*60*24*30) }  // Expires in 30 days
    ];

    try {
        const qrCodes = await QrCodes.bulkCreate(qrCodesData);
        console.log('QR Codes seeded successfully.');
        console.log(qrCodes);  // Optional: Log the inserted objects
    } catch (error) {
        console.error('Failed to seed QR Codes:', error);
    } finally {
        await sequelize.close();  // Close the database connection to prevent leaks
    }
}

seed();