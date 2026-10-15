# Prompts Claude Design

À envoyer **dans l'ordre, dans le même projet**, avec `DESIGN.md` joint au prompt 0.
Chaque prompt s'appuie sur le précédent : ne passe au suivant que quand le rendu te convient.

---

## Prompt 0 — Charte graphique

```
Voici le DESIGN.md de mon projet. Construis-en la charte graphique : couleurs, typographie,
espacements, rayons, ombres et composants de base (boutons, champs, cartes, bulles). On
s'en servira pour tous les écrans qui suivent.
```

---

## Prompt 1 — Cadrage et page complète (desktop)

```
Je conçois le front d'un projet open source de démonstration : un support client e-commerce
« agentique ». Respecte strictement la charte graphique qu'on vient d'établir.

## L'idée
Au lieu du formulaire de support classique (un énorme formulaire plein de champs), le client
discute avec un agent qui le guide pas à pas, et l'interface se compose sous ses yeux au fil de
l'échange : chaque question de l'agent apporte le bon contrôle (boutons, envoi de photo, champ
texte) au bon moment.

L'ergonomie s'inspire d'une conversation sur claude.ai (colonne de lecture centrée, beaucoup
d'air, zone de saisie en bas) — l'ergonomie seulement : ni le logo, ni les couleurs, ni le nom
de Claude. L'agent a sa propre identité (voir plus bas) et ne doit pas se faire passer pour
Claude.

## Contexte simulé
- Une boutique en ligne fictive ; le client y est déjà connecté. Propose un nom de boutique
  sobre et crédible.
- Une seule page : la page support. Pas de navigation, pas de connexion, pas de liste de
  commandes.
- En-tête discret : nom de la boutique à gauche, identité du client à droite (nom + avatar,
  ex. « Camille Martin »).

## Mise en page desktop
- À gauche : un panneau « Récap » (nom à affiner) qui résume ce qui s'est passé dans la
  conversation. Pour ce prompt, mets un contenu simple ; on le travaillera au prompt 4.
- Au centre : le fil de la conversation.
- En bas : la zone de saisie.

## Deux écrans
1. Écran d'accueil (aucune conversation) : un seul champ « Expliquez-nous votre problème »,
   texte libre, 2000 caractères maximum, bouton d'envoi. Rien d'autre qu'un court mot
   d'accueil de l'agent. Pas de panneau Récap à ce stade (ou vide).
2. Conversation en cours : le fil complet ci-dessous.

## Types de messages (c'est le contrat de l'API, chaque type a son rendu)
- USER : texte libre du client (bulle client).
- ASSISTANT et ASSISTANT_GEN : texte de l'agent. AUCUNE différence visuelle entre les deux.
- ASSISTANT_ACTION : l'agent demande une action → une petite carte soignée dans le fil.
  Types d'action : UNIQUE_CHOICE (une option parmi N), YES_NO (confirmer une valeur affichée
  dans la carte), PHOTO_UPLOAD (envoyer une photo), TEXT_INPUT (pas de carte : c'est la zone
  de saisie du bas qui s'active).
- USER_ACTION_RESPONSE : la réponse du client à une action (bulle client : le libellé du
  choix, « Oui »/« Non », la photo en vignette, ou le texte tapé).
- END : dernier message de l'agent ; la conversation est terminée.

Règle importante : la zone de saisie du bas n'est active que quand l'action en attente est
TEXT_INPUT. Pour toute autre action, elle est grisée (avec un indice du type « Répondez
dans la carte ci-dessus ») et c'est la carte qui porte la réponse.

Pas d'horodatage sur les messages (l'API n'en fournit pas).

## Scénario à afficher (textes réels de l'API)
USER : « Bonjour, j'ai reçu mon colis ce matin et la lampe est arrivée cassée, le pied est
fendu. »
ASSISTANT : « Pour être sûr de bien comprendre, votre demande concerne : »
ACTION UNIQUE_CHOICE : « Annuler ma commande » / « Ma commande est arrivée abîmée » /
« Autre chose » → répondu : « Ma commande est arrivée abîmée »
ASSISTANT : « C'est noté. »
ASSISTANT : « Quel est votre numéro de commande ? »
ACTION TEXT_INPUT → répondu : « CMA_48213 »
ASSISTANT : « Merci, j'ai bien votre numéro de commande. »
ASSISTANT : « Envoyez-nous une photo du produit abîmé, s'il vous plaît. »
ACTION PHOTO_UPLOAD → répondu : une photo (vignette)
ASSISTANT : « Voici ce que je vais transmettre au support. Est-ce correct ? »
ACTION YES_NO, valeur à confirmer (texte de plusieurs lignes, rédigé par l'agent) :
  « Commande CMA_48213 — Lampe de bureau Arco. Produit reçu endommagé : le pied en
  céramique est fendu sur toute la hauteur, la lampe ne tient plus droite. Photo jointe. »
→ en attente de réponse (c'est l'état actuel de l'écran).

Livre un prototype HTML interactif : on peut rejouer le scénario du début, choisir dans les
cartes, et voir le fil se construire.
```

---

## Prompt 2 — Les cartes d'action et leurs états

