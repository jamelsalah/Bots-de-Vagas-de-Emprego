// CONTROLLER: o "meio de campo".
// Recebe o pedido do navegador, chama os models e devolve a resposta.
const { runBot } = require("../models/botRunner");
const { mergeBots, readJobs, pruneBase } = require("../models/jobsData");
const { addToBlacklist } = require("../models/blacklist");
const bots = require("../bots");

const EMPTY = { term: null, fetchedAt: null, jobs: [] };

// GET /jobs -> lê a base unificada já salva (NÃO roda os bots).
function getJobsData(req, res) {
  const data = readJobs() || EMPTY;
  res.json({ ...data, sources: bots });
}

// GET /search?term= -> roda TODOS os bots, junta tudo e devolve a base unificada.
async function searchJobs(req, res) {
  const term = req.query.term || "python";

  // allSettled: espera todos terminarem mesmo que um falhe (ex: Indeed com o
  // Edge aberto). Assim um bot quebrado não derruba os resultados dos outros.
  const resultados = await Promise.allSettled(
    bots.map((source) => runBot(source, term))
  );

  // Avisa no log quais bots falharam (sem derrubar a resposta).
  resultados.forEach((r, i) => {
    if (r.status === "rejected") {
      console.error(`Bot "${bots[i]}" falhou:`, r.reason.message);
    }
  });

  const data = mergeBots(term);
  res.json({ ...data, sources: bots });
}

// POST /blacklist -> exclui uma vaga: guarda na blacklist e limpa a base unificada.
function blacklistJob(req, res) {
  const { source, id } = req.body;

  if (!source || !id) {
    return res.status(400).json({ error: "Faltou source ou id" });
  }

  addToBlacklist(source, id);
  pruneBase();
  res.json({ ok: true });
}

module.exports = { getJobsData, searchJobs, blacklistJob };
