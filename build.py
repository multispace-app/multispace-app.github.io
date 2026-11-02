#!/usr/bin/env python3
"""Genera el sitio estático de MultiSpace (ES/EN). Uso: python build.py
Fuentes de datos: site.config.json, data/release.json, data/apps.json. Salida: es/, en/, index.html, 404.html, sitemap.xml, robots.txt."""
import hashlib, html, json, pathlib, shutil

ROOT = pathlib.Path(__file__).parent
CFG = json.loads((ROOT / "site.config.json").read_text("utf8"))
REL = json.loads((ROOT / "data/release.json").read_text("utf8"))
APPS = json.loads((ROOT / "data/apps.json").read_text("utf8"))
URL = CFG["site_url"].rstrip("/")

def ver(rel_path):
    """?v=<huella> a partir del contenido real del archivo: cambia solo cuando el archivo cambia, así el navegador nunca sirve una copia vieja
    en caché tras publicar una actualización (CSS/JS se guardan 10 min según la cabecera Cache-Control de GitHub Pages)."""
    h = hashlib.sha1((ROOT / rel_path).read_bytes()).hexdigest()[:8]
    return f"/{rel_path}?v={h}"
CONTACT = CFG.get("owner_contact", "").strip()
GSV = (f'<meta name="google-site-verification" content="{html.escape(CFG["google_site_verification"])}">' if CFG.get("google_site_verification") else "")
e = html.escape
BY_ID = {a["id"]: a for a in APPS}
PHONE_IDS = ["facebook", "tiktok", "coc", "mlbb", "whatsapp"]

# ---------------------------------------------------------------- iconos SVG
def svg(body, w=24, sw=1.8):
    return f'<svg viewBox="0 0 24 24" width="{w}" height="{w}" fill="none" stroke="currentColor" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false">{body}</svg>'
CHECK = lambda w=22: svg('<path d="M5 12.5l4.5 4.5L19 7.5"/>', w, 2.4)
WARN = svg('<path d="M12 4l9 16H3z"/><path d="M12 10v4M12 17.2v.1"/>', 16, 2)
CHEV = '<svg class="chv" viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" focusable="false"><path d="M9 5l7 7-7 7"/></svg>'
DOWNLOAD = svg('<path d="M12 4v10"/><path d="M8 10.5l4 4 4-4"/><path d="M4 15v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3"/>', 22, 2.2)
IC_COPY = svg('<rect x="9" y="9" width="11" height="11" rx="2.8"/><path d="M15 9V6.8A2.8 2.8 0 0 0 12.2 4H6.8A2.8 2.8 0 0 0 4 6.8v5.4A2.8 2.8 0 0 0 6.8 15H9"/>', 26)
IC_DB = svg('<ellipse cx="12" cy="6" rx="7" ry="3"/><path d="M5 6v6c0 1.7 3.1 3 7 3s7-1.3 7-3V6"/><path d="M5 12v6c0 1.7 3.1 3 7 3s7-1.3 7-3v-6"/>', 26)
IC_FP = svg('<path d="M5 11a7 7 0 0 1 14 0"/><path d="M8 20c-.8-2-1-4-1-6a5 5 0 0 1 10 0c0 1.2.1 2.4.4 3.5"/><path d="M12 14c0 2.5.3 4.5 1.2 6.5"/><path d="M3 14.5c0-.5 0-1 .1-1.5"/><path d="M21 14c0 1.5-.2 3-.7 4.5"/>', 26)
IC_PHONE = svg('<rect x="7" y="2.5" width="10" height="19" rx="2.6"/><path d="M9.8 12.3l1.6 1.6 2.9-3.2"/><path d="M10.8 18.5h2.4"/>', 26)
CH_PHONE = svg('<rect x="7" y="2.5" width="10" height="19" rx="2.6"/><path d="M10.8 18.5h2.4"/>', 18, 1.7)
CH_LAYERS = svg('<path d="M12 3l9 5-9 5-9-5z"/><path d="M3 12.5l9 5 9-5"/>', 18, 1.7)
CH_GLOBE = svg('<circle cx="12" cy="12" r="9"/><path d="M3 12h18"/><path d="M12 3c2.5 2.5 3.5 5.5 3.5 9s-1 6.5-3.5 9c-2.5-2.5-3.5-5.5-3.5-9s1-6.5 3.5-9z"/>', 18, 1.7)
CH_GIFT = svg('<rect x="4" y="9.5" width="16" height="10.5" rx="1.6"/><path d="M4 13.5h16"/><path d="M12 9.5v10.5"/><path d="M12 9.5c-1-3-3-4.5-4.5-4.5A2 2 0 0 0 5.5 7c0 1.6 2 2.5 6.5 2.5z"/><path d="M12 9.5c1-3 3-4.5 4.5-4.5A2 2 0 0 1 18.5 7c0 1.6-2 2.5-6.5 2.5z"/>', 18, 1.7)
CP = svg('<circle cx="12" cy="12" r="9"/><path d="M14.8 9.5a3.4 3.4 0 1 0 0 5"/>', 20, 1.7)
INFO = svg('<circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 7.8v.1"/>', 22, 1.7)

def tile(a, extra=""):
    ic = a["icon"]
    if "img" in ic:
        return f'<div class="t pic2{extra}"><img src="{ic["img"]}" alt="" width="128" height="128" loading="lazy" decoding="async"></div>'
    return f'<div class="t {ic["cls"]}{extra}"><i></i></div>'

