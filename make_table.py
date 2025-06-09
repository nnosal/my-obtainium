# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "rich",
#   "pyyaml",  # AJOUT
# ]
# ///
import sys
import json
import os
import urllib.parse
from pathlib import Path
from collections import defaultdict
from rich import print
import yaml  # AJOUT

# ========== CONFIGURATION ==========
SRC_JSON = "src/export-obtainium.json"
OVERRIDE_YAML = "src/applications.yml"  # AJOUT
MINIFIED_JSON = "obtainium.json"
TABLE_MD = "pages/table.md"
README_MD = "README.md"
README_SECTIONS = [
    "pages/init.md",
    "pages/faq.md",
    TABLE_MD,
    "pages/development.md",
]
BADGE_SRC = "https://raw.githubusercontent.com/ImranR98/Obtainium/main/assets/graphics/badge_obtainium.png"
# ===================================


def make_obtainium_link(app: dict) -> str:
    """
    Créé le badge/URL pour une obtainium app
    """
    payload = {
        "id": app["id"],
        "url": app["url"],
        "author": app["author"],
        "name": app["name"],
        "categories": app["categories"],
        "preferredApkIndex": app.get("preferredApkIndex", 0),
        "additionalSettings": app.get("additionalSettings", ""),
    }
    encoded = urllib.parse.quote(json.dumps(payload), safe="")
    return f"http://apps.obtainium.imranr.dev/redirect.html?r=obtainium://app/{encoded}"


def get_display_name(app: dict) -> str:
    return app.get("meta", {}).get("nameOverride") or app.get("name", "")

def get_application_url(app: dict) -> str:
    return app.get("meta", {}).get("urlOverride") or app.get("url", "")

def make_repo_link(url: str) -> str:
    if not url:
        return "—"

    parsed = urllib.parse.urlparse(url)
    netloc = parsed.netloc.lower()
    path = parsed.path.strip("/")
    query = urllib.parse.parse_qs(parsed.query)

    if "github.com" in netloc:
        parts = path.split("/")
        if len(parts) >= 2:
            owner_repo = "/".join(parts[:2])
            return f'<a href="{url}">🐙 {owner_repo}</a>'

    elif "gitlab.com" in netloc:
        return f'<a href="{url}">🦊 {path}</a>'

    elif "codeberg.org" in netloc:
        return f'<a href="{url}">🌐 {path}</a>'

    elif "f-droid.org" in netloc or "fdroid" in path:
        pkg_name = query.get("appId", [None])[0] or path.split("/")[-1]
        return f'<a href="{url}">📦 {pkg_name}</a>'

    elif "openapk.net" in netloc or "openapk.dev" in netloc:
        return f'<a href="{url}">📥 OpenAPK</a>'

    # Fallback générique
    return f'<a href="{url}">🔗 link</a>'

def generate_table(apps: list[dict]) -> str:
    categorized = defaultdict(list)
    for app in apps:
        for category in app.get("categories", ["Autres"]):
            categorized[category].append(app)

    output = ["## 📱 Liste des Applications\n"]
    i=0
    for category in sorted(categorized.keys(), key=str.lower):
        openstr = "open" if i == 0 else ""
        if i == 0: i = 1
        output.append(f"<details {openstr}>\n<summary> <h3 style=\"display:inline-block;\">&nbsp; 🏷️ {category}</h3> </summary>\n")
        output.append("")
        output.append("| Application | Description | Add to Obtainium | ? |")
        output.append("|-------------|-------------|------------------|----------|")

        for app in sorted(categorized[category], key=get_display_name):
            meta = app.get("meta", {})
            if meta.get("excludeFromTable", False):
                continue

            name = get_display_name(app)
            url = get_application_url(app)
            about = json.loads(app.get("additionalSettings", "{}")).get("about", "").replace("|", "\\|") or "—"

            name_link = f'<a href="{url}">{name}</a>'
            repo_url = app.get("url", "")
            repo_md = f'<a href="{repo_url}">{repo_url}</a>'

            badge_html = (
                f'<a href="{make_obtainium_link(app)}">'
                f'<img src="{BADGE_SRC}" height="30" alt="Get it on Obtainium">'
                f'</a>'
            )

            included = "✅" if not meta.get("excludeFromExport", False) else "❌"

            output.append(f"| {name} ({make_repo_link(repo_url)}) | {about} | {badge_html} | {included} |")

        output.append("\n</details>\n")

    return "\n".join(output)

def generate_readme(sections: list[str], output_file: str = "README.md") -> None:
    combined = []
    for file in sections:
        if not Path(file).exists():
            print(f"[red]❌ Fichier manquant : {file}[/red]")
            sys.exit(1)
        content = Path(file).read_text(encoding="utf-8").strip()
        combined.append(content)

    Path(output_file).write_text("\n\n".join(combined) + "\n", encoding="utf-8")
    print(f"[green]✅ README généré : {output_file}[/green]")


