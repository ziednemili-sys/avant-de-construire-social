# Mise en place : pages Instagram et Facebook en pilote automatique

Chaîne : une routine Claude (cloud) écrit le post et le visuel la veille → Google Sheet → Make publie sur Instagram et Facebook à l'heure prévue.

| Jour | Heure | Format | Routine (la veille, 7 h) |
|---|---|---|---|
| Lundi | 18:30 | L'erreur qui coûte cher | dimanche |
| Mercredi | 18:30 | Checklist à enregistrer | mardi |
| Samedi | 10:00 | Vrai ou faux (semaines paires) / À éviter, à privilégier (impaires) | vendredi |

## 1. Créer les pages

**Page Facebook** (depuis ton profil : Pages → Créer une page)
- Nom : Avant de Construire
- Catégorie : Service de conseil (ajouter « Construction de maisons »)
- Bio (255 caractères max) :
  > Conseil indépendant pour faire construire ou rénover votre maison sans erreur coûteuse. Avis neutre sur plans, implantation, matériaux et options. À distance partout en France.
- Site : https://avant-de-construire.fr/ · E-mail : contact@avant-de-construire.fr · Téléphone : +33 7 60 03 09 16
- Bouton d'action : « Envoyer un e-mail » ou « Réserver » → site
- Photo de profil : l'icône maison (icone.png du site). Couverture : landing.jpg.

**Compte Instagram** (@avantdeconstruire ou @avant_de_construire)
- Passer en **compte professionnel** (Paramètres → Type de compte → Professionnel → Entreprise), catégorie « Service de conseil ».
- **Le relier à la page Facebook** (Meta Business Suite → Paramètres → Comptes Instagram). Sans ce lien, Make ne peut pas publier sur Instagram.
- Bio (150 caractères max) :
  > Faire construire sans regrets.
  > Conseil indépendant : plans, contrat, chantier.
  > Erreurs à éviter 3 fois par semaine.
- Lien : https://avant-de-construire.fr/

## 2. Google Sheet

Créer un Google Sheet **« Avant de Construire - Posts réseaux »**, renommer l'onglet en **Posts**, ligne 1 :

| A | B | C | D | E | F | G | H | I |
|---|---|---|---|---|---|---|---|---|
| Publier le (heure de Paris) | Sujet | Texte du post | Statut | Publié le | Image (URL) | Images (URLs séparées par \|) | Vidéo (URL) | Format |

F = première image (couverture). G = toutes les images dans l'ordre. H = vidéo du Reel. I = `carrousel`, `reel`, ou vide pour une image seule (anciennes lignes).

- Colonne A au format **Texte brut** (Format → Nombre → Texte brut).
- Colonne D : validation de données, liste « à publier, publié, annulé ».
- Envoyer l'identifiant du Sheet (dans l'URL, entre `/d/` et `/edit`) à Claude pour qu'il crée la routine.

## 3. Scénario Make « Avant de Construire - Instagram + Facebook »

Planification : toutes les 30 minutes (ou toutes les heures de 8 h à 20 h pour économiser les opérations).

Version 2 (novembre 2026) : carrousels le lundi et le mercredi, Reel le samedi.

1. **Google Sheets › Search Rows** : le Sheet, onglet Posts, en-têtes en ligne 1, filtre `Statut` *Equal to* `à publier`, Maximum number of returned rows : 1, tri par colonne A croissant.
2. **Filtre** (sur le lien) « heure arrivée », trois conditions (ET) :
   - `parseDate(A; "YYYY-MM-DD HH:mm"; "Europe/Paris")` *Datetime: Earlier than or equal to* `now`
   - `parseDate(A; "YYYY-MM-DD HH:mm"; "Europe/Paris")` *Datetime: Later than* `addHours(now; -3)` (évite de publier un vieux post en retard)
   - `F` *Exists*.
