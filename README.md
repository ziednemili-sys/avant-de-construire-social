# avant-de-construire-social

Visuels des posts Instagram et Facebook d'Avant de Construire, générés automatiquement trois fois par semaine.

- `gabarits/` : feuille de style, pied de page, logo et exemples de mise en page (1080 x 1350).
- `posts/AAAA-MM-JJ.html` : source de chaque visuel.
- `images/AAAA-MM-JJ.jpg` : visuel publié (JPEG, exigé par Instagram), lu par Make à l'adresse
  `https://raw.githubusercontent.com/ziednemili-sys/avant-de-construire-social/main/images/AAAA-MM-JJ.jpg`.
- `rendre.py` : rendu HTML vers JPEG avec contrôle de débordement.
