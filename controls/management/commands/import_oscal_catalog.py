"""Import an OSCAL 1.x catalog (and optional profiles as baselines) as a GovReady-Q control catalog.

GovReady-Q's catalog code (controls/oscal.py) reads an older OSCAL JSON layout:
`properties`/`parameters` instead of `props`/`params`, and parameter placeholders
written `{{ param-id }}` instead of `{{ insert: param, param-id }}`. This command
converts a current OSCAL catalog into that layout and stores it, with baselines
built from OSCAL profiles, in a CatalogData record.

Example:
    python manage.py import_oscal_catalog EXAMPLE_CATALOG /path/catalog.json \\
        --baseline moderate=/path/moderate_profile.json \\
        --baseline org-moderate=/path/org_resolved-profile_catalog.json \\
        --mapping /path/catalog_to_NIST_SP800-53r5_mapping.json --mapping-label "NIST SP 800-53 Rev. 5 mapping"
"""

import json
import re

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from controls.oscal import CatalogData

INSERT_PARAM = re.compile(r"\{\{\s*insert:\s*param,\s*([^\s}]+)\s*\}\}")
RENAMED_KEYS = {"props": "properties", "params": "parameters"}


def convert_value(value):
    """Recursively rename OSCAL 1.x keys and rewrite parameter placeholders."""
    if isinstance(value, dict):
        return {RENAMED_KEYS.get(k, k): convert_value(v) for k, v in value.items()}
    if isinstance(value, list):
        return [convert_value(v) for v in value]
    if isinstance(value, str):
        return INSERT_PARAM.sub(r"{{ \1 }}", value)
    return value


def label_selection_parameters(control):
    """Give choice-list parameters a readable label (GovReady-Q substitutes the label)."""
    for param in control.get("parameters", []):
        if "label" not in param and "select" in param:
            how_many = param["select"].get("how-many")
            prefix = "Selection (one or more)" if how_many == "one-or-more" else "Selection"
            choices = "; ".join(param["select"].get("choice", []))
            param["label"] = f"{prefix}: {choices}" if choices else prefix


def fold_extra_guidance(control, extra_part_names):
    """Render extra guidance parts (e.g. a jurisdiction-specific discussion) as additional guidance sections.

    GovReady-Q shows parts named 'guidance'. Other guidance-like parts are renamed to
    'guidance', with their title prepended to the prose so the source stays visible.
    """
    for part in control.get("parts", []):
        if part.get("name") in extra_part_names:
            title = part.get("title")
            part["name"] = "guidance"
            if title and part.get("prose"):
                part["prose"] = f"**{title}:** {part['prose']}"


def all_controls(catalog):
    for group in catalog.get("groups", []):
        for control in group.get("controls", []):
            yield control
            yield from control.get("controls", [])


def baseline_control_ids(path, catalog_ids):
    """Control ids for a baseline from an OSCAL profile or a resolved profile catalog.

    A profile is read for its include/exclude-controls (profiles that import other
    profiles or add controls through 'alters' should be resolved first). A catalog,
    e.g. a resolved profile catalog, contributes all of its controls.
    Returns (ids, profile_or_None).
    """
    with open(path) as f:
        document = json.load(f)
    profile = None
    ids = []
    if "catalog" in document:
        ids = [c["id"] for c in all_controls(document["catalog"])]
    elif "profile" in document:
        profile = document["profile"]
        for imp in profile.get("imports", []):
            if imp.get("include-all") is not None:
                ids.extend(sorted(catalog_ids))
            for include in imp.get("include-controls", []):
                ids.extend(include.get("with-ids", []))
            excluded = {i for exclude in imp.get("exclude-controls", []) for i in exclude.get("with-ids", [])}
            ids = [i for i in ids if i not in excluded]
    else:
        raise CommandError(f"{path}: not an OSCAL profile or catalog.")
    unknown = [i for i in ids if i not in catalog_ids]
    if unknown:
        raise CommandError(f"{path}: {len(unknown)} control ids are not in the catalog, e.g. {unknown[:5]}")
    # Keep order, drop duplicates.
    return list(dict.fromkeys(ids)), profile


