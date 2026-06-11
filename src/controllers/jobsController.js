// CONTROLLER: o "meio de campo".
// Recebe o pedido do navegador, chama os models e devolve a resposta.
const { collectJobs } = require("../models/gupyModel");
const { readData, saveData } = require("../models/jobsData");

// GET /jobs -> lê as vagas já salvas na base de dados (NÃO roda o scraper).
function getJobsData(req, res) {
  const data = readData();
  // Sem dados ainda: devolve um payload vazio para a página mostrar o estado vazio.
  res.json(data || { term: null, fetchedAt: null, jobs: [] });
}

// GET /search?term= -> rebusca na fonte, salva na base de dados e devolve.
async function searchJobs(req, res) {
  // Pega o termo da URL (?term=...). Sem termo, usa "python".
  const term = req.query.term || "python";

  try {
    const jobs = await collectJobs(term);
    const payload = { term, fetchedAt: new Date().toISOString(), jobs };
    saveData(payload); // atualiza a base de dados em dados/gupy.json
    res.json(payload);
  } catch (error) {
    console.error("Erro ao buscar vagas:", error);
    res.status(500).json({ error: "Falha ao buscar as vagas." });
  }
}

module.exports = { getJobsData, searchJobs };
