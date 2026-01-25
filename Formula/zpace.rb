class Zpace < Formula
  include Language::Python::Virtualenv

  desc "A CLI tool to discover what's consuming your disk space"
  homepage "https://github.com/AzisK/Zpace"
  url "https://files.pythonhosted.org/packages/source/z/zpace/zpace-0.4.4.tar.gz"
  sha256 "54d6c2f7caee33e9910c697b8eb5fddd4339c90ac0e45ae3dd1225706ec7843a"
  license "Apache-2.0"

  depends_on "python"

  resource "argparse" do
    url "https://files.pythonhosted.org/packages/18/dd/e617cfc3f6210ae183374cd9f6a26b20514bbb5a792af97949c5aacddf0f/argparse-1.4.0.tar.gz"
    sha256 "54d6c2f7caee33e9910c697b8eb5fddd4339c90ac0e45ae3dd1225706ec7843a"
  end

  resource "tqdm" do
    url "https://files.pythonhosted.org/packages/a7/81/7f3dce7bfed3f4d5a228e679aa06d28b72c8e1f56d35e5c8a36cfed7a2ab/tqdm-4.67.1.tar.gz"
    sha256 "54d6c2f7caee33e9910c697b8eb5fddd4339c90ac0e45ae3dd1225706ec7843a"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"zpace", "--help"
  end
end