# ---------------------------------------------------------------- textos
S = {
"es": {
 "locale": "es_ES", "other": "en", "skip": "Saltar al contenido",
 "nav": {"apps": "Apps", "how": "Cómo se usa", "feat": "Funciones", "faq": "Preguntas", "dl": "Descargar"},
 "nav_label": "Principal", "lang_label": "Idioma",
 "slug": {"home": "", "download": "descargar/", "games": "juegos/", "report": "reportar/", "privacy": "privacidad/"},
 "meta": {
  "home": ("MultiSpace: clona apps y juegos de Android, cada una con su cuenta", "Clona tus apps y juegos de Android sin root. Cada clon tiene su propia cuenta y puede reutilizar los archivos pesados de otro clon. Descarga directa del APK."),
  "download": ("Descargar MultiSpace (APK para Android)", "Descarga el APK de MultiSpace. No está en Google Play. Versión, tamaño y huellas de verificación publicados en esta página."),
  "games": ("Apps y juegos probados con MultiSpace", "Lista de apps y juegos probados dentro de clones de MultiSpace, con el dispositivo de prueba y notas de cada resultado."),
  "report": ("Reportar si un juego funciona en MultiSpace", "Cómo contar si un juego o app funciona en MultiSpace. Los informes se enviarán desde la propia app."),
  "privacy": ("Privacidad · MultiSpace", "Qué datos recoge este sitio y qué hace y qué no hace la app MultiSpace con tus datos."),
 },
 "hero_checks": ["Funciona sin root.", "Usar varias cuentas de redes sociales.", "Gestionar múltiples cuentas de juegos.", "Separar cuentas de trabajo y personales.", "Mantener tus datos organizados y seguros."],
 "logo_alt": "MultiSpace: clona apps y juegos de Android", "tagline": "Clona tus apps y juegos de Android. Cada clon, con su propia cuenta.",
 "dl_btn": "Descargar APK", "phone_label": "Pantalla de MultiSpace con cinco clones: Facebook, TikTok, Clash of Clans, Mobile Legends y WhatsApp",
 "clones": "Tus clones", "add_clone": "Añadir clon", "tab_home": "Inicio", "tab_add": "Añadir",
 "apps_h": "Apps que puedes clonar", "apps_sub": "La lista crece con cada app que se prueba y se aprueba.", "apps_more": "Ver las apps probadas y reportar la tuya →",
 "how_h": "Cómo se usa", "how_sub": "De descargar a jugar con dos cuentas, en cuatro pasos.",
 "steps": [("Instálalo", "Descarga el APK desde esta página y permite instalarlo cuando Android lo pida."),
           ("Elige la app", "MultiSpace muestra tus apps instaladas. Toca la que quieras clonar."),
           ("Decide qué comparte", "Reutiliza los archivos pesados de otro clon del mismo juego, o empieza con una cuenta limpia."),
           ("Ábrelo y juega", "Cada clon tiene su cuenta. Puedes tener hasta 8 abiertos a la vez.")],
 "pick": "Elegir app", "create": "Crear clon", "tog": "Usar el contenido de otro clon", "tog_note": "El juego no vuelve a descargarse: se reutilizan sus archivos pesados.", "create_btn": "Crear clon",
 "real_h1": "Qué hace", "real_h2": "de verdad", "real_sub": "Sin adornos: lo que ocurre en tu teléfono.", "phrase": ("Tu teléfono,", "tus datos,", "tus reglas."),
 "real": [(IC_COPY, "Datos separados por clon", "Cada clon guarda su sesión y sus archivos aparte del original."),
          (IC_DB, "Contenido compartido, si quieres", "Un clon nuevo puede reutilizar los archivos pesados de otro clon del mismo juego: ocupan espacio una sola vez."),
          (IC_FP, "Identificador propio, opcional", "Puedes darle al clon su propio identificador de dispositivo. Se explica el riesgo antes."),
          (IC_PHONE, "Todo queda en tu teléfono", "Sin cuenta ni registro. Los informes solo se envían si tú los envías.")],
 "keys_h": "Dos opciones que lo cambian todo", "keys_sub": "Aparecen al crear un clon. Las dos son opcionales y las decides tú.",
 "k1": {"t": "Contenido compartido", "lead": "El primer clon descarga el juego. Los siguientes pueden reutilizar esa descarga.", "ex": "Así el segundo clon del mismo juego no descarga nada otra vez ni ocupa el doble de espacio.",
        "sw": "Usar el contenido de otro clon", "sw_s": "El juego no vuelve a descargarse.", "src": "Origen", "src_v": "Clash of Clans · clon 1", "chip": "Carpetas pesadas del juego",
        "bad": ("Sin compartir", ["Clon 1", "Clon 2"], "2 descargas · doble espacio"), "good": ("Compartiendo", "1 descarga · el espacio de una"),
        "use": ("Úsala si", "ya tienes un clon de ese juego."), "note": ("Ten en cuenta", "que el primer clon no se puede borrar mientras otro dependa de él.")},
 "k2": {"t": "Identificador propio", "lead": "Hace que cada cuenta parezca estar en un teléfono distinto.", "ex": "Algunos juegos relacionan las cuentas que ven en el mismo teléfono. Así, cada clon se presenta con su propia identificación.",
        "sw": "Identificador de dispositivo propio", "sw_s": "El clon recibe su propio ANDROID_ID.", "orig": "Original", "clone": "Clon", "amber": "Opcional. Tú decides si lo activas.",
        "bad": ("Sin la opción", "1 identificación", "El juego ve un solo teléfono"), "good": ("Con la opción", "El juego ve dos teléfonos"), "acc": "Cuenta",
        "use": ("Úsala si", "el juego mezcla tus cuentas."), "note": ("Ten en cuenta", "que algunos juegos pueden reaccionar; el riesgo lo asumes tú.")},
 "faq_h": "Preguntas frecuentes",
 "faq": [("¿Necesito root?", "No."), ("¿Funciona con todos los juegos?", "No. Algunos rechazan clones. Mira las apps probadas en la lista."),
         ("¿Por qué no está en Google Play?", "Se descarga directo desde esta página; compara la huella SHA-256."),
         ("¿Tengo que descargar el juego otra vez?", "El primer clon sí descarga todo. Los siguientes del mismo juego pueden reutilizar esa descarga.")],
 "foot_tag": "Clona tus apps y juegos de Android. Cada clon, con su propia cuenta.", "chips": ["Gratis", "Android 13+", "Sin root", "Español · English"],
 "cols": {"explore": "Explorar", "learn": "Aprende", "legal": "Legal"},
 "links": {"dl": "Descargar", "games": "Apps probadas", "report": "Reportar un juego", "how": "Cómo se usa", "shared": "Contenido compartido", "ident": "Identificador propio", "faq": "Preguntas frecuentes",
           "privacy": "Privacidad", "brands": "Aviso de marcas", "contact": "Contacto"},
 "copy": "2026 MultiSpace · Proyecto independiente",
 "notice": "MultiSpace no está afiliado a Facebook, TikTok, Supercell, Moonton, WhatsApp ni a ninguna otra marca mencionada. Los nombres e iconos pertenecen a sus dueños.",
 "fcube": "",
},
"en": {
 "locale": "en_US", "other": "es", "skip": "Skip to content",
 "nav": {"apps": "Apps", "how": "How it works", "feat": "Features", "faq": "FAQ", "dl": "Download"},
 "nav_label": "Main", "lang_label": "Language",
 "slug": {"home": "", "download": "download/", "games": "games/", "report": "report/", "privacy": "privacy/"},
 "meta": {
  "home": ("MultiSpace: clone Android apps and games, each with its own account", "Clone your Android apps and games, no root. Each clone has its own account and can reuse another clone's heavy files. Direct APK download."),
  "download": ("Download MultiSpace (Android APK)", "Download the MultiSpace APK. It is not on Google Play. Version, size and verification fingerprints are published on this page."),
  "games": ("Apps and games tested with MultiSpace", "A list of apps and games tested inside MultiSpace clones, with the test device and notes for each result."),
  "report": ("Report whether a game works in MultiSpace", "How to tell us whether a game or app works in MultiSpace. Reports will be sent from inside the app."),
  "privacy": ("Privacy · MultiSpace", "What data this site collects and what the MultiSpace app does and does not do with your data."),
 },
 "hero_checks": ["Works without root.", "Use several social media accounts.", "Manage multiple game accounts.", "Keep work and personal accounts apart.", "Keep your data organized and safe."],
 "logo_alt": "MultiSpace: clone Android apps and games", "tagline": "Clone your Android apps and games. Each clone, with its own account.",
 "dl_btn": "Download APK", "phone_label": "MultiSpace screen with five clones: Facebook, TikTok, Clash of Clans, Mobile Legends and WhatsApp",
 "clones": "Your clones", "add_clone": "Add clone", "tab_home": "Home", "tab_add": "Add",
 "apps_h": "Apps you can clone", "apps_sub": "The list grows with every app that is tested and approved.", "apps_more": "See the tested apps and report yours →",
 "how_h": "How it works", "how_sub": "From download to playing with two accounts, in four steps.",
 "steps": [("Install it", "Download the APK from this page and allow the install when Android asks."),
           ("Pick the app", "MultiSpace lists your installed apps. Tap the one you want to clone."),
           ("Choose what it shares", "Reuse the heavy files of another clone of the same game, or start with a clean account."),
           ("Open it and play", "Each clone has its own account. You can keep up to 8 open at once.")],
 "pick": "Pick app", "create": "Create clone", "tog": "Use another clone's content", "tog_note": "The game is not downloaded again: its heavy files are reused.", "create_btn": "Create clone",
 "real_h1": "What it really", "real_h2": "does", "real_sub": "No fluff: what happens on your phone.", "phrase": ("Your phone,", "your data,", "your rules."),
 "real": [(IC_COPY, "Separate data per clone", "Each clone keeps its session and files apart from the original."),
          (IC_DB, "Shared content, if you want", "A new clone can reuse the heavy files of another clone of the same game: they take up space only once."),
          (IC_FP, "Own identifier, optional", "You can give the clone its own device identifier. The risk is explained first."),
          (IC_PHONE, "Everything stays on your phone", "No account or sign-up. Reports are only sent if you send them.")],
 "keys_h": "Two options that change everything", "keys_sub": "They appear when you create a clone. Both are optional and up to you.",
 "k1": {"t": "Shared content", "lead": "The first clone downloads the game. The next ones can reuse that download.", "ex": "So the second clone of the same game downloads nothing again and does not take double the space.",
        "sw": "Use another clone's content", "sw_s": "The game is not downloaded again.", "src": "Source", "src_v": "Clash of Clans · clone 1", "chip": "Heavy game folders",
        "bad": ("Not shared", ["Clone 1", "Clone 2"], "2 downloads · double the space"), "good": ("Sharing", "1 download · the space of one"),
        "use": ("Use it if", "you already have a clone of that game."), "note": ("Keep in mind", "the first clone cannot be deleted while another depends on it.")},
 "k2": {"t": "Own identifier", "lead": "Makes each account look like it is on a different phone.", "ex": "Some games link the accounts they see on the same phone. This way, each clone presents its own identification.",
        "sw": "Own device identifier", "sw_s": "The clone gets its own ANDROID_ID.", "orig": "Original", "clone": "Clone", "amber": "Optional. You decide whether to turn it on.",
        "bad": ("Without the option", "1 identification", "The game sees a single phone"), "good": ("With the option", "The game sees two phones"), "acc": "Account",
        "use": ("Use it if", "the game mixes your accounts."), "note": ("Keep in mind", "some games may react to it; you accept the risk.")},
 "faq_h": "Frequently asked questions",
 "faq": [("Do I need root?", "No."), ("Does it work with every game?", "No. Some games reject clones. See the tested apps in the list."),
         ("Why is it not on Google Play?", "You download it straight from this page; compare the SHA-256 fingerprint."),
         ("Do I have to download the game again?", "The first clone does download everything. The next ones of the same game can reuse that download.")],
 "foot_tag": "Clone your Android apps and games. Each clone, with its own account.", "chips": ["Free", "Android 13+", "No root", "Español · English"],
 "cols": {"explore": "Explore", "learn": "Learn", "legal": "Legal"},
 "links": {"dl": "Download", "games": "Tested apps", "report": "Report a game", "how": "How it works", "shared": "Shared content", "ident": "Own identifier", "faq": "FAQ",
           "privacy": "Privacy", "brands": "Trademark notice", "contact": "Contact"},
 "copy": "2026 MultiSpace · Independent project",
 "notice": "MultiSpace is not affiliated with Facebook, TikTok, Supercell, Moonton, WhatsApp or any other brand mentioned. Names and icons belong to their owners.",
 "fcube": "",
},
}

