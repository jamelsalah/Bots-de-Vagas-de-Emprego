// MODEL (blacklist): guarda as vagas excluídas e filtra elas da lista de vagas.
const fs = require("fs");
const path = require("path");

const DATA_DIR = path.join(__dirname, "..", "..", "data");
const BLACKLIST_FILE = path.join(DATA_DIR, "blacklist.json");

// Lê a blacklist (array de { source, id }); se não existir/inválido, devolve [].
function readBlacklist() {
  try {
    const content = fs.readFileSync(BLACKLIST_FILE, "utf-8");
    return JSON.parse(content);
  } catch (error) {
    return [];
  }
}

// Adiciona uma vaga à blacklist (sem duplicar) e salva.
function addToBlacklist(source, id) {
  const blacklist = readBlacklist();

  const jaExiste = blacklist.some((item) => item.source === source && item.id === id);
  if (!jaExiste) {
    blacklist.push({ source, id });
    fs.writeFileSync(BLACKLIST_FILE, JSON.stringify(blacklist, null, 2), "utf-8");
  }
}

// Remove da lista de vagas as que estão na blacklist (MUTA a lista no lugar).
function removeBlacklisted(jobs) {
  const blacklist = readBlacklist();
  const bloqueadas = new Set(blacklist.map((item) => item.source + ":" + item.id));

  const mantidas = jobs.filter((job) => !bloqueadas.has(job.source + ":" + job.id));
  jobs.length = 0;        // esvazia a lista original
  jobs.push(...mantidas); // repõe só as que sobraram
}

module.exports = { readBlacklist, addToBlacklist, removeBlacklisted };
