from __future__ import annotations

from typing import TYPE_CHECKING, Final, Literal, TypedDict
import xml.etree.ElementTree as ET

from jinjarope import iconfilters, icons


if TYPE_CHECKING:
    import os


Rotation = Literal["90", "180", "270", 90, 180, 270, "-90", 1, 2, 3]
Flip = Literal["horizontal", "vertical", "horizontal,vertical"]


class AsciiIconMapping(TypedDict):
    icon: str
    color: str


ICONIFY_ICONS: Final[dict[str, AsciiIconMapping]] = {
    # Programming Languages - Main
    "py": {"icon": "logos:python", "color": "#3776AB"},
    "pyc": {"icon": "logos:python", "color": "#3776AB"},
    "pyx": {"icon": "logos:python", "color": "#3776AB"},
    "pyd": {"icon": "logos:python", "color": "#3776AB"},
    "pyi": {"icon": "logos:python", "color": "#3776AB"},
    "pyw": {"icon": "logos:python", "color": "#3776AB"},
    "js": {"icon": "logos:javascript", "color": "#F7DF1E"},
    "mjs": {"icon": "logos:javascript", "color": "#F7DF1E"},
    "cjs": {"icon": "logos:javascript", "color": "#F7DF1E"},
    "ts": {"icon": "logos:typescript-icon", "color": "#3178C6"},
    "tsx": {"icon": "logos:react", "color": "#61DAFB"},
    "jsx": {"icon": "logos:react", "color": "#61DAFB"},
    # Programming Languages - JVM
    "java": {"icon": "logos:java", "color": "#007396"},
    "class": {"icon": "logos:java", "color": "#007396"},
    "jar": {"icon": "logos:java", "color": "#007396"},
    "gradle": {"icon": "logos:gradle", "color": "#02303A"},
    "groovy": {"icon": "logos:groovy", "color": "#4298B8"},
    "kt": {"icon": "logos:kotlin", "color": "#7F52FF"},
    "kts": {"icon": "logos:kotlin", "color": "#7F52FF"},
    "scala": {"icon": "logos:scala", "color": "#DC322F"},
    "clj": {"icon": "logos:clojure", "color": "#5881D8"},
    # Programming Languages - C-family
    "c": {"icon": "logos:c", "color": "#A8B9CC"},
    "h": {"icon": "logos:c", "color": "#A8B9CC"},
    "cpp": {"icon": "logos:c-plusplus", "color": "#00599C"},
    "hpp": {"icon": "logos:c-plusplus", "color": "#00599C"},
    "cc": {"icon": "logos:c-plusplus", "color": "#00599C"},
    "hh": {"icon": "logos:c-plusplus", "color": "#00599C"},
    "cs": {"icon": "logos:c-sharp", "color": "#239120"},
    "csx": {"icon": "logos:c-sharp", "color": "#239120"},
    # Programming Languages - Other
    "go": {"icon": "logos:go", "color": "#00ADD8"},
    "rs": {"icon": "logos:rust", "color": "#000000"},
    "rb": {"icon": "logos:ruby", "color": "#CC342D"},
    "erb": {"icon": "logos:ruby", "color": "#CC342D"},
    "rake": {"icon": "logos:ruby", "color": "#CC342D"},
    "php": {"icon": "logos:php", "color": "#777BB4"},
    "swift": {"icon": "logos:swift", "color": "#FA7343"},
    "perl": {"icon": "logos:perl", "color": "#39457E"},
    "pl": {"icon": "logos:perl", "color": "#39457E"},
    "r": {"icon": "logos:r-lang", "color": "#276DC3"},
    "lua": {"icon": "logos:lua", "color": "#000080"},
    "ex": {"icon": "logos:elixir", "color": "#9B30FF"},
    "exs": {"icon": "logos:elixir", "color": "#9B30FF"},
    "erl": {"icon": "logos:erlang", "color": "#A90533"},
    "hrl": {"icon": "logos:erlang", "color": "#A90533"},
    "hs": {"icon": "logos:haskell-icon", "color": "#5D4F85"},
    "elm": {"icon": "logos:elm", "color": "#1293D8"},
    "f90": {"icon": "vscode-icons:file-type-fortran", "color": "#4D41B1"},
    "f95": {"icon": "vscode-icons:file-type-fortran", "color": "#4D41B1"},
    "jl": {"icon": "logos:julia", "color": "#9558B2"},
    # Web Technologies
    "html": {"icon": "logos:html-5", "color": "#E34F26"},
    "htm": {"icon": "logos:html-5", "color": "#E34F26"},
    "xhtml": {"icon": "logos:html-5", "color": "#E34F26"},
    "css": {"icon": "logos:css-3", "color": "#1572B6"},
    "scss": {"icon": "logos:sass", "color": "#CC6699"},
    "sass": {"icon": "logos:sass", "color": "#CC6699"},
    "less": {"icon": "logos:less", "color": "#1D365D"},
    "styl": {"icon": "logos:stylus", "color": "#333333"},
    "vue": {"icon": "logos:vue", "color": "#4FC08D"},
    "svelte": {"icon": "logos:svelte-icon", "color": "#FF3E00"},
    "astro": {"icon": "logos:astro", "color": "#FF5D01"},
    "liquid": {"icon": "logos:liquid", "color": "#7AB55C"},
    "pug": {"icon": "logos:pug", "color": "#A86454"},
    "jade": {"icon": "logos:pug", "color": "#A86454"},
    # Shell and Scripts
    "sh": {"icon": "logos:terminal", "color": "#4EAA25"},
    "bash": {"icon": "logos:bash-icon", "color": "#4EAA25"},
    "zsh": {"icon": "logos:terminal", "color": "#4EAA25"},
    "fish": {"icon": "logos:terminal", "color": "#4EAA25"},
    "ps1": {"icon": "logos:powershell", "color": "#5391FE"},
    "psm1": {"icon": "logos:powershell", "color": "#5391FE"},
    "psd1": {"icon": "logos:powershell", "color": "#5391FE"},
    "bat": {"icon": "vscode-icons:file-type-bat", "color": "#C1F12E"},
    "cmd": {"icon": "vscode-icons:file-type-bat", "color": "#C1F12E"},
    # Data Formats
    "json": {"icon": "vscode-icons:file-type-json", "color": "#000000"},
    "json5": {"icon": "vscode-icons:file-type-json", "color": "#000000"},
    "jsonc": {"icon": "vscode-icons:file-type-json", "color": "#000000"},
    "yaml": {"icon": "vscode-icons:file-type-yaml", "color": "#CB171E"},
    "yml": {"icon": "vscode-icons:file-type-yaml", "color": "#CB171E"},
    "xml": {"icon": "vscode-icons:file-type-xml", "color": "#0D47A1"},
    "plist": {"icon": "vscode-icons:file-type-plist", "color": "#0D47A1"},
    "csv": {"icon": "vscode-icons:file-type-csv", "color": "#217346"},
    "tsv": {"icon": "vscode-icons:file-type-csv", "color": "#217346"},
    "sql": {"icon": "vscode-icons:file-type-sql", "color": "#CC2927"},
    "sqlite": {"icon": "vscode-icons:file-type-sqlite", "color": "#0F80CC"},
    "db": {"icon": "vscode-icons:file-type-sql", "color": "#CC2927"},
    "graphql": {"icon": "logos:graphql", "color": "#E10098"},
    "gql": {"icon": "logos:graphql", "color": "#E10098"},
    # Documentation
    "md": {"icon": "logos:markdown", "color": "#000000"},
    "mdx": {"icon": "logos:markdown", "color": "#000000"},
    "rst": {"icon": "vscode-icons:file-type-rst", "color": "#000000"},
    "txt": {"icon": "vscode-icons:file-type-text", "color": "#000000"},
    "pdf": {"icon": "vscode-icons:file-type-pdf2", "color": "#FB1F1F"},
    "doc": {"icon": "vscode-icons:file-type-word", "color": "#2B579A"},
    "docx": {"icon": "vscode-icons:file-type-word", "color": "#2B579A"},
    "odt": {"icon": "vscode-icons:file-type-word", "color": "#2B579A"},
    "rtf": {"icon": "vscode-icons:file-type-word", "color": "#2B579A"},
    "tex": {"icon": "vscode-icons:file-type-tex", "color": "#3D6117"},
    "latex": {"icon": "vscode-icons:file-type-tex", "color": "#3D6117"},
    "wiki": {"icon": "vscode-icons:file-type-wiki", "color": "#000000"},
    # Configuration Files
    "toml": {"icon": "vscode-icons:file-type-toml", "color": "#000000"},
    "ini": {"icon": "vscode-icons:file-type-config", "color": "#000000"},
    "conf": {"icon": "vscode-icons:file-type-config", "color": "#000000"},
    "cfg": {"icon": "vscode-icons:file-type-config", "color": "#000000"},
    "env": {"icon": "vscode-icons:file-type-env", "color": "#000000"},
    "properties": {"icon": "vscode-icons:file-type-properties", "color": "#000000"},
    "prop": {"icon": "vscode-icons:file-type-properties", "color": "#000000"},
    "settings": {"icon": "vscode-icons:file-type-settings", "color": "#000000"},
    "editorconfig": {"icon": "vscode-icons:file-type-editorconfig", "color": "#000000"},
    "babelrc": {"icon": "logos:babel", "color": "#F9DC3E"},
    "eslintrc": {"icon": "logos:eslint", "color": "#4B32C3"},
    "eslintignore": {"icon": "logos:eslint", "color": "#4B32C3"},
    "prettierrc": {"icon": "logos:prettier", "color": "#56B3B4"},
    "stylelintrc": {"icon": "logos:stylelint", "color": "#263238"},
    # Build and Package Files
    "dockerfile": {"icon": "logos:docker-icon", "color": "#2496ED"},
    "dockerignore": {"icon": "logos:docker-icon", "color": "#2496ED"},
    "vagrantfile": {"icon": "logos:vagrant", "color": "#1563FF"},
    "package.json": {"icon": "logos:npm-icon", "color": "#CB3837"},
    "package-lock.json": {"icon": "logos:npm-icon", "color": "#CB3837"},
    "yarn.lock": {"icon": "logos:yarn", "color": "#2C8EBB"},
    "requirements.txt": {"icon": "logos:python", "color": "#3776AB"},
    "pipfile": {"icon": "logos:python", "color": "#3776AB"},
    "pipfile.lock": {"icon": "logos:python", "color": "#3776AB"},
    "poetry.lock": {"icon": "vscode-icons:file-type-python", "color": "#3776AB"},
    "pyproject.toml": {"icon": "vscode-icons:file-type-python", "color": "#3776AB"},
    "setup.py": {"icon": "logos:python", "color": "#3776AB"},
    "cargo.toml": {"icon": "logos:rust", "color": "#000000"},
    "cargo.lock": {"icon": "logos:rust", "color": "#000000"},
    "gemfile": {"icon": "logos:ruby", "color": "#CC342D"},
    "gemfile.lock": {"icon": "logos:ruby", "color": "#CC342D"},
    "makefile": {"icon": "vscode-icons:file-type-makefile", "color": "#000000"},
    "cmake": {"icon": "logos:cmake", "color": "#064F8C"},
    "rakefile": {"icon": "logos:ruby", "color": "#CC342D"},
    # Version Control
    "git": {"icon": "logos:git-icon", "color": "#F05032"},
    "gitignore": {"icon": "logos:git-icon", "color": "#F05032"},
    "gitattributes": {"icon": "logos:git-icon", "color": "#F05032"},
    "gitmodules": {"icon": "logos:git-icon", "color": "#F05032"},
    "hg": {"icon": "logos:mercurial", "color": "#999999"},
    "hgignore": {"icon": "logos:mercurial", "color": "#999999"},
    "svn": {"icon": "vscode-icons:file-type-svn", "color": "#809CC9"},
    # Images and Media
    "png": {"icon": "vscode-icons:file-type-image", "color": "#FFB13B"},
    "jpg": {"icon": "vscode-icons:file-type-image", "color": "#FFB13B"},
    "jpeg": {"icon": "vscode-icons:file-type-image", "color": "#FFB13B"},
    "gif": {"icon": "vscode-icons:file-type-image", "color": "#FFB13B"},
    "bmp": {"icon": "vscode-icons:file-type-image", "color": "#FFB13B"},
    "tiff": {"icon": "vscode-icons:file-type-image", "color": "#FFB13B"},
    "webp": {"icon": "vscode-icons:file-type-image", "color": "#FFB13B"},
    "svg": {"icon": "vscode-icons:file-type-svg", "color": "#FFB13B"},
    "ico": {"icon": "vscode-icons:file-type-favicon", "color": "#FFB13B"},
    "mp3": {"icon": "vscode-icons:file-type-audio", "color": "#FF8A65"},
    "wav": {"icon": "vscode-icons:file-type-audio", "color": "#FF8A65"},
    "ogg": {"icon": "vscode-icons:file-type-audio", "color": "#FF8A65"},
    "mp4": {"icon": "vscode-icons:file-type-video", "color": "#FF8A65"},
    "avi": {"icon": "vscode-icons:file-type-video", "color": "#FF8A65"},
    "mov": {"icon": "vscode-icons:file-type-video", "color": "#FF8A65"},
    "webm": {"icon": "vscode-icons:file-type-video", "color": "#FF8A65"},
    # Archives and Compression
    "zip": {"icon": "vscode-icons:file-type-zip", "color": "#FFA000"},
    "rar": {"icon": "vscode-icons:file-type-rar", "color": "#FFA000"},
    "7z": {"icon": "vscode-icons:file-type-zip", "color": "#FFA000"},
    "tar": {"icon": "vscode-icons:file-type-tar", "color": "#FFA000"},
    "gz": {"icon": "vscode-icons:file-type-zip", "color": "#FFA000"},
    "bz2": {"icon": "vscode-icons:file-type-zip", "color": "#FFA000"},
    "xz": {"icon": "vscode-icons:file-type-zip", "color": "#FFA000"},
    "iso": {"icon": "vscode-icons:file-type-iso", "color": "#FFA000"},
    # Fonts
    "ttf": {"icon": "vscode-icons:file-type-font", "color": "#FF5252"},
    "otf": {"icon": "vscode-icons:file-type-font", "color": "#FF5252"},
    "woff": {"icon": "vscode-icons:file-type-font", "color": "#FF5252"},
    "woff2": {"icon": "vscode-icons:file-type-font", "color": "#FF5252"},
    "eot": {"icon": "vscode-icons:file-type-font", "color": "#FF5252"},
    # 3D and Design
    "blend": {"icon": "logos:blender", "color": "#F5792A"},
    "obj": {"icon": "vscode-icons:file-type-3d", "color": "#3B3B3B"},
    "stl": {"icon": "vscode-icons:file-type-3d", "color": "#3B3B3B"},
    "fbx": {"icon": "vscode-icons:file-type-3d", "color": "#3B3B3B"},
    "dae": {"icon": "vscode-icons:file-type-3d", "color": "#3B3B3B"},
    "3ds": {"icon": "vscode-icons:file-type-3d", "color": "#3B3B3B"},
    "psd": {"icon": "logos:adobe-photoshop", "color": "#31A8FF"},
    "ai": {"icon": "logos:adobe-illustrator", "color": "#FF9A00"},
    "sketch": {"icon": "logos:sketch", "color": "#F7B500"},
    "fig": {"icon": "logos:figma", "color": "#F24E1E"},
    # Others
    "lock": {"icon": "carbon:locked", "color": "#000000"},
    "log": {"icon": "vscode-icons:file-type-log", "color": "#000000"},
    "bak": {"icon": "vscode-icons:file-type-backup", "color": "#000000"},
    "tmp": {"icon": "vscode-icons:file-type-temp", "color": "#000000"},
    "swp": {"icon": "vscode-icons:file-type-temp", "color": "#000000"},
    "desktop": {"icon": "vscode-icons:file-type-linux", "color": "#000000"},
}


