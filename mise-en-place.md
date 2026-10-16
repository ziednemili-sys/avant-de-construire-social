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

| A | B | C | D | E | F |
|---|---|---|---|---|---|
| Publier le (heure de Paris) | Sujet | Texte du post | Statut | Publié le | Image (URL) |

- Colonne A au format **Texte brut** (Format → Nombre → Texte brut).
- Colonne D : validation de données, liste « à publier, publié, annulé ».
- Envoyer l'identifiant du Sheet (dans l'URL, entre `/d/` et `/edit`) à Claude pour qu'il crée la routine.

## 3. Scénario Make « Avant de Construire - Instagram + Facebook »

Planification : toutes les 30 minutes (ou toutes les heures de 8 h à 20 h pour économiser les opérations).

1. **Google Sheets › Search Rows** : le Sheet, onglet Posts, en-têtes en ligne 1, filtre `Statut` *Equal to* `à publier`, Maximum number of returned rows : 1, tri par colonne A croissant.
2. **Filtre** (sur le lien) « heure arrivée » — deux conditions (ET) :
   - `parseDate(A; "YYYY-MM-DD HH:mm"; "Europe/Paris")` *Datetime: Earlier than or equal to* `now`
   - `parseDate(A; "YYYY-MM-DD HH:mm"; "Europe/Paris")` *Datetime: Later than* `addHours(now; -3)` (évite de publier un vieux post en retard)
   - et `F` *Exists* (Instagram exige une image).
3. **Instagram for Business › Create a Photo Post** : compte Instagram relié, Photo URL = `F`, Caption = `C`.
4. **Facebook Pages › Create a Post with Photos** : page Avant de Construire, Photos → URL = `F`, Message = `C`.
5. **Google Sheets › Update a Row** : Row number = celui du module 1, `Statut` = `publié`, `Publié le` = `formatDate(now; "YYYY-MM-DD HH:mm"; "Europe/Paris")`.

Conseils :
- Clic droit sur le module Facebook → *Add error handler* → **Resume** : si Facebook échoue, la ligne passe quand même en « publié » et Instagram n'est pas republié au passage suivant.
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
