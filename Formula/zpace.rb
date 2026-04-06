class Zpace < Formula
  include Language::Python::Virtualenv

  desc "A CLI tool to discover what's consuming your disk space"
  homepage "https://github.com/AzisK/Zpace"
  url "https://files.pythonhosted.org/packages/source/z/zpace/zpace-0.5.0.tar.gz"
  sha256 "82d4ddade5491eeaa5e364a5107466ed86890c15061af91d2c8df7c5b91e454f"
  license "Apache-2.0"

  depends_on "python"

  def install
    venv = virtualenv_create(libexec, "python3")
    venv.pip_install_and_link buildpath
  end

  test do
    system bin/"zpace", "--help"
  end
end