def get_path_icon(path: str | os.PathLike[str]) -> str:
    """Get the icon mapping for a given file path or directory.

    Args:
        path: Path to the file or directory

    Returns:
        iconify icon slug
    """
    import upath

    path_obj = upath.UPath(path)

    # Handle directories
    if path_obj.is_dir():
        return {"icon": "vscode-icons:default-folder", "color": "#90A4AE"}["icon"]

    # Special cases for specific filenames
    if path_obj.name.lower() in ICONIFY_ICONS:
        return ICONIFY_ICONS[path_obj.name.lower()]["icon"]

    # Handle files by extension
    extension = path_obj.suffix.lower().lstrip(".")
    return ICONIFY_ICONS.get(
        extension, {"icon": "vscode-icons:default-file", "color": "#000000"}
    )["icon"]


def get_icon_svg(
    icon: str,
    color: str | None = None,
    height: str | int | None = None,
    width: str | int | None = None,
    flip: Flip | None = None,
    rotate: Rotation | None = None,
    box: bool | None = None,
) -> str:
    """Return svg for given pyconify icon key.

    Key should look like "mdi:file"
    For compatibility, this method also supports compatibility for
    emoji-slugs (":material-file:") as well as material-paths ("material/file")

    If no icon group is supplied as part of the string, mdi is assumed as group.

    When passing a string with "|" delimiters, the returned string will contain multiple
    icons.

    Args:
        icon: Pyconify icon name
        color: Icon color. Replaces currentColor with specific color, resulting in icon
               with hardcoded palette.
        height: Icon height. If only one dimension is specified, such as height, other
                dimension will be automatically set to match it.
        width: Icon width. If only one dimension is specified, such as height, other
               dimension will be automatically set to match it.
        flip: Flip icon.
        rotate: Rotate icon. If an integer is provided, it is assumed to be in degrees.
        box: Adds an empty rectangle to SVG that matches the icon's viewBox. It is needed
            when importing SVG to various UI design tools that ignore viewBox. Those
            tools, such as Sketch, create layer groups that automatically resize to fit
            content. Icons usually have empty pixels around icon, so such software crops
            those empty pixels and icon's group ends up being smaller than actual icon,
            making it harder to align it in design.

    Example:
        ``` py
        get_icon_svg("file")  # implicit mdi group
        get_icon_svg("mdi:file")  # pyconify key
        get_icon_svg("material/file")  # Material-style path
        get_icon_svg(":material-file:")  # material-style emoji slug
        get_icon_svg("mdi:file|:material-file:")  # returns a string with two svgs
        ```
    """
    label = ""
    for splitted in icon.split("|"):
        key = get_pyconify_key(splitted)
        import pyconify

        label += pyconify.svg(
            key,
            color=color,
            height=height,
            width=width,
            flip=flip,
            rotate=rotate,
            box=box,
        ).decode()
    return label


