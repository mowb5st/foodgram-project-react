import json
import os.path

from core.models import Ingredient
from django.core.management.base import BaseCommand

from foodgram.settings import BASE_DIR

FOODGRAM_PUB_DIR = os.path.abspath(os.path.join(BASE_DIR))
INGREDIENTS_JSON_PATH = f'{FOODGRAM_PUB_DIR}/data/ingredients.json'


class Command(BaseCommand):
    help = 'Loading data from JSON into DB'

    def handle(self, *args, **options):
        path = INGREDIENTS_JSON_PATH
        with open(path, encoding='utf-8') as file:
            Ingredient.objects.bulk_create(
                objs=[Ingredient(**x) for x in json.load(file)])