def just_minify_json(input_file: str, output_file: str) -> None:
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    if "apps" in data:
        filtered = []
        for app in data["apps"]:
            meta = app.get("meta", {})
            if not meta.get("excludeFromExport", False):
                app.pop("meta", None)
                filtered.append(app)
        data["apps"] = filtered

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"), ensure_ascii=False)

    print(f"[green]✅ JSON minifié : {output_file} ({len(data.get('apps', []))} apps)[/green]")

def apps_minify_json(apps: list[dict], output_file: str) -> None:
    """Génère le JSON minifié à partir de la liste d'apps modifiée"""
    filtered_apps = []
    for app in apps:
        # Vérifie si l'app doit être exclue
        if not app.get("meta", {}).get("excludeFromExport", False):
            # Crée une copie sans les métadonnées
            app_copy = app.copy()
            app_copy.pop("meta", None)
            filtered_apps.append(app_copy)
    
    data = {"apps": filtered_apps}
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, separators=(",", ":"), ensure_ascii=False)
    
    print(f"[green]✅ JSON minifié : {output_file} ({len(filtered_apps)} apps)[/green]")

def apply_overrides(apps: list[dict], override_file: str) -> list[dict]:
    """Applique les overrides depuis le fichier YAML"""
    if not Path(override_file).exists():
        print(f"[yellow]⚠️ Fichier override introuvable: {override_file}[/yellow]")
        return apps
    
    with open(override_file, "r", encoding="utf-8") as f:
        override_data = yaml.safe_load(f)
    
    override_apps = override_data.get("apps", [])
    
    # Créer un index des applications existantes
    app_index = {app["id"]: app for app in apps}
    
    for override in override_apps:
        app_id = override["id"]
        
        if app_id in app_index:
            # Fusion des métadonnées
            current_meta = app_index[app_id].get("meta", {})
            new_meta = override.get("meta", {})
            app_index[app_id]["meta"] = {**current_meta, **new_meta}
            
            # Mise à jour des champs standards
            for key in ["name", "url", "author", "categories", "preferredApkIndex", "additionalSettings"]:
                if key in override:
                    app_index[app_id][key] = override[key]
        else:
            # Ajout d'une nouvelle application
            apps.append(override)
            print(f"[green]✅ Ajout nouvelle app: {app_id}[/green]")
    
    return apps

def clean_json_data(file_path: str):
    """
    Ouvre un fichier JSON, supprimer la clé '.settings.github-creds' si elle existe.
    """
    try:
        print(f"[bold blue]🔎 Tentative de nettoyage de '{file_path}'...[/bold blue]")
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"[bold magenta]Info:[/bold magenta] Clés de niveau racine dans le JSON: {list(data.keys())}")

        # Vérifie si '.settings' existe au niveau racine
        if "settings" in data:
            print(f"[bold magenta]Info:[/bold magenta] Clé '.settings' trouvée.")
            settings_data = data["settings"]
            print(f"[bold magenta]Info:[/bold magenta] Clés sous '.settings': {list(settings_data.keys())}")

            # Vérifie si 'github-creds' existe sous '.settings'
            if "github-creds" in settings_data:
                del settings_data["github-creds"]
                print(f"[bold green]✓[/bold green] Clé '.settings.github-creds' supprimée de {file_path}")
            else:
                print(f"[bold yellow]![/bold yellow] Clé 'github-creds' non trouvée sous '.settings' dans {file_path}. Aucune modification nécessaire.")
        else:
            print(f"[bold yellow]![/bold yellow] Clé '.settings' non trouvée au niveau racine dans {file_path}. Aucune modification nécessaire.")

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"[bold green]✓[/bold green] Fichier '{file_path}' mis à jour.")

    except FileNotFoundError:
        print(f"[bold red]✗[/bold red] Erreur: Le fichier '{file_path}' n'a pas été trouvé. Assurez-vous que le chemin est correct et que le fichier existe.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[bold red]✗[/bold red] Erreur: Le fichier '{file_path}' n'est pas un JSON valide. Veuillez vérifier sa syntaxe. Détails: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"[bold red]✗[/bold red] Une erreur inattendue est survenue lors du traitement de '{file_path}': {e}")
        sys.exit(1)


def main():
    print("[bold blue]📦 Génération Obtainium Pack[/bold blue]")

    clean_json_data(SRC_JSON)

    with open(SRC_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    apps = data.get("apps", [])
    
    # AJOUT: Application des overrides
    print("[cyan]🔄 Application des overrides YAML...[/cyan]")
    apps = apply_overrides(apps, OVERRIDE_YAML)

    # Génération du tableau
    print("[cyan]📝 Génération du tableau markdown...[/cyan]")
    table_md = generate_table(apps)
    Path(TABLE_MD).write_text(table_md, encoding="utf-8")

    # Minification JSON
    print("[cyan]📉 Minification du JSON...[/cyan]")
    #just_minify_json(data.get("apps", []), MINIFIED_JSON)
    apps_minify_json(apps, MINIFIED_JSON)

    # Génération du README final
    print("[cyan]📚 Construction du README...[/cyan]")
    generate_readme(README_SECTIONS, README_MD)

if __name__ == "__main__":
    main()