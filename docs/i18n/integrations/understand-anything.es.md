# Flujo de trabajo complementario de Understand Anything

<!-- translations:start -->
<p align="center"><a href="../../integrations/understand-anything.md">English</a> · <a href="understand-anything.ko.md">한국어</a> · <a href="understand-anything.zh.md">中文</a> · <a href="understand-anything.ja.md">日本語</a> · <a href="understand-anything.ru.md">Русский</a> · <a href="understand-anything.es.md">Español</a> · <a href="understand-anything.fr.md">Français</a></p>
<!-- translations:end -->
[Understand Anything](https://github.com/Lum1104/Understand-Anything) y LLM-Wiki son proyectos complementarios.

- Understand Anything es excelente para producir un grafo de conocimiento de la base de código y un panel interactivo.
- LLM-Wiki se centra en memoria de agente duradera: documentos, compilación markdown/wiki, publicación estática, historial de sesiones y exportaciones orientadas a agentes.

LLM-Wiki no debe incorporar ni absorber Understand Anything. Trátalo como un acompañante independiente que puede producir artefactos de grafo útiles.

## ¿Por qué usar ambos?

Understand Anything puede escribir:

```text
.understand-anything/knowledge-graph.json
```

Ese grafo captura la estructura del código, como archivos, funciones, clases, módulos, conceptos, dependencias, capas y recorridos.

Luego LLM-Wiki puede conservar ese artefacto junto con el resto de la memoria del proyecto:

- documentos fuente y páginas markdown;
- archivos del repositorio;
- notas de investigación;
- historial local de sesiones Claude Code / Codex;
- páginas wiki estáticas generadas;
- vistas web del grafo 2D / 3D;
- `llms.txt`, `llms-full.txt`, `search-index.json`, `graph.json` y siblings de agente por página.

## Flujo actual de baja fricción

La ruta recomendada es el asistente de configuración:

```bash
llm_wiki project setup
```

Elige Understand Anything en el paso de herramientas complementarias. LLM-Wiki instala/actualiza las skills complementarias cuando se solicita y escribe un comando de actualización administrado en `.llm-wiki/config.json`. Las llamadas futuras a `llm_wiki project compile` ejecutan automáticamente ese wrapper cuando falta el grafo de UA o está obsoleto.

Para automatización no interactiva, usa:

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex
llm_wiki project compile
```

El comando almacenado pertenece a LLM-Wiki; no es algo que el usuario tenga que inventar:

```bash
llm_wiki project refresh-understand-anything --platform codex
```

Durante la compilación, LLM-Wiki:

1. comprueba si `.understand-anything/knowledge-graph.json` existe y coincide con el commit git actual cuando hay metadatos disponibles;
2. ejecuta la plataforma de agente configurada (`codex`, `opencode` o `claude`) solo cuando falta el grafo, está obsoleto o se fuerza la actualización;
3. verifica que el grafo se haya escrito;
4. materializa `.llm-wiki/external/understand-anything.md`;
5. continúa la compilación normal de memoria.

Puedes forzar todos los comandos externos de actualización configurados antes de compilar:

```bash
llm_wiki project compile --refresh-external-tools
```

¿También necesitas Cognee? Añade las banderas de memoria en tiempo de ejecución al mismo comando setup:

```bash
llm_wiki project setup \
  --yes \
  --with-understand-anything \
  --install-understand-anything \
  --understand-anything-platform codex \
  --run-cognee \
  --install-cognee
```

## Equivalente manual

Se prefiere la ruta de configuración administrada. Si intencionalmente quieres usar UA fuera de LLM-Wiki, ejecuta primero Understand Anything dentro de tu entorno de agente:

```bash
/understand
```

Luego ejecuta `llm_wiki project setup --with-understand-anything` para que LLM-Wiki registre la fuente de proyección markdown. Los archivos JSON directos se mantienen como artefactos complementarios sin procesar, no como rutas fuente introducidas a mano.

```bash
llm_wiki project setup --with-understand-anything
llm_wiki project compile
llm_wiki project build-site
```

Si también quieres memoria local de sesiones de agente:

```bash
llm_wiki project sessions discover --import
llm_wiki project build-site
```

## Posible puente futuro

Un puente opcional futuro podría mapear el schema de grafo de Understand Anything a la typed graph ontology de LLM-Wiki de forma más directa.

Mapeo probable:

| Understand Anything | dirección de LLM-Wiki |
|---|---|
| `project` | metadatos de repositorio/proyecto |
| `nodes[type=file]` | nodos de fuente/documento/archivo |
| `nodes[type=function]` | nodos de función/símbolo de código |
| `nodes[type=class]` | nodos de clase/símbolo de código |
| `nodes[type=module]` | nodos de módulo/paquete |
| `nodes[type=concept]` | nodos de concepto |
| `edges[type=imports]` | aristas de importaciones/dependencias |
| `edges[type=contains]` | aristas de contención |
| `edges[type=calls]` | aristas de llamada/referencia |
| `layers[]` | metadatos de agrupación de arquitectura |
| `tour[]` | páginas de onboarding/síntesis |

Mantén este puente opcional y externo salvo que ambos proyectos acuerden un contrato de intercambio estable.

## Principio de colaboración

No presentes LLM-Wiki como reemplazo de Understand Anything.

Un mejor encuadre:

- Understand Anything ayuda a un desarrollador a entender una base de código ahora.
- LLM-Wiki ayuda a los agentes a recordar, buscar, citar, actualizar y publicar conocimiento del proyecto con el tiempo.
