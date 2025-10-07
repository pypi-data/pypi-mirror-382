import shutil, json, os
from datetime import datetime
from pathlib import Path as P
from .__pre_init__ import cli


def current_file_dir(file: str) -> str:
    return P(file).parent.resolve()


def ls(folder: P) -> list[P]:
    return [f for f in folder.iterdir() if not f.name.startswith(".")]


def Info(msg: str):
    print(f"[INFO] {msg}")


def read_json(file: P) -> dict:
    with open(file, "r") as f:
        return json.load(f)


def write_json(file: P, data: dict):
    if not file.parent.exists():
        file.parent.mkdir(parents=True, exist_ok=True)
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def read_lines(file: P) -> list[str]:
    with open(file, "r") as f:
        return f.readlines()


def append_lines(file: P, lines: list[str]):
    if not file.parent.exists():
        file.parent.mkdir(parents=True, exist_ok=True)
    if not file.exists():
        with open(file, "w") as f:
            pass
    with open(file, "a") as f:
        f.writelines(lines)


@cli.command()
def update_prompts(dry_run: bool = False):
    # Track files that are created/copied
    added_files = []

    def copy(src_fldr: P, dst_fldr: P):
        for f in ls(src_fldr):
            to = dst_fldr / f.name
            Info(f"Updating {f} to {to}")

            if dry_run:
                continue

            if f.is_file():
                shutil.copy(f, to)
                added_files.append(str(to))
            elif f.is_dir():
                shutil.copytree(f, to, dirs_exist_ok=True)
                added_files.append(str(to))

    # Try local assets first (for packaged version), then fall back to root assets (for development)
    cwd = current_file_dir(__file__)
    local_assets = cwd / "assets"
    root_assets = cwd.parent.parent / "assets"

    if root_assets.exists():
        assets_dir = root_assets
        Info("Using development assets from project root")
    elif local_assets.exists():
        assets_dir = local_assets
        Info("Using packaged assets")
    else:
        raise FileNotFoundError(
            "Assets directory not found in either local or root location"
        )

    # Remove existing .daksh folder before copying
    daksh_dest = P(".daksh")
    if daksh_dest.exists():
        Info("Removing existing .daksh folder")
        if not dry_run:
            shutil.rmtree(daksh_dest)

    copy(assets_dir / "daksh-prompts", daksh_dest)

    if P(".vscode/settings.json").exists():
        settings = read_json(P(".vscode/settings.json"))
    else:
        settings = {}

    chat_mode_files_locations = settings.get("chat.modeFilesLocations", {})
    chat_mode_files_locations[".daksh/prompts/**/"] = True
    settings["chat.modeFilesLocations"] = chat_mode_files_locations
    write_json(P(".vscode/settings.json"), settings)
    added_files.append(".vscode/settings.json")

    if os.path.exists(".github/copilot-instructions.md"):
        if (
            input(
                "Found an existing .github/copilot-instructions.md should we back it up? [y/N]: "
            ).lower()
            != "y"
        ):
            Info("Skipping backup")
        else:
            bkp = f".github/copilot-instructions.md.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
            Info(f"Backing up existing .github/copilot-instructions.md to {bkp}")
            shutil.copy(".github/copilot-instructions.md", bkp)
            added_files.append(bkp)
    if not os.path.exists(".github"):
        os.makedirs(".github")
    shutil.copy(
        assets_dir / "copilot-instructions.md", ".github/copilot-instructions.md"
    )
    added_files.append(".github/copilot-instructions.md")

    shutil.copy(assets_dir / "mkdocs.yml", "mkdocs.yml")
    added_files.append("mkdocs.yml")

    os.makedirs("docs/overrides", exist_ok=True)
    shutil.copy(assets_dir / "extra.css", "docs/overrides/extra.css")
    added_files.append("docs/overrides/extra.css")

    shutil.copytree(assets_dir / "overrides", "./overrides", dirs_exist_ok=True)
    added_files.append("./overrides")

    if not os.path.exists("docs/index.md"):
        shutil.copy(assets_dir / "index.md", "docs/index.md")
        added_files.append("docs/index.md")

    # Display summary of added files
    print("\n📁 Files added to current working directory:")
    for file in added_files:
        print(f"   ✓ {file}")
    print(f"\nTotal: {len(added_files)} files/directories added or updated\n")
