#!/usr/bin/env python3
"""
Export Keystone-Codex entries to BioGrid2.0 glyph/protocol format.

Reads .fieldlink.json for the layer map and field mappings, then transforms
each keystone entry into the BioGrid manifest structure.

Usage: python3 -m src fieldlink-export
"""
import os, json

ROOT = os.path.dirname(os.path.dirname(__file__))


def load_fieldlink():
    """Load and return the .fieldlink.json config."""
    path = os.path.join(ROOT, ".fieldlink.json")
    with open(path) as f:
        return json.load(f)


def load_items():
    """Load all keystone data entries."""
    items = []
    data_dir = os.path.join(ROOT, "data")
    for base, _, files in os.walk(data_dir):
        for f in files:
            if f.endswith(".json") and f != "candidates.json":
                with open(os.path.join(base, f)) as fh:
                    items.append(json.load(fh))
    return items


def load_candidates():
    """Load candidate entries."""
    path = os.path.join(ROOT, "data", "candidates.json")
    if not os.path.exists(path):
        return []
    with open(path) as f:
        return json.load(f).get("candidates", [])


def domain_to_layer(domain, layers):
    """Map a keystone domain to its BioGrid layer name."""
    for layer in layers:
        if domain in layer["keystone_domains"]:
            return layer["layer"]
    return "unmapped"


def entry_to_glyph(entry, layers, shapes):
    """Transform a keystone entry into a BioGrid glyph record."""
    domain = entry["domain"]
    return {
        "source_id": entry["id"],
        "label": entry["name"],
        "layer": domain_to_layer(domain, layers),
        "origin_region": entry["region"],
        "epoch_start": entry["era"]["start"],
        "epoch_end": entry["era"]["end"],
        "description": entry["summary"],
        "edges_out": entry.get("unlocks", []),
        "shape": shapes.get(domain, "circle"),
        "fill": "solid"
    }


def entry_to_protocol(entry):
    """Transform a keystone entry into a BioGrid protocol record."""
    m = entry["metrics"]
    sources = []
    for ev in entry.get("evidence", []):
        sources.append({
            "ref": ev["source"],
            "type": ev["type"],
            "confidence": ev.get("quality", 0.0),
            "uri": ev.get("uri", "")
        })
    return {
        "source_id": entry["id"],
        "durability_years": m["longevity_years"],
        "spread_count": m["replication_regions"],
        "decentralization": m["decentralization_score"],
        "ethical_score": m.get("ethical_alignment"),
        "sources": sources,
        "source_confidence": sum(s["confidence"] for s in sources) / len(sources) if sources else 0.0
    }


def candidate_to_glyph(candidate, layers, shapes):
    """Transform a candidate into a dotted placeholder glyph."""
    domain = candidate.get("suggested_domain", "")
    return {
        "source_id": candidate["id"],
        "label": candidate["id"].replace("_", " ").title(),
        "layer": domain_to_layer(domain, layers),
        "origin_region": "",
        "epoch_start": None,
        "epoch_end": None,
        "description": candidate.get("notes", ""),
        "edges_out": [],
        "shape": shapes.get(domain, "circle"),
        "fill": "dotted"
    }


def validate_integrity(fieldlink, items):
    """Run integrity checks defined in .fieldlink.json."""
    errors = []
    entry_ids = {it["id"] for it in items}
    layers = fieldlink["layer_map"]["layers"]

    # Check all entry_ids in layer_map exist
    for layer in layers:
        for eid in layer.get("entry_ids", []):
            if eid not in entry_ids:
                errors.append(f"layer '{layer['layer']}' references unknown entry '{eid}'")

    # Check all 8 domains covered
    mapped_domains = set()
    for layer in layers:
        mapped_domains.update(layer["keystone_domains"])
    expected = set(fieldlink["source"]["domains"])
    missing = expected - mapped_domains
    if missing:
        errors.append(f"Unmapped domains: {', '.join(sorted(missing))}")

    # Check no domain in multiple layers
    seen = {}
    for layer in layers:
        for d in layer["keystone_domains"]:
            if d in seen:
                errors.append(f"Domain '{d}' in both '{seen[d]}' and '{layer['layer']}'")
            seen[d] = layer["layer"]

    return errors


def main():
    """Run the fieldlink export."""
    fieldlink = load_fieldlink()
    items = load_items()
    candidates = load_candidates()

    layers = fieldlink["layer_map"]["layers"]
    shapes = fieldlink["glyphs"]["shape_by_domain"]

    # Integrity checks
    errors = validate_integrity(fieldlink, items)
    if errors:
        print("Fieldlink integrity errors:")
        for e in errors:
            print(f"  ✗ {e}")
        return False

    # Build export
    export = {
        "source_repo": fieldlink["source"]["repo"],
        "target_repo": fieldlink["target"]["repo"],
        "entry_count": len(items),
        "candidate_count": len(candidates),
        "layers": [],
        "glyphs": [],
        "protocols": []
    }

    # Layer summary
    for layer in layers:
        export["layers"].append({
            "layer": layer["layer"],
            "analogy": layer["analogy"],
            "domains": layer["keystone_domains"],
            "biogrid_subsystems": layer["biogrid_subsystems"],
            "entry_count": len(layer.get("entry_ids", [])),
            "entry_ids": layer.get("entry_ids", [])
        })

    # Transform entries
    for entry in items:
        export["glyphs"].append(entry_to_glyph(entry, layers, shapes))
        export["protocols"].append(entry_to_protocol(entry))

    # Transform candidates as placeholder glyphs
    for candidate in candidates:
        export["glyphs"].append(candidate_to_glyph(candidate, layers, shapes))

    # Write output
    out_path = os.path.join(ROOT, "fieldlink_export.json")
    with open(out_path, "w") as f:
        json.dump(export, f, indent=2)

    print(f"Exported {len(items)} entries + {len(candidates)} candidates → fieldlink_export.json")
    print(f"  Glyphs:    {len(export['glyphs'])}")
    print(f"  Protocols: {len(export['protocols'])}")
    print(f"  Layers:    {len(export['layers'])}")
    return True


if __name__ == "__main__":
    main()
