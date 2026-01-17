class Zpace < Formula
  include Language::Python::Virtualenv

  desc "A CLI tool to discover what's consuming your disk space"
  homepage "https://github.com/AzisK/Zpace"
  url "https://files.pythonhosted.org/packages/source/z/zpace/zpace-0.4.1.tar.gz"
  sha256 "6acad731b676b9e77731630a530e96bf83992609c3e77226077c959f1d8ff1cf"
  license "Apache-2.0"

  depends_on "python"

  resource "argparse" do
    url "https://files.pythonhosted.org/packages/18/dd/e617cfc3f6210ae183374cd9f6a26b20514bbb5a792af97949c5aacddf0f/argparse-1.4.0.tar.gz"
    sha256 "62b089a55be1d8949cd2bc7e0df0bddb9e028faefc8c32038cc84862aefdd6e4"
  end

  resource "tqdm" do
    url "https://files.pythonhosted.org/packages/a7/81/7f3dce7bfed3f4d5a228e679aa06d28b72c8e1f56d35e5c8a36cfed7a2ab/tqdm-4.67.1.tar.gz"
    sha256 "f8aef9c52c08c13a65f30ea34f4e5aac3fd1a34959b7f74b0e277a39c7a40de0"
  end

  def install
    virtualenv_install_with_resources
  end

  test do
    system bin/"zpace", "--help"
  end
end
