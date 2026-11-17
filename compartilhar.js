// Botão "Compartilhar no Instagram": abre o menu de compartilhar do celular com o story.
// No menu, escolha Instagram e depois Story. No computador, baixa o story para postar pelo celular.
(function () {
  var botao = document.getElementById('compartilhar');
  var aviso = document.getElementById('aviso');
  var caminhoArte = botao.dataset.arte;
  var nomeArte = botao.dataset.nome;
  var celular = window.matchMedia('(pointer: coarse)').matches;
  var arquivo = null;
  var arteFalhou = false;

  // O story é carregado antes do toque: o iPhone só abre o menu de compartilhar
  // se ele for chamado logo no toque, sem esperar download.
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

  function avisar(texto) {
    aviso.textContent = texto;
  }

  function baixarArte() {
    var link = document.createElement('a');
    link.href = caminhoArte;
    link.download = nomeArte;
    document.body.appendChild(link);
    link.click();
    link.remove();
  }

  botao.addEventListener('click', function () {
    if (!celular) {
      baixarArte();
      avisar('O story foi baixado. O Instagram só posta story pelo celular: abra esta página no celular ou passe o arquivo para ele.');
      return;
    }
    if (!arquivo && !arteFalhou) {
      avisar('O story ainda está carregando. Espere um instante e toque de novo.');
      return;
    }

    var dados = arquivo ? { files: [arquivo] } : null;
    if (dados && navigator.canShare && navigator.canShare(dados)) {
      navigator.share(dados).then(
        function () {
          avisar('Pronto! No Instagram, escolha Story e use as sugestões abaixo.');
        },
        function (erro) {
          if (erro && erro.name === 'AbortError') return;
          baixarArte();
          avisar('Não deu para abrir o menu. O story foi baixado: abra o Instagram e poste pela galeria.');
        }
      );
    } else {
      baixarArte();
      avisar('Este navegador não abre o menu de compartilhar. O story foi baixado: abra o Instagram e poste pela galeria.');
    }
  });

  var copiarMusica = document.getElementById('copiar-musica');
  if (copiarMusica) {
    copiarMusica.addEventListener('click', function () {
      var nome = copiarMusica.dataset.musica;
      var copia = navigator.clipboard && navigator.clipboard.writeText
        ? navigator.clipboard.writeText(nome)
        : Promise.reject(new Error('sem clipboard'));
      copia.then(
        function () {
          avisar('Nome da música copiado. No story, toque na figurinha de música e cole na busca.');
        },
        function () {
          avisar('Não deu para copiar. A música é: ' + nome);
        }
      );
    });
  }
})();
