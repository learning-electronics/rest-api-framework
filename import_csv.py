import csv
from django.core.management import BaseCommand
from django.utils import timezone

from exercise.models import Theme

class Command(BaseCommand):
    help = "Loads themes of exercises from CSV"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str)

    def handle(self, *args, **options):
        start_time = timezone.now()
        file_path = options["file_path"]
        with open(file_path, "r") as csv_file:
            data = csv.reader(csv_file, delimiter=",")
            for row in data[1:]:
                Theme.objects.create(
                    id = row[0],
                    teacher = row[1]
                )
        end_time = timezone.now()
        self.stdout.write(
            self.style.SUCCESS(
                f"Loading CSV took: {(end_time-start_time).total_seconds()} seconds."
            )
        )
