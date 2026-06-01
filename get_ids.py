import json
import os
import re
import zipfile


def load_env(filepath: str = ".env") -> dict[str, str]:
    """Parse a simple .env file with KEY=VALUE pairs (supports quoted values)."""
    env = {}
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            match = re.match(r'(\w+)\s*=\s*"?(.*?)"?\s*$', line)
            if match:
                env[match.group(1)] = match.group(2)
    return env


def load_lang(jar: zipfile.ZipFile, namespace: str, lang: str) -> dict[str, str]:
    """Load a lang file from the JAR and return it as a dict."""
    lang_path = f"assets/{namespace}/lang/{lang}.json"
    if lang_path in jar.namelist():
        data = jar.read(lang_path)
        return json.loads(data.decode("utf-8"))
    return {}


def extract_ids(jar_path: str, lang_code: str) -> tuple[list[str], list[str], list[str]]:
    """
    Extract block and item IDs from a mod JAR with localized names.

    Returns:
        blocks:  list of "namespace:path - Name" (or "namespace:path" if no name)
        items:   list of "namespace:path - Name" (or "namespace:path" if no name)
        all_ids: combined sorted unique list, deduped by ID, preferring named entries
    """
    blocks: list[str] = []
    items: list[str] = []

    # Dicts keyed by raw ID (namespace:path) -> formatted string (with name if available)
    block_map: dict[str, str] = {}
    item_map: dict[str, str] = {}

    with zipfile.ZipFile(jar_path, "r") as jar:
        names = jar.namelist()

        # Discover namespaces under assets/
        namespaces: set[str] = set()
        for name in names:
            parts = name.split("/")
            if len(parts) >= 2 and parts[0] == "assets":
                namespaces.add(parts[1])

        if not namespaces:
            print("[WARN] No assets/ directory found inside the JAR.")
            return [], [], []

        for ns in sorted(namespaces):
            # Load localization for this namespace
            lang_data = load_lang(jar, ns, lang_code)

            # If requested lang not found, try en_us as fallback
            if not lang_data and lang_code != "en_us":
                lang_data = load_lang(jar, ns, "en_us")

            blockstates_prefix = f"assets/{ns}/blockstates/"
            models_item_prefix = f"assets/{ns}/models/item/"

            # Blocks — every .json in blockstates/
            for name in names:
                if name.startswith(blockstates_prefix) and name.endswith(".json"):
                    relative = name[len(blockstates_prefix):]
                    block_name = relative[: -len(".json")]
                    if "/" in block_name:
                        continue
                    block_id = f"{ns}:{block_name}"
                    lang_key = f"block.{ns}.{block_name}"
                    display_name = lang_data.get(lang_key, "")
                    if display_name:
                        block_map[block_id] = f"{block_id} - {display_name}"
                    else:
                        # Only set if not already set with a name (shouldn't happen, but safe)
                        block_map.setdefault(block_id, block_id)

            # Items — every .json in models/item/
            for name in names:
                if name.startswith(models_item_prefix) and name.endswith(".json"):
                    relative = name[len(models_item_prefix):]
                    item_name = relative[: -len(".json")]
                    if "/" in item_name:
                        continue
                    item_id = f"{ns}:{item_name}"
                    lang_key = f"item.{ns}.{item_name}"
                    display_name = lang_data.get(lang_key, "")
                    if display_name:
                        item_map[item_id] = f"{item_id} - {display_name}"
                    else:
                        item_map.setdefault(item_id, item_id)

    blocks = sorted(block_map.values())
    items = sorted(item_map.values())

    # Merge: for each unique ID, prefer the entry that has a display name
    merged: dict[str, str] = {}
    for id_map in (block_map, item_map):
        for raw_id, formatted in id_map.items():
            if raw_id not in merged:
                merged[raw_id] = formatted
            else:
                # Prefer the one with a display name
                if " - " in formatted and " - " not in merged[raw_id]:
                    merged[raw_id] = formatted

    all_ids = sorted(merged.values())

    return blocks, items, all_ids


def main():
    env = load_env(".env")
    jar_path = env.get("mod_path")
    lang_code = env.get("lang", "en_us")

    if not jar_path:
        print("ERROR: 'mod_path' not found in .env file.")
        return

    if not os.path.isfile(jar_path):
        print(f"ERROR: File not found: {jar_path}")
        return

    print(f"JAR:  {jar_path}")
    print(f"Lang: {lang_code}\n")

    blocks, items, all_ids = extract_ids(jar_path, lang_code)

    print(f"=== Blocks ({len(blocks)}) ===")
    for b in blocks:
        print(f"  {b}")

    print(f"\n=== Items ({len(items)}) ===")
    for i in items:
        print(f"  {i}")

    print(f"\n=== All unique IDs ({len(all_ids)}) ===")
    for aid in all_ids:
        print(f"  {aid}")

    # Save to file (include locale in filename)
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), f"ids_{lang_code}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        for aid in all_ids:
            f.write(aid + "\n")
    print(f"\nIDs saved to {output_path}")


if __name__ == "__main__":
    main()