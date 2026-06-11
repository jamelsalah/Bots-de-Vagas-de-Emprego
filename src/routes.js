// Define qual URL chama qual função do controller.
const express = require("express");
const { getCachedJobs, searchJobs } = require("./controllers/jobsController");

const routes = express.Router();

// GET /jobs          -> lê as vagas do cache (usado ao abrir a página)
routes.get("/jobs", getCachedJobs);

// GET /search?term=  -> rebusca na fonte, salva no cache e devolve
routes.get("/search", searchJobs);

module.exports = routes;
