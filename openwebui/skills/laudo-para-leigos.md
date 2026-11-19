---
name: laudo-para-leigos
description: Formato e tom do laudo final para quem não é da área de segurança - veredito, nota, evidências em linguagem simples e o que fazer agora. Use ao escrever a resposta para o usuário.
---

# Laudo para leigos

Quem lê o laudo não sabe o que é SPF, DMARC ou WHOIS. O laudo precisa ser entendido em 20 segundos e terminar com uma ação clara.

## Estrutura

**Veredito:** LEGÍTIMA, SUSPEITA ou FRAUDE, com um emoji de semáforo (🟢, 🟡 ou 🔴).
**Risco:** nota de 0 a 100.
**Em uma frase:** o resumo do que está acontecendo. Exemplo: "Alguém criou um site parecido com o do seu banco há 6 dias para roubar sua senha."
**Por que chegamos a essa conclusão:** de 3 a 5 evidências, cada uma em linguagem simples.
**O que fazer agora:** de 2 a 3 ações concretas.

## Tradução de termos técnicos

| Em vez de | Escreva |
|---|---|
| Domínio criado há 4 dias | O site foi criado há apenas 4 dias |
| Typosquatting / imita marca | O endereço foi feito para parecer o da empresa, mas não é |
| SPF/DMARC fail | O e-mail não saiu dos computadores da empresa: o remetente foi falsificado |
| Reply-To divergente | Se você responder, a resposta vai para outra pessoa |
| Macro no anexo | O arquivo tenta instalar um programa quando você o abre |
| Beneficiário divergente | O dinheiro iria para outra pessoa, não para a empresa |

## Ações recomendadas por situação

- **FRAUDE:** não clique, não pague, não responda. Apague a mensagem. Se já clicou ou pagou, ligue para o banco pelo número do cartão ou do app.
- **SUSPEITA:** não use os links nem os contatos da mensagem. Confirme direto com a empresa ou a pessoa por um canal que você já conhece.
- **LEGÍTIMA:** pode seguir, mas, por hábito, prefira sempre acessar pelo app ou digitando o endereço oficial.
