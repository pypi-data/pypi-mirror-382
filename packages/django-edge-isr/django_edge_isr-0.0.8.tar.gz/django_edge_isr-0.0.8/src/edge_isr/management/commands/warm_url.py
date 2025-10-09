from django.core.management.base import BaseCommand
from edge_isr.revalidate.tasks import warmup_url


class Command(BaseCommand):
    help = "Warm a specific URL (force refresh in background)."

    def add_arguments(self, parser):
        parser.add_argument("url", help="Absolute URL to warm up")

    def handle(self, *args, **opts):
        warmup_url(opts["url"])
        self.stdout.write(self.style.SUCCESS(f"Warming triggered for {opts['url']}"))
