// MODEL (base de dados): lê as vagas que o bot salvou no arquivo JSON da pasta data/.
const fs = require("fs");
const path = require("path");

const DATA_FILE = path.join(__dirname, "..", "..", "data", "gupy.json");

function readData() {
  try {
    const content = fs.readFileSync(DATA_FILE, "utf-8");
    return JSON.parse(content);
  } catch (error) {
    // Arquivo não existe ou está inválido: tratamos como "sem dados".
    return null;
  }
}

module.exports = { readData };
