const express = require("express");
const cors = require("cors");
const dotenv = require("dotenv");
const helmet = require("helmet");
const routes = require("./routes/index");

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
app.options("*", cors());

// v1 api routes
app.use("/", routes);

app.listen(process.env.PORT, () => {
    console.info(`Server listening on port ${process.env.PORT}`);
});
