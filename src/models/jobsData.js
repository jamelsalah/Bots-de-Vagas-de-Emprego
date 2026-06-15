// MODEL (base de dados): junta o que cada bot salvou e lê a base unificada.
const fs = require("fs");
const path = require("path");

const bots = require("../bots");
const { removeBlacklisted } = require("./blacklist");

const DATA_DIR = path.join(__dirname, "..", "..", "data");
const JOBS_FILE = path.join(DATA_DIR, "jobs.json");

// Lê um data/<source>.json; se não existir ou estiver inválido, devolve null.
function readBotFile(source) {
  try {
    const content = fs.readFileSync(path.join(DATA_DIR, `${source}.json`), "utf-8");
    return JSON.parse(content);
  } catch (error) {
    return null;
  }
}

// Junta as vagas de TODOS os bots num único data/jobs.json e devolve o payload.
function mergeBots(term) {
  let jobs = [];
  for (const source of bots) {
    const data = readBotFile(source);
    if (data && data.jobs) {
      // Enxuga o payload: na base unificada guardamos só um resumo da descrição.
      for (const job of data.jobs) {
        jobs.push({ ...job, description: (job.description || "").slice(0, 200) });
      }
    }
  }

  removeBlacklisted(jobs); // tira as vagas excluídas antes de salvar

  const payload = {
    term,
    fetchedAt: new Date().toISOString(),
    jobs,
  };
  fs.writeFileSync(JOBS_FILE, JSON.stringify(payload, null, 2), "utf-8");
  return payload;
}

// Lê a base unificada (ou null se ainda não existir).
function readJobs() {
  try {
    const content = fs.readFileSync(JOBS_FILE, "utf-8");
    return JSON.parse(content);
  } catch (error) {
    return null;
  }
}

// Reaplica a blacklist na base unificada já salva (limpa o jobs.json na hora).
function pruneBase() {
  const payload = readJobs();
  if (!payload) return;

  removeBlacklisted(payload.jobs);
  fs.writeFileSync(JOBS_FILE, JSON.stringify(payload, null, 2), "utf-8");
}

module.exports = { mergeBots, readJobs, pruneBase };
