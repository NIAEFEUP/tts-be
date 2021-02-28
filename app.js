const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const helmet = require('helmet');
const routes = require('./routes/index');
const httpStatus = require('http-status');

const app = express();

// load env variables
dotenv.config();

// set security HTTP headers
app.use(helmet());

// parse json request body
app.use(express.json());

// parse urlencoded request body
app.use(express.urlencoded({ extended: true }));

// enable cors
app.use(cors());
app.options('*', cors());

// v1 api routes
app.use('/', routes);

// send back a 404 error for any unknown api request
app.get("*", (req, res) => {
    res.send("404 - Not found");
});

app.listen(process.env.PORT, () => {
    console.log("Server has started");
})