// CONTROLLER: o "meio de campo".
// Recebe o pedido do navegador, chama o model e devolve a resposta.
const { coletarVagas } = require("../models/gupyModel");

async function buscarVagas(req, res) {
  // Pega o termo da URL (?termo=...). Sem termo, usa "python".
  const termo = req.query.termo || "python";

  try {
    const vagas = await coletarVagas(termo);
    res.json(vagas); // devolve as vagas como JSON para o front-end
  } catch (erro) {
    console.error("Erro ao buscar vagas:", erro);
    res.status(500).json({ erro: "Falha ao buscar as vagas." });
  }
}

module.exports = { buscarVagas };
