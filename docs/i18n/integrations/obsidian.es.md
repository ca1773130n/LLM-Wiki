# Obsidian — abre la wiki compilada como un vault real

<!-- translations:start -->
<p align="center"><a href="../../integrations/obsidian.md">English</a> · <a href="obsidian.ko.md">한국어</a> · <a href="obsidian.zh.md">中文</a> · <a href="obsidian.ja.md">日本語</a> · <a href="obsidian.ru.md">Русский</a> · <a href="obsidian.fr.md">Français</a> · <a href="obsidian.de.md">Deutsch</a></p>
<!-- translations:end -->

La exportación a Obsidian de LLM-Wiki convierte tu grafo tipado compilado en un vault de [Obsidian](https://obsidian.md) real y con criterio. No un directorio de markdown — un vault con configuración `.obsidian/`, [callouts](https://help.obsidian.md/Editing+and+formatting/Callouts) conscientes del tipo, frontmatter consultable con [Dataview](https://blacksmithgu.github.io/obsidian-dataview/), un dashboard del vault y un índice de referencias `wiki://` entre vaults.

## Requisitos previos

Compila primero el proyecto:

```bash
cd /path/to/your-project
llm_wiki project setup
llm_wiki project compile
```

La compilación produce `.llm-wiki/graph.json` (la fuente de verdad) y una proyección en markdown plano en `.llm-wiki/markdown_projection/`. La exportación a Obsidian se construye sobre esa proyección, pero superpone enriquecimientos nativos de Obsidian en cada página.

## 1) Exportar el vault

```bash
llm_wiki project export-obsidian --vault ~/Documents/llm-wiki-vault
```

El directorio se crea si no existe. Reejecutar lo sobrescribe de forma idempotente — la proyección markdown es determinista dado el mismo grafo.

Lo que queda en disco:

```text
llm-wiki-vault/
  .obsidian/                  # Obsidian config (app.json, graph.json, plugins)
  README.md                   # Vault entry point
  index.md                    # All nodes grouped by section
  _bridges.md                 # Cross-vault wiki:// references, grouped by alias
  _meta/
    dashboard.md              # Dataview overview tables
  papers/                     # Paper / Repository / SourceDocument pages
  concepts/                   # Concept / Topic / Field / Method / Algorithm pages
  claims/                     # Claim / OpenQuestion / Evidence pages
  raw/                        # Optional raw-source attachments (created lazily)
```

## 2) Abrir el directorio en Obsidian

`File → Open vault... → Open folder as vault → ~/Documents/llm-wiki-vault`.

Obsidian detectará `.obsidian/`, lo reconocerá como un vault real y lo cargará. La lista de community-plugins incluye Dataview, así que Obsidian preguntará si habilitarlo (recomendado — sin él los bloques dataview se renderizan como bloques de código).

`Settings → Community plugins → Browse → "Dataview" → Install → Enable`.

## 3) Recorrido por el vault

### Puntos de entrada

- `README.md` — qué es este vault y cómo refrescarlo
- `index.md` — cada nodo por sección (papers, concepts, claims) con wikilinks
- `_meta/dashboard.md` — dataview overview: páginas recientes, papers, concepts/claims

### Enriquecimientos por página

Cada página de nodo ahora incluye:

**Callouts conscientes del tipo.** Un callout semántico en la parte superior de cada página hace visible el tipo de nodo de un vistazo:

```markdown
> [!quote] Paper
> The paper triggered a wave of follow-on work: SuGaR aligns Gaussians...

> [!warning] Limitation
> No current method can achieve real-time display rates at 1080p...

> [!question] Open question
> How does dynamic-scene reconstruction scale...
```

Mapeo (destacados): `Paper → quote`, `Repository → info`, `Contribution → success`, `Performance → info`, `Limitation → warning`, `Causal → important`, `OpenQuestion → question`, `Evidence → example`.

**Aristas consultables con Dataview.** El frontmatter ahora lleva las aristas tipadas como mapas anidados:

```yaml
edges_out:
  uses: [gaussian-splatting, volumetric-rendering]
  part_of: [3d-4d-vision-and-reconstruction]
  supports_claim: [performance-claim-..., comparison-...]
edges_in:
  mentioned_in: [project-pulse, topic-visual-slam]
```

Puedes escribir consultas como:

````markdown
```dataview
LIST FROM "papers" WHERE contains(edges_out.uses, "nerf")
```

```dataview
TABLE edges_out.supports_claim AS "Claims"
FROM "papers"
WHERE length(edges_out.supports_claim) > 3
SORT length(edges_out.supports_claim) DESC
LIMIT 10
```
````

**Puentes entre vaults.** Cualquier URI `wiki://<alias>/<kind>/<slug>` mencionada en la descripción o metadatos de un nodo aparece tanto como campo de frontmatter:

```yaml
cross_vault: [wiki://research/concepts/rlhf, wiki://notes/papers/arxiv-2510-12323]
```

como en una sección de cuerpo `Cross-vault references`. El índice `_bridges.md` a nivel de vault agrega cada referencia saliente agrupada por alias de destino, así puedes auditar los enlaces entre vaults desde una sola página.

**Bloque Related (dataview).** Cada página termina con una consulta que muestra las páginas que enlazan de vuelta, poblada automáticamente:

````markdown
```dataview
LIST
FROM "papers" OR "concepts" OR "claims"
WHERE contains(file.outlinks, this.file.link) AND file.name != this.file.name
SORT file.name
LIMIT 25
```
````

### Dashboard del vault

`_meta/dashboard.md` incluye bloques dataview para las vistas agregadas más útiles: páginas actualizadas recientemente, todos los papers con columnas de metadatos, todos los concepts y claims ordenados por tipo. Edítalo libremente — es un punto de partida, no un contrato fijo.

### Vista de grafo del vault

La vista de grafo integrada de Obsidian (`Ctrl/Cmd+G`) ya funciona contra los wikilinks emitidos en las secciones `## Outgoing` / `## Incoming`. El `.obsidian/graph.json` preconfigurado colorea las rutas `papers/`, `concepts/`, `claims/` para facilitar la orientación. Puedes superponer vistas filtradas con dataview para cortes más ricos.

## Flujos de trabajo entre vaults

Registra varios vaults de LLM-Wiki para que las URIs `wiki://` se resuelvan entre ellos:

```bash
llm_wiki register-project /path/to/research --name research
llm_wiki register-project /path/to/notes    --name notes
```

Vuelve a exportar cada vault tras el registro. `_bridges.md` en cada exportación mostrará ahora referencias resolubles entre vaults agrupadas por alias.

Obsidian en sí no sigue las URIs `wiki://` de forma nativa — se renderizan como texto inline — pero `_bridges.md` más la sección `Cross-vault references` por página te dan un índice manual hasta que aterrice un plugin dedicado de Obsidian.

## Flujo de refresco

El vault de Obsidian es una **exportación de solo lectura** del grafo tipado. Las ediciones en Obsidian no vuelven a `.llm-wiki/graph.json`. Para incorporar nuevas fuentes o correcciones:

```bash
# Edit source files under your project's source dirs (NOT the vault), then:
llm_wiki project compile
llm_wiki project export-obsidian --vault ~/Documents/llm-wiki-vault
```

Obsidian recargará en caliente los archivos cambiados en disco. Si has añadido notas markdown dentro del vault que no están proyectadas desde el grafo (por ejemplo, tus anotaciones personales), sobrevivirán — la exportación solo sobrescribe los archivos que le pertenecen bajo `papers/`, `concepts/`, `claims/`, además de `index.md`, `_bridges.md`, `_meta/dashboard.md` y `README.md`.

## Cuándo usar esto frente al sitio estático

El sitio HTML compilado (`llm_wiki project build-site` → `.llm-wiki/site/`) es para compartir — publícalo en GitHub Pages, S3 o cualquier host estático. El vault de Obsidian es para **leer y consultar** localmente con Dataview y la vista de grafo de Obsidian. Ambos proyectan desde el mismo grafo, así que nunca divergen.
