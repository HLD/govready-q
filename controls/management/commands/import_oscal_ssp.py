"""Create a GovReady-Q system from an OSCAL system security plan and its companion documents.

Creates a project and system owned by --owner, then loads from the OSCAL documents:

* SSP: system name, description, security sensitivity and impact levels, the
  selected controls (or --baseline), one component per SSP component, and the
  per-control, per-component implementation narratives and statuses.
* Component definition (optional): component descriptions and purposes.
* Assessment results (optional): stored as a system assessment result.
* POA&M (optional): one POA&M per item, with its risk (likelihood, impact, deadline).

The controls are expected to come from a catalog already loaded with
import_oscal_catalog (--catalog-key).

Example:
    python manage.py import_oscal_ssp ssp.json --catalog-key EXAMPLE_CATALOG \\
        --baseline org-moderate --owner alice@example.com \\
        --component-definition component-definition.json \\
        --assessment-results assessment-results.json --poam poam.json
"""

import json
import re
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from controls.enums.statements import StatementTypeEnum
from controls.models import Element, ElementControl, ImportRecord, Poam, Statement, System, SystemAssessmentResult
from controls.oscal import CatalogData
from siteapp.models import Organization, Project, User

# OSCAL implementation-status states -> GovReady-Q statement statuses.
IMPLEMENTATION_STATUS = {
    "implemented": "Implemented",
    "partial": "Partially Implemented",
    "planned": "Planned",
    "alternative": "Implemented",  # an alternative implementation is in place; noted in remarks
    "not-applicable": "Not Applicable",
}


# OSCAL component types GovReady-Q does not list -> closest GovReady-Q type.
COMPONENT_TYPES = {"process-procedure": "process"}


def control_id_from_label(label):
    """'AC-02(03)' -> 'ac-2.3', 'SA-400(02)' -> 'sa-400.2', 'AU-06' -> 'au-6'."""
    m = re.match(r"^([A-Z]{2})-0*(\d+)(?:\(0*(\d+)\))?", label.strip())
    if not m:
        return None
    family, number, enhancement = m.groups()
    return f"{family.lower()}-{number}" + (f".{enhancement}" if enhancement else "")


def prop_value(obj, name):
    return next((p.get("value") for p in obj.get("props", []) if p.get("name") == name), None)


def load(path, root_key):
    with open(path) as f:
        document = json.load(f)
    if root_key not in document:
        raise CommandError(f"{path}: expected a top-level '{root_key}'.")
    return document[root_key]


