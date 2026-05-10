# Checklist de publication

<!-- translations:start -->
<p align="center"><a href="../publishing-checklist.md">English</a> · <a href="publishing-checklist.ko.md">한국어</a> · <a href="publishing-checklist.zh.md">中文</a> · <a href="publishing-checklist.ja.md">日本語</a> · <a href="publishing-checklist.ru.md">Русский</a> · <a href="publishing-checklist.es.md">Español</a> · <a href="publishing-checklist.fr.md">Français</a></p>
<!-- translations:end -->
Utilisez cette checklist avant de présenter LLM-Wiki publiquement.

## Hygiène du dépôt

- [ ] Le README explique ce qu'est le projet et le problème qu'il résout.
- [ ] La commande d'installation fonctionne depuis un shell neuf.
- [ ] Le Quickstart utilise `llm_wiki`, pas `python3 -m`.
- [ ] La documentation d'architecture explique raw evidence → graph → projections.
- [ ] La carte des fonctionnalités liste les fonctionnalités implémentées sans survendre le travail futur.
- [ ] La documentation d'historique de sessions explique l'import explicite, la revue de confidentialité, les routes générées et la transcript typography.
- [ ] La démo Self-dogfood a été exécutée et documentée.
- [ ] Les artefacts générés sont reproductibles et soit ignorés, soit publiés intentionnellement.

## Vérification

```bash
PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 python3 -m pytest tests/ -q
./scripts/install.sh --help
llm_wiki project setup --help
llm_wiki project compile --help
```

## Self-dogfood

```bash
llm_wiki project setup \
  --yes \
  --name llm_wiki_self \
  --source README.md \
  --source docs \
  --source llm_wiki \
  --source tests \
  --source scripts \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
llm_wiki project compile
llm_wiki project sessions list
llm_wiki project build-site
llm_wiki project serve --port 8765
```

## Points de discours pour la démo

- LLM-Wiki n'est pas un graphe générique de groupes nominaux. Il utilise une ontology contrôlée.
- Le code de recherche et le code de développement partagent l'infrastructure, mais gardent des schema distincts.
- Markdown et HTML sont des projections, pas des magasins de vérité faisant autorité.
- Le chemin par défaut est local et pratique sans API key.
- Les harnesses d'agent et MCP rendent le graphe utilisable par les coding agents.
- Les pages de sessions harness importées transforment les travaux Claude Code/Codex précédents en mémoire de projet consultable, tout en gardant explicite la découverte des transcript.
