"""Structural assertions on the client JS bundle.

We have no headless browser; these tests are intentionally cheap checks that
the assembled ``JS_BUNDLE`` carries the right hooks for the wiki frontend's
keyboard shortcuts, theme toggle, search palette, and 3D graph wiring.

If ``node`` is on PATH the bundle is also piped through ``node --check`` to
catch template-literal / string-escaping mistakes that would otherwise only
surface in a browser.
"""

from __future__ import annotations

import shutil
import subprocess

import pytest

from llm_wiki.site.js import (
    JS_BUNDLE,
    JS_GRAPH,
    JS_SEARCH_PALETTE,
    JS_THEME_TOGGLE,
)


# ---------------------------------------------------------------------------
# Theme toggle
# ---------------------------------------------------------------------------

def test_bundle_wires_data_toggle_theme_clicks():
    assert "data-toggle-theme" in JS_BUNDLE
    # The handler closes on the click target with that selector and toggles.
    assert "closest" in JS_THEME_TOGGLE
    assert "data-theme" in JS_THEME_TOGGLE


def test_bundle_uses_llm_wiki_theme_localstorage_key():
    assert "llm-wiki-theme" in JS_BUNDLE
    assert "localStorage" in JS_BUNDLE


def test_bundle_follows_prefers_color_scheme():
    assert "prefers-color-scheme" in JS_BUNDLE


def test_bundle_updates_aria_label_on_theme_toggle():
    assert "aria-label" in JS_THEME_TOGGLE


# ---------------------------------------------------------------------------
# Search palette
# ---------------------------------------------------------------------------

def test_bundle_fetches_search_index_json():
    assert "search-index.json" in JS_BUNDLE
    assert "fetch(" in JS_SEARCH_PALETTE


def test_bundle_keyboard_shortcuts_present():
    # cmd+k / ctrl+k variants
    assert "metaKey" in JS_BUNDLE and "ctrlKey" in JS_BUNDLE
    # the literal '/' shortcut
    assert "'/'" in JS_BUNDLE
    # Escape
    assert "'Escape'" in JS_BUNDLE
    # Graph view shortcuts
    assert "'f'" in JS_BUNDLE
    assert "'r'" in JS_BUNDLE
    assert "'2'" in JS_BUNDLE
    assert "'3'" in JS_BUNDLE


def test_bundle_handles_data_open_search_buttons():
    assert "data-open-search" in JS_BUNDLE


def test_bundle_palette_arrow_navigation():
    assert "ArrowDown" in JS_SEARCH_PALETTE
    assert "ArrowUp" in JS_SEARCH_PALETTE
    assert "Enter" in JS_SEARCH_PALETTE


def test_bundle_palette_recents_storage():
    assert "llm-wiki-recents" in JS_BUNDLE


# ---------------------------------------------------------------------------
# 3D graph view
# ---------------------------------------------------------------------------

def test_bundle_cursor_anchored_zoom():
    # A wheel listener is the load-bearing piece for cursor-anchored zoom.
    assert "addEventListener('wheel'" in JS_GRAPH or 'addEventListener("wheel"' in JS_GRAPH
    # Raycaster from cursor position is how we anchor zoom on the cursor.
    assert "Raycaster" in JS_GRAPH
    assert "setFromCamera" in JS_GRAPH


def test_bundle_link_hover_wired():
    assert "linkHoverPrecision" in JS_GRAPH
    assert "onLinkHover" in JS_GRAPH


def test_bundle_node_labels_present_in_both_modes():
    assert "nodeThreeObject" in JS_GRAPH
    assert "nodeCanvasObject" in JS_GRAPH


def test_bundle_edge_labels_present():
    assert "linkThreeObject" in JS_GRAPH or "linkCanvasObject" in JS_GRAPH


def test_bundle_fit_uses_engine_stop_and_camera_position():
    assert "onEngineStop" in JS_GRAPH
    assert "cameraPosition" in JS_GRAPH


def test_bundle_day_filter_listener():
    assert "data-graph-filter-day" in JS_GRAPH or "data-day-click" in JS_GRAPH


# ---------------------------------------------------------------------------
# JS parses
# ---------------------------------------------------------------------------

def test_bundle_parses_with_node_if_available():
    if not shutil.which("node"):
        pytest.skip("node binary not on PATH")
    proc = subprocess.run(
        ["node", "--check", "-"],
        input=JS_BUNDLE,
        text=True,
        capture_output=True,
        timeout=15,
    )
    assert proc.returncode == 0, (
        "node --check rejected JS_BUNDLE:\n" + proc.stderr
    )
