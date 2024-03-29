const express = require('express');
const cors = require('cors');
const dbConnect = require('./db');

const app = express();
const port = 3000;

app.use(cors());
app.use(express.json());

app.listen(port, () => {
    console.log(`Listening on port ${port}`);
});

dbConnect(); // Call the function to connect to the database