def path(l, page, anchor=""):
    return f"/{l}/{S[l]['slug'][page]}{anchor}"

# ---------------------------------------------------------------- bloques de la portada
def dl_link(l, cls="btn"):
    t = S[l]
    return f'<a class="{cls}" href="{path(l, "download")}">{DOWNLOAD}<span>{t["dl_btn"]}</span></a>'

def nav(l, page):
    t = S[l]; base = "" if page == "home" else path(l, "home")
    other = t["other"]
    lang = (f'<span class="lang" role="group" aria-label="{t["lang_label"]}">'
            f'<a href="{path("es", page)}" hreflang="es" lang="es"{" aria-current=\"true\"" if l == "es" else ""}>ES</a><i>|</i>'
            f'<a href="{path("en", page)}" hreflang="en" lang="en"{" aria-current=\"true\"" if l == "en" else ""}>EN</a></span>')
    return (f'<nav class="nav" aria-label="{t["nav_label"]}"><a class="lg" href="{path(l, "home")}"><img src="/assets/img/icon-192.png" alt="" width="44" height="44"><span class="wm">Multi<b>Space</b></span></a>'
            f'<div class="r"><a class="sec" href="{base}#apps" data-s="apps">{t["nav"]["apps"]}</a><a class="sec" href="{base}#como-se-usa" data-s="como-se-usa">{t["nav"]["how"]}</a>'
            f'<a class="sec" href="{base}#funciones" data-s="funciones">{t["nav"]["feat"]}</a><a class="sec" href="{base}#preguntas" data-s="preguntas">{t["nav"]["faq"]}</a>'
            f'<span class="sep"></span>{lang}<a class="pillb" href="{path(l, "download")}">{t["nav"]["dl"]}</a></div></nav>')

