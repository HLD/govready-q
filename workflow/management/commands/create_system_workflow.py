"""Create a workflow (recipe, image and instance) for a system and mark completed steps.

Example:
    python manage.py create_system_workflow 5 "Security assessment and authorization" \\
        --step categorize="Categorize (injury assessment)" --step tailor="Tailor organizational profile" \\
        --step authorize="Authorization decision" --completed-through tailor
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from controls.models import System
from workflow.factories import FlowImageFactory
from workflow.models import WorkflowImage, WorkflowInstance, WorkflowRecipe


class Command(BaseCommand):
    help = "Create a workflow for a system from a list of steps, optionally marking the first steps completed."

    def add_arguments(self, parser):
        parser.add_argument("system_id", type=int)
        parser.add_argument("name")
        parser.add_argument("--description", default="")
        parser.add_argument("--step", action="append", required=True, metavar="ID=PROMPT",
                            help="A workflow step (repeatable, in order). IDs: letters, digits, '_' or '-'.")
        parser.add_argument("--completed-through", metavar="STEP_ID",
                            help="Mark every step up to and including this one completed")
        parser.add_argument("--replace", action="store_true",
                            help="Replace an existing workflow with this name on the system")

    def handle(self, *args, **opts):
        system = System.objects.filter(id=opts["system_id"]).first()
        if not system:
            raise CommandError(f"System {opts['system_id']} does not exist.")
        steps = []
        for spec in opts["step"]:
            step_id, sep, prompt = spec.partition("=")
            if not sep or not step_id.replace("_", "").replace("-", "").isalnum() or not prompt or '"' in prompt:
                raise CommandError(f"--step must be ID=PROMPT (no double quotes in the prompt), got {spec!r}")
            steps.append((step_id, prompt))
        step_ids = [s[0] for s in steps]
        if opts["completed_through"] and opts["completed_through"] not in step_ids:
            raise CommandError(f"--completed-through {opts['completed_through']!r} is not a step id.")

        name = opts["name"]
        with transaction.atomic():
            existing = WorkflowInstance.objects.filter(system=system, name=name)
            if existing.exists():
                if not opts["replace"]:
                    raise CommandError(f"System {system.id} already has a workflow named '{name}'; use --replace.")
                existing.delete()
            recipe_text = "\n".join(f'<step prompt="{prompt}" id="{step_id}">' for step_id, prompt in steps)
            recipe, _ = WorkflowRecipe.objects.update_or_create(
                name=name, defaults={"description": opts["description"][:250], "recipe": recipe_text})
            image = FlowImageFactory(name).create_workflowimage_from_workflowrecipe(recipe)
            if not isinstance(image, WorkflowImage):
                raise CommandError("Could not create the workflow image from the recipe.")

            instance = image.create_workflowinstance_obj()
            instance.system = system
            if opts["completed_through"]:
                for step_id in step_ids[:step_ids.index(opts["completed_through"]) + 1]:
                    instance.set_curr_feature(step_id)
                    instance.set_curr_feature_completed()
                instance.advance_feature()
            instance.save()

        current = instance.workflow.get("curr_feature")
        self.stdout.write(self.style.SUCCESS(
            f"Created workflow '{name}' on system {system.id} ({len(steps)} steps; current step: "
            f"{dict(steps).get(current, current)})."))
