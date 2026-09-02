# CIV 2026 — Survey et orientations pour un hackathon Data open source

> État : proposition de cadrage, fondée sur les archives CIV 2025 disponibles localement et sur un panorama open source vérifié le 11 juillet 2026.

## Résumé exécutif

Le meilleur héritage du hackathon 2025 n'est pas l'interface ou le modèle de ressources de la solution X. C'est une boucle d'investigation reproductible :

1. explorer un enregistrement ROS 2 multimodal ;
2. identifier les signaux et les fenêtres temporelles utiles ;
3. formaliser une hypothèse de détection ;
4. exécuter cette logique sur plusieurs enregistrements ;
5. extraire des preuves compactes plutôt que transférer toutes les données ;
6. mesurer, visualiser et expliquer les résultats ;
7. relier le résultat à l'acquisition, à l'évaluation ou aux opérations d'un véhicule.

La recommandation pour 2026 est un format **« Data Detective — du bag à la preuve »** : un tronc commun proche de 2025, mais construit sur des fichiers et des contrats ouverts, puis trois niveaux d'approfondissement :

- **Signal** : détecter proprement un événement à partir de séries temporelles ;
- **Contexte** : corréler plusieurs modalités et produire une preuve visualisable ;
- **Agent** : utiliser un agent outillé pour investiguer, tout en conservant la provenance, les appels d'outils et une évaluation reproductible.

L'agentique doit être un accélérateur et un objet d'évaluation, pas une obligation pour réussir le cœur du challenge. Sinon, le concours mesure surtout l'accès aux modèles, la qualité des prompts et la chance, plutôt que la capacité à raisonner sur des données physiques.

La reconstruction minimale ne nécessite pas une nouvelle plateforme complète. Un kit open source ciblé suffit :

- un dataset MCAP préparé, avec manifeste, petit échantillon et vérité terrain partielle ;
- une CLI de référence pour inspecter, détecter, extraire et produire un rapport ;
- un format déclaratif d'événement indépendant de toute solution ;
- des sorties JSON/Parquet et des clips MCAP ;
- une visualisation locale ;
- un évaluateur automatique ;
- éventuellement un serveur d'outils pour les agents.

## 1. Périmètre et sources examinées

### Sources locales principales

Les documents suivants ont servi à reconstituer l'expérience 2025 et son évolution v2 :

- `data-hackathon-01-brainstorming.md` : objectifs initiaux CIV 2026 ;
- `Smart-Data Hackathon v1 (CIV 2025) - Main portal/...Participant page...md` : scénario, parcours, livrables et notation remis aux participants ;
- `Smart-Data Hackathon v1 (CIV 2025) - Main portal/...Organizer page...md` : données, sujets ROS, préparation, critères et correction ;
- `Smart-Data Hackathon v2 - Organizer Page...md` et `...Participant Main Session...md` : version plus guidée, orientée CLI et visualisation ;
- `Smart-Data Hackathon - Participants’ Feedback...md` : retours manuels, problèmes de workflow, de CLI, de replay et d'environnement ;
- `Smart-Data Hackathon v2 - Upgrading effort from v1 to v2...md` : intentions explicites de simplification ;
- `Internal Notes on Dataset from Tokyo University...md` : contenu technique, dépendances de messages et piste d'évaluation automatique ;
- `heex-samples/02-hackathon-urt-kashiwa-demo/` : instructions, correction et automatisation de référence ;
- `CIV2025 - Mail for Hackathon + CIV 2025 invite...md` : contraintes matérielles et préparation demandée.

Ces archives ne sont pas recopiées ici. Elles sont utilisées pour identifier des objectifs, des étapes, des points de friction et des interfaces fonctionnelles.

### Source de données publique