def phone(l):
    t = S[l]
    cards = "".join(f'<div class="card">{tile(BY_ID[i])}{e(BY_ID[i]["name"])}</div>' for i in PHONE_IDS)
    return (f'<div class="phones" role="img" aria-label="{e(t["phone_label"])}"><div class="ph a" aria-hidden="true"><div class="ui">'
            f'<img class="ulogo" src="/assets/img/logo.webp" alt="" width="170" height="85" loading="lazy">'
            f'<div class="bar"><span>{t["clones"]} <em>5</em></span><span>☰</span></div>'
            f'<div class="cards">{cards}<div class="card add"><div class="plus">+</div>{t["add_clone"]}</div></div>'
            f'<div class="tabs"><span class="cur">{t["tab_home"]}</span><span>{t["tab_add"]}</span></div></div></div></div>')

def hero(l, page):
    t = S[l]
    top = f'<div class="hero{"" if page == "home" else " slim"}"><header>{nav(l, page)}</header>'
    if page != "home":
        return top + "</div>"
    checks = "".join(f'<li>{CHECK()}<span>{c}</span></li>' for c in t["hero_checks"])
    return (f'<div class="hero"><header>{nav(l, page)}</header>'
            f'<div class="hg"><ul class="hl">{checks}</ul>'
            f'<div class="hc"><h1><img class="logo" src="/assets/img/logo.webp" alt="{e(t["logo_alt"])}" width="1200" height="600" fetchpriority="high"></h1>'
            f'<p class="l">{t["tagline"]}</p>{dl_link(l)}</div>{phone(l)}</div></div>')

def section_apps(l):
    t = S[l]
    items = "".join(f'<div class="it">{tile(a)}{e(a["name"])}</div>' for a in APPS)
    dup = "".join(f'<div class="it" aria-hidden="true">{tile(a)}{e(a["name"])}</div>' for a in APPS)
    return (f'<section class="apps" id="apps" aria-labelledby="h-apps"><div class="ahead"><h2 class="h2" id="h-apps">{t["apps_h"]}</h2><p class="sub">{t["apps_sub"]}</p></div>'
            f'<div class="mq"><div class="trk">{items}{dup}</div></div>'
            f'<a class="more" href="{path(l, "games")}">{t["apps_more"]}</a></section>')

def section_steps(l):
    t = S[l]
    sel = [BY_ID[i] for i in PHONE_IDS]
    rows = "".join(f'<div class="mrow{" sel" if a["id"] == "coc" else ""}">{tile(a)}<span>{e(a["name"])}</span></div>' for a in sel)
    mc = "".join(f'<div class="mc">{tile(a)}<span>{e(a["name"])}</span></div>' for a in sel) + f'<div class="mc add">+<span>{t["tab_add"]}</span></div>'
    coc = BY_ID["coc"]
    pics = [
        '<div class="apk"><img src="/assets/img/icon-192.png" alt="" width="110" height="110" loading="lazy"></div>',
        f'<div class="mini" aria-hidden="true"><div class="mh">{t["pick"]}</div>{rows}</div>',
        f'<div class="mini" aria-hidden="true"><div class="mh">{t["create"]}</div><div class="mrow">{tile(coc)}<span>{coc["name"]}</span></div><div class="mtog"><span>{t["tog"]}</span><b></b></div><div class="mnote">{t["tog_note"]}</div><div class="mbtn">{t["create_btn"]}</div></div>',
        f'<div class="mini" aria-hidden="true"><div class="mh">{t["clones"]} <em>5</em></div><div class="mgrid">{mc}</div></div>',
    ]
    st = "".join(f'<li class="stp"><div class="dot" aria-hidden="true">{i + 1}</div><div class="pic">{pics[i]}</div><h3>{h}</h3><p>{p}</p></li>' for i, (h, p) in enumerate(t["steps"]))
    return (f'<section class="steps" id="como-se-usa" aria-labelledby="h-how"><h2 class="h2" id="h-how">{t["how_h"]}</h2><p class="sub">{t["how_sub"]}</p><ol class="flow">{st}</ol></section>')

