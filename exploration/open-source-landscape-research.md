# Panorama open source pour le hackathon CIVE 2026

> État de la recherche : 11 juillet 2026. Sources limitées aux documentations, spécifications et dépôts officiels. Les appréciations de maturité sont des jugements d'ingénierie fondés sur la stabilité des interfaces, l'activité des versions et l'adoption visible ; ce ne sont pas des garanties de support.

## Résumé exécutif

Le hackathon 2025 faisait expérimenter une chaîne « données brutes → détection d'un événement → extraction d'une fenêtre utile → annotation → collecte sélective », à l'edge, plutôt qu'un téléversement intégral. Le brainstorming 2026 ajoute cinq attentes : ROS 2, données capteurs hétérogènes, analyse plus riche que la simple extraction, visualisation, et agents capables d'utiliser des outils de manière observable.

Cette fonction peut être reconstruite sans réimplémenter une plateforme entière. Le meilleur socle est :

1. **ROS 2 `rosbag2` + MCAP** comme preuve brute et format d'échange ;
2. **un petit moteur CIVE d'événements**, développé pour l'occasion, qui produit un manifeste explicite et des sous-bags MCAP ;
3. **DuckDB/Polars + SciPy/OpenCV** pour les analyses tabulaires, temporelles et visuelles ;
4. **PlotJuggler + Lichtblick** pour les signaux, le rejeu et la preuve robotique synchronisée ; Rerun reste une voie multimodale avancée ;
5. **LangGraph + outils Python/CLI, éventuellement exposés via MCP**, pour la piste agentique ;
6. **OpenTelemetry + MLflow ou Evidently** pour conserver traces, évaluations et régressions ;
7. **Podman ou Docker Engine, images préconstruites et versionnées par digest**, pour une exécution locale reproductible.

La recommandation pédagogique est un **tronc commun Smart Data OSS** suivi de trois voies optionnelles : détection de signaux, enquête multimodale, et « AgentOps Black Box ». Cela conserve le cœur du hackathon 2025 tout en récompensant ceux qui démontrent la qualité des preuves, la réduction de données, l'explicabilité et la reproductibilité — pas seulement ceux qui trouvent le bon timestamp.

### Pile minimale recommandée

Pour ne pas diluer le sujet robotique, le kit obligatoire devrait se limiter à :

```text
ROS 2 Jazzy (ou une seule distro LTS testée)
  + rosbag2_storage_mcap / MCAP CLI
  + Python scientifique (Polars ou DuckDB, SciPy, OpenCV si images)
  + moteur CIVE d'événements + JSON Schema
  + PlotJuggler pour les courbes
  + Lichtblick pour MCAP, images, transforms, point clouds et layouts
  + image OCI épinglée et tests de scoring
```

LangGraph/MCP, Rerun, MLflow et les dashboards web sont des **extensions de piste**, pas des prérequis du tronc commun. Tika n'est utile que si les organisateurs ajoutent volontairement un dossier documentaire hétérogène aux données ROS ; il ne fait pas partie du socle.

## 1. Fonction historique à remplacer

D'après `data-hackathon-01-brainstorming.md`, la capacité disparue ne se résume pas à une commande de découpage. Elle couvrait :

- l'ingestion de données de capteurs mixtes ;
- la détection d'événements au plus près de la source ;
- la sélection d'une fenêtre de contexte avant/après l'événement ;
- l'annotation de l'événement et de ses preuves ;
- la collecte d'un extrait plutôt que du fichier intégral ;
- un cycle répétable « trouver → comprendre → corriger → valider » ;
- la possibilité de modifier la logique de détection.

La cible clean-room doit donc être un **contrat de données et un pipeline composable**, non un clone de l'ancien produit :

```text
MCAP/rosbag brut
  -> inspection et normalisation
  -> détecteurs déterministes ou ML
  -> événement candidat + score + justification
  -> fenêtre temporelle et topics utiles
  -> annotation/provenance
  -> extrait MCAP + manifeste JSON + vues
  -> évaluation contre une vérité terrain cachée
```

