# dashboard_screenpipe

Página mínima para navegar e pesquisar as capturas de um [screenpipe](https://github.com/screenpipe/screenpipe) local.

- Ao centro: a captura selecionada.
- Em baixo: uma timeline do dia, com todas as capturas (cinzento), os resultados da pesquisa (azul) e a posição atual (vermelho). Pode clicar na timeline para saltar para essa hora.
- À esquerda: o campo de pesquisa (texto, app, janela ou URL), o dia e a lista de resultados.
- As setas ← e → avançam e recuam entre capturas.

## Arrancar

```bash
python3 serve.py
```

Depois abra http://localhost:3031.

O `serve.py` usa só a biblioteca padrão do Python. Serve o `index.html` e faz de proxy, apenas para `/search` e `/frames/`, para a API do screenpipe em `localhost:3030`. O token da API é lido com `screenpipe auth token` e adicionado pelo servidor, por isso nunca chega ao browser.

## Variáveis de ambiente

| Variável | Valor por defeito |
|---|---|
| `DASHBOARD_PORT` | `3031` |
| `SCREENPIPE_API` | `http://127.0.0.1:3030` |
| `SCREENPIPE_BIN` | `~/src/screenpipe/target/release/screenpipe` |
| `SCREENPIPE_API_KEY` | (lido do binário) |

## Notas

- O filtro **App** usa o nome exato da app (por exemplo, `iTerm2` e não `iTerm`).
- As capturas antigas são compactadas pelo screenpipe em MP4. Para as mostrar, o screenpipe precisa de conseguir extrair frames com o ffmpeg. As versões do screenpipe que usam `-vsync` falham com o ffmpeg 9 ou mais recente.