Le dépôt officiel [URT-Kashiwa](https://github.com/tlab-wide/URT-Kashiwa) décrit 16 routes enregistrées avec une plateforme Pixkit 3.0 sur le campus de Kashiwa, avec un piéton et un véhicule opposé, sous forme de rosbags ROS 2 Humble. Il documente des sujets de sensing, localisation, perception, planning et diagnostic.

Avant de republier ou redistribuer les données dans un kit CIV 2026, il faut toutefois effectuer une **revue explicite de la licence du dataset, des consentements et des éventuels droits sur les images**. Le fait qu'un dépôt GitHub soit public ne suffit pas, à lui seul, à autoriser tous les usages et redistributions.

## 2. Ce que faisait réellement le hackathon 2025

### 2.1 Le scénario pédagogique

Les participants jouaient le rôle d'une équipe ADAS devant analyser 16 enregistrements de 2 à 3 minutes, environ 7 Go et 400 000 messages chacun. Les situations recherchées étaient :

- freinage d'urgence ;
- virage non protégé ;
- virage avec véhicule arrivant en face ;
- virage avec piéton présent ;
- traversée de piéton en bonus.

Le problème métier était bien formulé : rechercher manuellement ces situations dans plusieurs heures de données multimodales est lent ; une logique événementielle permet de réduire le volume à examiner et d'accélérer la boucle `apprendre → corriger → valider`.

### 2.2 La chaîne de travail

La version 2025 demandait de :

1. préparer un environnement ROS 2, Docker et parfois une VM ou WSL ;
2. obtenir environ 110 Go de données, souvent par SSD ;
3. explorer les bags et les topics ;
4. représenter le véhicule et la source de données dans la solution X ;
5. choisir des champs de messages comme signaux ;
6. créer des conditions simples puis combinées ;
7. rejouer tous les bags pour générer des événements et des enregistrements ;
8. compter les événements et calculer quelques statistiques ;
9. expliquer l'utilité des détecteurs pour l'acquisition, l'évaluation et les opérations.

La v2 a amélioré ce parcours en mettant la visualisation au début, en favorisant une solution CLI scriptable, en conservant les sorties JSON et en ajoutant un chemin optionnel pour les messages Autoware/Tier4 personnalisés.

### 2.3 Les capacités fonctionnelles de la solution X

Les archives font apparaître neuf capacités, indépendamment de leur présentation dans le produit :

| Capacité | Rôle dans l'expérience | Remplacement CIV 2026 |
|---|---|---|
| Inventaire des données | Lister topics, schémas, fréquence et durée | MCAP CLI, `ros2 bag info`, index généré |
| Sélection de champs | Transformer un champ ROS en série exploitable | Lecteur MCAP/rosbag et registre de chemins |
| Définition d'événements | Comparaisons, seuils et logique AND | Petit DSL YAML/JSON ou API Python |
| Liaison au dataset | Appliquer la même recette à plusieurs bags | Manifeste de dataset et glob de fichiers |
| Replay/batch | Exécuter les détecteurs sur les 16 routes | Runner local déterministe |
| Fenêtre de contexte | Conserver les données autour du déclenchement | Extraction MCAP par intervalle et topics |
| Catalogue d'événements | Nom, temps, détecteur, contexte, provenance | JSONL/Parquet avec schéma versionné |
| Analyse | Fréquences et statistiques par scénario | Polars/DuckDB/Pandas + notebook ou rapport |
| Reproductibilité | Script de configuration et d'exécution | Dépôt d'équipe, conteneur et commande unique |

Le modèle propriétaire `System → Datasource → Signal → Trigger → Event` n'est pas une exigence pédagogique. Pour 2026, il peut être remplacé par des concepts plus proches des artefacts réels : `Dataset → Channel/Field → EventSpec → Detection → EvidenceWindow → Report`.

## 3. Enseignements des retours 2025

### 3.1 Ce qui a fonctionné

- Le scénario était concret et crédible pour l'automobile autonome.
- La visualisation préalable faisait comprendre la valeur du triage événementiel.
- Les équipes pouvaient progresser d'un seuil simple vers une corrélation de signaux.
- Le résultat final était démontrable : événements, fréquences, extraits et explication métier.
- Une grande partie de la notation pouvait être automatisée grâce aux sorties structurées.

### 3.2 Ce qui a consommé le temps sans servir l'apprentissage

- installation de ROS, Docker, WSL ou Multipass ;
- montage de dossiers et copie d'environ 110 Go ;
- téléchargement simultané d'outils par une vingtaine de personnes ;
- compilation ou import de nombreux messages ROS personnalisés ;
- authentification, API keys et confusion entre workspaces ;
- création d'entités dans un ordre imposé par le produit ;
- incohérences entre noms de champs dans le visualiseur et dans la plateforme.

### 3.3 Les échecs à transformer en exigences 2026

| Retour 2025 | Exigence CIV 2026 |
|---|---|
| Échecs silencieux lors du replay | Préflight, erreurs actionnables, code de sortie non nul et journal local |
| Aucun aperçu avant création des événements | Commande `dry-run` donnant compte, temps et exemples sans écrire d'artefacts finaux |
| Difficile de savoir quel détecteur a créé un événement | Provenance obligatoire : version de la spec, paramètres, commit et input |
| Difficulté à retrouver le bon topic/champ | Index consultable et recherche sémantique facultative |
| Multi-bags peu ergonomique | Traitement batch natif et reprise après erreur |
| Messages personnalisés fragiles | Schémas embarqués ou image précompilée ; aucun build le jour J |
| Instructions dispersées | Une seule page de départ et une première détection guidée |
| Dashboards dépendants du temps courant | Temps du dataset et temps d'exécution explicitement séparés |
| Cache et réseau insuffisants | Bundle testé hors ligne et miroir local des images/dépendances |

## 4. Principes de conception proposés

1. **File-first.** Les entrées, spécifications et sorties sont des fichiers portables, inspectables et versionnables.
2. **Local-first.** Le cœur du parcours fonctionne sans compte SaaS et sans réseau après installation.
3. **Evidence-first.** Une détection sans fenêtre de preuve, contexte et provenance n'est pas un résultat complet.
4. **Progressive disclosure.** Un bag d'échauffement et un signal standard avant le dataset complet et les messages personnalisés.
5. **Deterministic core.** La CLI et l'évaluateur doivent donner le même résultat sur la même entrée.
6. **Agent optional, trace required.** Un agent peut explorer et proposer, mais chaque conclusion doit pointer vers les commandes, données et fenêtres qui la supportent.
7. **No hidden platform points.** La notation porte sur le résultat et le raisonnement, pas sur la création d'objets propres à un produit.
8. **Quality over event count.** Les faux positifs, faux négatifs, doublons et instabilités de seuil comptent autant que la capacité à produire un événement.
9. **Portable outputs.** JSONL/Parquet pour les tables, MCAP pour les extraits, Markdown/HTML pour le rapport.
10. **One-command golden path.** Après le warm-up, une commande documentée doit permettre de rejouer la solution complète.

## 5. Trois orientations possibles

### Option A — Smart Data open source

La version la plus proche de 2025. Les équipes inspectent les bags, écrivent des règles, les exécutent sur tout le dataset et produisent des clips événementiels.

**Forces**

- continuité claire avec 2025 ;
- faisable en trois heures ;
- notation objective ;
- investissement d'organisation limité.

**Limites**

- risque de rester sur des seuils simples ;
- peu de différenciation entre les équipes fortes ;
- agentique et data quality seulement en bonus.

### Option B — Data Detective multimodal

Les équipes reçoivent une question, pas une recette. Elles doivent construire un dossier de preuve : signaux, fenêtres, qualité des données, hypothèse, détecteur, métriques, visualisation et limites.

**Forces**

- mesure réellement l'investigation et le raisonnement ;
- permet des approches signal, vision, localisation ou diagnostic ;
- valorise la visualisation et la communication ;
- offre des niveaux de difficulté naturels.

**Limites**

- nécessite une vérité terrain partielle ;
- la grille de notation doit accepter plusieurs bonnes solutions ;
- demande un kit d'évaluation plus soigné.

### Option C — AgentOps Black Box pour véhicule coopératif

Les équipes construisent ou observent un agent qui enquête sur des logs/MCAP. Elles doivent enregistrer ses appels d'outils, preuves, erreurs, coûts/latences éventuels, puis créer un test de régression.

**Forces**

- angle distinctif et très actuel ;
- relie agents, MCP/outils, observabilité, évaluation et gouvernance ;
- démonstration finale spectaculaire.

**Limites**

- risque de dériver vers un concours de framework ou de modèle ;
- dépendance possible au réseau ou au GPU ;
- maturité inégale des conventions d'observabilité agentique ;
- plus difficile à rendre équitable en trois heures.

### Comparaison

| Critère | A — Smart Data OSS | B — Data Detective | C — AgentOps Black Box |
|---|---:|---:|---:|
| Fidélité à 2025 | Forte | Moyenne à forte | Faible à moyenne |
| Valeur pédagogique data | Bonne | Excellente | Moyenne à bonne |
| Différenciation des équipes | Moyenne | Forte | Forte |
| Risque technique organisateur | Faible | Moyen | Fort |
| Faisable en 3 h | Oui | Oui, bien cadré | Seulement en stretch |
| Besoin de calcul IA | Nul | Optionnel | Important |
| Facilité d'évaluation | Forte | Moyenne | Moyenne à faible |

### Recommandation

Choisir **B comme format principal**, avec **A comme warm-up et socle technique**, puis **C comme niveau bonus**. Cette composition conserve l'expérience réussie de 2025, augmente l'exigence d'analyse et permet l'agentique sans rendre la réussite dépendante d'un LLM.

## 6. Expérience recommandée : « Data Detective — du bag à la preuve »

### Brief participant

> Une flotte de véhicules coopératifs a enregistré plusieurs passages d'une intersection. Un comportement à risque a été signalé, mais le rapport est incomplet. Votre équipe doit retrouver les occurrences pertinentes, produire des extraits de preuve, mesurer la qualité de son détecteur et proposer comment cette logique serait utilisée à l'acquisition, en validation et en exploitation.

### Déroulé de référence sur 3 h 30

| Temps | Étape | Résultat observable |
|---|---|---|
| 0:00–0:20 | Démarrage commun | Environnement validé, bag d'exemple ouvert |
| 0:20–0:45 | Warm-up guidé | Première détection et premier clip |
| 0:45–1:20 | Exploration libre | Hypothèse, signaux choisis, fenêtres annotées |
| 1:20–2:05 | Détecteur batch | `events.jsonl` sur les bags de développement |
| 2:05–2:35 | Qualité et robustesse | Métriques, cas limites, test sur bag caché |
| 2:35–3:05 | Visualisation/preuve | Dashboard ou vue synchronisée d'un événement |
| 3:05–3:30 | Pitch | Reproduction en une commande et limites assumées |

Si le créneau reste strictement de trois heures, fournir le détecteur du warm-up déjà exécuté et limiter la soutenance à trois minutes par équipe.

### Niveaux de difficulté

#### Niveau 1 — Signal

- trouver un champ pertinent ;
- justifier une transformation et un seuil ;
- gérer durée minimale, hystérésis et fusion de doublons ;
- extraire une fenêtre avant/après.

#### Niveau 2 — Contexte

- combiner deux modalités ou plus ;
- distinguer corrélation temporelle et causalité ;
- détecter une donnée manquante ou un capteur incohérent ;
- montrer la situation dans une visualisation synchronisée.

#### Niveau 3 — Agent

- donner à un agent des outils de lecture limités et documentés ;
- faire produire à l'agent une hypothèse puis la valider par exécution ;
- conserver trace, paramètres, sources et résultats d'outils ;
- écrire un test où l'agent ou le workflow échouait initialement.

## 7. Architecture fonctionnelle minimale

```text
MCAP + manifest + partial ground truth
                 |
                 v
        inspect / index / sample
                 |
                 v
       EventSpec YAML or Python API
                 |
                 v
       deterministic batch detector
          |          |           |
          v          v           v
    events.jsonl  clips.mcap  run-manifest.json
          |          |           |
          +----------+-----------+
                     v
          metrics + report + visualization
                     |
                     v
          optional agent tool server
```

### Composants à fournir par l'organisation

#### 1. Bundle de données

- `sample/` : un fichier court pour le warm-up ;
- `dev/` : plusieurs bags avec labels partiels ;
- `test/` : bags cachés ou labels cachés ;
- `manifest.yaml` : fichiers, hash, durée, taille, topics et scénario ;
- `labels/` : intervalles temporels, classe, confiance et notes organisateur ;
- layouts de visualisation déjà testés.

#### 2. CLI de référence

Une petite CLI spécifique au hackathon peut être construite sans recréer une plateforme :

```text
civ doctor                  # valide le poste, les fichiers et les schémas
civ inspect BAG             # inventaire et statistiques
civ sample BAG --topic ...  # extrait quelques valeurs
civ detect SPEC DATASET     # dry-run ou exécution batch
civ clip EVENTS DATASET     # produit les fenêtres de preuve
civ score SUBMISSION        # évalue le format et les métriques
civ report SUBMISSION       # génère un rapport local
```

Le cœur doit être open source, documenté, versionné et remplaçable. Il peut orchestrer des outils existants plutôt que réimplémenter le format MCAP.

#### 3. Format d'événement

Un contrat ouvert évite de reproduire les entités de la solution X. Exemple conceptuel :

```yaml
apiVersion: civ.dev/v1alpha1
kind: EventSpec
metadata:
  name: hard-braking-context
spec:
  inputs:
    longitudinal_acceleration: /some/topic.some.field
    ego_speed: /some/other/topic.some.field
  preprocessing:
    - median_window: 5
  condition:
    all:
      - longitudinal_acceleration: {lt: "team-derived-value"}
      - ego_speed: {gt: "team-derived-value"}
  debounce: 1s
  evidenceWindow: {before: 4s, after: 6s}
```

Les seuils de l'ancienne correction ne doivent pas être transplantés. Ils doivent être retrouvés sur les données publiques/de développement, justifiés et testés sur un jeu séparé.

#### 4. Artefacts de sortie

Chaque événement devrait au minimum contenir :

- identifiant stable ;
- classe et score/confiance ;
- fichier source et hash ;
- temps de début, pic et fin dans l'horloge du bag ;
- version de l'EventSpec et commit de l'équipe ;
- signaux et valeurs ayant déclenché la décision ;
- fenêtre de contexte ;
- chemin vers le clip MCAP ;
- outil ou agent ayant produit la décision ;
- avertissements de qualité.

#### 5. Évaluateur

L'évaluateur doit distinguer :

- validité du format ;
- reproductibilité ;
- précision/rappel ou IoU temporelle sur labels cachés ;
- taux de doublons ;
- robustesse à des données manquantes ;
- coût de traitement et volume extrait ;
- qualité de la preuve et de l'explication.

## 8. Briques open source à privilégier

Le panorama détaillé et ses licences sont dans [open-source-landscape-research.md](./open-source-landscape-research.md). Le socle recommandé est volontairement court :

| Besoin | Premier choix | Raison |
|---|---|---|
| Format et opérations fichier | MCAP et MCAP CLI | Format adapté aux données robotiques, inspection, filtrage et récupération |
| Compatibilité ROS 2 | `rosbag2_storage_mcap` | Utilise MCAP avec les commandes `ros2 bag` standard |
| Visualisation temporelle | PlotJuggler 3 | Très bon pour les séries, transformations et corrélations ; garder v4 en option tant qu'elle est annoncée bêta |
| Visualisation robotique | Lichtblick | Rejeu MCAP, images, transforms, point clouds et layouts ; cœur MPL-2.0/open-core, version à figer |
| Visualisation multimodale avancée | Rerun | Timeline synchronisée pour images, point clouds, transforms et séries ; extension optionnelle à figer car le projet évolue vite |
| Tables analytiques | Polars ou DuckDB, Parquet | Local, rapide, scriptable, facile à noter |
| Rapport/dashboard | Panel ou Streamlit selon prototype | Démonstration locale à faible friction ; ne retenir qu'un framework dans le kit |
| Agent Python | LangGraph | Graphe d'états, checkpoints et validation humaine des appels d'outils |
| Modèle local optionnel | llama.cpp ou Ollama | Exécution locale, mais modèle et licence à valider séparément |
| Traces et évaluation | OpenTelemetry + MLflow ou Evidently | Contrat de trace indépendant du framework, sans imposer toute une plateforme d'observabilité |
| Exécution locale | Podman ou Docker Engine | Images OCI préconstruites ; distinguer Docker Engine OSS de Docker Desktop propriétaire |

Points déjà vérifiés dans les sources officielles :

- le [MCAP CLI](https://mcap.dev/guides/cli) sait notamment inspecter, filtrer, convertir, compresser, trier et récupérer des fichiers ;
- le plugin officiel [`rosbag2_storage_mcap`](https://docs.ros.org/en/humble/p/rosbag2_storage_mcap/) permet d'utiliser MCAP via les commandes `ros2 bag` et documente les compromis d'indexation/compression.

Une règle de gouvernance est nécessaire : **« dépôt public » ne veut pas dire automatiquement « open source »**. Chaque brique retenue doit avoir une licence explicite compatible avec la distribution du kit ; les fonctions commerciales, cloud ou source-available doivent être séparées du chemin obligatoire.

## 9. Agentique : une progression utile plutôt qu'un chatbot

### Outils exposés à l'agent

Un agent n'a pas besoin d'un accès arbitraire au shell. Un serveur d'outils restreint peut fournir :

- `list_bags()` ;
- `describe_bag(path)` ;
- `search_topics(query)` ;
- `sample_signal(path, field, interval)` ;
- `plot_signals(fields, interval)` ;
- `run_event_spec(spec, files, dry_run=true)` ;
- `extract_evidence(event_ids)` ;
- `score_predictions(predictions)`.

Ces outils sont suffisamment puissants pour une investigation, tout en rendant les actions auditables et reproductibles.

### Ce qui doit être évalué

- l'agent cite-t-il les données qu'il a réellement inspectées ?
- distingue-t-il une hypothèse d'un résultat exécuté ?
- détecte-t-il l'absence ou la mauvaise qualité d'un signal ?
- sait-il réduire son espace de recherche plutôt que lire tout le dataset ?
- produit-il une EventSpec et des tests déterministes ?
- son résultat résiste-t-il à un bag caché ?

### Anti-patterns

- demander directement au LLM « quels sont les bons timestamps ? » ;
- accepter un résultat sans appel d'outil ni preuve ;
- noter le style du prompt plutôt que la qualité du détecteur ;
- imposer un modèle payant ou une clé personnelle ;
- confondre trace agentique et logs verbeux non structurés.

## 10. Proposition de notation

### Tronc commun — 100 points

| Catégorie | Points | Critères |
|---|---:|---|
| Investigation et hypothèse | 15 | Choix des signaux, exploration et justification |
| Détection | 25 | Exactitude, logique temporelle, gestion des doublons |
| Preuve et extraction | 15 | Clips corrects, contexte utile, réduction du volume |
| Qualité et évaluation | 15 | Métriques, faux positifs/négatifs, cas limites |
| Visualisation et explication | 15 | Lisibilité, synchronisation, décision métier |
| Reproductibilité | 15 | Commande unique, manifest, logs, environnement |

### Bonus — jusqu'à 20 points

- agent outillé avec traces exploitables : 10 ;
- détection multimodale ou qualité de données avancée : 5 ;
- test de régression sur un échec trouvé pendant le hackathon : 5.

Le bonus ne compense pas un détecteur non reproductible.

## 11. Protocole de clean-room engineering

Il faut distinguer deux ambitions :

- **remplacement fonctionnel indépendant** : écrire un nouvel outil sans reprendre le code de la solution X ;
- **clean room stricte** : pouvoir démontrer que les personnes qui implémentent n'ont reçu qu'une spécification comportementale autorisée et aucune expression protégée du produit d'origine.

Ce survey a consulté des archives internes et des scripts de démonstration. Il peut donc servir à la **spécification fonctionnelle**, mais la même conversation et les mêmes personnes ne devraient pas être présentées comme une équipe d'implémentation « aveugle » si une garantie juridique forte est recherchée.

### Processus proposé

1. **Valider les droits** sur chaque source interne, le dataset, les layouts, noms et exemples.
2. **Équipe spécification** : produire uniquement comportements observables, entrées, sorties, contraintes et tests d'acceptation.
3. **Revue IP/juridique** : retirer code, commandes propriétaires, identifiants, textes, captures et seuils provenant de la correction historique.
4. **Gel de la spec** : publier un document propre avec une matrice de traçabilité vers des besoins pédagogiques ou des standards publics.
5. **Équipe d'implémentation séparée** : construire depuis la spec, les standards ROS/MCAP et le dataset autorisé.
6. **Journal de provenance** : licences, dépendances, auteurs, sources consultées et décisions.
7. **Tests black-box** : vérifier les comportements attendus sans comparer le code ou l'UI à la solution X.

La directive européenne 2009/24/CE permet, sous conditions, à l'utilisateur légitime d'observer, étudier ou tester le fonctionnement d'un programme, et encadre plus strictement la décompilation nécessaire à l'interopérabilité. Cela ne remplace pas l'analyse des contrats, secrets d'affaires, droits sur les données et licences applicables. Voir le [texte officiel EUR-Lex](https://eur-lex.europa.eu/legal-content/FR/TXT/?uri=CELEX%3A32009L0024). Ce document n'est pas un avis juridique.

## 12. Roadmap de préparation

### Phase 0 — Décisions de cadrage

- durée réelle et nombre d'équipes ;
- niveau ROS/Python attendu ;
- GPU disponible ou non ;
- dataset redistribuable ou accessible seulement sur place ;
- place de l'agentique dans la notation ;
- définition de « open source » retenue par l'organisation.

### Phase 1 — Spike de faisabilité

- prendre un seul bag public ;
- vérifier lecture, schémas personnalisés et visualisation sur les OS ciblés ;
- détecter un événement simple ;
- extraire un clip ;
- produire `events.jsonl` et un rapport ;
- mesurer temps, RAM, disque et taille de l'image.

**Go/no-go :** le chemin complet doit fonctionner hors ligne sur la machine minimale prévue.

### Phase 2 — Golden path

- écrire `civ doctor` ;
- préparer le sample de moins de quelques Go ;
- figer le schéma EventSpec ;
- créer une détection de référence indépendante ;
- fournir une seule page de démarrage ;
- tester Windows/WSL et Ubuntu au minimum.

### Phase 3 — Dataset et évaluation

- produire les labels partiels et cachés ;
- définir les tolérances temporelles ;
- tester les métriques sur plusieurs implémentations ;
- injecter un ou deux défauts de données documentés ;
- préparer la soumission et le scoring hors ligne.

### Phase 4 — Agent et visualisation

- exposer les outils de lecture restreints ;
- choisir un petit modèle local de référence si le matériel le permet ;
- tracer les appels et relier chaque conclusion à une fenêtre ;
- préparer un exemple d'agent qui échoue puis un test de régression.

### Phase 5 — Répétition générale

- fresh install sur machines propres ;
- test sans Internet ;
- test avec 25 participants simultanés ;
- test des SSD, câbles et copies par lot ;
- chronométrage du warm-up ;
- exercice de secours avec fichiers déjà extraits si ROS ou Docker échoue.

## 13. MVP à construire

Le MVP n'est pas une plateforme. Il contient seulement :

1. un sample MCAP ;
2. un manifeste de dataset ;
3. `civ doctor`, `inspect`, `detect`, `clip` et `score` ;
4. une EventSpec versionnée ;
5. un layout de visualisation ;
6. une correction et un jeu de labels caché ;
7. une image ou un bundle local ;
8. une soumission d'exemple reproductible.

À reporter après le premier prototype : interface web multi-utilisateur, catalogue persistant, gestion des comptes, déploiement edge réel, OTA et orchestration de flotte. Ces fonctions sont intéressantes, mais elles ne sont pas nécessaires pour valider l'expérience pédagogique.

## 14. Décisions recommandées maintenant

1. Valider le format hybride **A → B → C bonus**.
2. Confirmer un créneau de 3 h 30 ou réduire le scope à trois bags de développement.
3. Faire la revue licence/données d'URT-Kashiwa avant toute préparation publique.
4. Lancer un spike sur un bag avec MCAP CLI, PlotJuggler et un lecteur Python.
5. Concevoir la vérité terrain et le score avant de développer l'interface.
6. Écrire une spécification propre indépendante de X avant toute implémentation prétendant au clean-room.
7. Ne retenir qu'une visualisation principale et une pile agentique de référence pour limiter le support.

## Conclusion

CIV 2026 peut dépasser l'expérience 2025 sans reconstruire une solution SaaS disparue. La meilleure évolution consiste à déplacer le centre de gravité : de la création d'entités dans un produit vers la production d'une **preuve data compacte, explicable, évaluée et reproductible**.

Le fil rouge reste le même — trouver l'aiguille dans la botte de foin — mais le niveau supérieur devient : prouver que l'aiguille est bien la bonne, expliquer comment elle a été trouvée, mesurer ce qui a été manqué et permettre à un humain ou à un agent de rejouer exactement l'enquête.