Un manifeste minimal pourrait contenir `event_id`, `detector_id/version`, `start_ns`, `end_ns`, `topics`, `trigger_values`, `confidence`, `evidence`, `source_sha256`, `code_commit` et `created_at`. Il devient la frontière stable entre détecteurs, agents, visualisations et jury.

## 2. Ce que « open source » veut dire ici

Le code visible n'est pas automatiquement open source. La définition OSI exige notamment la libre redistribution, la possibilité de modifier et redistribuer les dérivés, et l'absence de restriction par domaine d'activité ([Open Source Definition](https://opensource.org/osd)). Dans ce document :

- **OSS réel** : licence approuvée OSI, par exemple MIT, Apache-2.0, BSD-3-Clause, MPL-2.0 ou AGPL-3.0 ;
- **open-core** : un cœur OSS, mais des services/fonctions d'équipe commerciaux autour ;
- **source-available** : code consultable sous une licence non OSI ou qui restreint certains usages.

AGPL-3.0 reste une vraie licence open source, mais son copyleft réseau demande une revue si l'outil modifié est fourni comme service. À l'inverse, Elastic License 2.0 interdit notamment de fournir une part substantielle du logiciel comme service hébergé ([texte ELv2 de Phoenix](https://github.com/Arize-ai/phoenix/blob/main/LICENSE)) : elle est **source-available, pas OSS**, même si une page produit emploie le terme « open-source ».

## 3. Briques recommandées

### 3.1 Capture, stockage, découpage et inspection

| Brique | Fonction utile | Licence/statut | Maturité et risques |
|---|---|---|---|
| **ROS 2 `rosbag2` + `rosbag2_storage_mcap`** | Enregistrement/rejeu ROS 2 avec backend MCAP. Le plugin est Apache-2.0 et livré dans `rosbag2` ([package officiel](https://docs.ros.org/en/iron/p/rosbag2_storage_mcap/standard_docs/PACKAGE.html), [dépôt](https://github.com/ros2/rosbag2/tree/rolling/rosbag2_storage_mcap)). Depuis ROS 2 Iron, MCAP est le format par défaut et `rosbag2` stocke les définitions de messages dans le bag ([notes de version Iron](https://docs.ros.org/en/foxy/Releases/Release-Iron-Irwini.html)). | Apache-2.0 : OSS. | **Élevée** pour un atelier ROS. Épingler une distribution supportée ; `rolling` est mouvante. Vérifier chaque bag avec un type custom sur une machine sans workspace source. |
| **MCAP + CLI** | Conteneur de messages pub/sub horodatés, indépendant de la sérialisation ; schémas, canaux, messages, pièces jointes, métadonnées, compression et index temporels sont définis par la spécification ([spec MCAP](https://mcap.dev/spec)). Le CLI sait inspecter, convertir, filtrer, fusionner, trier et récupérer un fichier corrompu ([CLI officiel](https://mcap.dev/guides/cli)). | MIT ([licence](https://github.com/foxglove/mcap/blob/main/LICENSE)) : OSS. | **Élevée** et excellent format pivot. Le CLI filtre topics/temps, mais la sémantique d'événement et l'annotation métier restent à construire. |
| **Apache Tika — option documentaire uniquement** | Détection de type et extraction de texte/métadonnées si un dossier annexe mêle PDF, présentations, tableurs ou pièces jointes ([site officiel](https://tika.apache.org/index.html), [formats](https://tika.apache.org/3.1.0/formats.html)). | Apache-2.0 : OSS. | **Hors socle ROS**. Choisir la branche stable 3.x (3.3.1), pas la bêta 4.0 ([téléchargements](https://tika.apache.org/download.html)), et isoler les parseurs de fichiers non fiables. |

**Décision** : imposer MCAP comme format de remise et enregistrer avec une distribution ROS 2 moderne. MCAP possède des enregistrements `Schema` intégrés au format ([spécification](https://mcap.dev/spec#schema-op0x03)) ; le plugin ROS 2 écrit les définitions MSG ou IDL auto-contenues dans ces schémas ([cache de définitions](https://docs.ros.org/en/humble/p/rosbag2_storage_mcap/generated/classrosbag2__storage__mcap_1_1internal_1_1MessageDefinitionCache.html), [historique du plugin](https://docs.ros.org/en/ros2_packages/rolling/api/rosbag2_storage_mcap/__CHANGELOG.html)). La CLI peut ainsi convertir les bags ROS 2 Iron et ultérieurs sans sourcer le workspace ; les `.db3` plus anciens demandent encore le workspace d'origine ([guide de conversion](https://mcap.dev/guides/cli#ros-bag-to-mcap-conversion)). Cette disponibilité doit être vérifiée, pas supposée, pour tous les messages custom du dataset.

### 3.2 Analyse tabulaire, temporelle, signal et vision

| Brique | Fonction utile | Licence/statut | Maturité et risques |
|---|---|---|---|
| **DuckDB** | SQL local directement sur CSV, JSON et Parquet, avec lecture sélective des colonnes et filtres poussés dans Parquet ([import](https://duckdb.org/docs/current/data/overview), [Parquet](https://duckdb.org/docs/stable/data/parquet/overview)). | MIT ([licence officielle](https://github.com/duckdb/duckdb/blob/main/LICENSE)) : OSS. | **Élevée**. Très bon moteur d'exploration et de scoring ; ne décode pas seul tous les messages ROS custom. |
| **Polars** | DataFrames lazy/eager, optimisation de requêtes et exécution streaming pour des jeux plus grands que la RAM ([dépôt officiel](https://github.com/pola-rs/polars), [guide lazy](https://docs.pola.rs/user-guide/lazy/)). | MIT : OSS. | **Élevée**, mais les opérations streaming ne couvrent pas nécessairement toutes les expressions ; prévoir des échantillons bornés. |
| **SciPy `signal`** | Filtrage, convolution/corrélation, détection de pics, spectres, cohérence, STFT et rééchantillonnage ([référence officielle](https://docs.scipy.org/doc/scipy/reference/signal.html)). | BSD-3-Clause ([licence](https://github.com/scipy/scipy/blob/main/LICENSE.txt)) : OSS. | **Très élevée**. Le vrai risque est méthodologique : taux d'échantillonnage, dérive d'horloge et resampling doivent être explicités. |
| **OpenCV + `cv_bridge`** | Traitement d'images/vidéo et pont entre messages image ROS 2 et représentations OpenCV ([licence OpenCV](https://opencv.org/license/), [`vision_opencv`](https://github.com/ros-perception/vision_opencv)). | OpenCV ≥4.5 Apache-2.0 ; pont ROS Apache-2.0/BSD : OSS. | **Très élevée**. Décoder toute la vidéo coûte cher : fournir extraction de frames et limites CPU/GPU. |

**Décision** : normaliser seulement les caractéristiques nécessaires en Parquet (`timestamp`, topic, valeurs dérivées, qualité, event id). Conserver l'octet brut dans MCAP. Cette séparation permet à DuckDB/Polars d'aller vite sans perdre la traçabilité vers la preuve originale.

### 3.3 Visualisation et investigation multimodale

| Brique | Fonction utile | Licence/statut | Maturité et risques |
|---|---|---|---|
| **Lichtblick** | Outil intégré de visualisation/diagnostic robotique, web ou desktop, qui charge ROS 1, ROS 2 et MCAP, accepte données live ou enregistrées, layouts, panels et extensions ([documentation officielle](https://lichtblick-suite.github.io/docs/), [dépôt officiel](https://github.com/lichtblick-suite/lichtblick)). | Le dépôt est MPL-2.0 ([licence](https://github.com/lichtblick-suite/lichtblick/blob/main/LICENSE)) : OSS pour le code couvert ; le projet se décrit comme **open-core**, donc vérifier séparément toute fonction externe au dépôt. | **Moyenne à élevée** : fork activement maintenu de Foxglove Studio, version 1.27.0 en juillet 2026. Excellent visualiseur MCAP transversal ; geler la version et tester les messages/panels du dataset, notamment services et schémas custom. |
| **PlotJuggler 3/4** | Séries temporelles, millions de points, transformations, layouts réutilisables et intégration ROS/rosbag ([dépôt officiel](https://github.com/PlotJuggler/PlotJuggler), [site v4](https://plotjuggler.io/)). | MPL-2.0 ([licence officielle](https://github.com/PlotJuggler/PlotJuggler/blob/main/LICENSE.md)) : OSS ; plugins fermés permis sans changer le statut du cœur. | **Élevée** pour le signal. PlotJuggler 4 est encore présenté comme bêta : préparer une version 3 stable et tester les plugins ROS exacts. |
| **Rerun** | Images, point clouds, transforms, séries, vidéo et autres données multi-rate dans une timeline synchronisée ; import MCAP et SDK Python/Rust/C++ ([dépôt officiel](https://github.com/rerun-io/rerun)). | Double Apache-2.0/MIT pour le dépôt : OSS ; **open-core**, car Rerun Hub vise les équipes. | **Moyenne à élevée** : très adapté au sujet, développement actif, mais version 0.x et migrations fréquentes. Geler version, blueprint et importeur MCAP. |
| **Panel / HoloViz** | Dashboard Python riche, compatible hvPlot/HoloViews/Datashader pour grandes séries ([dépôt officiel](https://github.com/holoviz/panel)). | BSD-3-Clause : OSS. | **Élevée**. Meilleur choix si l'on veut une application scientifique durable plutôt qu'un prototype minimal. |
| **Dash / Plotly.js** | Applications web de données, callbacks Python, graphiques interactifs, sélection et cross-filtering ([page officielle](https://plotly.com/dash/), [dépôt Dash](https://github.com/plotly/dash)). | MIT : OSS ; offre Enterprise séparée. | **Élevée**. Authentification non incluse dans l'édition OSS ; sans enjeu pour un serveur local d'équipe. |
| **Streamlit** | Création très rapide d'apps de données avec widgets, cache, cartes et graphiques ([documentation officielle](https://docs.streamlit.io/)). | Apache-2.0 : OSS. | **Élevée pour prototypage**. Son modèle de rerun et son contrôle fin de l'UI sont moins adaptés à une grosse timeline synchronisée. |

**Décision** : fournir **PlotJuggler et Lichtblick** dans l'image/laptop de référence. PlotJuggler couvre l'analyse fine des séries ; Lichtblick couvre le rejeu MCAP et les vues robotiques synchronisées. Rerun reste une voie multimodale avancée, tandis que Panel/Dash/Streamlit ne concernent que les équipes qui veulent construire un « cockpit de preuve ». Ne pas imposer plusieurs frameworks web.

### 3.4 Orchestration agentique et usage d'outils

| Brique | Fonction utile | Licence/statut | Maturité et risques |
|---|---|---|---|
| **LangGraph** | Graphe d'états explicite, checkpoints, reprise après erreur, interruptions et validation humaine des tool calls ([persistance](https://docs.langchain.com/oss/python/langgraph/persistence), [human-in-the-loop](https://docs.langchain.com/oss/python/langchain/human-in-the-loop)). | MIT ([licence](https://github.com/langchain-ai/langgraph/blob/main/LICENSE)) : OSS. | **Moyenne à élevée** : cœur désormais 1.x mais évolution rapide. Bon choix si le graphe reste petit, typé et inspectable. |
| **Haystack** | Pipelines modulaires, agents, outils, mémoire, recherche documentaire et évaluation ([documentation](https://docs.haystack.deepset.ai/), [dépôt](https://github.com/deepset-ai/haystack)). | Apache-2.0 ([licence](https://github.com/deepset-ai/haystack/blob/main/LICENSE)) : OSS ; plateforme deepset séparée. | **Élevée** pour RAG et pipelines explicites. Option crédible si l'analyse de documents est centrale ; ne pas ajouter `haystack-experimental` au socle. |
| **Microsoft AutoGen** | API Core/AgentChat, agents et équipes utilisables comme outils ([dépôt](https://github.com/microsoft/autogen)). | Code MIT ; documentation CC-BY-4.0 ([licence code](https://github.com/microsoft/autogen/blob/main/LICENSE-CODE)) : OSS. | **Maintenance uniquement** : le README officiel annonce qu'il ne recevra plus de fonctionnalités, devient community-managed et recommande Microsoft Agent Framework aux nouveaux projets. À conserver seulement comme option patrimoniale/expérimentale, pas comme socle 2026. |
| **Model Context Protocol (MCP)** | Standardise découverte et appel d'outils via schémas JSON ; spécification, schémas et docs sont publics ([dépôt officiel](https://github.com/modelcontextprotocol/modelcontextprotocol)). | Spécification MIT : ouverte/OSS. | **Émergente**. La fonctionnalité `Tasks` de la spec 2025-11-25 est encore expérimentale ([spec Tasks](https://modelcontextprotocol.io/specification/2025-11-25/basic/utilities/tasks)). MCP standardise le transport, pas la confiance : serveur allowlisté, outils read-only par défaut et validation humaine avant toute écriture. |

Le bon design n'est pas « donner un shell à un LLM ». Il faut exposer quelques outils étroits et testables :

- `inspect_bag(path) -> metadata` ;
- `query_signal(topic, fields, t0, t1) -> table` ;
- `detect_events(detector, params) -> candidates` ;
- `render_evidence(event_id, view) -> artifact` ;
- `export_slice(event_id) -> mcap + manifest` ;
- `score_submission(path) -> metrics`.

Tous les paramètres et résultats doivent être structurés, bornés en taille et journalisés. Les appels qui écrivent ou exportent exigent une approbation explicite. LangGraph sait suspendre le graphe avant un tool call puis accepter, modifier ou rejeter l'action ([cycle HITL officiel](https://docs.langchain.com/oss/python/langchain/human-in-the-loop#execution-lifecycle)).

### 3.5 Inférence locale

| Brique | Fonction utile | Licence/statut | Maturité et risques |
|---|---|---|---|
| **Ollama** | Installation simple, API REST locale et intégrations avec agents ([dépôt officiel](https://github.com/ollama/ollama)). | MIT ([licence](https://github.com/ollama/ollama/blob/main/LICENSE)) : runtime OSS. | **Élevée pour atelier**. La commodité n'efface ni le coût mémoire ni la licence propre de chaque modèle. |
| **llama.cpp** | Inférence CPU/GPU de modèles quantifiés, serveur compatible OpenAI, multimodal et function calling ([serveur officiel](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md)). | MIT ([licence](https://github.com/ggml-org/llama.cpp/blob/master/LICENSE)) : OSS. | **Élevée**, mais API et templates d'outils dépendent du modèle ; valider le couple modèle/template avant le jour J. |
| **vLLM** | Serveur GPU à haut débit, API compatible OpenAI, support multimodal et parseurs de tool calls ([documentation officielle](https://docs.vllm.ai/en/latest/serving/openai_compatible_server.html)). | Apache-2.0 ([licence](https://github.com/vllm-project/vllm/blob/main/LICENSE)) : OSS. | **Élevée côté serveur GPU**, surdimensionné pour chaque laptop. Pertinent comme service local partagé si le réseau du hackathon le permet. |

**Risque de licence essentiel** : la licence du runtime n'est pas celle des poids. Le Hub Hugging Face permet à chaque dépôt de déclarer sa propre licence et la model card l'affiche ([documentation licences](https://huggingface.co/docs/hub/main/en/repositories-licenses), [model cards](https://huggingface.co/docs/hub/model-cards)). Le kit doit donc épingler **modèle, révision, hash, licence et usage autorisé**, pas seulement `ollama:latest`.

### 3.6 Exécution locale et reproductibilité

| Brique | Fonction utile | Licence/statut | Maturité et risques |
|---|---|---|---|
| **Podman** | Moteur OCI daemonless, exécution rootless sans privilèges supplémentaires par rapport à l'utilisateur ([documentation](https://docs.podman.io/en/stable/markdown/podman.1.html), [dépôt](https://github.com/containers/podman)). | Apache-2.0 : OSS. | **Élevée sous Linux**. Sur Windows/macOS, une VM reste nécessaire : tester le parc réel avant le hackathon. |
| **Docker Engine / Docker Desktop** | Engine de conteneurs largement connu. Docker Engine est Apache-2.0 et open source ([docs Engine](https://docs.docker.com/engine/)). | **Engine OSS** ; **Desktop propriétaire sous contrat de souscription**, gratuit notamment pour l'éducation mais pas universellement ([licence Desktop](https://docs.docker.com/subscription/desktop-license/)). | **Très élevée** techniquement. Ne pas écrire « Docker est entièrement open source » ; proposer Podman ou Engine Linux comme chemin sans ambiguïté. |
| **DVC** | Versionne les références de datasets/modèles avec Git, décrit des graphes de pipeline et reproduit seulement les étapes impactées ([dépôt officiel](https://github.com/treeverse/dvc)). | Apache-2.0 : OSS ; services Iterative séparés. | **Élevée**, mais peut être excessif pour une seule journée. À utiliser pour le dataset maître et le scoring ; pour les participants, un manifeste + hashes peut suffire. |
| **JupyterLab** | Atelier notebooks, terminaux et visualisations dans une interface locale ([dépôt officiel](https://github.com/jupyterlab/jupyterlab)). | BSD-3-Clause : OSS. | **Très élevée**. Fournir une image figée et traiter les notebooks remis comme du code non fiable ; les sorties cachées et l'ordre d'exécution ne garantissent pas, seuls, la reproductibilité. |

Le kit de référence doit inclure : image OCI épinglée par digest, fichier de dépendances verrouillé, petit jeu de données local, commandes `make/just` simples, mode CPU, et cache préchauffé. Les résultats doivent enregistrer l'image, le commit, les paramètres, seeds, modèle/révision et hash des sources. Un notebook seul n'est pas une preuve de reproductibilité.

### 3.7 Observabilité et évaluation

| Brique | Fonction utile | Licence/statut | Maturité et risques |
|---|---|---|---|
| **OpenTelemetry** | Standard neutre pour instrumenter, générer, collecter et exporter traces, métriques et logs ([documentation officielle](https://opentelemetry.io/docs/)). | Apache-2.0 : OSS, projet CNCF. | **Très élevée** pour l'instrumentation générale, mais le projet publie une maturité par signal/composant et plusieurs éléments restent mixtes ou en développement ([tableau de statut officiel](https://opentelemetry.io/status/)). Éviter les profiles/éléments alpha et ajouter des attributs CIVE stables (`event_id`, `tool`, `topic`, `window`). |
| **MLflow** | Tracing compatible OpenTelemetry, évaluation de réponses et de trajectoires d'outils, jeux d'évaluation et expériences ([tracing](https://mlflow.org/docs/latest/genai/tracing), [évaluation de traces](https://mlflow.org/docs/latest/genai/eval-monitor/running-evaluation/traces/)). | Apache-2.0 : OSS ([page officielle](https://www.mlflow.org/genai)). | **Élevée**, mais large. Choisir uniquement tracking + traces + scorers pour éviter de transformer le hackathon en cours de MLOps. |
| **Evidently** | Qualité de données, dérive, métriques classification/régression/ranking et évaluation LLM ([dépôt officiel](https://github.com/evidentlyai/evidently)). | Bibliothèque cœur Apache-2.0 : OSS ; Evidently Cloud séparé ([distinction officielle](https://www.evidentlyai.com/pricing)). | **Élevée** pour rapports et checks ; complément de MLflow, pas nécessairement à déployer avec lui. |
| **Grafana + Loki + Tempo** | Dashboards, logs et traces ; Tempo accepte OpenTelemetry et relie traces, logs et métriques ([docs Tempo](https://grafana.com/docs/tempo/latest/)). | AGPL-3.0 pour l'OSS : vrai open source, avec offres Cloud/Enterprise séparées ([licence Tempo](https://grafana.com/oss/tempo/)). | **Très élevée**, mais lourde et copyleft réseau. À préinstaller pour la piste AgentOps, pas à faire déployer par chaque équipe. |
| **Arize Phoenix** | Traces, datasets, expériences, évaluations et playground, avec instrumentation OpenTelemetry/OpenInference ([docs officielles](https://arize.com/docs/phoenix/)). | **Elastic License 2.0 : source-available, non OSI** ([licence du dépôt](https://github.com/Arize-ai/phoenix/blob/main/LICENSE)). | Fonctionnellement pertinent, mais à exclure du « socle 100 % OSS » ou à étiqueter sans ambiguïté. |

## 4. Architecture de référence proposée

### Couche 1 — preuve immuable

- Dataset distribué en MCAP, avec schémas embarqués, checksum et licence de données.
- Topics mêlant au moins trois modalités : état véhicule/commande, signal continu, et image ou point cloud.
- Vérité terrain séparée, partiellement cachée au jury.

### Couche 2 — moteur CIVE d'événements

Petit projet Apache-2.0 ou MIT créé pour l'occasion :

- registre de détecteurs Python ;
- détecteurs par règles et par caractéristiques ;
- fenêtres pré/post-événement ;
- déduplication et classement des candidats ;
- manifeste JSON Schema public ;
- export via la CLI MCAP ;
- provenance et hashes ;
- API CLI d'abord, MCP facultatif ensuite.

Cette couche remplace précisément la fonction historique sans dépendre d'un produit SaaS. Elle est assez petite pour être comprise, forkée et améliorée pendant le hackathon.

### Couche 3 — analyse et vues

- Adaptateur MCAP → tables Parquet pour signaux sélectionnés.
- DuckDB/Polars pour interrogation et feature engineering.
- SciPy/OpenCV pour détecteurs avancés.
- PlotJuggler pour les signaux et Lichtblick pour le rejeu/vues robotiques ; Rerun en extension multimodale ; dashboard libre seulement si utile à la restitution.

### Couche 4 — agent sous contrôle

- LangGraph orchestre uniquement des outils bornés et read-only par défaut.
- MCP est une frontière d'interopérabilité optionnelle, pas une exigence pédagogique initiale.
- Aucun accès Internet, secret, shell arbitraire ou écriture hors du dossier de remise.
- Toute trajectoire est exportée en traces OpenTelemetry ; les appels d'outils et leurs résultats sont évaluables.

## 5. Trois orientations de hackathon

### Orientation A — Smart Data OSS (recommandée comme tronc commun)

**Question** : comment réduire un enregistrement massif à quelques fenêtres réellement actionnables sans perdre la preuve ?

Livrables : détecteur, manifests, sous-bags MCAP, métriques, layout PlotJuggler et vue Lichtblick. Scoring : rappel/précision temporelle, ratio octets utiles/octets bruts, intégrité/provenance, temps de calcul et reproductibilité.

**Atout** : continuité directe avec 2025, difficulté réglable, résultat objectif. **Limite** : moins spectaculaire si l'on ne fournit pas une bonne narration d'incident.

### Orientation B — Enquête multimodale

**Question** : quel enchaînement de signaux explique l'incident, et quelles preuves synchronisées le démontrent ?

Livrables : hypothèse, timeline, événements dérivés, vue Rerun/PlotJuggler et rapport citant exactement topics et fenêtres. Scoring : qualité de synchronisation, causalité prudente, diversité des preuves, lisibilité et capacité à reproduire la vue.

**Atout** : différencie les équipes qui comprennent les données de celles qui trouvent seulement un timestamp. **Limite** : jugement plus subjectif ; fournir une grille et des faits attendus.

### Orientation C — AgentOps Black Box

**Question** : un agent peut-il enquêter sur un incident robotique tout en restant traçable, évaluable et gouvernable ?

Livrables : graphe agentique, outils structurés, trace complète, politique d'approbation, réponse sourcée et tests de régression. Scoring : exactitude finale, qualité de la trajectoire, appels inutiles, respect des permissions, coût/latence, robustesse à une instruction malveillante cachée dans un log.

**Atout** : très distinctif et démontrable. **Limite** : le modèle peut dominer le résultat ; imposer le même modèle local et séparer le score d'ingénierie du score de réponse.

### Format conseillé

Un **tronc commun A** donne à tous le vocabulaire et le pipeline. Puis chaque équipe choisit B ou C comme multiplicateur d'ambition. Cette structure évite trois hackathons parallèles et garde une comparaison équitable.

## 6. Grille d'évaluation proposée

| Axe | Poids indicatif | Preuve attendue |
|---|---:|---|
| Détection et pertinence des fenêtres | 25 % | précision/rappel, erreur temporelle, contexte suffisant |
| Réduction et efficacité | 15 % | ratio de volume, durée CPU/GPU, mémoire |
| Qualité et provenance | 15 % | schémas, hashes, transformations, gestion des trous/NaN/horloges |
| Analyse multimodale | 15 % | au moins deux modalités synchronisées et une conclusion justifiée |
| Reproductibilité | 15 % | exécution one-command, versions épinglées, résultat stable |
| Visualisation/communication | 10 % | timeline exploitable, preuves navigables, pas seulement une capture |
| Agentique sûre et observable | 5 % de base, bonus jusqu'à 15 % | trace, permissions, tests de trajectoire, refus des actions hors périmètre |

Le jury doit évaluer à la fois **la sortie** et **le processus**. Une bonne réponse obtenue par hasard ou par un outil non traçable ne doit pas battre une pipeline reproductible et explicable.

## 7. Risques à traiter avant l'événement

1. **Périmètre trop large** : préparer les adaptateurs MCAP, images OCI et exemples ; les participants construisent détecteurs et enquête, pas la plomberie ROS.
2. **Horloges incohérentes** : MCAP distingue `log_time` et `publish_time` ([spécification Message](https://mcap.dev/spec#message-op0x05)). Documenter l'époque, la dérive et le choix de temps canonique.
3. **Messages ROS custom introuvables** : embarquer définitions et workspace minimal, puis tester la conversion sur une machine vierge.
4. **Licence des données et modèles** : fournir un inventaire `LICENSES.md` et les hashes ; ne pas assimiler poids accessibles et modèles open source.
5. **Matériel hétérogène** : baseline CPU obligatoire ; GPU partagé facultatif ; dataset réduit pour laptops.
6. **Prompt injection dans les logs/fichiers** : les contenus analysés sont des données non fiables, jamais des instructions. Outils allowlistés, lecture seule, sorties bornées et approbation avant export.
7. **Non-déterminisme agentique** : même modèle/révision, température fixée si possible, répétitions et métriques de variance ; score séparé pour la trajectoire.
8. **Dépendance réseau** : précharger images, wheels, modèles et docs ; prévoir un mode complètement hors ligne.
9. **Fausses promesses OSS** : tenir un SBOM/licence inventory et distinguer OSS, open-core, source-available et service propriétaire dans l'énoncé.
10. **API mouvantes** : geler ROS, PlotJuggler, Rerun, LangGraph, MCP SDK et modèle plusieurs semaines avant ; exécuter un dry-run sur les postes cibles.

## 8. Décisions à prendre maintenant

1. Choisir le scénario d'incident et les modalités du dataset.
2. Définir le JSON Schema du manifeste d'événement et la vérité terrain de scoring.
3. Prototyper le chemin minimal `MCAP -> détecteur -> manifest -> mcap filter -> PlotJuggler/Lichtblick`.
4. Décider si Rerun est fourni en voie B et si Grafana/MLflow est fourni en voie C.
5. Sélectionner un modèle local dont **les poids** ont une licence compatible, puis valider son tool calling sur le matériel réel.
6. Construire et signer l'image OCI, le dataset et leurs checksums ; tester en mode hors ligne.
7. Faire un mini-hackathon interne de deux heures pour calibrer le dataset, la difficulté et la grille.

## Conclusion

Le remplacement open source ne doit pas chercher un « nouveau produit X ». La bonne unité d'architecture est un format de preuve ouvert, un manifeste d'événement stable et de petits outils composables. Cela recrée la chaîne utile de 2025, rend chaque étape inspectable, et ouvre naturellement les extensions 2026 : analyse avancée, visualisation multimodale, agents outillés, traçage et évaluation.
