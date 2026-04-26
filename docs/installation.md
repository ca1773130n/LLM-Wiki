# Installation

LLM-Wiki is installable as a Python package and exposes shell commands so users do not have to run `python3 -m llm_wiki.cli` manually.

## Quick install

```bash
curl -fsSL https://raw.githubusercontent.com/ca1773130n/LLM-Wiki/main/scripts/install.sh | bash
```

The installer is intentionally similar to modern CLI installers:

1. clone or update the repository;
2. create a project-local `.venv` by default;
3. run `pip install -e` so local source changes are reflected immediately;
4. write `llm_wiki` and `llm-wiki` command wrappers into `~/.local/bin`;
5. optionally append `~/.local/bin` to shell rc files.

## Local checkout install

```bash
git clone https://github.com/ca1773130n/LLM-Wiki.git
cd LLM-Wiki
./scripts/install.sh --dir "$PWD"
```

If you do not want the installer to edit shell startup files:

```bash
./scripts/install.sh --dir "$PWD" --skip-shell-config
```

Then either restart the shell or run:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

## Installer options

```bash
./scripts/install.sh --help
```

Supported options:

| Option | Purpose |
| --- | --- |
| `--dir PATH` | Install or update the checkout at `PATH`. |
| `--branch NAME` | Install a specific branch. |
| `--repo URL` | Override the Git repository URL. Useful for forks or local smoke tests. |
| `--bin-dir PATH` | Write command wrappers somewhere other than `~/.local/bin`. |
| `--no-venv` | Install into the current Python environment instead of creating `.venv`. |
| `--skip-shell-config` | Avoid editing `.zshrc` / `.bashrc`. |

## Commands installed

```bash
llm_wiki --help
llm-wiki --help
llm_wiki_mcp --help
```

The canonical command in docs is `llm_wiki`.

## Optional dependencies

The default package is intentionally light. Optional integrations require their own dependencies:

```bash
python3 -m pip install --user kuzu cognee graphiti-core
```

- `kuzu` enables Kuzu graph persistence.
- `cognee` enables direct Cognee import/cognify workflows.
- `graphiti-core` enables live Graphiti/Neo4j sync; `export-graphiti` and `sync-graphiti --dry-run` do not require it.

## Verify installation

```bash
llm_wiki project init --help
llm_wiki project compile --help
llm_wiki project build-site --help
```
