#!/usr/bin/env python3
"""Update resource blocks in Formula/zpace.rb using homebrew-pypi-poet.

Usage:
    python update_resources.py <package> <formula_path> [version]

Example:
    python update_resources.py zpace Formula/zpace.rb 0.6.0
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from typing import Optional


def get_resource_blocks(package: str, version: Optional[str] = None) -> str:
    pkg_spec = f"{package}=={version}" if version else package
    with tempfile.TemporaryDirectory() as tmpdir:
        venv = os.path.join(tmpdir, "venv")
        subprocess.run(["uv", "venv", venv], check=True, capture_output=True)
        subprocess.run(
            ["uv", "pip", "install", "--python", venv, pkg_spec],
            check=True,
            capture_output=True,
        )
        installed = json.loads(subprocess.run(
            ["uv", "pip", "list", "--python", venv, "--format", "json"],
            capture_output=True, text=True, check=True,
        ).stdout)

    blocks = []
    for dep in installed:
        name, dep_version = dep["name"], dep["version"]
        if name.lower() == package.lower():
            continue
        with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/{dep_version}/json") as resp:
            urls = json.loads(resp.read())["urls"]
        sdist = next((u for u in urls if u["packagetype"] == "sdist"), None)
        if not sdist:
            raise RuntimeError(f"No sdist found for {name}=={dep_version} on PyPI")
        blocks.append(
            f'  resource "{name}" do\n'
            f'    url "{sdist["url"]}"\n'
            f'    sha256 "{sdist["digests"]["sha256"]}"\n'
            f'  end'
        )
    return "\n\n".join(blocks)


def update_formula(formula_path: str, resource_blocks: str) -> None:
    with open(formula_path) as f:
        content = f.read()

    # Remove all existing resource blocks
    content = re.sub(
        r'\n  resource "[^"]*" do\n(?:.*\n)*?  end\n',
        "\n",
        content,
    )

    # Insert new resource blocks before def install
    content = content.replace("\n  def install", f"\n{resource_blocks}\n\n  def install", 1)

    # Ensure virtualenv_install_with_resources pattern is used
    content = re.sub(
        r"(  def install\n).*?(\n  end)",
        r"\1    virtualenv_install_with_resources\2",
        content,
        count=1,
        flags=re.DOTALL,
    )

    # Normalise any double blank lines left by removal/insertion
    content = re.sub(r'\n{3,}', '\n\n', content)

    with open(formula_path, "w") as f:
        f.write(content)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: {sys.argv[0]} <package> <formula_path> [version]")
        sys.exit(1)

    package = sys.argv[1]
    formula_path = sys.argv[2]
    version = sys.argv[3] if len(sys.argv) > 3 else None

    print(f"Fetching resources for {package}{f'=={version}' if version else ''} ...")
    blocks = get_resource_blocks(package, version)
    print(blocks)

    print(f"\nUpdating {formula_path} ...")
    update_formula(formula_path, blocks)
    print("Done.")
