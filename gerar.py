#!/usr/bin/env python3
"""Gera a página "Enviar no WhatsApp" de cada programação e a página inicial.

Cada programação é uma pasta AAAA-MM-DD-nome com:
  titulo.txt    linha 1: nome da programação; linha 2: dia e horário
  mensagem.txt  a mensagem do WhatsApp, igual ao bloco de código do Notion
  arte.png      a arte de post ou feed, nunca o story (pode ser .jpg)

Sem arte, a página fica só com a mensagem e o botão abre o WhatsApp com o texto.

Rode `python3 gerar.py` depois de criar ou mudar uma pasta.
"""
import html
import pathlib
import re

RAIZ = pathlib.Path(__file__).resolve().parent
ENDERECO = "https://ylucas2003.github.io/enviar-whatsapp"
PASTA = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9-]+$")

PAGINA = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo} · Enviar no WhatsApp</title>
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{quando}">
{og_imagem}<link rel="stylesheet" href="../estilo.css">
</head>
<body>
<main>
  <p class="igreja">IEADTC Vila Velha III</p>
  <h1>{titulo}</h1>
  <p class="quando">{quando}</p>
{imagem}  <button id="enviar" class="enviar" type="button" data-arte="{arte}" data-nome="{nome}">Enviar no WhatsApp</button>
  <p id="aviso" class="aviso" role="status"></p>
  <h2>{titulo_mensagem}</h2>
  <pre id="mensagem" class="mensagem">{mensagem}</pre>
  <div class="extras">
    <button id="copiar" type="button">Copiar mensagem</button>
{baixar}  </div>
</main>
<script src="../enviar.js"></script>
</body>
</html>
"""

INICIO = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Enviar no WhatsApp · IEADTC Vila Velha III</title>
<link rel="stylesheet" href="estilo.css">
</head>
<body>
<main>
  <p class="igreja">IEADTC Vila Velha III</p>
  <h1>Enviar no WhatsApp</h1>
  <ul class="lista">
{itens}
  </ul>
</main>
</body>
</html>
"""


def achar_arte(pasta):
    for extensao in (".png", ".jpg", ".jpeg", ".webp"):
        arte = pasta / ("arte" + extensao)
        if arte.exists():
            return arte
    return None


def gerar():
    programacoes = []
    for pasta in sorted(p for p in RAIZ.iterdir() if p.is_dir() and PASTA.match(p.name)):
        linhas = (pasta / "titulo.txt").read_text(encoding="utf-8").strip().splitlines()
        titulo, quando = linhas[0].strip(), linhas[1].strip()
        mensagem = (pasta / "mensagem.txt").read_text(encoding="utf-8").rstrip("\n")
        arte = achar_arte(pasta)
        if arte:
            nome = pasta.name + arte.suffix
            og_imagem = f'<meta property="og:image" content="{ENDERECO}/{pasta.name}/{arte.name}">\n'
            imagem = f'  <img class="arte" src="{arte.name}" alt="Arte de divulgação: {html.escape(titulo)}">\n'
            baixar = f'    <a href="{arte.name}" download="{nome}">Baixar arte</a>\n'
            titulo_mensagem = "Mensagem que vai junto"
        else:
            nome = og_imagem = imagem = baixar = ""
            titulo_mensagem = "Mensagem"
        (pasta / "index.html").write_text(
            PAGINA.format(
                titulo=html.escape(titulo),
                quando=html.escape(quando),
                og_imagem=og_imagem,
                imagem=imagem,
                arte=arte.name if arte else "",
                nome=nome,
                titulo_mensagem=titulo_mensagem,
                mensagem=html.escape(mensagem),
                baixar=baixar,
            ),
            encoding="utf-8",
        )
        programacoes.append((pasta.name, titulo, quando))

    itens = "\n".join(
        f'    <li><a href="{nome}/">{html.escape(titulo)}<span>{html.escape(quando)}</span></a></li>'
        for nome, titulo, quando in reversed(programacoes)
    )
    (RAIZ / "index.html").write_text(INICIO.format(itens=itens), encoding="utf-8")
    print(f"{len(programacoes)} programações geradas")


if __name__ == "__main__":
    gerar()