def parse_datetime(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")) if value else None
    except ValueError:
        return None


class Command(BaseCommand):
    help = "Create a GovReady-Q system from an OSCAL SSP (plus optional component definition, assessment results and POA&M)."

    def add_arguments(self, parser):
        parser.add_argument("ssp_path")
        parser.add_argument("--catalog-key", required=True, help="GovReady-Q catalog key of the SSP's controls")
        parser.add_argument("--baseline", help="Assign this baseline of the catalog (default: the SSP's implemented requirements)")
        parser.add_argument("--owner", required=True, help="Username of the system owner (must exist)")
        parser.add_argument("--organization", default="main", help="Organization slug (default: main)")
        parser.add_argument("--app", default="blank", help="Compliance app in govready-q-files-startpack used to create the project")
        parser.add_argument("--component-definition")
        parser.add_argument("--assessment-results")
        parser.add_argument("--poam")
        parser.add_argument("--poam-detection-source", default="Security assessment",
                            help="Weakness detection source recorded on imported POA&Ms")
        parser.add_argument("--replace", action="store_true",
                            help="Delete a system (and the components) previously imported from this SSP first")

    def handle(self, *args, **opts):
        ssp = load(opts["ssp_path"], "system-security-plan")
        catalog_key = opts["catalog_key"]
        catalog = CatalogData.objects.filter(catalog_key=catalog_key).first()
        if not catalog:
            raise CommandError(f"Catalog '{catalog_key}' is not loaded; run import_oscal_catalog first.")
        if opts["baseline"] and opts["baseline"] not in (catalog.baselines_json or {}):
            raise CommandError(f"Catalog '{catalog_key}' has no baseline '{opts['baseline']}'.")
        owner = User.objects.filter(username=opts["owner"]).first()
        if not owner:
            raise CommandError(f"User '{opts['owner']}' does not exist (users are created when they first sign in).")
        org = Organization.objects.get(slug=opts["organization"])

        chars = ssp["system-characteristics"]
        system_name = chars["system-name"]
        import_name = f"OSCAL SSP import: {system_name} ({ssp['uuid']})"

        existing = ImportRecord.objects.filter(name=import_name).first()
        if existing:
            if not opts["replace"]:
                raise CommandError(f"'{system_name}' was already imported from this SSP; use --replace to re-import.")
            self.delete_previous_import(existing)

        project = self.create_project(owner, org, opts["app"])
        try:
            with transaction.atomic():
                summary = self.populate(project, owner, ssp, catalog_key, import_name, opts)
        except Exception:
            # The project is created outside the transaction (by the app's own views); remove it.
            system = project.system
            project.delete()
            if system:
                system.root_element.delete()
                system.delete()
            raise
        self.stdout.write(self.style.SUCCESS(
            f"Created system '{system_name}' (project {project.id}, system {project.system.id}): " + summary))
        self.stdout.write(f"Open it at /projects/{project.id}/")

    # -- setup ------------------------------------------------------------

    def delete_previous_import(self, import_record):
        systems = System.objects.filter(root_element__import_record=import_record)
        for system in systems:
            for project in Project.objects.filter(system=system):
                project.delete()
            system.delete()
        # Deleting the import record deletes its components and their statements.
        import_record.delete()
        self.stdout.write("Deleted the previous import.")

    def create_project(self, owner, org, app):
        from loadtesting.web import WebClient
        portfolio = owner.default_portfolio or owner.create_default_portfolio_if_missing()
        client = WebClient(owner.username, org.slug)
        client.post(f"/store/govready-q-files-startpack/{app}?portfolio={portfolio.id}", {"organization": org.slug})
        m = re.search(r"/projects/(\d+)/", getattr(client.response, "url", "") or "")
        if not m:
            raise CommandError(f"Could not create a project from app '{app}'.")
        project = Project.objects.get(id=m.group(1))
        if not project.system:
            raise CommandError(f"App '{app}' did not create a system for the project.")
        return project

    # -- import -----------------------------------------------------------

    def populate(self, project, owner, ssp, catalog_key, import_name, opts):
        chars = ssp["system-characteristics"]
        system = project.system
        root = system.root_element
        import_record = ImportRecord.objects.create(name=import_name)

        # System identity and categorization.
        name = chars["system-name"]
        short = chars.get("system-name-short")
        project.root_task.title_override = name
        project.root_task.save()
        project.root_task.on_answer_changed()
        root.name = name if not Element.objects.filter(name=name).exclude(id=root.id).exists() else f"{name} ({ssp['uuid'][:8]})"
        root.full_name = f"{name} ({short})" if short else name
        root.description = chars.get("description", root.description)
        root.import_record = import_record
        root.save()
        if chars.get("security-sensitivity-level"):
            system.set_security_sensitivity_level(chars["security-sensitivity-level"])
        impact = chars.get("security-impact-level")
        if impact:
            system.set_security_impact_level({k.replace("-", "_"): v for k, v in impact.items()})

        # Controls.
        ir_list = ssp["control-implementation"]["implemented-requirements"]
        if opts["baseline"]:
            root.assign_baseline_controls(owner, catalog_key, opts["baseline"])
        else:
            for control_id in dict.fromkeys(ir["control-id"] for ir in ir_list):
                ElementControl.objects.get_or_create(element=root, oscal_ctl_id=control_id, oscal_catalog_key=catalog_key)

        # Components.
        definitions = {}
        if opts["component_definition"]:
            for c in load(opts["component_definition"], "component-definition").get("components", []):
                definitions[c["uuid"]] = c
                definitions[c["title"]] = c
        components = {}
        for c in ssp["system-implementation"].get("components", []):
            if c.get("type") == "this-system":
                components[c["uuid"]] = root
                continue
            definition = definitions.get(c["uuid"]) or definitions.get(c["title"]) or {}
            description = definition.get("description") or c.get("description") or "Description needed"
            if definition.get("purpose"):
                description += f"\n\nPurpose: {definition['purpose']}"
            title = c["title"]
            if Element.objects.filter(name=title).exists():
                title = f"{title} ({system_name_short(chars)})"
            element = Element.objects.create(
                name=title, full_name=title, description=description, element_type="system_element",
                component_type=COMPONENT_TYPES.get(c.get("type"), c.get("type") or "software"),
                component_state=(c.get("status") or {}).get("state", "operational"),
                import_record=import_record, uuid=c["uuid"], oscal_version="1.2.3")
            element.assign_owner_permissions(owner)
            components[c["uuid"]] = element

        # Implementation statements: a prototype on the component and an instance on the system.
        statements = 0
        status_counts = {}
        for ir in ir_list:
            approach = prop_value(ir, "implementation-approach")
            for bc in ir.get("by-components", []):
                producer = components.get(bc["component-uuid"], root)
                state = (bc.get("implementation-status") or {}).get("state", "implemented")
                status = IMPLEMENTATION_STATUS.get(state, "Unknown")
                status_counts[state] = status_counts.get(state, 0) + 1
                remarks = []
                if approach:
                    remarks.append(f"Implementation approach: {approach}")
                if state == "alternative":
                    remarks.append("Alternative implementation")
                if (bc.get("implementation-status") or {}).get("remarks"):
                    remarks.append(bc["implementation-status"]["remarks"])
                common = dict(sid=ir["control-id"], sid_class=catalog_key, source=catalog_key, body=bc.get("description", ""),
                              status=status, remarks="; ".join(remarks), producer_element=producer)
                if producer is root:
                    Statement.objects.create(statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name,
                                             consumer_element=root, uuid=bc.get("uuid") or ir["uuid"], **common)
                else:
                    prototype = Statement.objects.create(statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION_PROTOTYPE.name,
                                                         **common)
                    prototype.import_record.add(import_record)
                    Statement.objects.create(statement_type=StatementTypeEnum.CONTROL_IMPLEMENTATION.name,
                                             consumer_element=root, prototype=prototype, uuid=bc.get("uuid") or ir["uuid"], **common)
                statements += 1

        # Assessment results.
        findings_summary = ""
        if opts["assessment_results"]:
            ar = load(opts["assessment_results"], "assessment-results")
            for result in ar.get("results", []):
                states = [f.get("target", {}).get("status", {}).get("state") for f in result.get("findings", [])]
                satisfied = states.count("satisfied")
                SystemAssessmentResult.objects.create(
                    name=result.get("title", "Assessment results")[:250],
                    description=f"{satisfied} satisfied, {len(states) - satisfied} not satisfied "
                                f"({result.get('start', '')[:10]} to {result.get('end', '')[:10]})"[:255],
                    system=system, assessment_results={"assessment-results": {**ar, "results": [result]}})
                findings_summary = f"{satisfied} findings satisfied, {len(states) - satisfied} not satisfied"

        # POA&Ms.
        poams = 0
        if opts["poam"]:
            poam_doc = load(opts["poam"], "plan-of-action-and-milestones")
            risks = {r["uuid"]: r for r in poam_doc.get("risks", [])}
            for item in poam_doc.get("poam-items", []):
                risk = next((risks[r["risk-uuid"]] for r in item.get("related-risks", []) if r["risk-uuid"] in risks), {})
                facets = {f["name"]: f["value"] for ch in risk.get("characterizations", []) for f in ch.get("facets", [])}
                control_id = control_id_from_label(item["title"]) or ""
                smt = Statement.objects.create(
                    statement_type=StatementTypeEnum.POAM.name, sid=control_id, sid_class=catalog_key, source=catalog_key,
                    body=item.get("description", ""), status=(risk.get("status") or "open").capitalize(),
                    producer_element=root, consumer_element=root)
                poams += 1
                Poam.objects.create(
                    statement=smt, poam_id=poams, controls=control_id, weakness_name=item["title"],
                    weakness_detection_source=opts["poam_detection_source"],
                    weakness_source_identifier=prop_value(item, "poam-id"),
                    remediation_plan=risk.get("statement") or item.get("description"),
                    scheduled_completion_date=parse_datetime(risk.get("deadline")),
                    risk_rating_original=facets.get("impact"), risk_rating_adjusted=facets.get("impact"),
                    extra={"POAM ID": prop_value(item, "poam-id"), "Likelihood": facets.get("likelihood"),
                           "Impact": facets.get("impact"), "Risk": risk.get("title"),
                           "Scheduled Completion Date": (risk.get("deadline") or "")[:10]})

        system.add_event("import", f"Imported from OSCAL SSP {ssp['uuid']}")
        statuses = ", ".join(f"{n} {s}" for s, n in sorted(status_counts.items()))
        return (f"{root.controls.count()} controls, {len(components) - 1} components, {statements} implementation "
                f"statements ({statuses}), {poams} POA&Ms" + (f", {findings_summary}" if findings_summary else "") + ".")


def system_name_short(chars):
    return chars.get("system-name-short") or chars["system-name"]
