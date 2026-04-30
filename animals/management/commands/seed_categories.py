from django.core.management.base import BaseCommand
from accounts.models import Farmer, Farm
from animals.models import AnimalCategory, Breed


class Command(BaseCommand):
    help = 'Seed the database with initial animal categories and breeds'

    def handle(self, *args, **options):
        categories = [
            {'name': 'Cattle', 'icon': '🐄'},
            {'name': 'Goats', 'icon': '🐐'},
            {'name': 'Sheep', 'icon': '🐑'},
            {'name': 'Poultry', 'icon': '🐔'},
            {'name': 'Pigs', 'icon': '🐷'},
            {'name': 'Rabbits', 'icon': '🐰'},
        ]

        breeds_map = {
            'Cattle': ['Friesian', 'Ayrshire', 'Guernsey', 'Jersey', 'Sahiwal', 'Boran', 'Zebu'],
            'Goats': ['Boer', 'Saanen', 'Toggenburg', 'Alpine', 'Galla', 'East African'],
            'Sheep': ['Merino', 'Dorper', 'Hampshire', 'Suffolk', 'Romney', 'Red Maasai'],
            'Poultry': ['Broiler', 'Layers (Kuroiler)', 'Layers (Kenbro)', 'Kienyeji', 'Turkeys', 'Ducks'],
            'Pigs': ['Large White', 'Landrace', 'Duroc', 'Hampshire', 'Camborough'],
            'Rabbits': ['New Zealand White', 'Californian', 'Dutch', 'Chinchilla', 'Flemish Giant'],
        }

        created_cats = 0
        created_breeds = 0

        for cat_data in categories:
            cat, created = AnimalCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={'icon': cat_data['icon']}
            )
            if created:
                created_cats += 1

            for breed_name in breeds_map.get(cat_data['name'], []):
                breed, created = Breed.objects.get_or_create(
                    category=cat,
                    name=breed_name
                )
                if created:
                    created_breeds += 1

        self.stdout.write(self.style.SUCCESS(
            f'Seeded {created_cats} categories and {created_breeds} breeds.'
        ))