3. **Router** avec 4 routes, dans cet ordre :
   - **Route 1 « Instagram Reel »**, filtre `I` *Equal to* `reel` :
     **Instagram for Business › Create a Reel Post** : Video URL = `H`, Caption = `C`, partager aussi dans le fil (Share to feed) = Oui.
   - **Route 2 « Instagram carrousel »**, filtre `I` *Equal to* `carrousel` :
     **Flow Control › Iterator** : Array = `split(G; "|")`
     → **Flow Control › Array aggregator** : Source module = l'Iterator, Target structure type = le module Instagram suivant (Files), Media type = `IMAGE`, URL = `Value` de l'Iterator
     → **Instagram for Business › Create a Carousel Post** : Files = le tableau de l'Array aggregator, Caption = `C`.
   - **Route 3 « Instagram image seule »**, filtre `I` *Does not exist* (anciennes lignes) :
     **Instagram for Business › Create a Photo Post** : Photo URL = `F`, Caption = `C`.
   - **Route 4 « Facebook + statut »**, sans filtre (s'exécute toujours, en dernier) :
     **Flow Control › Iterator** : Array = `split(ifempty(G; F); "|")`
     → **Flow Control › Array aggregator** : Source module = cet Iterator, Target structure type = le module Facebook suivant (Photos), URL = `Value`
     → **Facebook Pages › Create a Post with Photos** : page Avant de Construire, Photos = le tableau de l'aggregator, Message = `C`
     → **Google Sheets › Update a Row** : Row number = celui du module 1, `Statut` = `publié`, `Publié le` = `formatDate(now; "YYYY-MM-DD HH:mm"; "Europe/Paris")`.

Sur Facebook, le samedi, le post part avec les images du Reel en album photo : c'est plus simple et plus fiable qu'une vidéo, et l'album se lit bien sur Facebook.

Conseils :
- Ajoute un error handler **Resume** sur chaque module Instagram et sur le module Facebook : une erreur sur un réseau n'empêche pas la ligne de passer en « publié », ce qui évite un double post au passage suivant.
- Les vidéos sont servies par jsDelivr (`cdn.jsdelivr.net/gh/...@<commit>/videos/...mp4`), qui envoie le bon type `video/mp4`. GitHub brut les sert en `application/octet-stream`, ce qu'Instagram peut refuser.
- Instagram prend quelques minutes pour traiter un Reel : si le module renvoie une erreur de délai, augmente son délai d'attente (timeout) dans les réglages avancés du module.
- Pour tester : une ligne de test avec `I` = `reel` et `H` = `https://cdn.jsdelivr.net/gh/ziednemili-sys/avant-de-construire-social@ad42105f90c0c3ae5430a8106f011765e2fa83ab/videos/exemple-reel.mp4`.
- Les images sont en JPEG 1080 × 1350 (format 4:5 accepté par Instagram). Instagram télécharge l'image lui-même depuis l'URL raw.githubusercontent : le dépôt doit rester **public**.
- Pour suspendre un post : passer sa ligne en « annulé ». Pour le corriger : modifier les colonnes B, C avant l'heure de publication.

## 4. Premier post (à ajouter à la main une fois les pages créées)

Ligne : `'AAAA-MM-JJ 18:30` · « Bienvenue » · texte ci-dessous · à publier · (vide) · URL de `images/bienvenue.jpg`

> Faire construire sa maison, c'est prendre des dizaines de décisions qu'on ne pourra plus changer.
>
> L'orientation sur le terrain. La place de chaque prise. Ce que dit vraiment le contrat. Ce qu'il faut vérifier le jour de la réception.
>
> Sur cette page, une équipe de professionnels de la construction et de la rénovation partage ce qu'elle voit sur le terrain, trois fois par semaine :
> → le lundi, une erreur qui coûte cher et comment l'éviter
> → le mercredi, une checklist à enregistrer
> → le samedi, les idées reçues démontées
>
> Pas de vente de matériaux, pas d'options à placer : seulement des conseils neutres pour que votre maison soit la bonne du premier coup.
>
> Vous faites construire ou rénover en ce moment ? Dites-nous à quelle étape vous en êtes.
>
> #construiremamaison #maisonindividuelle #faireconstruire #projetmaison #renovationmaison