def get_pyconify_key(icon: str) -> str:
    """Convert given string to a pyconify key.

    Converts the keys from MkDocs-Material ("material/sth" or ":material-sth:")
    to their pyconify equivalent.

    Args:
        icon: The string which should be converted to a pyconify key.
    """
    for k, v in icons.PYCONIFY_TO_PREFIXES.items():
        path = f"{v.replace('-', '/')}/"
        icon = icon.replace(path, f"{k}:")
        icon = icon.replace(f":{v}-", f"{k}:")
    icon = icon.strip(":")
    mapping = {k: v[0] for k, v in icons._get_collection_map().items()}
    for prefix in mapping:
        if icon.startswith(f"{prefix}-"):
            icon = icon.replace(f"{prefix}-", f"{prefix}:")
            break
    if (count := icon.count(":")) > 1:
        icon = icon.replace(":", "-", count - 1)
    if ":" not in icon:
        icon = f"mdi:{icon}"
    return icon


def icon_for_url(url: str) -> str | None:
    """Return a pyconify icon key for given url."""
    from urllib import parse

    socials = {
        "matrix.to": "fa-brands:gitter",
        "x.com": "fa-brands:twitter",
        "fosstodon.org": "fa-brands:mastodon",
    }
    netloc = parse.urlsplit(url).netloc.lower()

    # First check exact matches
    if icon := socials.get(netloc):
        return icon

    # Try to find a matching brand icon
    domain = netloc.split(".")[-2]
    icon_index = icons._get_pyconify_icon_index()
    if (icon_name := f":fa-brands-{domain}:") in icon_index:
        return iconfilters.get_pyconify_key(icon_index[icon_name]["name"])

    return None


def get_emoji_slug(icon: str) -> str:
    """Return a icon string which can be used in markdown texts.

    The icon string will get picked up by pymdownx.emoji extension.

    Args:
        icon: The string to convert to an emoji slug.
    """
    return f":{iconfilters.get_pyconify_key(icon).replace(':', '-')}:"


def get_icon_xml(icon: str) -> ET.Element:
    """Return a xmlElement for given MaterialIcon.

    Args:
        icon: Icon to fetch. If iconname is not explicit (aka does not contain "/"),
              then it will try to get the icon from material/ folder.
    """
    ET.register_namespace("", "http://www.w3.org/2000/svg")
    svg_text = iconfilters.get_icon_svg(icon)
    return ET.fromstring(svg_text)