def section_real(l):
    t = S[l]
    items = "".join(f'<div><b class="ic">{ic}</b><dt>{h}</dt><dd>{p}</dd></div>' for ic, h, p in t["real"])
    a, b, c = t["phrase"]
    return (f'<section class="real" id="funciones" aria-labelledby="h-real"><div class="rg"><div><h2 class="h2" id="h-real">{t["real_h1"]}<br><em>{t["real_h2"]}</em></h2>'
            f'<p class="sub rsub">{t["real_sub"]}</p><div class="rside"><p>{a}<br><b>{b}</b><br>{c}</p></div></div><dl class="defs">{items}</dl></div></section>')

def dia_pair(bad, good, bad_nodes, good_nodes, bad_b, good_b):
    nd = lambda nodes: "".join(f'<span class="arr">{n[1:]}</span>' if n.startswith("~") else f'<span>{e(n)}</span>' for n in nodes)
    return (f'<div class="dia"><div class="dr bad"><em>{bad}</em><div class="nd">{nd(bad_nodes)}</div><b>{bad_b}</b></div>'
            f'<div class="dr good"><em>{good}</em><div class="nd">{nd(good_nodes)}</div><b>{good_b}</b></div></div>')

def section_keys(l):
    t = S[l]; k1, k2 = t["k1"], t["k2"]
    ul = lambda k: f'<ul><li>{CHECK(16)}<span><b>{k["use"][0]}</b> {k["use"][1]}</span></li><li>{WARN}<span><b>{k["note"][0]}</b> {k["note"][1]}</span></li></ul>'
    d1 = dia_pair(k1["bad"][0], k1["good"][0], k1["bad"][1], [k1["bad"][1][0], "~→", k1["bad"][1][1]], k1["bad"][2], k1["good"][1])
    acc = k2["acc"]
    d2 = dia_pair(k2["bad"][0], k2["good"][0], [f"{acc} 1", f"{acc} 2", "~→", k2["bad"][1]], [f"{acc} 1", "~→", "ID A", f"{acc} 2", "~→", "ID B"], k2["bad"][2], k2["good"][1])
    c1 = (f'<article class="kc" id="contenido-compartido"><div class="panel" aria-hidden="true"><div class="ph1">{t["create"]}</div>'
          f'<div class="sw"><div><b>{k1["sw"]}</b><small>{k1["sw_s"]}</small></div><i class="on"></i></div>'
          f'<div class="src"><span>{k1["src"]}</span><b>{k1["src_v"]}</b></div><div class="chips"><span>{CHECK(16)} {k1["chip"]}</span></div></div>'
          f'<div class="kt"><div class="ico">{IC_DB}</div><div><h3>{k1["t"]}</h3><p class="lead">{k1["lead"]}</p><p class="ex">{k1["ex"]}</p>{d1}{ul(k1)}</div></div></article>')
    c2 = (f'<article class="kc" id="identificador-propio"><div class="panel" aria-hidden="true"><div class="ph1">{t["create"]}</div>'
          f'<div class="sw"><div><b>{k2["sw"]}</b><small>{k2["sw_s"]}</small></div><i class="on"></i></div>'
          f'<div class="ids"><div><span>{k2["orig"]}</span><code>•••• •••• 7c2e</code></div><div><span>{k2["clone"]}</span><code class="new">•••• •••• 91ab</code></div></div>'
          f'<div class="amber">{WARN}<span>{k2["amber"]}</span></div></div>'
          f'<div class="kt"><div class="ico">{IC_FP}</div><div><h3>{k2["t"]}</h3><p class="lead">{k2["lead"]}</p><p class="ex">{k2["ex"]}</p>{d2}{ul(k2)}</div></div></article>')
    return (f'<section class="keys" aria-labelledby="h-keys"><div class="kh"><h2 class="h2" id="h-keys">{t["keys_h"]}</h2><p class="sub">{t["keys_sub"]}</p></div><div class="kg">{c1}{c2}</div></section>')

def section_faq(l):
    t = S[l]
    qs = "".join(f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in t["faq"])
    return f'<section class="faq" id="preguntas" aria-labelledby="h-faq"><div class="fg"><div><h2 class="h2" id="h-faq">{t["faq_h"]}</h2></div><div>{qs}</div></div></section>'

def footer(l):
    t = S[l]; L = t["links"]; H = path(l, "home")
    link = lambda href, txt: f'<a href="{href}">{CHEV}<span>{txt}</span></a>'
    col = lambda img, title, links: f'<div class="fc"><div class="fh"><span class="fi"><img src="/assets/img/{img}" alt="" width="200" height="200" loading="lazy"></span><h2>{title}</h2></div>{"".join(links)}</div>'
    legal = [link(path(l, "privacy"), L["privacy"]), link("#aviso", L["brands"])]
    if CONTACT:
        legal.append(link(f"mailto:{e(CONTACT)}", L["contact"]))
    chips = "".join(f'<span>{ic} {txt}</span>' for ic, txt in zip((CH_GIFT, CH_PHONE, CH_LAYERS, CH_GLOBE), t["chips"]))
    return (f'<footer class="ft2"><div class="fcap"><div class="fmain"><div class="fbr"><img src="/assets/img/logo.webp" alt="MultiSpace" width="280" height="140" loading="lazy"><p>{t["foot_tag"]}</p><div class="fchip">{chips}</div></div>'
            + col("ic-download.webp", t["cols"]["explore"], [link(path(l, "download"), L["dl"]), link(path(l, "games"), L["games"]), link(path(l, "report"), L["report"])])
            + col("ic-book.webp", t["cols"]["learn"], [link(H + "#como-se-usa", L["how"]), link(H + "#contenido-compartido", L["shared"]), link(H + "#identificador-propio", L["ident"]), link(H + "#preguntas", L["faq"])])
            + col("ic-shield.webp", t["cols"]["legal"], legal)
            + f'<div class="fcube" aria-hidden="true"><img src="/assets/img/cube-ring.webp" alt="" width="160" height="146" loading="lazy"></div></div>'
            f'<div class="fend"><span class="cc">{CP}<span>{t["copy"]}</span></span><p class="nf" id="aviso">{INFO}<span>{t["notice"]}</span></p></div></div></footer>')

