// CONTROLLER: o "meio de campo".
// Recebe o pedido do navegador, chama os models e devolve a resposta.
const { collectJobs } = require("../models/gupyModel");
const { readCache, saveCache } = require("../models/jobsCache");

// GET /jobs -> lê as vagas já salvas no cache (NÃO roda o scraper).
function getCachedJobs(req, res) {
  const cache = readCache();
  // Sem cache ainda: devolve um payload vazio para a página mostrar o estado vazio.
  res.json(cache || { term: null, fetchedAt: null, jobs: [] });
}

// GET /search?term= -> rebusca na fonte, salva no cache e devolve.
async function searchJobs(req, res) {
  // Pega o termo da URL (?term=...). Sem termo, usa "python".
  const term = req.query.term || "python";

  try {
    const jobs = await collectJobs(term);
    const payload = { term, fetchedAt: new Date().toISOString(), jobs };
    saveCache(payload); // atualiza o cache em dados/gupy.json
    res.json(payload);
  } catch (error) {
    console.error("Erro ao buscar vagas:", error);
    res.status(500).json({ error: "Falha ao buscar as vagas." });
  }
}

module.exports = { getCachedJobs, searchJobs };