```
Travaillons les cartes d'action, cœur de l'expérience. Fais une planche qui montre chaque
carte dans tous ses états, puis intègre-les au prototype.

États communs à toutes les cartes :
- en attente : la carte est active, c'est elle qui attend le client ;
- envoi en cours : le client a répondu, l'appel API part (peut durer plusieurs secondes) ;
  la carte ne doit plus être cliquable ;
- répondue : la carte reste figée dans le fil, le choix fait est mis en évidence, les autres
  options sont grisées. On ne peut pas revenir en arrière.

UNIQUE_CHOICE : 2 à 5 options aux libellés de longueur variable. Exemples réels :
« Annuler la commande » / « Changer l'adresse de livraison » / « Changer le mode de
livraison », ou « À domicile » / « En point relais » / « Retrait en magasin ».

YES_NO : la carte affiche une valeur à confirmer, puis « Oui » / « Non ». La valeur peut
être courte (une adresse : « 12 rue des Lilas, 69003 Lyon ») ou longue (un compte rendu de
5-6 lignes). Prévois les deux.

PHOTO_UPLOAD : sélection d'un fichier image (pas de prise de vue caméra), aperçu de la
photo avant l'envoi avec possibilité de changer de photo, puis bouton d'envoi. Prévois
l'état « photo trop lourde » (au-delà de ~7 Mo).

TEXT_INPUT : pas de carte. Montre la zone de saisie du bas dans ses états : active (avec
placeholder), grisée (une carte attend une réponse), envoi en cours, masquée/bloquée en fin
de conversation.

Les cartes doivent apparaître avec une entrée animée discrète : l'interface « se compose »
sous les yeux du client. Reste sobre, pas de rebond appuyé.
```

---

## Prompt 3 — L'agent vivant

```
Donnons de la vie à l'agent.

1. Identité : propose 3 pistes d'identité visuelle pour l'agent (nom, avatar ou emblème,
   manière de signer ses messages). Mieux qu'un simple point animé, mais sans imiter Claude
   ni aucun assistant existant. Cohérent avec le DESIGN.md.

2. « L'agent réfléchit » : l'API ne streame pas ; un tour peut prendre de 1 à 8 secondes
   (appel à un LLM). Conçois l'animation affichée pendant ce temps, liée à l'identité de
   l'agent.

3. Arrivée des messages : quand l'API répond, 2 à 4 messages arrivent d'un coup (ex. « C'est
   noté. » + « Quel est votre numéro de commande ? » + l'action). Ils s'affichent un par un
   avec un court délai, l'animation de réflexion faisant la liaison entre eux. La carte
   d'action arrive en dernier, et seulement alors la zone de saisie change d'état.

Montre la séquence complète dans le prototype : envoi du client → réflexion → messages un
par un → carte.
```

---

## Prompt 4 — Le panneau Récap, deux versions

```
Le panneau de gauche résume ce qui a été fait, sans devoir remonter le fil. Génère deux
versions côte à côte pour que je choisisse. Dans les deux : cliquer un élément fait défiler
la conversation jusqu'au message correspondant (et le met brièvement en évidence).

Version A — Journal (ce que l'API fournit aujourd'hui)
La liste des questions posées et des réponses données, dans l'ordre : chaque question de
l'agent ayant appelé une action, suivie de la réponse du client (libellé du choix, Oui/Non,
vignette de la photo, texte tapé). Puis le message de fin si la conversation est terminée.
Avec le scénario du prompt 1 :
- Votre demande concerne → Ma commande est arrivée abîmée
- Numéro de commande → CMA_48213
- Photo du produit abîmé → [vignette]
- Compte rendu à transmettre → en attente

Version B — Dossier (évolution future de l'API, données à simuler)
- En titre : le problème identifié, en libellé client : « Colis endommagé ».
- Un statut : « En cours » / « En attente de votre réponse » / « Résolu ».
- Les étapes franchies en frise verticale, libellés lisibles (« Demande identifiée »,
  « Commande retrouvée », « Photo reçue »…). Pas d'étapes futures : le parcours se décide
  au fil des réponses.
- Les informations recueillies sous forme de fiche : commande, produit, photo en vignette,
  compte rendu, confirmation.

Montre chaque version dans 3 moments : début de conversation, milieu, conversation terminée.
```

---

## Prompt 5 — Erreurs, fin et cas limites

```
Couvrons les états hors du chemin heureux.

1. Erreur pendant un tour (500) : une bulle d'erreur temporaire dans le fil (« Un problème
   est survenu, vous pouvez réessayer. »), puis la dernière action est proposée à nouveau
   pour réessayer. La bulle n'est pas un message de l'agent : elle doit se distinguer
   clairement sans être alarmante.
2. Erreur à l'ouverture : le premier message n'a pas pu être envoyé depuis l'écran
   d'accueil ; le texte tapé est conservé.
3. Conversation introuvable : le client recharge une URL de conversation qui n'existe plus.
   Message clair + bouton « Nouvelle demande ».
4. Fin de conversation (END, ex. « Votre signalement est transmis au support : nous revenons
   vite vers vous. » puis « Merci, bonne journée ! ») : la zone de saisie disparaît, un
   bouton « Nouvelle demande » apparaît, le Récap passe à l'état terminé.
5. Contenus extrêmes : premier message du client de 2000 caractères, conversation de 30
   messages, libellé de choix très long.
6. Conversation en anglais : les messages de l'agent arrivent en anglais (traduits par
   l'API), les textes de l'interface restent en français.
```

---

## Prompt 6 — Mobile

```
Déclinons tout en mobile (375 px de large).
- Le fil prend toute la largeur ; la zone de saisie reste collée en bas, au-dessus du
  clavier.
- Le panneau Récap se replie en un petit onglet sur le bord gauche ; un tap l'ouvre en
  tiroir par-dessus la conversation. Cliquer un élément ferme le tiroir et fait défiler
  jusqu'au message.
- Les cartes d'action restent confortables au pouce (cibles ≥ 44 px), le sélecteur de
  photo ouvre la galerie.
Montre l'écran d'accueil, une conversation en cours avec une carte en attente, le tiroir
Récap ouvert (versions A et B), et la fin de conversation.
```
