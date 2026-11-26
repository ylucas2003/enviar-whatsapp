#!/usr/bin/env python3
"""Gera a página "Enviar no WhatsApp" de cada programação e a página inicial.

Cada programação é uma pasta AAAA-MM-DD-nome com:
  titulo.txt    linha 1: nome da programação; linha 2: dia e horário
  mensagem.txt  a mensagem do WhatsApp, igual ao bloco de código do Notion
  arte.png      a arte de post ou feed (pode ser .jpg); no Resumo semanal, o story

Sem arte, a página fica só com a mensagem e o botão abre o WhatsApp com o texto.
Sem mensagem.txt (só a arte), a página manda só a arte: toda imagem da Divulgação WhatsApp
tem o seu botão, mesmo antes de a mensagem chegar.

Story do Instagram é uma pasta AAAA-MM-DD-nome-story com:
  titulo.txt    linha 1: "Story · nome"; linha 2: dia e horário
  sugestao.txt  "Música: nome · artista", "Trecho: que parte usar", "Por que: a ligação com o culto"
                e "Na imagem: o que pôr em cima" (figurinha, texto); só "Música" e "Na imagem" são obrigatórias
  arte.png      o story

A página do story tem o botão "Compartilhar no Instagram", que abre o menu de compartilhar
do celular com o story, e mostra as sugestões para quem for postar.

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
{bloco_mensagem}  <div class="extras">
{copiar}{baixar}  </div>
</main>
<script src="../enviar.js"></script>
</body>
</html>
"""

PAGINA_STORY = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{titulo} · Compartilhar no Instagram</title>
<meta property="og:title" content="{titulo}">
<meta property="og:description" content="{quando}">
<meta property="og:image" content="{endereco}/{pasta}/{arte}">
<link rel="stylesheet" href="../estilo.css">
</head>
<body>
<main>
  <p class="igreja">IEADTC Vila Velha III</p>
  <h1>{titulo}</h1>
  <p class="quando">{quando}</p>
  <img class="arte" src="{arte}" alt="Story de divulgação: {titulo}">
  <button id="compartilhar" class="enviar instagram" type="button" data-arte="{arte}" data-nome="{nome}">Compartilhar no Instagram</button>
  <p id="aviso" class="aviso" role="status"></p>
  <h2>Sugestões para o story</h2>
  <dl class="sugestoes">
{sugestoes}  </dl>
  <div class="extras">
{copiar_musica}    <a href="{arte}" download="{nome}">Baixar story</a>
  </div>
</main>
<script src="../compartilhar.js"></script>
</body>
</html>
"""

ROTULOS = {
    "Música": "Música de fundo",
    "Trecho": "Parte da música",
    "Por que": "Por que essa música",
    "Na imagem": "Em cima da imagem",
}

INICIO = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Enviar e compartilhar · IEADTC Vila Velha III</title>
<link rel="stylesheet" href="estilo.css">
</head>
<body>
<main>
  <p class="igreja">IEADTC Vila Velha III</p>
  <h1>Enviar e compartilhar</h1>
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


def ler_sugestoes(arquivo):
    sugestoes = {}
    for linha in arquivo.read_text(encoding="utf-8").splitlines():
        chave, _, valor = linha.partition(":")
        if valor.strip():
            sugestoes[chave.strip()] = valor.strip()
    return sugestoes


def gerar_story(pasta, titulo, quando, arquivo):
    arte = achar_arte(pasta)
    if not arte:
        raise SystemExit(f"{pasta.name}: falta a arte do story")
    nome = pasta.name + arte.suffix
    sugestoes = ler_sugestoes(arquivo)
    itens = "".join(
        f"    <dt>{rotulo}</dt>\n    <dd>{html.escape(sugestoes[chave])}</dd>\n"
        for chave, rotulo in ROTULOS.items()
        if chave in sugestoes
    )
    musica = sugestoes.get("Música", "")
    busca = musica.replace(" · ", " ").replace("(hino)", "").strip()
    copiar_musica = (
        f'    <button id="copiar-musica" type="button" data-musica="{html.escape(busca)}">Copiar nome da música</button>\n'
        if musica
        else ""
    )
    (pasta / "index.html").write_text(
        PAGINA_STORY.format(
            titulo=html.escape(titulo),
            quando=html.escape(quando),
            endereco=ENDERECO,
            pasta=pasta.name,
            arte=arte.name,
            nome=nome,
            sugestoes=itens,
            copiar_musica=copiar_musica,
        ),
        encoding="utf-8",
    )


def gerar():
    programacoes = []
    for pasta in sorted(p for p in RAIZ.iterdir() if p.is_dir() and PASTA.match(p.name)):
        linhas = (pasta / "titulo.txt").read_text(encoding="utf-8").strip().splitlines()
        titulo, quando = linhas[0].strip(), linhas[1].strip()
        sugestao = pasta / "sugestao.txt"
        if sugestao.exists():
            gerar_story(pasta, titulo, quando, sugestao)
            programacoes.append((pasta.name, titulo, quando))
            continue
        arquivo_mensagem = pasta / "mensagem.txt"
        mensagem = arquivo_mensagem.read_text(encoding="utf-8").rstrip("\n") if arquivo_mensagem.exists() else ""
        arte = achar_arte(pasta)
        if not mensagem and not arte:
            raise SystemExit(f"{pasta.name}: falta a arte ou a mensagem")
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
                bloco_mensagem=(
                    f'  <h2>{titulo_mensagem}</h2>\n  <pre id="mensagem" class="mensagem">{html.escape(mensagem)}</pre>\n'
                    if mensagem
                    else '  <pre id="mensagem" class="mensagem" hidden></pre>\n'
                ),
                copiar='    <button id="copiar" type="button">Copiar mensagem</button>\n' if mensagem else "",
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
    print(f"{len(programacoes)} páginas geradas")


if __name__ == "__main__":
    gerar()
