class Zpace < Formula
  include Language::Python::Virtualenv

  desc "A CLI tool to discover what's consuming your disk space"
  homepage "https://github.com/AzisK/Zpace"
  url "https://files.pythonhosted.org/packages/source/z/zpace/zpace-0.4.2.tar.gz"
  sha256 "20f4d43c1954ee09fcb8fd1a81c9005ce6028bac94ab7b5196ab402386b7a569"
  license "Apache-2.0"

  depends_on "python"

  resource "argparse" do
    url "https://files.pythonhosted.org/packages/18/dd/e617cfc3f6210ae183374cd9f6a26b20514bbb5a792af97949c5aacddf0f/argparse-1.4.0.tar.gz"
    sha256 "20f4d43c1954ee09fcb8fd1a81c9005ce6028bac94ab7b5196ab402386b7a569"
  end

  resource "tqdm" do
    url "https://files.pythonhosted.org/packages/a7/81/7f3dce7bfed3f4d5a228e679aa06d28b72c8e1f56d35e5c8a36cfed7a2ab/tqdm-4.67.1.tar.gz"
    sha256 "20f4d43c1954ee09fcb8fd1a81c9005ce6028bac94ab7b5196ab402386b7a569"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"zpace", "--help"
  end
end
