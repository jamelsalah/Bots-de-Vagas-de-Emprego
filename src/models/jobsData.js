// MODEL (base de dados): lê e grava as vagas em um arquivo JSON na pasta dados/.
const fs = require("fs");
const path = require("path");

const DATA_FILE = path.join(__dirname, "..", "..", "dados", "gupy.json");

function readData() {
  try {
    const content = fs.readFileSync(DATA_FILE, "utf-8");
    return JSON.parse(content);
  } catch (error) {
    // Arquivo não existe ou está inválido: tratamos como "sem dados".
    return null;
  }
}

function saveData(data) {
  fs.writeFileSync(DATA_FILE, JSON.stringify(data, null, 2), "utf-8");
}

module.exports = { readData, saveData };