# ---------------------------------------------------------------- páginas interiores
def pill_btn(label, href=None, disabled=False):
    if disabled:
        return f'<span class="btn off" aria-disabled="true">{DOWNLOAD}<span>{label}</span></span>'
    return f'<a class="btn" href="{href}" download>{DOWNLOAD}<span>{label}</span></a>'

def body_download(l):
    es = l == "es"; pub = REL["published"] and REL["url"]
    pend = "Pendiente de publicar" if es else "To be published"
    row = lambda k, v: f'<dt>{k}</dt><dd>{e(v) if v else pend}</dd>'
    meta = "".join([row("Versión" if es else "Version", REL["version"]), row("Fecha" if es else "Date", REL["date"]),
                    row("Tamaño" if es else "Size", (REL["size_mb"] + " MB") if REL["size_mb"] else ""),
                    row("Android", ("Android " + REL["min_android"] + ("+" if REL["min_android"] else "")))])
    tech = "".join([row("Arquitectura" if es else "Architecture", REL["arch"]),
                    row("SHA-256 del APK" if es else "APK SHA-256", REL["sha256"]), row("Huella del certificado" if es else "Certificate fingerprint", REL["cert_sha256"])])
    tech_block = (f'<details class="techdl"><summary>{"Detalles técnicos y verificación" if es else "Technical details and verification"}</summary>'
                  f'<dl class="meta">{tech}</dl>'
                  f'<p>{"Compara la huella SHA-256 con la del archivo que descargaste antes de instalarlo. Si no coinciden, no lo instales." if es else "Compare the SHA-256 fingerprint with the one of the file you downloaded before installing. If they do not match, do not install it."}</p></details>')
    if es:
        note = "" if pub else '<p class="notice"><strong>Todavía no hay un APK publicado.</strong> Cuando exista, aquí aparecerá el botón de descarga con su tamaño y sus huellas de verificación reales.</p>'
        btn = pill_btn(f'Descargar APK · v{e(REL["version"])}', REL["url"]) if pub else pill_btn("APK disponible muy pronto", disabled=True)
        return (f'<h1>Descargar MultiSpace</h1><p>MultiSpace es totalmente gratis. No está en Google Play: se descarga como APK directamente desde esta página. Android te pedirá permitir la instalación desde el navegador o el gestor de archivos que uses.</p>'
                f'{note}<p>{btn}</p><dl class="meta">{meta}</dl>{tech_block}<h2>Cómo instalarlo</h2><ol><li>Descarga el APK desde esta página.</li><li>Ábrelo y, si Android lo pide, permite instalar apps desde esa fuente.</li><li>Abre MultiSpace y crea tu primer clon.</li></ol>'
                f'<h2>Qué puede aparecer al instalarlo</h2><p>Como MultiSpace no está en Google Play, Android añade avisos que no salen con las apps de la tienda. No significa que la app tenga nada malo: es la seguridad normal de Android y de Google Play Protect para cualquier APK que no venga de la tienda.</p>'
                '<div class="installs">'
                '<div class="istep"><h3>«Permitir instalar desde esta fuente»</h3><p>La primera vez, tu navegador o gestor de archivos te pedirá este permiso antes de instalar. Actívalo solo para esa app y continúa.</p></div>'
                '<div class="istep"><h3>«Analizando la app…» (Google Play Protect)</h3><p>Es automático: Play Protect revisa cualquier app instalada fuera de la tienda antes de dejarte continuar. Es normal y no significa nada malo.</p></div>'
                '<div class="istep"><h3>«Se bloqueó la app dañina» o un aviso parecido</h3><p>A veces Play Protect muestra una advertencia más fuerte porque MultiSpace es una app nueva y con pocas instalaciones, y porque pide un permiso para instalar apps y carga el código de otras: dos cosas normales en MultiSpace, pero que a Play Protect le parecen sospechosas. Si confías en la fuente, toca «Más detalles» y luego «Instalar de todas formas».</p></div>'
                '</div>'
                f'<h2>Actualizaciones</h2><p>Una vez instalada, MultiSpace te avisa dentro de la app cuando hay una versión nueva, con la opción de actualizar o de recordártelo más tarde. No tienes que volver a esta página. La primera vez que actualices puede volver a pedir alguno de los permisos de arriba.</p>')
    note = "" if pub else '<p class="notice"><strong>No APK has been published yet.</strong> Once it exists, the download button will appear here with its real size and verification fingerprints.</p>'
    btn = pill_btn(f'Download APK · v{e(REL["version"])}', REL["url"]) if pub else pill_btn("APK coming soon", disabled=True)
    return (f'<h1>Download MultiSpace</h1><p>MultiSpace is completely free. It is not on Google Play: you download it as an APK straight from this page. Android will ask you to allow installs from the browser or file manager you use.</p>'
            f'{note}<p>{btn}</p><dl class="meta">{meta}</dl>{tech_block}<h2>How to install</h2><ol><li>Download the APK from this page.</li><li>Open it and, if Android asks, allow installing apps from that source.</li><li>Open MultiSpace and create your first clone.</li></ol>'
            f'<h2>What might appear during install</h2><p>Because MultiSpace is not on Google Play, Android adds warnings that do not show up with Play Store apps. That does not mean anything is wrong with the app: it is the normal security check Android and Google Play Protect run on any APK that is not from the store.</p>'
            '<div class="installs">'
            '<div class="istep"><h3>"Allow installs from this source"</h3><p>The first time, your browser or file manager will ask for this permission before installing. Turn it on just for that app and continue.</p></div>'
            '<div class="istep"><h3>"Scanning the app…" (Google Play Protect)</h3><p>This is automatic: Play Protect checks any app installed outside the store before letting you continue. It is normal and does not mean anything is wrong.</p></div>'
            '<div class="istep"><h3>"Harmful app blocked" or a similar warning</h3><p>Sometimes Play Protect shows a stronger warning because MultiSpace is a new app with few installs, and because it asks for a permission to install apps and loads other apps\' code: both normal for MultiSpace, but things Play Protect treats as suspicious. If you trust the source, tap "More details" and then "Install anyway".</p></div>'
            '</div>'
            f'<h2>Updates</h2><p>Once installed, MultiSpace tells you inside the app when a new version is out, with the option to update or be reminded later. You do not need to come back to this page. The first time you update, it may ask for one of the permissions above again.</p>')

