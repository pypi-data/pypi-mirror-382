#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil
from pathlib import Path
import tempfile
import tarfile
import urllib.request
import platform
import json


def refresh_shell_environment():
    """Refresh shell environment by sourcing profile files"""
    home = Path.home()
    shell_profiles = [home / ".bashrc", home / ".zshrc", home / ".profile"]

    for profile in shell_profiles:
        if profile.exists():
            try:
                result = subprocess.run(
                    f"source {profile} && echo $PATH",
                    shell=True,
                    capture_output=True,
                    text=True,
                    executable="/bin/bash",
                )
                if result.returncode == 0 and result.stdout.strip():
                    new_path = result.stdout.strip()
                    if new_path != os.environ.get("PATH", ""):
                        os.environ["PATH"] = new_path
                        print(f"Updated PATH from {profile}")
                        break
            except Exception as e:
                print(f"Failed to source {profile}: {e}")


def install_noirup():
    """Install noirup if not present"""
    if shutil.which("noirup"):
        print("noirup already installed")
        return True

    print("Installing noirup...")
    try:
        result = subprocess.run(
            [
                "curl",
                "-L",
                "https://raw.githubusercontent.com/noir-lang/noirup/main/install",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            print(f"Failed to download noirup installer: {result.stderr}")
            return False

        process = subprocess.Popen(
            ["bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input=result.stdout)

        if process.returncode != 0:
            print(f"Failed to install noirup: {stderr}")
            return False

        home = Path.home()
        noirup_bin = home / ".noirup" / "bin"
        if noirup_bin.exists():
            os.environ["PATH"] = f"{noirup_bin}:{os.environ['PATH']}"

        return True
    except Exception as e:
        print(f"Error installing noirup: {e}")
        return False


def install_nargo():
    """Install nargo using noirup"""
    if shutil.which("nargo"):
        print("nargo already installed")
        return True

    print("Installing nargo...")
    try:
        home = Path.home()
        noirup_cmd = str(home / ".nargo" / "bin" / "noirup")

        result = subprocess.run(
            [noirup_cmd, "--version", "1.0.0-beta.12"], capture_output=True, text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error installing nargo: {e}")
        return False


def install_bbup():
    """Install bbup if not present"""
    if shutil.which("bbup"):
        print("bbup already installed")
        return True

    print("Installing bbup...")
    try:
        result = subprocess.run(
            [
                "curl",
                "-L",
                "https://raw.githubusercontent.com/AztecProtocol/aztec-packages/refs/heads/master/barretenberg/bbup/install",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        if result.returncode != 0:
            print(f"Failed to download bbup installer: {result.stderr}")
            return False

        process = subprocess.Popen(
            ["bash"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        stdout, stderr = process.communicate(input=result.stdout)

        if process.returncode != 0:
            print(f"Failed to install bbup: {stderr}")
            return False

        home = Path.home()
        for bin_dir in [".bbup/bin", "bin", ".local/bin"]:
            bbup_bin = home / bin_dir
            if bbup_bin.exists():
                os.environ["PATH"] = f"{bbup_bin}:{os.environ['PATH']}"

        return True
    except Exception as e:
        print(f"Error installing bbup: {e}")
        return False


def install_bb():
    """Install bb using bbup"""
    if shutil.which("bb"):
        print("bb already installed")
        return True

    print("Installing bb...")
    try:
        home = Path.home()
        bbup_cmd = str(home / ".bb" / "bbup")

        if not Path(bbup_cmd).exists():
            print(f"bbup not found at {bbup_cmd}")
            return False

        versions_to_try = ["0.87.0"]

        for version in versions_to_try:
            print(f"Trying bb version {version}...")
            result = subprocess.run(
                [bbup_cmd, "--version", version], capture_output=True, text=True
            )

            if result.returncode == 0:
                bb_path = str(home / ".bb" / "bb")
                if Path(bb_path).exists():
                    test_result = subprocess.run(
                        [bb_path, "--version"],
                        capture_output=True,
                        text=True,
                    )
                    if test_result.returncode == 0:
                        print(f"Successfully installed bb version {version}")
                        return True
                    elif (
                        "GLIBC" in test_result.stderr or "GLIBCXX" in test_result.stderr
                    ):
                        print(
                            f"Version {version} has incompatible GLIBC requirements, trying pre-built binary..."
                        )
                        if download_prebuilt_bb():
                            return True
                        print(
                            "Pre-built binary not available, trying compilation from source..."
                        )
                        return compile_bb_from_source()
            else:
                print(f"Failed to install version {version}: {result.stderr}")

        print("Could not find a compatible bb version")
        return False
    except Exception as e:
        print(f"Error installing bb: {e}")
        return False


def download_prebuilt_bb():
    """Download pre-built bb binary from GitHub releases"""
    print("Downloading pre-built bb binary...")
    try:
        machine = platform.machine().lower()
        if machine in ["x86_64", "amd64"]:
            arch = "linux-x86_64"
        elif machine in ["aarch64", "arm64"]:
            arch = "linux-aarch64"
        else:
            print(f"Unsupported architecture: {machine}")
            return False

        repo_url = "https://api.github.com/repos/inference-labs-inc/bb/releases"

        try:
            response = urllib.request.urlopen(repo_url)
            releases = json.loads(response.read().decode())

            bb_release = None
            for release in releases:
                if release["tag_name"].startswith("bb-v0.87.0"):
                    bb_release = release
                    break

            if not bb_release:
                print("No pre-built bb releases found")
                return False

            bb_asset = None
            ubuntu_version = (
                platform.release().split(".")[0]
                if platform.system() == "Linux"
                else "22"
            )
            ubuntu_codename = f"ubuntu{ubuntu_version}04"

            for asset in bb_release["assets"]:
                if asset["name"] == f"bb-{arch}-{ubuntu_codename}":
                    bb_asset = asset
                    break

            if not bb_asset:
                for asset in bb_release["assets"]:
                    if asset["name"] == f"bb-{arch}-ubuntu2204":
                        bb_asset = asset
                        break

            if not bb_asset:
                print(
                    f"No bb binary found for architecture: {arch} with Ubuntu {ubuntu_version}.04"
                )
                return False

            print(f"Downloading bb binary for {arch}...")
            bb_dir = Path.home() / ".bb"
            bb_dir.mkdir(exist_ok=True)
            bb_path = bb_dir / "bb"

            urllib.request.urlretrieve(bb_asset["browser_download_url"], bb_path)
            bb_path.chmod(0o755)

            test_result = subprocess.run(
                [str(bb_path), "--version"], capture_output=True, text=True
            )
            if test_result.returncode != 0:
                print("Downloaded bb binary failed version check")
                return False

            print("Successfully downloaded and installed pre-built bb binary")
            return True

        except Exception as e:
            print(f"Failed to download pre-built binary: {e}")
            return False

    except Exception as e:
        print(f"Error downloading pre-built bb: {e}")
        return False


def compile_bb_from_source():
    """Fallback: compile bb from source (requires build tools)"""
    print("Compiling bb from source as fallback...")
    print("Note: This requires build tools (cmake, ninja, clang-18) to be installed")
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            print("Downloading aztec packages v0.87.0...")
            url = "https://github.com/AztecProtocol/aztec-packages/archive/refs/tags/v0.87.0.tar.gz"
            tar_path = temp_path / "v0.87.0.tar.gz"

            urllib.request.urlretrieve(url, tar_path)

            print("Extracting source code...")
            with tarfile.open(tar_path, "r:gz") as tar:
                tar.extractall(temp_path)

            cpp_dir = temp_path / "aztec-packages-0.87.0" / "barretenberg" / "cpp"
            build_dir = cpp_dir / "build"
            build_dir.mkdir(exist_ok=True)

            print("Configuring build with cmake...")
            cmake_cmd = [
                "cmake",
                "..",
                "-DCMAKE_BUILD_TYPE=Release",
                "-DTESTING=OFF",
                "-DBENCHMARK=OFF",
                "-DFUZZING=OFF",
            ]

            if shutil.which("ninja"):
                cmake_cmd.append("-GNinja")
                build_cmd = ["ninja", "bb"]
            else:
                build_cmd = ["make", "bb", "-j4"]

            result = subprocess.run(
                cmake_cmd, cwd=build_dir, capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"CMake configuration failed: {result.stderr}")
                return False

            print("Building bb (this may take several minutes)...")
            result = subprocess.run(
                build_cmd, cwd=build_dir, capture_output=True, text=True
            )
            if result.returncode != 0:
                print(f"Build failed: {result.stderr}")
                return False

            bb_bin = build_dir / "bin" / "bb"
            if not bb_bin.exists():
                print("Built bb binary not found")
                return False

            test_result = subprocess.run(
                [str(bb_bin), "--version"], capture_output=True, text=True
            )
            if test_result.returncode != 0:
                print("Built bb binary failed version check")
                return False

            bb_dir = Path.home() / ".bb"
            bb_dir.mkdir(exist_ok=True)

            shutil.copy2(bb_bin, bb_dir / "bb")

            print("Successfully compiled and installed bb from source")
            return True

    except Exception as e:
        print(f"Error compiling bb from source: {e}")
        return False


def main():
    if os.environ.get("POP_SKIP_INSTALL"):
        return

    success = True

    if not install_noirup():
        success = False
    else:
        refresh_shell_environment()
        if not install_nargo():
            success = False

    if not install_bbup():
        success = False
    else:
        refresh_shell_environment()
        if not install_bb():
            success = False

    if not success:
        print(
            "Some dependencies failed to install. You may need to install them manually."
        )
        print("See install.sh for manual installation steps.")
        sys.exit(1)


if __name__ == "__main__":
    main()
