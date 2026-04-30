from datetime import datetime, timedelta, date
from decimal import Decimal
from django.utils import timezone
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from accounts.models import Farmer, Farm
from animals.models import AnimalCategory, Breed, Animal, HealthRecord, ProductionRecord, AnimalMovement
from payments.models import MpesaTransaction
from marketplace.models import MarketplaceListing, BuyerInquiry
from notifications_app.models import Notification, FeedingSchedule
import random

random.seed(42)


class Command(BaseCommand):
    help = 'Seed the database with comprehensive test data for demo purposes'

    def handle(self, *args, **options):
        self.stdout.write('Creating test data...\n')
        farmers = self._create_farmers()
        farms = self._create_farms(farmers)
        animals = self._create_animals(farms)
        self._create_health_records(animals)
        self._create_production_records(animals)
        self._create_transactions(farmers)
        self._create_marketplace_listings(farmers, farms, animals)
        self._create_notifications_and_schedules(farmers, farms, animals)
        self.stdout.write(self.style.SUCCESS('\nTest data seeded successfully!'))
        self.stdout.write('\n  Login credentials:')
        self.stdout.write('    Admin:  admin / admin123')
        self.stdout.write('    User 1: john_farmer / testpass123')
        self.stdout.write('    User 2: mary_farmer / testpass123')
        self.stdout.write('    User 3: peter_farmer / testpass123')
        self.stdout.write('    Vet:    vet_james / testpass123\n')

    def _create_farmers(self):
        self.stdout.write('  [1/8] Creating farmers...')
        data = [
            {'username': 'admin', 'first_name': 'Admin', 'last_name': 'User', 'email': 'admin@zfarm.co.ke', 'phone_number': '+254700000001', 'mpesa_number': '+254700000001', 'location': 'Nairobi', 'county': 'Nairobi', 'farm_type': 'Mixed', 'farm_name': 'ZFarm Admin', 'is_vet': True, 'is_superuser': True, 'is_staff': True, 'is_verified': True, 'password': 'admin123'},
            {'username': 'john_farmer', 'first_name': 'John', 'last_name': 'Kamau', 'email': 'john@zfarm.co.ke', 'phone_number': '+254712345678', 'mpesa_number': '+254712345678', 'location': 'Nakuru', 'county': 'Nakuru', 'farm_type': 'Dairy', 'farm_name': 'Happy Valley Farm', 'is_verified': True, 'password': 'testpass123'},
            {'username': 'mary_farmer', 'first_name': 'Mary', 'last_name': 'Wanjiku', 'email': 'mary@zfarm.co.ke', 'phone_number': '+254723456789', 'mpesa_number': '+254723456789', 'location': 'Eldoret', 'county': 'Uasin Gishu', 'farm_type': 'Poultry', 'farm_name': 'Sunrise Poultry Farm', 'is_verified': True, 'password': 'testpass123'},
            {'username': 'vet_james', 'first_name': 'James', 'last_name': 'Ochieng', 'email': 'james@zfarm.co.ke', 'phone_number': '+254734567890', 'mpesa_number': '+254734567890', 'location': 'Kisumu', 'county': 'Kisumu', 'farm_type': 'Mixed', 'farm_name': 'Lake Side Vet & Farm', 'is_vet': True, 'is_verified': True, 'password': 'testpass123'},
            {'username': 'peter_farmer', 'first_name': 'Peter', 'last_name': 'Mwangi', 'email': 'peter@zfarm.co.ke', 'phone_number': '+254745678901', 'mpesa_number': '+254745678901', 'location': 'Kiambu', 'county': 'Kiambu', 'farm_type': 'Mixed', 'farm_name': 'Green Hills Farm', 'is_verified': True, 'password': 'testpass123'},
        ]
        farmers = []
        for d in data:
            password = d.pop('password')
            farmer, created = Farmer.objects.get_or_create(username=d['username'], defaults={**d, 'password': make_password(password)})
            farmers.append(farmer)
        return farmers

    def _create_farms(self, farmers):
        self.stdout.write('  [2/8] Creating farms...')
        farm_data = [
            {'owner': farmers[1], 'name': 'Happy Valley Dairy', 'location': 'Molo, Nakuru', 'county': 'Nakuru', 'size_acres': 25, 'livestock_type': 'cattle', 'description': 'A 25-acre dairy farm specializing in Friesian and Ayrshire cattle. Located in the cool highlands of Molo.'},
            {'owner': farmers[1], 'name': 'Kamau Poultry Unit', 'location': 'Nakuru Town', 'county': 'Nakuru', 'size_acres': 2, 'livestock_type': 'poultry', 'description': 'Backyard poultry operation with layers and broilers.'},
            {'owner': farmers[2], 'name': 'Sunrise Poultry Farm', 'location': 'Eldoret', 'county': 'Uasin Gishu', 'size_acres': 5, 'livestock_type': 'poultry', 'description': 'Commercial poultry farm with 2000+ layers and broiler production.'},
            {'owner': farmers[3], 'name': 'Lake Side Farm', 'location': 'Kisumu', 'county': 'Kisumu', 'size_acres': 15, 'livestock_type': 'mixed', 'description': 'Mixed farm near Lake Victoria with cattle, goats, and poultry.'},
            {'owner': farmers[4], 'name': 'Green Hills Farm', 'location': 'Limuru, Kiambu', 'county': 'Kiambu', 'size_acres': 30, 'livestock_type': 'cattle', 'description': 'Premium dairy farm in Limuru highlands. Known for high-quality Friesian cattle.'},
            {'owner': farmers[4], 'name': 'Green Hills Goats', 'location': 'Limuru, Kiambu', 'county': 'Kiambu', 'size_acres': 10, 'livestock_type': 'goats', 'description': 'Boer goat breeding unit for meat production.'},
        ]
        farms = []
        for d in farm_data:
            farm, _ = Farm.objects.get_or_create(owner=d['owner'], name=d['name'], defaults=d)
            farms.append(farm)
        return farms

    def _create_animals(self, farms):
        self.stdout.write('  [3/8] Creating animals...')
        cat_cattle = AnimalCategory.objects.get(name='Cattle')
        cat_goats = AnimalCategory.objects.get(name='Goats')
        cat_poultry = AnimalCategory.objects.get(name='Poultry')
        cat_sheep = AnimalCategory.objects.get(name='Sheep')
        breed_friesian = Breed.objects.get(name='Friesian')
        breed_ayrshire = Breed.objects.get(name='Ayrshire')
        breed_jersey = Breed.objects.get(name='Jersey')
        breed_boer = Breed.objects.get(name='Boer')
        breed_saanen = Breed.objects.get(name='Saanen')
        breed_broiler = Breed.objects.get(name='Broiler')
        breed_layers = Breed.objects.get(name='Layers (Kuroiler)')
        breed_dorper = Breed.objects.get(name='Dorper')
        today = date.today()
        animal_data = [
            {'farm': farms[0], 'tag_id': 'HV-COW-001', 'name': 'Daisy', 'category': cat_cattle, 'breed': breed_friesian, 'gender': 'female', 'date_of_birth': today - timedelta(days=900), 'weight': Decimal('450'), 'color': 'Black and White', 'status': 'active'},
            {'farm': farms[0], 'tag_id': 'HV-COW-002', 'name': 'Rosie', 'category': cat_cattle, 'breed': breed_friesian, 'gender': 'female', 'date_of_birth': today - timedelta(days=1200), 'weight': Decimal('520'), 'color': 'Black and White', 'status': 'active'},
            {'farm': farms[0], 'tag_id': 'HV-COW-003', 'name': 'Lily', 'category': cat_cattle, 'breed': breed_ayrshire, 'gender': 'female', 'date_of_birth': today - timedelta(days=600), 'weight': Decimal('380'), 'color': 'Brown and White', 'status': 'active'},
            {'farm': farms[0], 'tag_id': 'HV-COW-004', 'name': 'Bella', 'category': cat_cattle, 'breed': breed_jersey, 'gender': 'female', 'date_of_birth': today - timedelta(days=1500), 'weight': Decimal('400'), 'color': 'Light Brown', 'status': 'active'},
            {'farm': farms[0], 'tag_id': 'HV-COW-005', 'name': 'Bull Max', 'category': cat_cattle, 'breed': breed_friesian, 'gender': 'male', 'date_of_birth': today - timedelta(days=730), 'weight': Decimal('680'), 'color': 'Black and White', 'status': 'active'},
            {'farm': farms[0], 'tag_id': 'HV-COW-006', 'name': 'Clover', 'category': cat_cattle, 'breed': breed_friesian, 'gender': 'female', 'date_of_birth': today - timedelta(days=300), 'weight': Decimal('280'), 'color': 'Black and White', 'status': 'sick'},
            {'farm': farms[0], 'tag_id': 'HV-COW-007', 'name': 'Star', 'category': cat_cattle, 'breed': breed_ayrshire, 'gender': 'female', 'date_of_birth': today - timedelta(days=2000), 'weight': Decimal('480'), 'color': 'Brown and White', 'status': 'active'},
            {'farm': farms[0], 'tag_id': 'HV-COW-008', 'name': 'Old Ben', 'category': cat_cattle, 'breed': breed_jersey, 'gender': 'male', 'date_of_birth': today - timedelta(days=2500), 'weight': Decimal('420'), 'color': 'Brown', 'status': 'sold'},
            {'farm': farms[1], 'tag_id': 'KP-CHK-001', 'name': 'Layer 1-50', 'category': cat_poultry, 'breed': breed_layers, 'gender': 'female', 'date_of_birth': today - timedelta(days=180), 'weight': Decimal('2.5'), 'color': 'Brown', 'status': 'active'},
            {'farm': farms[1], 'tag_id': 'KP-CHK-002', 'name': 'Broiler Batch A', 'category': cat_poultry, 'breed': breed_broiler, 'gender': 'female', 'date_of_birth': today - timedelta(days=35), 'weight': Decimal('2.0'), 'color': 'White', 'status': 'active'},
            {'farm': farms[2], 'tag_id': 'SP-CHK-001', 'name': 'Layer House A', 'category': cat_poultry, 'breed': breed_layers, 'gender': 'female', 'date_of_birth': today - timedelta(days=150), 'weight': Decimal('2.2'), 'color': 'Brown', 'status': 'active'},
            {'farm': farms[2], 'tag_id': 'SP-CHK-002', 'name': 'Layer House B', 'category': cat_poultry, 'breed': breed_layers, 'gender': 'female', 'date_of_birth': today - timedelta(days=150), 'weight': Decimal('2.3'), 'color': 'Brown', 'status': 'active'},
            {'farm': farms[2], 'tag_id': 'SP-CHK-003', 'name': 'Broiler Batch 1', 'category': cat_poultry, 'breed': breed_broiler, 'gender': 'female', 'date_of_birth': today - timedelta(days=28), 'weight': Decimal('1.8'), 'color': 'White', 'status': 'active'},
            {'farm': farms[3], 'tag_id': 'LS-COW-001', 'name': 'Grace', 'category': cat_cattle, 'breed': breed_friesian, 'gender': 'female', 'date_of_birth': today - timedelta(days=1000), 'weight': Decimal('420'), 'color': 'Black and White', 'status': 'active'},
            {'farm': farms[3], 'tag_id': 'LS-GT-001', 'name': 'Billy', 'category': cat_goats, 'breed': breed_boer, 'gender': 'male', 'date_of_birth': today - timedelta(days=365), 'weight': Decimal('85'), 'color': 'White', 'status': 'active'},
            {'farm': farms[3], 'tag_id': 'LS-GT-002', 'name': 'Nanny', 'category': cat_goats, 'breed': breed_saanen, 'gender': 'female', 'date_of_birth': today - timedelta(days=500), 'weight': Decimal('65'), 'color': 'White', 'status': 'active'},
            {'farm': farms[3], 'tag_id': 'LS-SHP-001', 'name': 'Woolly', 'category': cat_sheep, 'breed': breed_dorper, 'gender': 'female', 'date_of_birth': today - timedelta(days=400), 'weight': Decimal('55'), 'color': 'White', 'status': 'active'},
            {'farm': farms[4], 'tag_id': 'GH-COW-001', 'name': 'Queen', 'category': cat_cattle, 'breed': breed_friesian, 'gender': 'female', 'date_of_birth': today - timedelta(days=1100), 'weight': Decimal('500'), 'color': 'Black and White', 'status': 'active'},
            {'farm': farms[4], 'tag_id': 'GH-COW-002', 'name': 'Princess', 'category': cat_cattle, 'breed': breed_friesian, 'gender': 'female', 'date_of_birth': today - timedelta(days=800), 'weight': Decimal('470'), 'color': 'Black and White', 'status': 'active'},
            {'farm': farms[4], 'tag_id': 'GH-COW-003', 'name': 'Duke', 'category': cat_cattle, 'breed': breed_ayrshire, 'gender': 'male', 'date_of_birth': today - timedelta(days=600), 'weight': Decimal('600'), 'color': 'Brown and White', 'status': 'active'},
            {'farm': farms[5], 'tag_id': 'GH-GT-001', 'name': 'Thunder', 'category': cat_goats, 'breed': breed_boer, 'gender': 'male', 'date_of_birth': today - timedelta(days=250), 'weight': Decimal('95'), 'color': 'Brown', 'status': 'active'},
            {'farm': farms[5], 'tag_id': 'GH-GT-002', 'name': 'Breeze', 'category': cat_goats, 'breed': breed_boer, 'gender': 'female', 'date_of_birth': today - timedelta(days=300), 'weight': Decimal('70'), 'color': 'White', 'status': 'active'},
            {'farm': farms[5], 'tag_id': 'GH-GT-003', 'name': 'Storm', 'category': cat_goats, 'breed': breed_boer, 'gender': 'male', 'date_of_birth': today - timedelta(days=180), 'weight': Decimal('60'), 'color': 'Brown and White', 'status': 'active'},
        ]
        animals = []
        for d in animal_data:
            animal, _ = Animal.objects.get_or_create(farm=d['farm'], tag_id=d['tag_id'], defaults=d)
            animals.append(animal)
        return animals

    def _create_health_records(self, animals):
        self.stdout.write('  [4/8] Creating health records...')
        today = date.today()
        records = [
            {'animal': animals[0], 'record_type': 'vaccination', 'date': today - timedelta(days=90), 'vet_name': 'Dr. Ochieng', 'diagnosis': 'Routine FMD vaccination', 'treatment': 'FMD vaccine administered', 'medicine': 'FMD Vaccine', 'cost': Decimal('500'), 'next_due_date': today + timedelta(days=10)},
            {'animal': animals[0], 'record_type': 'deworming', 'date': today - timedelta(days=60), 'vet_name': 'Dr. Ochieng', 'treatment': 'Oral dewormer given', 'medicine': 'Ivermectin', 'cost': Decimal('300')},
            {'animal': animals[1], 'record_type': 'vaccination', 'date': today - timedelta(days=120), 'vet_name': 'Dr. Ochieng', 'treatment': 'Anthrax vaccination', 'medicine': 'Anthrax Spore Vaccine', 'cost': Decimal('400'), 'next_due_date': today + timedelta(days=60)},
            {'animal': animals[1], 'record_type': 'checkup', 'date': today - timedelta(days=30), 'vet_name': 'Dr. Ochieng', 'diagnosis': 'Healthy, good body condition', 'cost': Decimal('1000')},
            {'animal': animals[2], 'record_type': 'treatment', 'date': today - timedelta(days=15), 'vet_name': 'Dr. Ochieng', 'diagnosis': 'Mild mastitis', 'treatment': 'Antibiotic injection and udder spray', 'medicine': 'Penicillin, Mastitis Spray', 'cost': Decimal('2500')},
            {'animal': animals[5], 'record_type': 'treatment', 'date': today - timedelta(days=3), 'vet_name': 'Dr. Ochieng', 'diagnosis': 'Bloating and loss of appetite', 'treatment': 'Antifoaming agent administered, IV fluids', 'medicine': 'Dimethicone, Dextrose IV', 'cost': Decimal('3000'), 'next_due_date': today - timedelta(days=1)},
            {'animal': animals[3], 'record_type': 'vaccination', 'date': today - timedelta(days=200), 'vet_name': 'Dr. Ochieng', 'treatment': 'Rabies vaccination', 'medicine': 'Rabies Vaccine', 'cost': Decimal('600'), 'next_due_date': today - timedelta(days=5)},
            {'animal': animals[6], 'record_type': 'checkup', 'date': today - timedelta(days=10), 'vet_name': 'Dr. Ochieng', 'diagnosis': 'Healthy, due for calving in 2 months', 'cost': Decimal('800')},
            {'animal': animals[16], 'record_type': 'vaccination', 'date': today - timedelta(days=45), 'vet_name': 'Dr. Ochieng', 'treatment': 'Brucellosis vaccination', 'medicine': 'S19 Vaccine', 'cost': Decimal('700'), 'next_due_date': today + timedelta(days=90)},
            {'animal': animals[16], 'record_type': 'checkup', 'date': today - timedelta(days=5), 'vet_name': 'Dr. Ochieng', 'diagnosis': 'Excellent condition, producing 28L daily', 'cost': Decimal('1000')},
            {'animal': animals[17], 'record_type': 'vaccination', 'date': today - timedelta(days=100), 'vet_name': 'Dr. Ochieng', 'treatment': 'FMD booster', 'medicine': 'FMD Vaccine', 'cost': Decimal('500'), 'next_due_date': today - timedelta(days=2)},
        ]
        for d in records:
            HealthRecord.objects.get_or_create(animal=d['animal'], record_type=d['record_type'], date=d['date'], defaults=d)

    def _create_production_records(self, animals):
        self.stdout.write('  [5/8] Creating production records...')
        today = date.today()
        dairy_cows = [a for a in animals if a.category and a.category.name == 'Cattle' and a.status == 'active']
        layer_poultry = [animals[8], animals[10], animals[11]]
        for cow in dairy_cows:
            base = random.uniform(15, 28)
            for days_ago in range(30):
                qty = round(Decimal(str(base + random.uniform(-3, 3))), 1)
                ProductionRecord.objects.get_or_create(animal=cow, record_type='milk', date=today - timedelta(days=days_ago), defaults={'quantity': qty})
        for bird in layer_poultry:
            base = random.uniform(80, 120)
            for days_ago in range(30):
                qty = round(Decimal(str(base + random.uniform(-20, 20))), 0)
                ProductionRecord.objects.get_or_create(animal=bird, record_type='eggs', date=today - timedelta(days=days_ago), defaults={'quantity': qty})

    def _create_transactions(self, farmers):
        self.stdout.write('  [6/8] Creating M-Pesa transactions...')
        today = timezone.now()
        txns = [
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('5000'), 'purpose': 'feed', 'description': 'Dairy meal purchase - 5 bags', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK4H5Q6KL', 'created_at': today - timedelta(days=2)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('2500'), 'purpose': 'vet_services', 'description': 'Clover treatment - bloating', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK3F2R8KM', 'created_at': today - timedelta(days=3)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('500'), 'purpose': 'medicine', 'description': 'Dewormer for cattle', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK7G1N4PQ', 'created_at': today - timedelta(days=7)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('12000'), 'purpose': 'feed', 'description': 'Hay bales - 50 bales', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK9H3W2RT', 'created_at': today - timedelta(days=15)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('3000'), 'purpose': 'labour', 'description': 'Farm worker weekly pay', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK2J6K5MN', 'created_at': today - timedelta(days=20)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('8000'), 'purpose': 'transport', 'description': 'Transport to market', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK5L8P3QR', 'created_at': today - timedelta(days=25)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('35000'), 'purpose': 'product_sale', 'description': 'Milk sales - Brookside 2 weeks', 'is_expense': False, 'status': 'success', 'mpesa_receipt': 'SBK1M4N7ST', 'created_at': today - timedelta(days=1)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('15000'), 'purpose': 'product_sale', 'description': 'Milk sales - Brookside', 'is_expense': False, 'status': 'success', 'mpesa_receipt': 'SBK6N9Q2UV', 'created_at': today - timedelta(days=10)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('85000'), 'purpose': 'animal_sale', 'description': 'Sold Old Ben - Friesian bull', 'is_expense': False, 'status': 'success', 'mpesa_receipt': 'SBK3P5R8WX', 'created_at': today - timedelta(days=18)},
            {'farmer': farmers[2], 'phone_number': '+254723456789', 'amount': Decimal('15000'), 'purpose': 'feed', 'description': 'Layer mash - 10 bags', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK8Q6S1YZ', 'created_at': today - timedelta(days=3)},
            {'farmer': farmers[2], 'phone_number': '+254723456789', 'amount': Decimal('8000'), 'purpose': 'feed', 'description': 'Broiler starter - 5 bags', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK4R7T3AB', 'created_at': today - timedelta(days=10)},
            {'farmer': farmers[2], 'phone_number': '+254723456789', 'amount': Decimal('2000'), 'purpose': 'medicine', 'description': 'Vaccines - Newcastle', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK9S8U5CD', 'created_at': today - timedelta(days=20)},
            {'farmer': farmers[2], 'phone_number': '+254723456789', 'amount': Decimal('25000'), 'purpose': 'product_sale', 'description': 'Egg sales - 10 trays', 'is_expense': False, 'status': 'success', 'mpesa_receipt': 'SBK2T9V7EF', 'created_at': today - timedelta(days=2)},
            {'farmer': farmers[2], 'phone_number': '+254723456789', 'amount': Decimal('18000'), 'purpose': 'product_sale', 'description': 'Egg sales - 7 trays', 'is_expense': False, 'status': 'success', 'mpesa_receipt': 'SBK5U1W9GH', 'created_at': today - timedelta(days=12)},
            {'farmer': farmers[2], 'phone_number': '+254723456789', 'amount': Decimal('45000'), 'purpose': 'animal_sale', 'description': 'Sold 500 broilers', 'is_expense': False, 'status': 'success', 'mpesa_receipt': 'SBK7V2X3IJ', 'created_at': today - timedelta(days=22)},
            {'farmer': farmers[4], 'phone_number': '+254745678901', 'amount': Decimal('20000'), 'purpose': 'feed', 'description': 'Dairy meal - 10 bags', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK1W3Y5KL', 'created_at': today - timedelta(days=5)},
            {'farmer': farmers[4], 'phone_number': '+254745678901', 'amount': Decimal('40000'), 'purpose': 'product_sale', 'description': 'Milk sales - monthly', 'is_expense': False, 'status': 'success', 'mpesa_receipt': 'SBK6X4Z7MN', 'created_at': today - timedelta(days=8)},
            {'farmer': farmers[4], 'phone_number': '+254745678901', 'amount': Decimal('1500'), 'purpose': 'vet_services', 'description': 'Vaccination - Brucellosis', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK3Y5A1OP', 'created_at': today - timedelta(days=14)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('30000'), 'purpose': 'product_sale', 'description': 'Milk sales', 'is_expense': False, 'status': 'success', 'mpesa_receipt': 'SBK8A2B4QR', 'created_at': today - timedelta(days=40)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('8000'), 'purpose': 'feed', 'description': 'Dairy meal', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK4B3C6ST', 'created_at': today - timedelta(days=45)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('28000'), 'purpose': 'product_sale', 'description': 'Milk sales', 'is_expense': False, 'status': 'success', 'mpesa_receipt': 'SBK9C4D7UV', 'created_at': today - timedelta(days=70)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('10000'), 'purpose': 'vet_services', 'description': 'Vet checkup all cattle', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK2D5E8WX', 'created_at': today - timedelta(days=75)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('32000'), 'purpose': 'product_sale', 'description': 'Milk sales', 'is_expense': False, 'status': 'success', 'mpesa_receipt': 'SBK7E6F9YZ', 'created_at': today - timedelta(days=100)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('6000'), 'purpose': 'medicine', 'description': 'Vaccines', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK1F7G1AB', 'created_at': today - timedelta(days=105)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('25000'), 'purpose': 'product_sale', 'description': 'Milk sales', 'is_expense': False, 'status': 'success', 'mpesa_receipt': 'SBK5G8H2CD', 'created_at': today - timedelta(days=135)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('7000'), 'purpose': 'feed', 'description': 'Hay purchase', 'is_expense': True, 'status': 'success', 'mpesa_receipt': 'SBK3H9I3EF', 'created_at': today - timedelta(days=140)},
            {'farmer': farmers[1], 'phone_number': '+254712345678', 'amount': Decimal('27000'), 'purpose': 'product_sale', 'description': 'Milk sales', 'is_expense': False, 'status': 'success', 'mpesa_receipt': 'SBK8I1J4GH', 'created_at': today - timedelta(days=165)},
        ]
        for d in txns:
            d['transaction_type'] = 'stk_push'
            MpesaTransaction.objects.get_or_create(farmer=d['farmer'], mpesa_receipt=d['mpesa_receipt'], defaults=d)

    def _create_marketplace_listings(self, farmers, farms, animals):
        self.stdout.write('  [7/8] Creating marketplace listings...')
        listings = [
            {'seller': farmers[1], 'farm': farms[0], 'title': 'Grade 1 Friesian Heifer - Ready for Breeding', 'category': 'animal', 'animal': animals[2], 'description': 'Beautiful Ayrshire heifer, 20 months old, well-fed and vaccinated. Ready for first service. Located in Molo.', 'price': Decimal('65000'), 'negotiable': True, 'location': 'Molo, Nakuru', 'county': 'Nakuru', 'status': 'active', 'views_count': 23},
            {'seller': farmers[4], 'farm': farms[5], 'title': 'Boer Buck - Premium Breeding Stock', 'category': 'animal', 'animal': animals[18], 'description': 'Purebred Boer buck, 6 months old. Excellent genetics. Perfect for upgrading your goat herd.', 'price': Decimal('35000'), 'negotiable': True, 'location': 'Limuru, Kiambu', 'county': 'Kiambu', 'status': 'active', 'views_count': 45},
            {'seller': farmers[4], 'farm': farms[5], 'title': 'Boer Doe - Ready for Breeding', 'category': 'animal', 'animal': animals[19], 'description': '10-month old Boer doe, vaccinated and dewormed. Healthy and well-fed.', 'price': Decimal('25000'), 'negotiable': True, 'location': 'Limuru, Kiambu', 'county': 'Kiambu', 'status': 'active', 'views_count': 31},
            {'seller': farmers[2], 'farm': farms[2], 'title': 'Fresh Kuroiler Eggs - Farm Direct', 'category': 'eggs', 'description': 'Farm-fresh Kuroiler eggs, collected daily. Bulk discounts available for orders over 5 trays.', 'price': Decimal('450'), 'negotiable': False, 'location': 'Eldoret', 'county': 'Uasin Gishu', 'status': 'active', 'views_count': 67},
            {'seller': farmers[1], 'farm': farms[0], 'title': 'Fresh Whole Milk - Daily Delivery', 'category': 'milk', 'description': 'Premium fresh whole milk from Friesian cows. Available daily in Nakuru town. Minimum 20 litres.', 'price': Decimal('60'), 'negotiable': False, 'location': 'Nakuru Town', 'county': 'Nakuru', 'status': 'active', 'views_count': 89},
            {'seller': farmers[3], 'farm': farms[3], 'title': 'Mixed Goat Herd - 5 Does + 1 Buck', 'category': 'animal', 'description': 'Package deal: 5 mature Boer/Saanen does and 1 Boer buck. All vaccinated and healthy.', 'price': Decimal('120000'), 'negotiable': True, 'location': 'Kisumu', 'county': 'Kisumu', 'status': 'active', 'views_count': 52},
        ]
        created = []
        for d in listings:
            lst, _ = MarketplaceListing.objects.get_or_create(seller=d['seller'], title=d['title'], defaults=d)
            created.append(lst)
        BuyerInquiry.objects.get_or_create(listing=created[0], buyer=farmers[4], defaults={'message': 'I am interested in the Ayrshire heifer. Can you share more details about her vaccination history?', 'offer_price': Decimal('60000'), 'phone_number': '+254745678901', 'status': 'pending'})
        BuyerInquiry.objects.get_or_create(listing=created[1], buyer=farmers[1], defaults={'message': 'Is the Boer buck still available? Can you deliver to Nakuru?', 'offer_price': Decimal('32000'), 'phone_number': '+254712345678', 'status': 'responded', 'seller_response': 'Yes! Delivery to Nakuru at KES 3,000 extra.'})
        BuyerInquiry.objects.get_or_create(listing=created[3], buyer=farmers[1], defaults={'message': 'I need 10 trays of Kuroiler eggs weekly. Best price?', 'phone_number': '+254712345678', 'status': 'accepted', 'seller_response': 'KES 420 per tray for regular orders.'})

    def _create_notifications_and_schedules(self, farmers, farms, animals):
        self.stdout.write('  [8/8] Creating notifications and schedules...')
        today = timezone.now()
        notifs = [
            {'farmer': farmers[1], 'title': 'Vaccination Overdue - Bella (HV-COW-004)', 'message': 'The rabies vaccination for Bella was due 5 days ago. Please schedule a vet visit immediately.', 'notification_type': 'vaccination', 'action_url': '/animals/' + str(animals[3].pk) + '/', 'is_read': False},
            {'farmer': farmers[1], 'title': 'Vaccination Due Soon - Daisy (HV-COW-001)', 'message': 'FMD vaccination for Daisy is due in 10 days. Contact your vet to schedule.', 'notification_type': 'vaccination', 'action_url': '/animals/' + str(animals[0].pk) + '/', 'is_read': False},
            {'farmer': farmers[1], 'title': 'New Buyer Inquiry - Ayrshire Heifer', 'message': 'Peter Mwangi is interested in your listing. They offered KES 60,000.', 'notification_type': 'marketplace', 'is_read': True},
            {'farmer': farmers[1], 'title': 'Payment Received - KES 35,000', 'message': 'KES 35,000 received from Brookside for milk sales.', 'notification_type': 'payment', 'is_read': True},
            {'farmer': farmers[1], 'title': 'Health Alert - Clover (HV-COW-006)', 'message': 'Clover was treated for bloating 3 days ago. Follow-up is overdue.', 'notification_type': 'health', 'action_url': '/animals/' + str(animals[5].pk) + '/', 'is_read': False},
            {'farmer': farmers[2], 'title': 'Egg Supply Order Confirmed', 'message': 'John Kamau accepted your egg supply offer. 10 trays/week at KES 420 each.', 'notification_type': 'marketplace', 'is_read': False},
            {'farmer': farmers[4], 'title': 'Vaccination Overdue - Princess (GH-COW-002)', 'message': 'FMD booster for Princess was due 2 days ago. Schedule urgently.', 'notification_type': 'vaccination', 'action_url': '/animals/' + str(animals[17].pk) + '/', 'is_read': False},
            {'farmer': farmers[4], 'title': 'Marketplace Response Received', 'message': 'Seller responded to your inquiry about the Boer buck.', 'notification_type': 'marketplace', 'is_read': True},
        ]
        for d in notifs:
            Notification.objects.get_or_create(farmer=d['farmer'], title=d['title'], defaults=d)
        schedules = [
            {'farm': farms[0], 'feed_type': 'Dairy Meal', 'quantity': '3kg per cow', 'frequency': 'twice_daily', 'time': '06:00:00'},
            {'farm': farms[0], 'feed_type': 'Hay', 'quantity': '5kg per cow', 'frequency': 'twice_daily', 'time': '12:00:00'},
            {'farm': farms[0], 'animal': animals[5], 'feed_type': 'Special Treatment Feed', 'quantity': '2kg', 'frequency': 'daily', 'time': '07:00:00'},
            {'farm': farms[2], 'feed_type': 'Layer Mash', 'quantity': '120g per bird', 'frequency': 'daily', 'time': '06:30:00'},
            {'farm': farms[2], 'feed_type': 'Broiler Starter', 'quantity': 'Ad libitum', 'frequency': 'daily', 'time': '06:30:00'},
            {'farm': farms[4], 'feed_type': 'Premium Dairy Meal', 'quantity': '4kg per cow', 'frequency': 'twice_daily', 'time': '05:30:00'},
            {'farm': farms[5], 'feed_type': 'Goat Pellets + Hay', 'quantity': '2kg pellets + hay', 'frequency': 'daily', 'time': '07:00:00'},
        ]
        for d in schedules:
            FeedingSchedule.objects.get_or_create(farm=d['farm'], feed_type=d['feed_type'], defaults=d)
