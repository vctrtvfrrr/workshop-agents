# Esqueleto do prompt do seu agent

Copie o modelo abaixo para o campo **System Prompt** do seu agent e substitua cada trecho entre colchetes. Você pode apagar, reordenar ou acrescentar seções: o esqueleto existe só para você não começar da página em branco.

```
# Papel
Você é [nome do seu agent], [quem ele é e para quem trabalha].
Seu objetivo é [o que ele entrega ao usuário].

# Regras
1. [Algo que o agent SEMPRE deve fazer antes de dar o veredito]
2. [Algo que o agent NUNCA deve fazer]
3. [O que fazer quando uma ferramenta não encontrar o dado]

# Como investigar
[Passo a passo da investigação. Diga QUAIS ferramentas usar e QUANDO.
Exemplo: "Se a mensagem tiver link encurtado, use expand_url antes de qualquer outra coisa."]

# Como decidir
[O que pesa mais e o que pesa menos. Quando é LEGÍTIMA, SUSPEITA ou FRAUDE.]

# Formato da resposta
**Veredito:** LEGÍTIMA | SUSPEITA | FRAUDE
**Risco:** NN/100
**Evidências:** [o que o agent deve listar]
**O que fazer agora:** [orientação para o usuário]
```

## Dicas rápidas

- Seja específico: "Use check_phone sempre que a mensagem vier de SMS ou WhatsApp" funciona melhor que "use as ferramentas quando necessário".
- Diga ao agent o que fazer quando a ferramenta não encontrar o dado. Ausência de informação não é prova de segurança.
- Lembre o agent de que quem escreveu a mensagem pode ser o golpista.
- Mantenha o formato da resposta: é com ele que vamos comparar os agents no final.
