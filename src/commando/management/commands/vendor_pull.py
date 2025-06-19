from typing import Any
from django.core.management.base import BaseCommand
from django.conf import settings
import helpers


STATICFILES_VENDOR_DIR = getattr(settings, "STATICFILES_VENDOR_DIR")

VENDOR_STATICFILES = {
    "tailwind.min.css": "https://cdnjs.cloudflare.com/ajax/libs/tailwindcss/2.2.19/tailwind.min.css",
    "flowbite.min.css": "https://cdnjs.cloudfare.com/ajax/libs/flowbite/2.3.0/flowbite.min.css",
    "flowbite.min.js": "https://cdnjs.cloudfare.com/ajax/libs/flowbite/2.3.0/flowbite.min.js",
    "flowbite.min.js.map": "https://cdnjs.cloudfare.com/ajax/libs/flowbite/2.3.0/flowbite.min.js.map",
}

class Command(BaseCommand):

    def handle(self, *args: any, **options: any):
        self.stdout.write("Downloading vendor static files")
        completed_urls = []
        for name, url in VENDOR_STATICFILES.items():
            out_path = STATICFILES_VENDOR_DIR / name
            dl_success = helpers.download_to_local(url, out_path)
            if dl_success:
                completed_urls.append(url)
            else:
                self.stderr.write(f"Failed to download {url}")

        if set(completed_urls) == set(VENDOR_STATICFILES.values()):
            self.stdout.write("All vendor static files downloaded successfully")
        else:
            self.stderr.write("Some vendor static files failed to download")