// Define qual URL chama qual função do controller.
const express = require("express");
const { searchJobs } = require("./controllers/jobsController");

const routes = express.Router();

// GET /buscar?termo=python  ->  função searchJobs
routes.get("/buscar", searchJobs);

module.exports = routes;
