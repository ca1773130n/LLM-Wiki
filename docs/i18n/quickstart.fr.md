# Démarrage rapide

<!-- translations:start -->
<p align="center"><a href="../quickstart.md">English</a> · <a href="quickstart.ko.md">한국어</a> · <a href="quickstart.zh.md">中文</a> · <a href="quickstart.ja.md">日本語</a> · <a href="quickstart.ru.md">Русский</a> · <a href="quickstart.es.md">Español</a> · <a href="quickstart.fr.md">Français</a></p>
<!-- translations:end -->
Cette page montre le chemin le plus court depuis un répertoire de projet existant jusqu'à un LLM-Wiki navigable.

## 1. Lancez l'assistant de configuration

Depuis le projet que vous voulez indexer :

```bash
cd /path/to/my-project
llm_wiki project setup
```

L'assistant détecte les sources courantes comme `README.md`, `docs`, `src`, `lib`, `app`, `packages` et `data`, puis écrit `.llm-wiki/config.json`. Il configure aussi le backend Cognee par défaut afin que `project ask` puisse essayer Cognee puis fallback vers la recherche du wiki compilé.

Pour une configuration entièrement automatisée avec Understand Anything et Cognee runtime memory activés :

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
```

Ce que cela fait :

| Flag | Effect |
|---|---|
| `--with-understand-anything` | Ajoute la UA graph projection comme source. |
| `--install-understand-anything` | Installe/met à jour les UA companion skills. |
| `--understand-anything-platform codex` | Utilise Codex pour exécuter le managed UA refresh wrapper de LLM-Wiki. |
| `--run-cognee` | Lance best-effort Cognee runtime cognify pendant compile. |
| `--install-cognee` | Installe Cognee avec le Python courant s'il manque. |

Les utilisateurs n'ont pas besoin de connaître le UA install path ni de taper `/understand` ; `project compile` exécute `project refresh-understand-anything` lorsque le UA graph manque ou est obsolète.

## 2. Compilez le graphe et les projections

```bash
llm_wiki project compile
```

`project compile` écrit les durable artifacts :

```text
.llm-wiki/
  config.json
  graph.json
  manifest.json
  sqlite.db
  temporal_facts.jsonl
  graphiti_episodes.jsonl
  report.md
  competitive_report.md
  markdown_projection/
  obsidian_vault/
  agent_harness/
  harness_sessions/
  site/
  cognee_bundle/
```

Utilisez `--changed-only` après le premier run pour ignorer les fichiers markdown inchangés tout en conservant le graph précédent quand aucun fichier n'a changé. Si Understand Anything est activé, compile refresh/materialize d'abord `.llm-wiki/external/understand-anything.md` ; si Cognee runtime est activé, il met aussi à jour Cognee en best-effort après l'écriture de `.llm-wiki/cognee_bundle/`.

## 3. Construisez et servez le frontend statique

```bash
llm_wiki project build-site
llm_wiki project serve --port 8765
```

Ouvrez :

```text
http://127.0.0.1:8765/
```

<!-- BEGIN: subagent-r-watch -->
### Auto-rebuild à l'enregistrement

Associez le dev server à un polling watcher pour que les modifications sous `data/` et `docs/` déclenchent une incremental recompile :

```bash
# terminal 1
python3 -m http.server 56821 --directory .llm-wiki/site

# terminal 2
llm_wiki project watch
```

`project watch` poll toutes les 2 s, debounce 1 s, puis exécute `compile --changed-only`. Utilisez `--once` pour des rebuilds façon cron (snapshots vs `.llm-wiki/.watch-cache.json`), `--paths <dir>` pour ajouter des custom watch dirs, et `--interval` / `--debounce` pour ajuster la cadence.
<!-- END: subagent-r-watch -->

Pour un tour annoté de chaque route visible — home, sources, concepts, entities, papers, repos, topics, syntheses, questions, timeline, graph, plus les AI siblings — voir [`docs/frontend-redesign.md`](frontend-redesign.fr.md).

Le frontend a peu de dépendances et écrit :

```text
.llm-wiki/site/index.html
.llm-wiki/site/sessions/index.html
.llm-wiki/site/graph.json
.llm-wiki/site/search-index.json
.llm-wiki/site/llms.txt
```

## 4. Importez l'historique local des sessions agent

L'import d'historique de session est explicite : compile/build normal lit les sessions déjà normalisées, mais ne scanne pas seul les transcript stores privés Claude Code ou Codex.

```bash
# Preview matching Claude Code/Codex sessions for this project:
llm_wiki project sessions discover

