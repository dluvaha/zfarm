from django.db import models
from django.conf import settings
import uuid


class AnimalCategory(models.Model):
    """Livestock category (cattle, goats, sheep, poultry, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    icon = models.CharField(max_length=50, default='🐄', help_text="Emoji icon for display")
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Animal Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Breed(models.Model):
    """Animal breeds within categories"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(AnimalCategory, on_delete=models.CASCADE, related_name='breeds')
    name = models.CharField(max_length=100)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class Animal(models.Model):
    """Individual animal record"""
    GENDER_CHOICES = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('sold', 'Sold'),
        ('died', 'Died'),
        ('transferred', 'Transferred'),
        ('sick', 'Sick'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    farm = models.ForeignKey('accounts.Farm', on_delete=models.CASCADE, related_name='animals')
    tag_id = models.CharField(max_length=50, unique=True, help_text="Unique ear tag or identification number")
    name = models.CharField(max_length=100, blank=True)
    category = models.ForeignKey(AnimalCategory, on_delete=models.SET_NULL, null=True)
    breed = models.ForeignKey(Breed, on_delete=models.SET_NULL, null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='female')
    date_of_birth = models.DateField(null=True, blank=True)
    date_purchased = models.DateField(null=True, blank=True)
    purchase_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    purchase_from = models.CharField(max_length=200, blank=True)
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, help_text="Current weight in kg")
    color = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notes = models.TextField(blank=True)
    image = models.ImageField(upload_to='animals/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['farm', 'tag_id']

    def __str__(self):
        return f"{self.tag_id} - {self.name or self.breed or 'Unnamed'}"

    @property
    def age_display(self):
        if not self.date_of_birth:
            return "Unknown"
        from django.utils import timezone
        from dateutil.relativedelta import relativedelta
        delta = relativedelta(timezone.now().date(), self.date_of_birth)
        years = delta.years
        months = delta.months
        if years > 0:
            return f"{years}y {months}m"
        return f"{months}m"

    @property
    def health_records_count(self):
        return self.health_records.count()

    @property
    def last_health_check(self):
        return self.health_records.order_by('-date').first()


class HealthRecord(models.Model):
    """Animal health records (vaccinations, treatments, checkups)"""
    RECORD_TYPES = [
        ('vaccination', 'Vaccination'),
        ('treatment', 'Treatment'),
        ('checkup', 'Checkup'),
        ('deworming', 'Deworming'),
        ('surgery', 'Surgery'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='health_records')
    record_type = models.CharField(max_length=20, choices=RECORD_TYPES, default='checkup')
    date = models.DateField()
    vet_name = models.CharField(max_length=200, blank=True, help_text="Veterinarian who performed the service")
    diagnosis = models.TextField(blank=True)
    treatment = models.TextField(blank=True)
    medicine = models.CharField(max_length=200, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    next_due_date = models.DateField(null=True, blank=True, help_text="Next vaccination or checkup date")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.animal.tag_id} - {self.record_type} on {self.date}"

    @property
    def is_overdue(self):
        if not self.next_due_date:
            return False
        from django.utils import timezone
        return timezone.now().date() > self.next_due_date


class ProductionRecord(models.Model):
    """Production tracking (milk, eggs, weight)"""
    TYPE_CHOICES = [
        ('milk', 'Milk Production'),
        ('eggs', 'Egg Production'),
        ('weight', 'Weight Check'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='production_records')
    record_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date = models.DateField()
    quantity = models.DecimalField(max_digits=10, decimal_places=2, help_text="Litres for milk, count for eggs, kg for weight")
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Production Record'
        verbose_name_plural = 'Production Records'

    def __str__(self):
        unit = {'milk': 'L', 'eggs': 'pcs', 'weight': 'kg'}[self.record_type]
        return f"{self.animal.tag_id} - {self.quantity} {unit} on {self.date}"


class AnimalMovement(models.Model):
    """Track animal movements (sold, bought, died, transferred)"""
    MOVEMENT_TYPES = [
        ('purchased', 'Purchased'),
        ('sold', 'Sold'),
        ('died', 'Died'),
        ('transferred_in', 'Transferred In'),
        ('transferred_out', 'Transferred Out'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    animal = models.ForeignKey(Animal, on_delete=models.CASCADE, related_name='movements')
    movement_type = models.CharField(max_length=20, choices=MOVEMENT_TYPES)
    date = models.DateField()
    from_location = models.CharField(max_length=200, blank=True)
    to_location = models.CharField(max_length=200, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"{self.animal.tag_id} - {self.movement_type} on {self.date}"
