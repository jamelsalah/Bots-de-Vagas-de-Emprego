// Define qual URL chama qual função do controller.
const express = require("express");
const { searchJobs } = require("./controllers/jobsController");

const routes = express.Router();

// GET /search?term=python  ->  função searchJobs
routes.get("/search", searchJobs);

module.exports = routes;