def body_games(l):
    es = l == "es"
    tested = [a for a in APPS if a.get("tested")]
    if tested:
        cards = "".join(f'<li class="gc">{tile(a)}<div><h3>{e(a["name"])}</h3><p class="gt">{e(a["tested_on"])}</p><p>{e(a["note_" + l])}</p></div></li>' for a in tested)
        lst = f'<ul class="glist">{cards}</ul>'
    else:
        lst = f'<p class="notice">{"Todavía no hay apps probadas." if es else "No apps have been tested yet."}</p>'
    if es:
        return (f'<h1>Apps y juegos probados</h1><p>Esta lista solo incluye apps que se han probado de verdad dentro de un clon de MultiSpace, con el dispositivo en que se probó. Crece con cada prueba que se aprueba.</p>{lst}'
                f'<p>¿No ves tu juego? Pruébalo y <a class="tl" href="{path(l, "report")}">cuéntanos el resultado</a>.</p>'
                f'<p class="small">Los nombres e iconos pertenecen a sus dueños; MultiSpace no está afiliado a ellos.</p>')
    return (f'<h1>Tested apps and games</h1><p>This list only includes apps that were really tested inside a MultiSpace clone, with the device they were tested on. It grows with every approved test.</p>{lst}'
            f'<p>Do not see your game? Try it and <a class="tl" href="{path(l, "report")}">tell us the result</a>.</p>'
            f'<p class="small">Names and icons belong to their owners; MultiSpace is not affiliated with them.</p>')

def body_report(l):
    if l == "es":
        return ('<h1>Reportar si un juego funciona</h1><p>Los informes se enviarán desde dentro de la app MultiSpace, para que incluyan el modelo de teléfono y la versión de Android sin que tengas que escribirlos.</p>'
                '<p class="notice"><strong>Función en preparación.</strong> Todavía no está activa. Cuando lo esté, verás el mensaje completo antes de enviarlo y podrás editarlo o cancelar.</p>'
                '<h2>Qué incluirá un informe</h2><ul><li>El nombre del juego o app que probaste.</li><li>Si funciona, funciona a medias o no funciona, y un comentario tuyo.</li><li>El modelo del teléfono y la versión de Android.</li></ul>'
                '<p>No incluirá tus cuentas, mensajes ni archivos. Solo se envía si tú lo envías.</p>')
    return ('<h1>Report whether a game works</h1><p>Reports will be sent from inside the MultiSpace app, so they include the phone model and Android version without you typing them.</p>'
            '<p class="notice"><strong>Feature in preparation.</strong> It is not active yet. When it is, you will see the full message before sending and can edit or cancel it.</p>'
            '<h2>What a report will include</h2><ul><li>The name of the game or app you tested.</li><li>Whether it works, partly works or does not work, and a comment from you.</li><li>The phone model and Android version.</li></ul>'
            '<p>It will not include your accounts, messages or files. It is only sent if you send it.</p>')

def body_privacy(l):
    gc_on = bool(CFG.get("goatcounter_code"))
    if l == "es":
        an = ("Este sitio usa GoatCounter para contar las visitas de forma anónima. GoatCounter no usa cookies ni guarda datos personales: solo cuenta páginas vistas, sin poder identificarte a ti ni a tu dispositivo." if gc_on else "Este sitio no usa analíticas ni cookies.")
        return (f'<h1>Privacidad</h1><p class="small">Última actualización: noviembre de 2026.</p><h2>Este sitio</h2><p>{an} Está alojado en GitHub Pages, que puede registrar datos técnicos de conexión (como la dirección IP) según su propia política.</p>'
                '<h2>La app MultiSpace</h2><ul><li>No pide cuenta ni registro.</li><li>Los clones y sus datos se guardan en tu teléfono.</li><li>MultiSpace no envía tus clones ni tus datos a ningún servidor.</li>'
                '<li>Lo único que consulta, como mucho una vez al día, es un archivo público de esta web para saber si hay una versión nueva. Puedes apagarlo en Ajustes. Al pedirlo, GitHub puede ver tu dirección IP, como en cualquier descarga.</li>'
                '<li>Las actualizaciones solo se instalan si las aceptas, y Android te pide confirmarlas. La app comprueba la huella del archivo antes de instalarlo.</li>'
                '<li>Las apps que clones se conectan a internet como lo harían normalmente, con sus propios servidores y sus propias políticas.</li><li>Los informes de compatibilidad solo se enviarán si tú los envías, tras ver su contenido (función en preparación).</li></ul>'
                '<h2>Contacto</h2><p>' + (f'Escríbenos a <a class="tl" href="mailto:{e(CONTACT)}">{e(CONTACT)}</a>.' if CONTACT else 'Los datos de contacto se publicarán aquí.') + '</p>')
    an = ("This site uses GoatCounter to count visits anonymously. GoatCounter uses no cookies and stores no personal data: it only counts page views, without identifying you or your device." if gc_on else "This site uses no analytics or cookies.")
    return (f'<h1>Privacy</h1><p class="small">Last updated: November 2026.</p><h2>This site</h2><p>{an} It is hosted on GitHub Pages, which may log technical connection data (such as the IP address) under its own policy.</p>'
            '<h2>The MultiSpace app</h2><ul><li>It asks for no account or sign-up.</li><li>Clones and their data stay on your phone.</li><li>MultiSpace does not send your clones or your data to any server.</li>'
            '<li>The only thing it checks, at most once a day, is a public file on this site to learn whether a new version exists. You can turn it off in Settings. When requested, GitHub can see your IP address, as with any download.</li>'
            '<li>Updates are only installed if you accept them, and Android asks you to confirm. The app verifies the file\'s fingerprint before installing.</li>'
            '<li>The apps you clone connect to the internet as they normally would, with their own servers and policies.</li><li>Compatibility reports will only be sent if you send them, after seeing their content (feature in preparation).</li></ul>'
            '<h2>Contact</h2><p>' + (f'Write to us at <a class="tl" href="mailto:{e(CONTACT)}">{e(CONTACT)}</a>.' if CONTACT else 'Contact details will be published here.') + '</p>')

