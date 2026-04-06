#!/usr/bin/env python3
"""Update resource blocks in Formula/zpace.rb using homebrew-pypi-poet.

Usage:
    python update_resources.py <package> <formula_path> [version]

Example:
    python update_resources.py zpace Formula/zpace.rb 0.6.0
"""

import os
import re
import subprocess
import sys
from typing import Optional


def get_resource_blocks(package: str, version: Optional[str] = None) -> str:
    pkg_spec = f"{package}=={version}" if version else package
    result = subprocess.run(
        ["uvx", "--from", "homebrew-pypi-poet", "--with", pkg_spec, "poet", package],
        stdout=subprocess.PIPE,
        text=True,
        check=True,
    )
    return result.stdout.strip()


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
    indented = "\n".join(f"  {line.lstrip()}" if line.strip() else "" for line in resource_blocks.splitlines())
    content = content.replace("\n  def install", f"\n{indented}\n\n  def install", 1)

    # Ensure virtualenv_install_with_resources pattern is used
    content = re.sub(
        r"(  def install\n).*?(\n  end)",
        r"\1    virtualenv_install_with_resources\2",
        content,
        count=1,
        flags=re.DOTALL,
    )

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
