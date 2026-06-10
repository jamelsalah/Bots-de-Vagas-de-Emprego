// Define qual URL chama qual função do controller.
const express = require("express");
const { buscarVagas } = require("./controllers/vagasController");

const rotas = express.Router();

// GET /buscar?termo=python  ->  função buscarVagas
rotas.get("/buscar", buscarVagas);

module.exports = rotas;
