from pathlib import Path
import shutil
import subprocess
import sys
from typing import cast
import tomllib


def main():
    stdout = subprocess.check_output(["git", "status", "--porcelain"])
    if stdout != b"":
        print("cannot continue, git working tree must be clean")
        sys.exit(1)

    projectfile = tomllib.loads(Path("pyproject.toml").read_text())
    version = cast(str, projectfile["project"]["version"])
    print("This script will make a release for version:", version)
    print("You must first update CHANGELOG.md and pyproject.toml with the new version. Then, make a release commit with these changes.")
    print("Press enter to continue")
    input()

    print("Creating git tag")
    subprocess.check_call(["git", "tag", f"v{version}"])

    print("Pushing git tag")
    subprocess.check_call(["git", "push", "origin", f"v{version}"])

    print("Compiling translations")
    subprocess.check_call([sys.executable, "-m", "babel.messages.frontend", "compile", "-d", "raphson_mp/translations"])

    print("Building wheel")
    if Path("dist").is_dir():
        shutil.rmtree("dist")
    subprocess.check_call([sys.executable, "-m", "build"])

    print("Uploading release to PyPi")
    subprocess.check_call([sys.executable, "-m", "twine", "upload", f"dist/raphson_mp-{version}.tar.gz", f"dist/raphson_mp-{version}-py3-none-any.whl"])

    print("Building containers")
    subprocess.check_call(["podman", "build", "-t", f"codeberg.org/raphson/music-server:{version}", "--target", "prod", "."])
    subprocess.check_call(["podman", "build", "-t", f"codeberg.org/raphson/music-server-nginx:{version}", "-f", "Containerfile.nginx", "."])

    print("Pushing containers")
    subprocess.check_call(["podman", "push", f"codeberg.org/raphson/music-server:{version}"])
    subprocess.check_call(["podman", "push", f"codeberg.org/raphson/music-server-nginx:{version}"])


if __name__ == "__main__":
    main()
