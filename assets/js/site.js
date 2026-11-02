// MultiSpace: resalta en el menú la sección por la que vas (según el scroll, no solo al hacer clic). La sección activa se calcula con la
// posición real de scroll, no con un rastreador de intersección: así nunca se queda "pegada" en la última sección visitada al volver a subir.
// (La medición de visitas, si está activada, es GoatCounter: se carga directamente en el <head> y no necesita JavaScript propio ni aviso de
// cookies, porque no usa cookies ni guarda datos personales.)
(function () {
  var secs = ['apps', 'como-se-usa', 'funciones', 'preguntas'].map(function (id) {
    var el = document.getElementById(id), link = document.querySelector('.nav a.sec[data-s="' + id + '"]');
    return (el && link) ? { el: el, link: link } : null;
  }).filter(Boolean);
  if (!secs.length) return;
  var ticking = false;
  function update() {
    ticking = false;
    var ref = scrollY + 140; // compensa la cabecera fija; cuando aún no se llegó a "Apps" (estás en la portada), esa queda marcada por defecto
    var current = secs[0];
    for (var i = 0; i < secs.length; i++) { if (secs[i].el.getBoundingClientRect().top + scrollY <= ref) current = secs[i]; else break; }
    secs.forEach(function (s) { s.link.classList.toggle('on', s === current); });
  }
  function onScroll() { if (!ticking) { ticking = true; requestAnimationFrame(update); } }
  addEventListener('scroll', onScroll, { passive: true });
  addEventListener('resize', onScroll);
  // Al hacer clic, la píldora se mueve al instante: no espera a que termine el scroll (que puede tardar si la sección está lejos). Si luego
  // se sigue desplazando con el ratón, onScroll retoma el control con la sección que corresponda.
  secs.forEach(function (s) { s.link.addEventListener('click', function () { secs.forEach(function (o) { o.link.classList.toggle('on', o === s); }); }); });
  update();
})();
