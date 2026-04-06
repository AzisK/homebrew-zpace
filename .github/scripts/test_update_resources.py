#!/usr/bin/env python3
"""Tests for update_resources.py — run with: pytest"""

import subprocess
import sys
import textwrap
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))
from update_resources import update_formula

FORMULA_BASE = textwrap.dedent("""\
    class Zpace < Formula
      include Language::Python::Virtualenv

      desc "A CLI tool to discover what's consuming your disk space"
      homepage "https://github.com/AzisK/Zpace"
      url "https://files.pythonhosted.org/packages/source/z/zpace/zpace-0.5.0.tar.gz"
      sha256 "abc123"
      license "Apache-2.0"

      depends_on "python"

      def install
        virtualenv_install_with_resources
      end

      test do
        system bin/"zpace", "--help"
      end
    end
""")

POET_OUTPUT = (
    '  resource "tqdm" do\n'
    '    url "https://files.pythonhosted.org/packages/tqdm-4.67.3.tar.gz"\n'
    '    sha256 "deadbeef"\n'
    '  end'
)


def apply(formula: str, blocks: str, tmp_path: Path) -> str:
    path = tmp_path / "zpace.rb"
    path.write_text(formula)
    update_formula(str(path), blocks)
    return path.read_text()


# ------------------------------------------------------------------ #
# Indentation: resource blocks must use correct 2/4-space indentation
# ------------------------------------------------------------------ #
def test_resource_indentation_is_correct(tmp_path):
    result = apply(FORMULA_BASE, POET_OUTPUT, tmp_path)
    assert '  resource "tqdm" do' in result, "resource line should have 2-space indent"
    assert '    url "' in result,            "url line should have 4-space indent"
    assert '    sha256 "' in result,         "sha256 line should have 4-space indent"
    assert '    resource "tqdm" do' not in result, "resource line must not be double-indented"
    assert '      url "' not in result,      "url line must not be double-indented"


# ------------------------------------------------------------------ #
# def install: simple case — content gets replaced
# ------------------------------------------------------------------ #
def test_install_replaced_with_virtualenv_helper(tmp_path):
    formula = FORMULA_BASE.replace(
        "    virtualenv_install_with_resources",
        '    venv = virtualenv_create(libexec, "python3")\n    venv.pip_install_and_link buildpath',
    )
    result = apply(formula, POET_OUTPUT, tmp_path)
    assert "virtualenv_install_with_resources" in result
    assert "virtualenv_create" not in result
    assert "pip_install_and_link" not in result


# ------------------------------------------------------------------ #
# def install: nested end must not be matched prematurely
# ------------------------------------------------------------------ #
def test_install_with_nested_block(tmp_path):
    formula = FORMULA_BASE.replace(
        "    virtualenv_install_with_resources",
        "    if OS.mac?\n      do_something\n    end\n    virtualenv_install_with_resources",
    )
    result = apply(formula, POET_OUTPUT, tmp_path)
    lines = result.splitlines()
    # test block must survive intact after def install's closing end
    install_end_idx = next(
        i for i, l in enumerate(lines)
        if l == "  end" and i > lines.index("  def install")
    )
    test_idx = next(i for i, l in enumerate(lines) if "test do" in l)
    assert install_end_idx < test_idx, "test block appears before def install's end — nested end was matched early"
    assert "virtualenv_install_with_resources" in result


# ------------------------------------------------------------------ #
# Resource replacement: existing blocks are removed and re-inserted
# ------------------------------------------------------------------ #
def test_existing_resources_are_replaced(tmp_path):
    formula_with_old = FORMULA_BASE.replace(
        "\n  def install",
        '\n  resource "old-dep" do\n    url "https://old.example.com/old-1.0.tar.gz"\n    sha256 "oldsha"\n  end\n\n  def install',
    )
    new_blocks = textwrap.dedent("""\
      resource "tqdm" do
        url "https://files.pythonhosted.org/packages/tqdm-4.67.3.tar.gz"
        sha256 "newsha"
      end""")
    result = apply(formula_with_old, new_blocks, tmp_path)
    assert "old-dep" not in result
    assert "tqdm" in result
    assert "newsha" in result
    assert result.count('resource "') == 1


# ------------------------------------------------------------------ #
# sha256 awk: only the package sha256 appears before resource blocks
# ------------------------------------------------------------------ #
def test_awk_updates_only_package_sha256(tmp_path):
    formula_with_resource = FORMULA_BASE.replace(
        "\n  def install",
        '\n  resource "tqdm" do\n    url "https://example.com/tqdm.tar.gz"\n    sha256 "resource_sha"\n  end\n\n  def install',
    )
    lines = formula_with_resource.splitlines()
    sha_lines = [(i, l) for i, l in enumerate(lines) if '  sha256 "' in l]
    assert sha_lines[0][1].strip().startswith('sha256'), "first sha256 should be the package sha256"
    assert "resource_sha" in sha_lines[1][1]


# ------------------------------------------------------------------ #
# Idempotency: running the update twice produces identical output
# ------------------------------------------------------------------ #
def test_idempotent(tmp_path):
    result1 = apply(FORMULA_BASE, POET_OUTPUT, tmp_path)
    result2 = apply(result1, POET_OUTPUT, tmp_path)
    assert result1 == result2, "update_formula is not idempotent"


# ------------------------------------------------------------------ #
# No double blank lines anywhere in the output
# ------------------------------------------------------------------ #
def test_no_double_blank_lines(tmp_path):
    result = apply(FORMULA_BASE, POET_OUTPUT, tmp_path)
    assert "\n\n\n" not in result, "double blank line found in formula output"


# ------------------------------------------------------------------ #
# sed anchor: resource URLs containing zpace-X.Y.Z.tar.gz are untouched
# ------------------------------------------------------------------ #
def test_sed_anchor_does_not_corrupt_resource_urls(tmp_path):
    formula = FORMULA_BASE.replace(
        "  def install",
        '  resource "something" do\n    url "https://evil.com/zpace-0.5.0.tar.gz"\n    sha256 "evil"\n  end\n\n  def install',
    )
    rb = tmp_path / "zpace.rb"
    rb.write_text(formula)
    subprocess.run(
        ["sed", "-i.bak", "/^  url/s|zpace-[0-9.]*\\.tar\\.gz|zpace-0.6.0.tar.gz|", str(rb)],
        check=True,
    )
    result = rb.read_text()
    assert "zpace-0.6.0.tar.gz" in result, "main URL was not updated"
    assert "evil.com/zpace-0.5.0.tar.gz" in result, "resource URL was incorrectly modified"