def add_mapping_guidance(catalog, mapping_path, target_label):
    """Show an OSCAL mapping-collection's target controls as a guidance section on each control."""
    with open(mapping_path) as f:
        collection = json.load(f)["mapping-collection"]
    by_source = {}
    unmapped = set()
    for mapping in collection.get("mappings", []):
        for m in mapping.get("maps", []):
            targets = [t["id-ref"].upper() for t in m.get("targets", [])]
            score = m.get("confidence-score", {}).get("percentage")
            text = f"{', '.join(targets)} ({m.get('relationship', 'related')}"
            text += f", similarity {score:.2f})" if isinstance(score, (int, float)) else ")"
            if m.get("remarks"):
                text += f" - {m['remarks']}"
            for source in m.get("sources", []):
                by_source.setdefault(source["id-ref"], []).append(text)
        for gap in [mapping.get("source-gap-summary") or {}]:
            for unmapped_group in gap.get("unmapped-controls", []):
                unmapped.update(unmapped_group.get("with-ids", []))
    mapped = 0
    for control in all_controls(catalog):
        if control["id"] in by_source:
            prose = f"**{target_label}:** " + "; ".join(by_source[control["id"]])
            mapped += 1
        elif control["id"] in unmapped:
            prose = f"**{target_label}:** no equivalent control (not mapped)."
        else:
            continue
        control.setdefault("parts", []).append(
            {"id": f"{control['id']}_mapping", "name": "guidance", "prose": prose})
    return mapped, len(unmapped)


class Command(BaseCommand):
    help = "Import an OSCAL 1.x catalog, and optional profiles as baselines, as a GovReady-Q control catalog."

    def add_arguments(self, parser):
        parser.add_argument("catalog_key", help="Key for the catalog in GovReady-Q, e.g. EXAMPLE_CATALOG")
        parser.add_argument("catalog_path", help="Path to the OSCAL catalog JSON")
        parser.add_argument("--baseline", action="append", default=[], metavar="NAME=PROFILE_PATH",
                            help="Add a baseline from an OSCAL profile (repeatable)")
        parser.add_argument("--extra-guidance-part", action="append", default=[],
                            help="Additional part names to show as guidance (repeatable)")
        parser.add_argument("--mapping", metavar="MAPPING_COLLECTION_PATH",
                            help="OSCAL mapping-collection whose target controls are shown in each control's guidance")
        parser.add_argument("--mapping-label", default="Mapped controls",
                            help="Heading for the mapping guidance, e.g. 'NIST SP 800-53 Rev. 5 mapping'")
        parser.add_argument("--replace", action="store_true", help="Replace an existing catalog with this key")

    def handle(self, *args, **options):
        key = options["catalog_key"]
        if not re.match(r"^[A-Za-z0-9_.-]+$", key):
            raise CommandError("catalog_key may only contain letters, digits, '.', '_' and '-'.")

        with open(options["catalog_path"]) as f:
            source = json.load(f)
        if "catalog" not in source:
            raise CommandError("Not an OSCAL catalog (no top-level 'catalog').")

        catalog = convert_value(source["catalog"])
        catalog.setdefault("id", catalog.get("uuid", key))
        for control in all_controls(catalog):
            label_selection_parameters(control)
            fold_extra_guidance(control, set(options["extra_guidance_part"]))
        catalog_ids = {c["id"] for c in all_controls(catalog)}
        if options["mapping"]:
            mapped, unmapped = add_mapping_guidance(catalog, options["mapping"], options["mapping_label"])
            self.stdout.write(f"Mapping: {mapped} controls mapped, {unmapped} listed as unmapped.")

        baselines = {}
        for spec in options["baseline"]:
            name, sep, path = spec.partition("=")
            if not sep or not name or not path:
                raise CommandError(f"--baseline must be NAME=PROFILE_PATH, got {spec!r}")
            ids, profile = baseline_control_ids(path, catalog_ids)
            baselines[name] = {"controls": ids}  # the layout controls.models.Baselines reads
            modify = (profile or {}).get("modify", {})
            if modify.get("set-parameters") or modify.get("alters"):
                self.stdout.write(self.style.WARNING(
                    f"Baseline '{name}': the profile's {len(modify.get('set-parameters', []))} parameter settings "
                    f"and {len(modify.get('alters', []))} alterations are not applied (GovReady-Q baselines "
                    f"are lists of control ids)."))

        with transaction.atomic():
            existing = CatalogData.objects.filter(catalog_key=key).first()
            if existing and not options["replace"]:
                raise CommandError(f"Catalog '{key}' already exists; use --replace to overwrite it.")
            record = existing or CatalogData(catalog_key=key)
            record.catalog_json = {"catalog": catalog}
            record.baselines_json = baselines
            record.save()

        self.stdout.write(self.style.SUCCESS(
            f"{'Replaced' if existing else 'Imported'} catalog '{key}': {catalog['metadata'].get('title')} "
            f"({len(catalog_ids)} controls and enhancements, {len(catalog.get('groups', []))} families); "
            f"baselines: {', '.join(f'{n} ({len(v["controls"])})' for n, v in baselines.items()) or 'none'}."))
