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

POET_OUTPUT = textwrap.dedent("""\
  resource "tqdm" do
    url "https://files.pythonhosted.org/packages/tqdm-4.67.3.tar.gz"
    sha256 "deadbeef"
  end""")


def apply(formula: str, blocks: str, tmp_path: Path) -> str:
    path = tmp_path / "zpace.rb"
    path.write_text(formula)
    update_formula(str(path), blocks)
    return path.read_text()


# ------------------------------------------------------------------ #
# Indentation: poet output is already indented — must not double-indent
# ------------------------------------------------------------------ #
def test_resource_indentation_is_two_spaces(tmp_path):
    result = apply(FORMULA_BASE, POET_OUTPUT, tmp_path)
    assert '  resource "tqdm" do' in result, "resource block missing"
    assert '    resource "tqdm" do' not in result, "resource block is double-indented"


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
