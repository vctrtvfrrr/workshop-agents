# Workshop Agents & Skills: Detetive de Golpes

Exercício prático em que cada participante cria, no Open WebUI, um agent que classifica mensagens (e-mail, SMS, WhatsApp) como LEGÍTIMA, SUSPEITA ou FRAUDE, usando tools prontas que consultam uma base de dados **fictícia**.

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `participante/` | Guia do participante, esqueleto do prompt e mensagens de teste |
| `openwebui/tools/` | Os 3 kits de tools para o Open WebUI |
| `openwebui/functions/` | Filtro que acrescenta o aviso de ambiente simulado em cada resposta |
| `openwebui/skills/` | 4 skills de exemplo prontas para importar |
| `site/` | SPA com as instruções do participante, publicada no GitHub Pages |
| `tests/` | Testes automatizados das tools |

## Site do participante

O workflow `.github/workflows/pages.yml` publica a SPA de `site/` no GitHub Pages a cada push em `master` que altere `site/` ou `participante/`. A SPA lê os arquivos Markdown de `participante/`, então basta editar esses arquivos para atualizar o site.

Para visualizar localmente:

```powershell
New-Item -ItemType Directory -Force _site/content | Out-Null; Copy-Item -Recurse -Force site/* _site/; Copy-Item participante/*.md _site/content/; python -m http.server 8765 -d _site
```

## Cadastro no Open WebUI

1. **Tools:** em **Workspace → Tools → +**, cole o código de cada arquivo de `openwebui/tools/` e salve. Deixe o acesso como público (ou para o grupo do workshop).
2. **Filtro:** em **Admin Panel → Functions → +**, cole `openwebui/functions/simulated_environment_notice.py` e ative. Marque como **Global** apenas se a instância for dedicada ao workshop.
3. **Skills (opcional):** em **Workspace → Skills**, importe os arquivos de `openwebui/skills/`.
4. **Modelo base:** use um modelo com bom suporte a function calling, com **Function Calling = Native**.
5. **Permissões:** usuários comuns precisam poder criar modelos e skills e usar as tools e o filtro.

## Testes

```powershell
python -m unittest tests/test_tools.py -v
```

## Cenário fictício

Todas as empresas, domínios, CNPJs, telefones, chaves PIX e boletos são inventados. Qualquer dado fora do cenário faz as tools responderem `fora_da_base_simulada`, e o agent deve informar que não consegue verificar mensagens reais.
