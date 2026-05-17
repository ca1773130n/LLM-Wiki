# Lista de verificación de publicación

<!-- translations:start -->
<p align="center"><a href="../publishing-checklist.md">English</a> · <a href="publishing-checklist.ko.md">한국어</a> · <a href="publishing-checklist.zh.md">中文</a> · <a href="publishing-checklist.ja.md">日本語</a> · <a href="publishing-checklist.ru.md">Русский</a> · <a href="publishing-checklist.es.md">Español</a> · <a href="publishing-checklist.fr.md">Français</a> · <a href="publishing-checklist.de.md">Deutsch</a></p>
<!-- translations:end -->
Usa esta lista antes de presentar LLM-Wiki públicamente.

## Higiene del repositorio

- [ ] El README explica qué es el proyecto y qué problema resuelve.
- [ ] El comando de instalación funciona desde una shell nueva.
- [ ] El Quickstart usa `llm_wiki`, no `python3 -m`.
- [ ] La documentación de arquitectura explica raw evidence → graph → projections.
- [ ] El mapa de funciones enumera las funciones implementadas sin exagerar el trabajo futuro.
- [ ] La documentación del historial de sesiones explica la importación explícita, la revisión de privacidad, las routes generadas y la transcript typography.
- [ ] La demo Self-dogfood se ha ejecutado y documentado.
- [ ] Los artefactos generados son reproducibles y se ignoran o se publican intencionalmente.

## Verificación

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

## Puntos para la demo

- LLM-Wiki no es un grafo genérico de frases nominales. Usa una ontology controlada.
- El código de investigación y el de desarrollo comparten infraestructura, pero mantienen schema distintos.
- Markdown y HTML son proyecciones, no almacenes autoritativos de la verdad.
- La ruta por defecto es local y amigable sin API key.
- Los harnesses de agente y MCP hacen que el grafo sea usable por coding agents.
- Las páginas importadas de sesiones de harness convierten el trabajo previo de Claude Code/Codex en memoria de proyecto buscable, manteniendo explícito el descubrimiento de transcript.
