"""Tests for ``tesserae.site.code_link_rewriter``.

The rewriter turns markdown links that target source-code files
(``[cli.py](../tesserae/cli.py)``) into absolute GitHub blob URLs at
compile time. The audit on the dogfood corpus found 505 dangling
internal hrefs of this shape; the rewriter is how we fix them at the
source.
"""

from __future__ import annotations

from tesserae.site.code_link_rewriter import (
    derive_blob_base,
    looks_like_code_file_target,
    resolve_to_repo_relative,
    rewrite_code_links,
)


# ----------------------------------------------------------------------
# looks_like_code_file_target
# ----------------------------------------------------------------------


def test_looks_like_code_file_target_recognizes_extensions():
    assert looks_like_code_file_target("tesserae/cli.py") is True
    assert looks_like_code_file_target("tesserae/site/pages.py") is True
    assert looks_like_code_file_target("../pyproject.toml") is True
    assert looks_like_code_file_target("Dockerfile") is True
    assert looks_like_code_file_target("foo.toml") is True
    # ``.json`` is data, not code, per spec — bare json files are
    # NOT classified as code. ``package.json`` is special-cased via
    # ``_CODE_FILENAMES`` and IS classified as code (covered below).
    assert looks_like_code_file_target("foo.json") is False


def test_looks_like_code_file_target_skips_content_and_external():
    assert looks_like_code_file_target("concepts/rlhf.html") is False
    assert looks_like_code_file_target("../sources/foo.html") is False
    assert looks_like_code_file_target("https://github.com/x/y") is False
    assert looks_like_code_file_target("#anchor") is False
    assert looks_like_code_file_target("") is False
    # Common non-code mediums must be skipped.
    assert looks_like_code_file_target("assets/diagram.svg") is False
    assert looks_like_code_file_target("assets/style.css") is False
    assert looks_like_code_file_target("assets/screenshot.png") is False


def test_looks_like_code_file_target_special_filenames():
    # Known config / build filenames without code extensions still
    # qualify as "code files" — they're not content pages.
    assert looks_like_code_file_target("Makefile") is True
    assert looks_like_code_file_target("foo/bar/Dockerfile") is True
    assert looks_like_code_file_target("../package.json") is True
    assert looks_like_code_file_target("Cargo.toml") is True


# ----------------------------------------------------------------------
# resolve_to_repo_relative
# ----------------------------------------------------------------------


def test_resolve_to_repo_relative_handles_dotdot_segments():
    # link from docs/feature-map.md
    assert (
        resolve_to_repo_relative("../tesserae/cli.py", source_path="docs/feature-map.md")
        == "tesserae/cli.py"
    )
    # link from docs/i18n/feature-map.zh.md needs an extra ..
    assert (
        resolve_to_repo_relative(
            "../../tesserae/cli.py", source_path="docs/i18n/feature-map.zh.md"
        )
        == "tesserae/cli.py"
    )
    # link with bare filename from same-dir source
    assert (
        resolve_to_repo_relative("cli.py", source_path="tesserae/feature-map.md")
        == "tesserae/cli.py"
    )


def test_resolve_to_repo_relative_skips_absolute_and_external():
    assert resolve_to_repo_relative("/abs/path.py", source_path="docs/x.md") is None
    assert resolve_to_repo_relative("https://example.com/x.py", source_path="docs/x.md") is None
    assert resolve_to_repo_relative("", source_path="docs/x.md") is None


# ----------------------------------------------------------------------
# rewrite_code_links
# ----------------------------------------------------------------------


def test_rewrite_code_links_replaces_only_code_targets():
    html = (
        '<p><a href="../tesserae/cli.py">cli.py</a> '
        'and <a href="concepts/rlhf.html">rlhf</a></p>'
    )
    out = rewrite_code_links(
        html,
        source_path="docs/feature-map.md",
        github_blob_base="https://github.com/ca1773130n/Tesserae/blob/main",
    )
    assert "https://github.com/ca1773130n/Tesserae/blob/main/tesserae/cli.py" in out
    # Content-page href is left untouched.
    assert 'href="concepts/rlhf.html"' in out


def test_rewrite_code_links_is_no_op_when_base_missing():
    html = '<a href="../tesserae/cli.py">x</a>'
    assert (
        rewrite_code_links(html, source_path="docs/x.md", github_blob_base=None) == html
    )
    assert (
        rewrite_code_links(html, source_path="docs/x.md", github_blob_base="") == html
    )


def test_rewrite_code_links_handles_i18n_source_paths_correctly():
    """English and i18n source pages must produce the same final URL for
    the same logical link, regardless of how many ``../`` segments the
    markdown uses to escape its containing directory."""
    base = "https://github.com/ca1773130n/Tesserae/blob/main"
    en = rewrite_code_links(
        '<a href="../tesserae/cli.py">x</a>',
        source_path="docs/feature-map.md",
        github_blob_base=base,
    )
    zh = rewrite_code_links(
        '<a href="../../tesserae/cli.py">x</a>',
        source_path="docs/i18n/feature-map.zh.md",
        github_blob_base=base,
    )
    assert f'{base}/tesserae/cli.py' in en
    assert f'{base}/tesserae/cli.py' in zh


def test_rewrite_code_links_preserves_external_urls():
    base = "https://github.com/ca1773130n/Tesserae/blob/main"
    html = (
        '<a href="https://github.com/foo/bar/blob/main/x.py">external</a>'
        '<a href="mailto:user@example.com">mail</a>'
        '<a href="#anchor">anchor</a>'
    )
    out = rewrite_code_links(html, source_path="docs/x.md", github_blob_base=base)
    assert out == html  # all hrefs untouched


def test_rewrite_code_links_handles_trailing_slash_in_base():
    base = "https://github.com/ca1773130n/Tesserae/blob/main/"
    html = '<a href="../tesserae/cli.py">x</a>'
    out = rewrite_code_links(html, source_path="docs/x.md", github_blob_base=base)
    # No double-slash between the base and the resolved path.
    assert "blob/main/tesserae/cli.py" in out
    assert "blob/main//tesserae" not in out


def test_rewrite_code_links_dockerfile_target():
    base = "https://github.com/ca1773130n/Tesserae/blob/main"
    html = '<a href="../Dockerfile">Dockerfile</a>'
    out = rewrite_code_links(html, source_path="docs/x.md", github_blob_base=base)
    assert f"{base}/Dockerfile" in out


# ----------------------------------------------------------------------
# derive_blob_base
# ----------------------------------------------------------------------


def test_derive_blob_base_from_repo_url():
    assert (
        derive_blob_base(github_repo_url="https://github.com/ca1773130n/Tesserae")
        == "https://github.com/ca1773130n/Tesserae/blob/main"
    )


def test_derive_blob_base_explicit_override_wins():
    explicit = "https://github.com/ca1773130n/Tesserae/blob/develop"
    assert (
        derive_blob_base(
            github_repo_url="https://github.com/ca1773130n/Tesserae",
            github_blob_base=explicit,
        )
        == explicit
    )


def test_derive_blob_base_returns_none_when_unset():
    assert derive_blob_base() is None
    assert derive_blob_base(github_repo_url=None, github_blob_base=None) is None
    assert derive_blob_base(github_repo_url="", github_blob_base="") is None


def test_derive_blob_base_supports_custom_default_ref():
    assert (
        derive_blob_base(
            github_repo_url="https://github.com/foo/bar",
            default_ref="release/v1",
        )
        == "https://github.com/foo/bar/blob/release/v1"
    )