BODIES = {"download": body_download, "games": body_games, "report": body_report, "privacy": body_privacy}

# ---------------------------------------------------------------- datos estructurados (JSON-LD): solo campos reales, nunca inventados
def ld_website(l):
    return {"@context": "https://schema.org", "@type": "WebSite", "name": "MultiSpace", "url": path_abs(l, "home"), "inLanguage": l}

def ld_faq(l):
    t = S[l]
    return {"@context": "https://schema.org", "@type": "FAQPage",
            "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in t["faq"]]}

def ld_software(l):
    es = l == "es"
    d = {"@context": "https://schema.org", "@type": "SoftwareApplication", "name": "MultiSpace",
         "applicationCategory": "UtilitiesApplication", "operatingSystem": "Android",
         "description": S[l]["meta"]["download"][1], "url": path_abs(l, "download")}
    if REL["published"] and REL["url"]:
        d["softwareVersion"] = REL["version"]
        d["fileSize"] = f'{REL["size_mb"]}MB'
        d["downloadUrl"] = REL["url"]
        d["offers"] = {"@type": "Offer", "price": "0", "priceCurrency": "USD"}
    return d

def jsonld(*objs):
    return "".join(f'<script type="application/ld+json">{json.dumps(o, ensure_ascii=False)}</script>' for o in objs)

def path_abs(l, page):
    return URL + path(l, page)

# ---------------------------------------------------------------- documento
def document(l, page):
    t = S[l]; title, desc = t["meta"][page]
    canon = URL + path(l, page); alt = URL + path(t["other"], page)
    if page == "home":
        main = section_apps(l) + section_steps(l) + section_real(l) + section_keys(l) + section_faq(l)
        ld = jsonld(ld_website(l), ld_faq(l))
    elif page == "download":
        main = f'<div class="pg">{BODIES[page](l)}</div>'
        ld = jsonld(ld_software(l))
    else:
        main = f'<div class="pg">{BODIES[page](l)}</div>'
        ld = jsonld(ld_website(l))
    gc = (f'<script data-goatcounter="https://{e(CFG["goatcounter_code"])}.goatcounter.com/count" async src="https://gc.zgo.at/count.js"></script>'
          if CFG.get("goatcounter_code") else "")
    return f'''<!doctype html>
<html lang="{l}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canon}"><link rel="alternate" hreflang="{l}" href="{canon}"><link rel="alternate" hreflang="{t["other"]}" href="{alt}"><link rel="alternate" hreflang="x-default" href="{URL}/">
<meta name="theme-color" content="#08080a"><link rel="icon" type="image/png" sizes="32x32" href="/assets/img/icon-32.png"><link rel="apple-touch-icon" href="/assets/img/icon-180.png">{GSV}
<meta property="og:type" content="website"><meta property="og:site_name" content="MultiSpace"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canon}"><meta property="og:locale" content="{t["locale"]}"><meta property="og:image" content="{URL}/assets/img/og-image.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta name="twitter:card" content="summary_large_image">
<link rel="preload" href="/assets/fonts/rajdhani-latin-700-normal.woff2" as="font" type="font/woff2" crossorigin><link rel="preload" href="/assets/fonts/barlow-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{ver('assets/css/site.css')}"><link rel="stylesheet" href="{ver('assets/css/pages.css')}">{gc}{ld}</head>
<body><a class="skip" href="#main">{t["skip"]}</a>
{hero(l, page)}
<main id="main" tabindex="-1">{main}</main>
{footer(l)}
<script src="{ver('assets/js/site.js')}" defer></script></body></html>
'''

def write(rel, text):
    p = ROOT / rel; p.parent.mkdir(parents=True, exist_ok=True); p.write_text(text, "utf8")

for d in ("es", "en"):
    shutil.rmtree(ROOT / d, ignore_errors=True)
urls = []
for l in ("es", "en"):
    for page in S[l]["slug"]:
        write(path(l, page).strip("/") + "/index.html", document(l, page))
        urls.append(URL + path(l, page))

write("index.html", f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>MultiSpace</title>
<link rel="canonical" href="{URL}/es/"><link rel="alternate" hreflang="es" href="{URL}/es/"><link rel="alternate" hreflang="en" href="{URL}/en/"><link rel="alternate" hreflang="x-default" href="{URL}/">
<meta name="robots" content="noindex,follow"><meta name="theme-color" content="#08080a">{GSV}<style>body{{background:#08080a;color:#f4f1f2;font:18px system-ui;padding:2rem}}a{{color:#ff6670}}</style>
<script>var l=(navigator.language||"es").slice(0,2)==="en"?"en":"es";location.replace("/"+l+"/");</script></head>
<body><p><a href="/es/">Español</a> · <a href="/en/">English</a></p></body></html>
''')
write("404.html", f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>404 · MultiSpace</title><meta name="robots" content="noindex">
<link rel="stylesheet" href="{ver('assets/css/site.css')}"></head><body><main class="pg" id="main"><h1>404</h1><p>Esta página no existe. / This page does not exist.</p><p><a class="tl" href="/es/">Inicio</a> · <a class="tl" href="/en/">Home</a></p></main></body></html>
''')
write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(f"<url><loc>{u}</loc></url>\n" for u in urls) + "</urlset>\n")
write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {URL}/sitemap.xml\n")
write(".nojekyll", "")
print("ok", len(urls), "páginas")
