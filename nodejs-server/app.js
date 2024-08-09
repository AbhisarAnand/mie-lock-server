const express = require('express');
const sequelize = require('./database/database');

const app = express();
const PORT = 3000;

sequelize.sync({ force: false })  // Set to 'true' if you need to rebuild the tables
  .then(() => {
    console.log('Database synced');

    app.get('/', (req, res) => {
      res.send('Hello World!');
    });

    app.listen(PORT, () => {
      console.log(`Server running on http://localhost:${PORT}`);
    });
  })
  .catch(err => {
    console.error('Failed to sync database:', err);
  });