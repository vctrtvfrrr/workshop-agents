# Guia do participante: crie seu Detetive de Golpes

## A missão

Construir, em 30 minutos, um agent que recebe uma mensagem (e-mail, SMS ou WhatsApp) e responde se ela é **LEGÍTIMA**, **SUSPEITA** ou **FRAUDE**, com uma nota de risco e as evidências que sustentam o veredito.

Você escreve o prompt e decide quais tools ligar. Se quiser, também cria skills. As tools já estão prontas.

## Regras do jogo

1. **Use apenas as mensagens M1 a M8** do arquivo de mensagens. Elas vivem num cenário fictício com empresas, sites e telefones inventados.
2. **As tools consultam uma base simulada.** Se você colar uma mensagem real da sua caixa de entrada, as tools vão responder `fora_da_base_simulada`. Isso é proposital: este agent é um exercício, não uma ferramenta de segurança de verdade.
3. **Não abra os links das mensagens no navegador.** Eles existem só dentro do cenário.
4. **Mantenha o formato de resposta** (Veredito, Risco, Evidências, O que fazer agora). É assim que vamos comparar os agents no final.

## Passo a passo no Open WebUI

1. Vá em **Workspace → Models → +** (novo modelo).
2. Dê um nome ao seu agent e escolha o modelo base indicado pelo instrutor.
3. Cole o seu prompt no campo **System Prompt**. Comece pelo esqueleto do prompt.
4. Em **Tools**, marque os kits que você quer usar.
5. Em **Filters**, marque **Aviso de Ambiente Simulado**.
6. (Opcional) Em **Workspace → Skills**, crie suas skills e marque-as no seu agent.
7. Salve, abra um chat com o seu agent e cole uma mensagem de teste.
8. Leia a resposta, ajuste o prompt e teste de novo.

## As tools disponíveis

As tools estão organizadas em 3 kits. Cada kit é uma caixinha para marcar no seu agent.

### Kit Remetente: quem enviou?

| Tool | O que descobre | Quando usar |
|---|---|---|
| `lookup_domain` | Quando o site ou domínio foi criado e quem é o dono | Remetente de e-mail ou link desconhecido |
| `check_email_authentication` | Se o e-mail saiu mesmo dos servidores do domínio e se o "Responder para" é de outro lugar | Toda mensagem de e-mail |
| `check_brand_similarity` | Se o domínio é o oficial de uma marca ou uma imitação | Quando a mensagem diz ser de uma empresa |
| `get_official_channels` | Os sites, e-mails e telefones oficiais da empresa e o que ela **nunca** pede por mensagem | Para comparar o pedido da mensagem com a regra da empresa |
| `lookup_cnpj` | Situação cadastral e idade de uma empresa pelo CNPJ ou nome | Quando aparece um CNPJ ou um beneficiário desconhecido |

### Kit Conteúdo: o que tem dentro?

| Tool | O que descobre | Quando usar |
|---|---|---|
| `expand_url` | Para onde um link encurtado leva de verdade | Sempre que houver link encurtado |
| `check_url_reputation` | Se o link está em listas de bloqueio e quantas denúncias tem | Qualquer link |
| `analyze_attachment` | O tipo real do arquivo, se tem macro e se antivírus detectam algo | Quando houver anexo |

### Kit Pagamentos e Telefone: para onde vai o dinheiro?

| Tool | O que descobre | Quando usar |
|---|---|---|
| `lookup_pix_key` | Quem recebe o dinheiro de uma chave PIX | Pedido de PIX |
| `decode_boleto` | O banco e o beneficiário real de um boleto | Linha digitável de boleto |
| `check_phone` | Tipo de linha, dono, idade do número e denúncias | SMS e WhatsApp |

## Pontos de atenção

- **As tools trazem fatos, não vereditos.** Quem decide é o seu agent, e é o seu prompt que ensina como decidir.
- **Ligar todas as tools não garante um agent melhor.** Sem instrução clara, o modelo pode chamar tool errada, chamar tudo em toda mensagem ou ficar lento. Diga no prompt quando usar cada uma.
- **"Sem denúncias" não quer dizer "seguro".** Um golpe criado ontem ainda não foi denunciado por ninguém.
- **E-mail autenticado não quer dizer legítimo.** O golpista pode ter o próprio domínio, e contas reais podem ser invadidas.
- **Falta de informação não é prova de nada.** Diga ao agent o que fazer quando a tool não encontrar o dado.
- **Mensagem legítima também pode ser urgente.** Um agent que marca tudo como fraude também está errado.
- **Quem escreveu a mensagem pode ser o golpista**, e o golpista sabe que a sua mensagem pode ser lida por uma IA.

## Ideias de skills

Skill é conhecimento que o agent consulta quando precisa: uma lista, um critério, um procedimento. Tool busca um dado; skill ensina a pensar sobre ele. Algumas ideias:

1. **Sinais de manipulação.** Lista os gatilhos psicológicos dos golpes (urgência, ameaça, recompensa, autoridade, sigilo) com frases típicas de cada um. Ajuda o agent a apontar no texto onde está a manipulação.
2. **Golpes comuns no Brasil.** Descreve em uma ou duas linhas os golpes mais frequentes (falso parente, taxa de entrega, falsa central do banco, boleto adulterado, falsa cobrança) e o sinal típico de cada um. Ajuda o agent a reconhecer e dar nome ao golpe.
3. **Critério de pontuação.** Define quanto cada evidência pesa no risco: por exemplo, domínio com menos de 30 dias pesa muito, link encurtado sozinho pesa pouco, PIX em nome de pessoa física cobrando por uma empresa é quase decisivo. Deixa as notas consistentes entre as mensagens.
4. **Laudo para leigos.** Define como escrever o resultado: veredito, nota, as 3 evidências principais em linguagem simples e o que a pessoa deve fazer agora. Ajuda o agent a falar com o usuário final, não com um analista.

Sem tempo para skills? Tudo bem: um bom prompt com as tools certas já resolve boa parte das mensagens.
