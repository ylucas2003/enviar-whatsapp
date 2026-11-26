// Botão "Enviar no WhatsApp": manda a arte com a mensagem de legenda.
// No celular abre o menu de compartilhar; no computador baixa a arte e abre o WhatsApp Web com a mensagem.
// Página sem arte: o botão só abre o WhatsApp com a mensagem.
(function () {
  var botao = document.getElementById('enviar');
  var aviso = document.getElementById('aviso');
  var mensagem = document.getElementById('mensagem').textContent;
  var caminhoArte = botao.dataset.arte;
  var nomeArte = botao.dataset.nome;
  var celular = window.matchMedia('(pointer: coarse)').matches;
  var arquivo = null;
  var arteFalhou = false;

  // A arte é carregada antes do toque: o iPhone só abre o menu de compartilhar
  // se ele for chamado logo no toque, sem esperar download.
  if (caminhoArte) {
    fetch(caminhoArte)
      .then(function (resposta) {
        if (!resposta.ok) throw new Error('arte ' + resposta.status);
        return resposta.blob();
      })
      .then(function (blob) {
        arquivo = new File([blob], nomeArte, { type: blob.type || 'image/png' });
      })
      .catch(function () {
        arteFalhou = true;
      });
  }

  function avisar(texto) {
    aviso.textContent = texto;
  }

  function copiarMensagem() {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(mensagem).then(
        function () { return true; },
        function () { return false; }
      );
    }
    return Promise.resolve(false);
  }

  function baixarArte() {
    var link = document.createElement('a');
    link.href = caminhoArte;
    link.download = nomeArte;
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  function enviarPeloLink() {
    baixarArte();
    window.open('https://wa.me/?text=' + encodeURIComponent(mensagem), '_blank');
    avisar(mensagem
      ? 'A arte foi baixada e o WhatsApp abriu com a mensagem. Escolha o contato e anexe a arte.'
      : 'A arte foi baixada e o WhatsApp abriu. Escolha o contato e anexe a arte.');
  }

  botao.addEventListener('click', function () {
    // Copia antes de compartilhar: se o WhatsApp do iPhone perder o texto, é só colar na legenda.
    if (mensagem) copiarMensagem();

    if (!caminhoArte) {
      var link = 'https://wa.me/?text=' + encodeURIComponent(mensagem);
      avisar('O WhatsApp abriu com a mensagem. É só escolher o contato ou o grupo.');
      if (celular) {
        window.location.href = link;
      } else {
        window.open(link, '_blank');
      }
      return;
    }

    if (!celular) {
      enviarPeloLink();
      return;
    }
    if (!arquivo && !arteFalhou) {
      avisar('A arte ainda está carregando. Espere um instante e toque de novo.');
      return;
    }

    var dados = arquivo ? (mensagem ? { files: [arquivo], text: mensagem } : { files: [arquivo] }) : null;
    if (dados && navigator.canShare && navigator.canShare(dados)) {
      navigator.share(dados).then(
        function () {
          avisar(mensagem
            ? 'Pronto! Se a mensagem não foi junto com a arte, ela já está copiada: é só colar na legenda.'
            : 'Pronto!');
        },
        function (erro) {
          if (erro && erro.name === 'AbortError') return;
          enviarPeloLink();
        }
      );
    } else {
      enviarPeloLink();
    }
  });

  var botaoCopiar = document.getElementById('copiar');
  if (botaoCopiar) botaoCopiar.addEventListener('click', function () {
    copiarMensagem().then(function (copiou) {
      avisar(copiou ? 'Mensagem copiada.' : 'Não deu para copiar. Segure o dedo na mensagem para copiar.');
    });
  });
})();
