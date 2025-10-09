import os
import argparse
import subprocess
import shutil
from pathlib import Path


def build(no_mpi, native_only):
    # Build without MPI
    if no_mpi:
        os.environ["USE_MPI"] = "OFF"
    # Set environment variable for OpenMP on macOS
    if os.name == "posix" and shutil.which("brew"):
        brew_prefix = subprocess.run(
            ["brew", "--prefix"], capture_output=True, text=True
        ).stdout.strip()
        os.environ["OpenMP_ROOT"] = str(Path(brew_prefix, "opt", "libomp"))
    if native_only:
        build_folder = "dist-native-only"
        if not os.path.exists(build_folder):
            os.makedirs(build_folder)
        os.chdir(build_folder)
        subprocess.run(["cmake", "../src/qupled/native/src"], check=True)
        subprocess.run(["cmake", "--build", "."], check=True)
    else:
        subprocess.run(["python3", "-m", "build"], check=True)
    print("Build completed.")


def get_wheel_file():
    wheel_file = list(Path().rglob("qupled*.whl"))
    if not wheel_file:
        print("No .whl files found. Ensure the package is built first.")
        return None
    else:
        return str(wheel_file[0])


def run_tox(environment):
    tox_path = Path(".tox")
    if tox_path.exists():
        shutil.rmtree(tox_path)
    wheel_file = get_wheel_file()
    if wheel_file is not None:
        os.environ["WHEEL_FILE"] = wheel_file
        subprocess.run(["tox", "-e", environment], check=True)


def test(no_native):
    if no_native:
        run_tox("no_native")
    else:
        run_tox("test")


def examples():
    run_tox("examples")


def format_code():
    subprocess.run(["black", "."], check=True)
    native_files_folder = Path("src", "qupled", "native")
    cpp_files = list(native_files_folder.rglob("*.cpp"))
    hpp_files = list(native_files_folder.rglob("*.hpp"))
    for f in cpp_files + hpp_files:
        subprocess.run(["clang-format", "--style=file", "-i", str(f)], check=True)


def docs():
    subprocess.run(["sphinx-build", "-b", "html", "docs", str(Path("docs", "_build"))])


def clean():
    folders_to_clean = [
        Path("dist"),
        Path("dist-native-only"),
        Path("src", "qupled.egg-info"),
        Path("docs", "_build"),
    ]
    for folder in folders_to_clean:
        if folder.exists():
            print(f"Removing folder: {folder}")
            shutil.rmtree(folder)


def install():
    wheel_file = get_wheel_file()
    if wheel_file is not None:
        subprocess.run(["pip", "uninstall", "-y", wheel_file], check=True)
        subprocess.run(["pip", "install", wheel_file], check=True)


def install_dependencies():
    print("Installing dependencies...")
    script_dir = Path(__file__).resolve().parent
    pip_requirements = script_dir / "requirements-pip.txt"
    if os.name == "posix":
        if shutil.which("apt-get"):
            _install_with_apt(script_dir / "requirements-apt.txt")
        elif shutil.which("brew"):
            _install_with_brew(script_dir / "requirements-brew.txt")
        else:
            print("Unsupported package manager. Please install dependencies manually.")
    else:
        print("Unsupported operating system. Please install dependencies manually.")
    subprocess.run(["pip", "install", "-r", str(pip_requirements)], check=True)


def _install_with_apt(apt_requirements):
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    with apt_requirements.open("r") as apt_file:
        subprocess.run(
            ["xargs", "sudo", "apt-get", "install", "-y"],
            stdin=apt_file,
            check=True,
        )


def _install_with_brew(brew_requirements):
    subprocess.run(["brew", "update"], check=True)
    subprocess.run(["brew", "bundle", f"--file={brew_requirements}"], check=True)


def update_version(build_version):
    pyproject_file = Path("pyproject.toml")
    if not pyproject_file.exists():
        return
    with pyproject_file.open("r") as file:
        content = file.readlines()
    with pyproject_file.open("w") as file:
        for line in content:
            if line.startswith("version = "):
                file.write(f'version = "{build_version}"')
                file.write("\n")
            else:
                file.write(line)


def run():
    parser = argparse.ArgumentParser(
        description="""A utility script for building, testing, formatting,
        and generating documentation for the qupled project."""
    )

    subparsers = parser.add_subparsers(dest="command", help="Sub-command to run")

    # Build command
    build_parser = subparsers.add_parser("build", help="Build the qupled package")
    build_parser.add_argument(
        "--no_mpi",
        action="store_true",
        help="Build without MPI support (default: False).",
    )
    build_parser.add_argument(
        "--native-only",
        action="store_true",
        help="Build only native code in C++ (default: False).",
    )

    # Test command
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument(
        "--no-native",
        action="store_true",
        help="Exclude the tests for the native classes (default: False).",
    )

    # Update version command
    version_parser = subparsers.add_parser(
        "update-version", help="Update package version"
    )
    version_parser.add_argument("build_version", help="The new version number.")

    # Other commands
    subparsers.add_parser("clean", help="Clean up build artifacts")
    subparsers.add_parser("docs", help="Generate documentation")
    subparsers.add_parser("examples", help="Run tests for the examples")
    subparsers.add_parser("format", help="Format the source code")
    subparsers.add_parser("install", help="Install the qupled package")
    subparsers.add_parser("install-deps", help="Install system dependencies")

    args = parser.parse_args()

    if args.command == "build":
        build(args.no_mpi, args.native_only)
    elif args.command == "clean":
        clean()
    elif args.command == "docs":
        docs()
    elif args.command == "examples":
        examples()
    elif args.command == "format":
        format_code()
    elif args.command == "install":
        install()
    elif args.command == "test":
        test(args.no_native)
    elif args.command == "install-deps":
        install_dependencies()
    elif args.command == "update-version":
        update_version(args.build_version)
    else:
        parser.print_help()


if __name__ == "__main__":
    run()
