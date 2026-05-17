# Historique des sessions Harness

<!-- translations:start -->
<p align="center"><a href="../session-history.md">English</a> · <a href="session-history.ko.md">한국어</a> · <a href="session-history.zh.md">中文</a> · <a href="session-history.ja.md">日本語</a> · <a href="session-history.ru.md">Русский</a> · <a href="session-history.es.md">Español</a> · <a href="session-history.fr.md">Français</a> · <a href="session-history.de.md">Deutsch</a></p>
<!-- translations:end -->
Tesserae peut importer des transcript locaux d'AI-agent et les rendre comme mémoire de projet dans la section `sessions/` du site statique.

Cette fonctionnalité est volontairement séparée de `export-agent-harness` :

- `export-agent-harness` est un contexte sortant pour des outils comme Claude Code, Codex, Gemini, Cursor, Kiro et OpenCode.
- `project sessions ...` est un historique entrant : il normalise les sessions Claude Code/Codex précédentes pour le projet courant, les stocke dans `.tesserae/harness_sessions/`, et permet à `project build-site` de publier les pages index/detail des sessions.

## Modèle de confidentialité

L'import de sessions est explicite. Un `project compile` ou `project build-site` normal lit les sessions déjà normalisées depuis `.tesserae/harness_sessions/`, mais ne surprise-scrape pas les répertoires privés de transcript harness.

Les enregistrements de session importés sont des artefacts locaux du projet. Relisez-les avant de publier un site public, surtout si vos transcript peuvent contenir des secrets, chemins privés, données client ou code non publié.

## Découvrir et importer les sessions locales

Depuis la racine du projet :

```bash
tesserae project sessions discover --import
```

Discovery scanne les racines locales de transcript Claude Code et Codex qui appartiennent au répertoire de travail du projet courant. Utilisez `--root` pour scanner un répertoire de configuration précis, et répétez `--harness` pour limiter discovery :

```bash
tesserae project sessions discover \
  --root ~/.claude \
  --root ~/.codex \
  --harness claude-code \
  --harness codex \
  --import
```

Sans `--import`, discovery affiche ce qu'il a trouvé sans écrire d'enregistrements de session normalisés.

## Importer directement du JSON normalisé

Si un autre outil a déjà produit du JSON `HarnessSession` normalisé, importez un fichier ou une liste de fichiers :

```bash
tesserae project sessions import path/to/session.json path/to/more-sessions.json
```

Chaque entrée peut contenir un objet session ou une liste d'objets session.

## Lister les sessions importées

```bash
tesserae project sessions list
```

Les sessions sont stockées sous :

```text
.tesserae/harness_sessions/
  manifest.json
  <harness>/
    <session>.json
    <session>.md
```

## Construire les pages statiques de sessions

Après avoir importé les sessions, reconstruisez le site :

```bash
tesserae project build-site
```

Le site émet :

```text
.tesserae/site/sessions/index.html
.tesserae/site/sessions/<project>/<session>.html
```

Le site généré relie Sessions depuis le global rail, les cartes Browse de l'accueil, les entrées de recherche et le breadcrumb trail de chaque page de détail de session.

## Mise en page de la page détail de session

Les pages détail de session utilisent le shell partagé du site statique plutôt qu'un transcript dump autonome. Elles incluent :

- hero et stat strip ;
- résumé de haut niveau ;
- timeline et size metadata ;
- decisions, files, commands, tools et errors lorsqu'ils existent ;
- subagent tree replié ;
- conversation user/assistant tour par tour ;
- tool-use blocks repliés attachés sous le tour assistant précédent ;
- un conversation rail gauche qui pointe vers les anchors `#turn-N`.

Le markdown de conversation est rendu via le renderer markdown du site. Les surfaces sémantiques comme inline code, command/tag markup explicite, paths, filenames et hashtags sont décorées en chips compactes ; les noms aléatoires capitalisés ne sont pas chipés automatiquement.

Typography actuelle des transcript :

| Surface | Selector | Size |
|---|---|---|
| Prose markdown de conversation | `.session-turn-text`, prose children | `8px` |
| Code fences génériques de conversation | `.session-turn-text pre` | `10px` |
| Contenu fenced code Bash/shell | `.session-code-block code.language-bash`, `.language-sh`, `.language-shell`, `.language-zsh` | `11px` |
| Tool details/summary | `.session-tool-details`, `.session-tool-details > summary` | `10px` |
| Tool-use header | `.session-tool-use-header` | `8px` |
| Tool payload text | `.session-tool-use-text` | `6px` |

## Checklist de publication des sessions

Avant de déployer un site public qui inclut des sessions :

1. Exécutez `tesserae project sessions list` et confirmez que le nombre est attendu.
2. Inspectez `.tesserae/harness_sessions/` pour du contenu sensible.
3. Reconstruisez avec `tesserae project build-site`.
4. Ouvrez localement `sessions/index.html` et au moins une page détail de session.
5. Confirmez que les tool blocks sont repliés par défaut et que les raw tool payloads sont acceptables à publier.
6. Déployez avec `tesserae project deploy --build` une fois le source tree committed.