# Normalize and store them under .llm-wiki/harness_sessions/:
llm_wiki project sessions discover --import

# Confirm the imported set:
llm_wiki project sessions list

# Rebuild so sessions/index.html and session detail pages are emitted:
llm_wiki project build-site
```

Les sessions importées apparaissent dans la section globale Sessions, la recherche du site et les cartes Browse de l'accueil. Les pages détail de session rendent les tours user/assistant en markdown lisible, attachent les tool-use blocks sous le tour assistant précédent et exposent un turn rail gauche pour la navigation `#turn-N`. Voir [`docs/session-history.md`](session-history.fr.md) pour les notes de confidentialité, formats d'import et la transcript typography map courante.

## 5. Lintez le wiki

```bash
llm_wiki project lint
```

Parcourt le compiled graph + wiki + site et signale orphan papers, stale citations, drift entre graph et wiki/, ghost synthesis inputs, etc. Écrit `.llm-wiki/lint-report.md` et `.llm-wiki/lint-report.json`. Passez `--fix-trivial` pour appliquer des auto-fixes sûrs (missing `implemented_in` edges, ghost-input pruning) et `--severity error` pour ne faire échouer l'exit code que sur les errors.

## 6. Interrogez le wiki

```bash
llm_wiki project query "What is Gaussian Splatting?"
```

Par défaut, recherche seule — BM25 sur `.llm-wiki/site/search-index.json`, avec un excerpt de 200 caractères pris depuis le `wiki/<kind>/<slug>.md` correspondant. Passez `--kind papers` (ou `concepts`, `repos`, etc.) pour restreindre, `--top-k N` pour élargir, et `--json` pour une sortie structurée. Ajoutez `--llm` (ou définissez `LLM_WIKI_QUERY_LLM=1`) pour demander à Claude une réponse synthétisée avec citations `[node_id]` ; `--interactive` ouvre un REPL readline — ligne vide ou EOF quitte. `LLM_WIKI_QUERY_DRY_RUN=1` exerce le prompt sans appel API.

## 7. Exportez les fichiers agent harness

```bash
llm_wiki project export-agent-harness
```

Targets supportés :

- Claude Code
- Codex
- Gemini
- Kiro
- Cursor
- OpenCode

Subset d'exemple :

```bash
llm_wiki project export-agent-harness \
  --target claude-code \
  --target cursor \
  --target opencode
```

## 8. Exportez un vault Obsidian

```bash
llm_wiki project export-obsidian
```

Ou écrivez dans un vault existant :

```bash
llm_wiki project export-obsidian --vault "$OBSIDIAN_VAULT_PATH"
```

Le vault inclut les markdown projections, les defaults `.obsidian`, le graph coloring, `raw/assets/` et un dashboard Dataview.

## 9. Configurez MCP

```bash
llm_wiki project mcp-config --server-name my_project_wiki
```

Collez la sortie sous `mcp_servers` dans `~/.hermes/config.yaml`, puis redémarrez Hermes/gateway.

## 10. Graphiti export / sync

Episode export sans dépendance :

```bash
llm_wiki project export-graphiti
```

Dry-run sync smoke sans Graphiti installé :

```bash
llm_wiki project sync-graphiti --dry-run
```

Live sync nécessite `graphiti_core` et un backend Neo4j joignable :

```bash
llm_wiki project sync-graphiti \
  --neo4j-uri bolt://localhost:7687 \
  --neo4j-user neo4j \
  --neo4j-password '<password>'
```

## 11. Déployez sur GitHub Pages

Poussez le compiled site dans `.llm-wiki/site/` vers la branche `gh-pages` du git origin du projet :

```bash
llm_wiki project deploy --build --enable-pages
```

`--build` exécute d'abord `project compile` pour que le site soit frais. `--enable-pages` active Pages via la CLI `gh` (idempotent ; ignoré avec une indication si `gh` manque). Utilisez `--dry-run` pour stage et commit sans push, `--branch` / `--remote` pour remplacer les defaults, et `--force` pour autoriser le déploiement avec un working tree dirty.

Le site devient accessible à `https://<owner>.github.io/<repo>/`.
