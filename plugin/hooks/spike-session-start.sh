#!/usr/bin/env bash
# Phase 0 spike — touch a marker file on every SessionStart so we can
# confirm hook registration works. Always exit 0 so a missing /tmp dir
# can never block a session.
set -u
: > /tmp/tesserae-plugin-spike-ran 2>/dev/null || true
exit 0
