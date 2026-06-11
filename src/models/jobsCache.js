// MODEL (cache): lê e grava as vagas em um arquivo JSON na pasta dados/.
const fs = require("fs");
const path = require("path");

const CACHE_FILE = path.join(__dirname, "..", "..", "dados", "gupy.json");

function readCache() {
  try {
    const content = fs.readFileSync(CACHE_FILE, "utf-8");
    return JSON.parse(content);
  } catch (error) {
    // Arquivo não existe ou está inválido: tratamos como "sem cache".
    return null;
  }
}

function saveCache(data) {
  fs.writeFileSync(CACHE_FILE, JSON.stringify(data, null, 2), "utf-8");
}

module.exports = { readCache, saveCache };
