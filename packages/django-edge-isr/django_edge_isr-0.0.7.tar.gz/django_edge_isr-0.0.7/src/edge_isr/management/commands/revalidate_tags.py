from django.core.management.base import BaseCommand
from edge_isr.revalidate.tasks import revalidate_by_tags


class Command(BaseCommand):
    help = "Revalidate URLs associated with the given tags."

    def add_arguments(self, parser):
        parser.add_argument("tags", nargs="+", help="Tags like post:42 category:7")

    def handle(self, *args, **opts):
        tags = opts["tags"]
        urls = revalidate_by_tags(tags)
        self.stdout.write(self.style.SUCCESS(f"Triggered revalidation for {len(urls)} URLs"))
        for u in urls:
            self.stdout.write(f"- {u}")
