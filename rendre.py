"""Rend un visuel HTML en JPEG 1080 x 1350 et signale ce qui déborde.

Image seule : /usr/bin/python3 rendre.py posts/2026-10-19.html images/2026-10-19.jpg
Carrousel   : même commande ; si le HTML contient des <section class="diapo">,
              chaque diapo devient images/2026-10-19-1.jpg, -2.jpg, etc.
Reel        : ajoutez --reel pour masquer le bouton « Faites défiler » (inutile en vidéo).
Chaque commentaire <!--PIED--> du HTML est remplacé par gabarits/pied.html.
Instagram n'accepte que le JPEG : gardez l'extension .jpg.
"""
import os, sys
from playwright.sync_api import sync_playwright

ICI = os.path.dirname(os.path.abspath(__file__))
reel = "--reel" in sys.argv
source, sortie = [a for a in sys.argv[1:] if a != "--reel"][:2]
html = open(source, encoding="utf-8").read()
if reel:
    html = html.replace("</head>", "<style>.defiler { display: none; }</style></head>")
html = html.replace("<!--PIED-->", open(os.path.join(ICI, "gabarits", "pied.html"), encoding="utf-8").read())
tmp = os.path.join(os.path.dirname(os.path.abspath(source)), "_rendu.html")
open(tmp, "w", encoding="utf-8").write(html)

# Vérifie chaque zone (la page entière, ou chaque diapo) : rien ne doit descendre
# sous les sources ou le pied, ni dépasser à droite.
VERIF = """() => {
  const zones = [...document.querySelectorAll('.diapo')];
  if (!zones.length) zones.push(document.body);
  const pb = [];
  zones.forEach((zone, i) => {
    const nom = zones.length > 1 ? `diapo ${i + 1} : ` : '';
    const haut = zone.getBoundingClientRect().top;
    const borne = zone.querySelector('.sources') || zone.querySelector('.pied');
    const limite = borne ? borne.getBoundingClientRect().top : zone.getBoundingClientRect().bottom;
    zone.querySelectorAll('.haut *, .contenu *, .interieur *').forEach(e => {
      const r = e.getBoundingClientRect();
      if (r.bottom > limite + 1) pb.push(`${nom}${e.tagName}.${e.className} descend à ${Math.round(r.bottom - haut)} px (limite ${Math.round(limite - haut)})`);
      if (r.right > 1080 - 40) pb.push(`${nom}${e.tagName}.${e.className} dépasse à droite (${Math.round(r.right)} px)`);
    });
  });
  return [...new Set(pb)].slice(0, 12);
}"""

fichiers = []
with sync_playwright() as p:
    nav = p.chromium.launch()
    page = nav.new_page(viewport={"width": 1080, "height": 1350})
    page.goto("file://" + tmp)
    page.wait_for_load_state("networkidle")
    page.evaluate("document.fonts.ready")
    problemes = page.evaluate(VERIF)
    diapos = page.locator(".diapo")
    n = diapos.count()
    if n == 0:
        page.screenshot(path=sortie, type="jpeg", quality=92)
        fichiers.append(sortie)
    else:
        base, ext = os.path.splitext(sortie)
        for i in range(n):
            nom = f"{base}-{i + 1}{ext}"
            diapos.nth(i).screenshot(path=nom, type="jpeg", quality=92)
            fichiers.append(nom)
    nav.close()
os.remove(tmp)

if problemes:
    print("DÉBORDEMENT, raccourcissez le texte ou réduisez les tailles :")
    print("\n".join(problemes))
    sys.exit(1)
print("OK", " ".join(fichiers))
