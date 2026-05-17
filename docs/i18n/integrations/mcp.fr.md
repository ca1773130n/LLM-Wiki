# MCP — connecter LLM-Wiki à Claude Code, Codex, Cursor

<!-- translations:start -->
<p align="center"><a href="../../integrations/mcp.md">English</a> · <a href="mcp.ko.md">한국어</a> · <a href="mcp.zh.md">中文</a> · <a href="mcp.ja.md">日本語</a> · <a href="mcp.ru.md">Русский</a> · <a href="mcp.es.md">Español</a> · <a href="mcp.de.md">Deutsch</a></p>
<!-- translations:end -->

LLM-Wiki fournit un serveur stdio [Model Context Protocol](https://modelcontextprotocol.io) qui expose le graphe typé compilé à tout client compatible MCP : Claude Code, Codex CLI, Cursor, Claude Desktop, et d'autres. Le serveur annonce trois surfaces MCP complètes — **tools**, **resources** et **prompts** — afin que les clients puissent à la fois interroger le graphe à la demande et amorcer le contexte à moindre coût depuis des URI canoniques.

## Prérequis

Le serveur lit depuis `.llm-wiki/graph.json`, donc une compilation initiale est requise :

```bash
cd /path/to/your-project
llm_wiki project setup    # interactive; or --yes for non-interactive
llm_wiki project compile  # deterministic, no LLM calls, no API keys
```

Recompilez chaque fois que vos sources changent. Le serveur prendra en compte le nouveau graphe au prochain appel d'outil, sans nécessiter de redémarrage.

## 1) Générer la configuration client

```bash
llm_wiki project mcp-config
```

Affiche un fragment JSON ressemblant à :

```json
{
  "mcpServers": {
    "llm-wiki": {
      "command": "python3",
      "args": [
        "-m", "llm_wiki.mcp_server",
        "--graph", "/path/to/your-project/.llm-wiki/graph.json"
      ]
    }
  }
}
```

Le chemin exact est rempli à partir du projet courant. Passez `--name <alias>` si vous souhaitez un nom d'entrée de serveur différent de `llm-wiki`.

## 2) Coller la configuration dans votre client MCP

| Client | Emplacement de la configuration |
|---|---|
| Claude Code | `~/.claude/mcp-servers.json` (or `~/.config/claude-code/mcp-servers.json`) |
| Claude Desktop | macOS: `~/Library/Application Support/Claude/claude_desktop_config.json` |
| Codex CLI | `~/.config/codex/mcp-servers.json` |
| Cursor | Settings → MCP Servers → coller le JSON |
| Hermes | `~/.hermes/config.toml` (utilisez le bloc équivalent TOML affiché par `mcp-config --format hermes`) |

Redémarrez le client après modification. La session suivante se connectera et découvrira la surface LLM-Wiki.

## 3) Ce que voit le client

### Tools — invoqués par le modèle

| Outil | Rôle |
|---|---|
| `schema` | Vocabulaire contrôlé des nœuds, arêtes et wiki-kinds |
| `graph_summary` | Compteurs de nœuds et d'arêtes ainsi que distributions de types pour le projet actif |
| `search_nodes` | Filtre les nœuds du graphe par requête, type, kind, avec un top-N classé par score |
| `node_context` | Un nœud + ses arêtes incidentes + les nœuds voisins |
| `search_facts` | Faits temporels projetés depuis le graphe (style Graphiti) |
| `timeline` | Faits ordonnés par `valid_from` pour une vue longitudinale |
| `wiki_page` | Le corps de la page markdown compilée pour un nœud |
| `raw_source` | Le markdown source d'origine (plafonné à 16 KB) |
| `lint_report` | Les derniers résultats de lint produits à la compilation |
| `ask` | Questions-réponses en langage naturel via le backend de mémoire configuré (raganything, cognee, ou wiki compilé) |
| `list_projects` / `register_project` / `activate_project` / `unregister_project` | Contrôle du registre multi-projets |

### Resources — chargées automatiquement dans le contexte du modèle

URI que le client peut tirer via son sélecteur de ressources sans consommer un tour d'outil :

- `llm-wiki://graph/schema` — même charge utile que l'outil `schema`, prête à servir de contexte statique
- `llm-wiki://graph/summary` — résumé du projet actif
- `llm-wiki://lint-report` — le dernier lint report au format markdown

Plus des templates d'URI que le client peut construire à la demande :

- `llm-wiki://wiki/{kind}/{slug}` — le corps de n'importe quelle page wiki compilée
- `llm-wiki://raw/{source_path}` — n'importe quel markdown source brut

### Prompts — modèles de recherche en un clic

Ils apparaissent dans le menu slash du client (par ex. la palette `/` de Claude Code) :

| Prompt | Arguments | Ce qu'il fait |
|---|---|---|
| `summarize-paper` | `slug` (requis) | Appelle `node_context` + `wiki_page` + éventuellement `raw_source`, puis renvoie un résumé structuré : contribution, esquisse de méthode, résultats principaux, limites, nœuds liés |
| `find-related-work` | `topic` (requis), `limit` | Enchaîne `search_nodes` + `node_context` pour les K éléments liés les plus pertinents avec justifications de pertinence |
| `compare-approaches` | `a`, `b` (les deux requis) | Récupère `node_context` pour les deux + `search_facts` pour les affirmations de performance ; renvoie une comparaison côte à côte avec synthèse |
| `gap-analysis` | `topic` (optionnel) | Fait remonter les questions ouvertes non résolues, les benchmarks manquants, les affirmations peu étayées |
| `triage-open-questions` | _aucun_ | Liste chaque nœud `OpenQuestion`, les regroupe par sujet, propose un ordre de priorité |

Chaque prompt se matérialise par un unique message utilisateur qui indique au modèle exactement quels outils LLM-Wiki enchaîner, afin que le modèle n'ait pas à redécouvrir la surface à chaque fois.

## Multi-projet : enregistrer plusieurs vaults sous un même serveur

Un registre persistant à `~/.llm-wiki/registry.json` permet au même serveur MCP de résoudre n'importe quel projet enregistré par son nom :

```bash
llm_wiki register-project /path/to/research --name research
llm_wiki register-project /path/to/notes    --name notes
```

Après cela, tout outil acceptant `project` ou `graph_path` résoudra `project: "research"` via le registre au lieu d'exiger un chemin complet. Le serveur vérifie même que le `graph_path` enregistré existe toujours et renvoie une erreur claire si une recompilation est nécessaire.

### Fan-out sur chaque vault enregistré

L'outil `ask` accepte `scope: "all-registered"` pour interroger en parallèle chaque projet enregistré et renvoyer les résultats agrégés :

```jsonc
{
  "name": "ask",
  "arguments": {
    "question": "Where is splatting used?",
    "scope": "all-registered"
  }
}
```

Restreignez à un sous-ensemble avec `scope_aliases: ["research", "notes"]`.

## CLI Claude multi-comptes

Si votre outil `ask` passe par la CLI Claude et que vous avez plusieurs comptes (par ex. `~/.claude` et `~/.claude-personal2`), passez `claude_config_dir` à chaque appel :

```jsonc
{
  "name": "ask",
  "arguments": {
    "question": "...",
    "claude_config_dir": "/Users/you/.claude-personal2"
  }
}
```

Le serveur exporte `CLAUDE_CONFIG_DIR` pour la durée de cet appel uniquement et restaure la valeur précédente ensuite. Aucune fuite entre les appels.

## Vérification

Après le redémarrage de votre client MCP, confirmez la connexion :

- Claude Code : `/mcp` devrait lister `llm-wiki` avec le nombre d'outils.
- Cursor : l'icône MCP dans la barre de chat devrait afficher `llm-wiki: connected` avec les compteurs de tools/resources/prompts.
- Codex / Hermes : invoquez n'importe quel outil par son nom (par ex. `schema`) et vérifiez la réponse.

Si rien n'apparaît, vérifiez à deux fois que `--graph` pointe vers un `.llm-wiki/graph.json` existant — le serveur valide désormais cela au démarrage et à chaque appel d'outil, vous verrez donc un message d'erreur clair plutôt qu'une 500 silencieuse.

## Où cela s'inscrit

Le serveur MCP est l'**interface de lecture** du graphe typé. Pour le **chemin d'écriture** (ingestion des sources, recompilation, rafraîchissement d'outils compagnons comme RAG-Anything ou Understand-Anything), utilisez la CLI directement. Les deux sont découplés : la CLI met à jour `.llm-wiki/`, le serveur MCP lit ce qui s'y trouve au prochain appel d'outil.
