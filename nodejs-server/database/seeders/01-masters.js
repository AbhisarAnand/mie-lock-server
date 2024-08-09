const sequelize = require('../database');  // Make sure the path is correct to your Sequelize setup
const Master = require('../models/master');  // Adjust the path to your Master model as necessary

async function seed() {
    await sequelize.sync({ force: false });  // Make sure this aligns with how you want to handle syncing

    const mastersData = [
        { Name: 'John Doe', PhoneNumber: 1234567890 },
        { Name: 'Jane Doe', PhoneNumber: 9876543210 }
    ];

    try {
        const masters = await Master.bulkCreate(mastersData);
        console.log('Masters seeded successfully.');
        console.log(masters);  // Optional: Log the inserted objects
    } catch (error) {
        console.error('Failed to seed Masters:', error);
    } finally {
        await sequelize.close();  // Ensure you close the database connection
    }
}

seed();