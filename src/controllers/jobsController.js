// CONTROLLER: o "meio de campo".
// Recebe o pedido do navegador, chama o model e devolve a resposta.
const { collectJobs } = require("../models/gupyModel");

async function searchJobs(req, res) {
  // Pega o termo da URL (?term=...). Sem termo, usa "python".
  const term = req.query.term || "python";

  try {
    const jobs = await collectJobs(term);
    res.json(jobs); // devolve as vagas como JSON para o front-end
  } catch (error) {
    console.error("Erro ao buscar vagas:", error);
    res.status(500).json({ error: "Falha ao buscar as vagas." });
  }
}

module.exports = { searchJobs };
