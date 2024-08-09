const sequelize = require('./database');  // Make sure the path is correct to your Sequelize setup
require('./models/master');  // Load Master model
require('./models/verification');  // Load Verification model
require('./models/securityQuestion');  // Load SecurityQuestion model
require('./models/protected');  // Load Protected model
require('./models/lock');  // Load Lock model
require('./models/userAccess');  // Load UserAccess model
require('./models/rfidTags');  // Load RFIDTags model
require('./models/rfidAccess');  // Load RFIDAccess model
require('./models/qrCodes');  // Load QrCodes model
require('./models/qrAccess');  // Load QrAccess model

sequelize.sync({ force: true })  // This will drop the tables if they exist and recreate them
  .then(() => {
    console.log('Database tables created successfully!');
    process.exit();  // Exit the script after successful sync
  })
  .catch((error) => {
    console.error('Error syncing database:', error);
    process.exit(1);  // Exit with error code 1 in case of failure
  });