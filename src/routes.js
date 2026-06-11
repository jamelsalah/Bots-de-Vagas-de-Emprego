// Define qual URL chama qual função do controller.
const express = require("express");
const { getJobsData, searchJobs } = require("./controllers/jobsController");

const routes = express.Router();

// GET /jobs          -> lê as vagas da base de dados (usado ao abrir a página)
routes.get("/jobs", getJobsData);

// GET /search?term=  -> rebusca na fonte, salva na base de dados e devolve
routes.get("/search", searchJobs);

module.exports = routes;
