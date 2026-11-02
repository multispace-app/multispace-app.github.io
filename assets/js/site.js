// MultiSpace: la píldora del menú solo se mueve cuando haces clic en una de sus opciones. No sigue el scroll: si subes o bajas la página con el
// ratón, se queda donde la dejaste; solo cambia con un clic o al recargar la página (vuelve a "Apps").
(function () {
  var links = [].slice.call(document.querySelectorAll('.nav a.sec[data-s]'));
  if (!links.length) return;
  links.forEach(function (link) {
    link.addEventListener('click', function () {
      links.forEach(function (l) { l.classList.toggle('on', l === link); });
    });
  });
  var apps = links.filter(function (l) { return l.dataset.s === 'apps'; })[0];
  if (apps) apps.classList.add('on');
})();
