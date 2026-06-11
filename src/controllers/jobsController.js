// CONTROLLER: o "meio de campo".
// Recebe o pedido do navegador, chama os models e devolve a resposta.
const { runBot } = require("../models/gupyModel");
const { readData } = require("../models/jobsData");

// GET /jobs -> lê as vagas já salvas na base de dados (NÃO roda o bot).
function getJobsData(req, res) {
  const data = readData();
  // Sem dados ainda: devolve um payload vazio para a página mostrar o estado vazio.
  res.json(data || { term: null, fetchedAt: null, jobs: [] });
}

// GET /search?term= -> manda o bot rodar (ele grava o JSON) e devolve o que foi salvo.
async function searchJobs(req, res) {
  // Pega o termo da URL (?term=...). Sem termo, usa "python".
  const term = req.query.term || "python";

  try {
    await runBot(term);      // o bot busca na fonte e grava data/gupy.json
    const data = readData(); // lê o que o bot acabou de salvar
    res.json(data || { term: null, fetchedAt: null, jobs: [] });
  } catch (error) {
    console.error("Erro ao buscar vagas:", error);
    res.status(500).json({ error: "Falha ao buscar as vagas." });
  }
}

module.exports = { getJobsData, searchJobs };
