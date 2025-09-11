from django.db import models
from django.core.validators import RegexValidator

class Customer(models.Model):
    """Customer model for car service system"""
    
    # Basic customer information
    number = models.IntegerField(unique=True, verbose_name="Номер")
    
    # Customer details (multiple Customer fields from the structure)
    customer_name = models.CharField(max_length=255, verbose_name="Име на клиент")
    customer_address_1 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес 1")
    customer_address_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес 2")
    customer_mol = models.CharField(max_length=255, blank=True, null=True, verbose_name="МОЛ")
    customer_taxno = models.CharField(max_length=20, blank=True, null=True, verbose_name="ДДС номер")
    customer_doctype = models.SmallIntegerField(default=0, verbose_name="Тип документ")
    
    # Receiver information
    receiver = models.CharField(max_length=255, blank=True, null=True, verbose_name="Получател")
    receiver_details = models.CharField(max_length=255, blank=True, null=True, verbose_name="Детайли за получател")
    
    # Contact information
    customer_bulstat = models.CharField(
        max_length=11, 
        blank=True, 
        null=True, 
        verbose_name="БУЛСТАТ",
        validators=[RegexValidator(r'^\d{9,11}$', 'БУЛСТАТ трябва да бъде 9-11 цифри')]
    )
    telno = models.CharField(max_length=50, blank=True, null=True, verbose_name="Телефон")
    faxno = models.CharField(max_length=50, blank=True, null=True, verbose_name="Факс")
    email = models.EmailField(blank=True, null=True, verbose_name="Имейл")
    
    # Residential address
    res_address_1 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес за живеене 1")
    res_address_2 = models.CharField(max_length=255, blank=True, null=True, verbose_name="Адрес за живеене 2")
    
    # Dates and status
    eidate = models.DateTimeField(blank=True, null=True, verbose_name="Дата на влизане")
    include = models.BooleanField(default=False, verbose_name="Включен")
    active = models.BooleanField(default=True, verbose_name="Активен")
    customer = models.BooleanField(default=True, verbose_name="Клиент")
    supplier = models.BooleanField(default=False, verbose_name="Доставчик")
    
    # Additional information
    contact = models.CharField(max_length=255, blank=True, null=True, verbose_name="Контакт")
    partida = models.IntegerField(blank=True, null=True, verbose_name="Партида")
    bulstatletter = models.CharField(max_length=10, blank=True, null=True, verbose_name="БУЛСТАТ буква")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Създаден на")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновен на")
    
    class Meta:
        verbose_name = "Клиент"
        verbose_name_plural = "Клиенти"
        ordering = ['customer_name']
        indexes = [
            models.Index(fields=['customer_name']),
            models.Index(fields=['customer_taxno']),
            models.Index(fields=['customer_bulstat']),
            models.Index(fields=['active']),
        ]
    
    def __str__(self):
        return f"{self.number} - {self.customer_name}"
    
    @property
    def full_address(self):
        """Return full address as string"""
        address_parts = [self.customer_address_1, self.customer_address_2]
        return ', '.join(filter(None, address_parts))
    
    @property
    def contact_info(self):
        """Return contact information as string"""
        contact_parts = []
        if self.telno:
            contact_parts.append(f"Тел: {self.telno}")
        if self.email:
            contact_parts.append(f"Имейл: {self.email}")
        return ' | '.join(contact_parts)


class Car(models.Model):
    """Car model for customer vehicles"""
    
    customer = models.ForeignKey(
        Customer, 
        on_delete=models.CASCADE, 
        related_name='cars',
        verbose_name="Клиент"
    )
    
    # Car information
    brand_model = models.CharField(
        max_length=255, 
        verbose_name="Марка и модел",
        help_text="Например: FIAT DUCATO (250) 120 Multijet 2,3 D"
    )
    vin = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="VIN/Шаси номер",
        help_text="Уникален номер на шасито"
    )
    plate_number = models.CharField(
        max_length=20, 
        blank=True, 
        null=True, 
        verbose_name="Регистрационен номер",
        help_text="Например: CA1234AB"
    )
    
    # Additional car details
    year = models.IntegerField(
        blank=True, 
        null=True, 
        verbose_name="Година на производство"
    )
    color = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="Цвят"
    )
    engine_number = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="Номер на двигател"
    )
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Създадена на")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновена на")
    
    class Meta:
        verbose_name = "Кола"
        verbose_name_plural = "Коли"
        ordering = ['brand_model']
        indexes = [
            models.Index(fields=['brand_model']),
            models.Index(fields=['vin']),
            models.Index(fields=['plate_number']),
            models.Index(fields=['is_active']),
        ]
        unique_together = [
            ['customer', 'vin'],  # Same VIN can't be assigned to same customer twice
        ]
    
    def __str__(self):
        return f"{self.brand_model} - {self.plate_number or self.vin or 'Без номер'}"
    
    @property
    def display_name(self):
        """Return formatted car name for display"""
        parts = [self.brand_model]
        if self.plate_number:
            parts.append(f"({self.plate_number})")
        elif self.vin:
            parts.append(f"VIN: {self.vin}")
        return " ".join(parts)


class Employee(models.Model):
    """Employee model for car service staff"""
    
    # Basic information
    first_name = models.CharField(
        max_length=100, 
        verbose_name="Име"
    )
    last_name = models.CharField(
        max_length=100, 
        verbose_name="Фамилия"
    )
    
    hourly_rate = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        blank=True, 
        null=True, 
        verbose_name="Почасова ставка",
        help_text="Почасова ставка в лева"
    )
    
    # Employment details
    hire_date = models.DateField(
        blank=True, 
        null=True, 
        verbose_name="Дата на назначаване"
    )
    is_active = models.BooleanField(
        default=True, 
        verbose_name="Активен"
    )
    
    # Annual leave tracking
    annual_leave_days = models.IntegerField(
        default=20,
        verbose_name="Годишни отпускни дни",
        help_text="Общо годишни отпускни дни (по подразбиране 20 за България)"
    )
    current_year_leave_used = models.IntegerField(
        default=0,
        verbose_name="Използвани отпускни дни за текущата година"
    )
    
    # Additional information
    notes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Бележки"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Създаден на")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновен на")
    
    class Meta:
        verbose_name = "Служител"
        verbose_name_plural = "Служители"
        ordering = ['first_name', 'last_name']
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Return full name"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def remaining_leave_days(self):
        """Calculate remaining annual leave days for current year"""
        return max(0, self.annual_leave_days - self.current_year_leave_used)
    
    def update_leave_usage(self):
        """Update current year leave usage based on approved vacation days"""
        from datetime import date
        
        current_year = date.today().year
        approved_vacation_days_off = self.days_off.filter(
            day_off_type='vacation',
            is_approved=True,
            start_date__year=current_year
        )
        
        # Calculate total days manually
        total_days = 0
        for day_off in approved_vacation_days_off:
            total_days += day_off.duration_days
        
        
        self.current_year_leave_used = total_days
        self.save(update_fields=['current_year_leave_used'])


class DaysOff(models.Model):
    """Model for tracking employee days off"""
    
    DAY_OFF_TYPES = [
        ('vacation', 'Годишен отпуск'),
        ('sick', 'Болничен'),
        ('personal', 'Лични причини'),
        ('holiday', 'Празник'),
        ('other', 'Друго'),
    ]
    
    employee = models.ForeignKey(
        Employee, 
        on_delete=models.CASCADE, 
        related_name='days_off',
        verbose_name="Служител"
    )
    
    # Date information
    start_date = models.DateField(verbose_name="Начална дата")
    end_date = models.DateField(verbose_name="Крайна дата")
    
    # Type and details
    day_off_type = models.CharField(
        max_length=20, 
        choices=DAY_OFF_TYPES, 
        default='vacation',
        verbose_name="Тип отпуск"
    )
    reason = models.CharField(
        max_length=255, 
        blank=True, 
        null=True, 
        verbose_name="Причина"
    )
    notes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Бележки"
    )
    
    # Status
    is_approved = models.BooleanField(
        default=False, 
        verbose_name="Одобрен"
    )
    approved_by = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name="Одобрен от"
    )
    approved_at = models.DateTimeField(
        blank=True, 
        null=True, 
        verbose_name="Одобрен на"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Създаден на")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновен на")
    
    class Meta:
        verbose_name = "Дни отпуск"
        verbose_name_plural = "Дни отпуск"
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['day_off_type']),
            models.Index(fields=['is_approved']),
        ]
    
    def __str__(self):
        return f"{self.employee.full_name} - {self.get_day_off_type_display()} ({self.start_date} - {self.end_date})"
    
    @property
    def duration_days(self):
        """Calculate duration in days (inclusive)"""
        return (self.end_date - self.start_date).days + 1
    
    @property
    def is_current(self):
        """Check if the day off is current (includes today)"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date


class Event(models.Model):
    """Model for calendar events (like Google Calendar)"""
    EVENT_TYPES = [
        ('meeting', 'Среща'),
        ('appointment', 'Записване'),
        ('maintenance', 'Поддръжка'),
        ('inspection', 'Преглед'),
        ('delivery', 'Доставка'),
        ('other', 'Друго'),
    ]
    
    title = models.CharField(max_length=255, verbose_name="Заглавие")
    description = models.TextField(blank=True, null=True, verbose_name="Описание")
    event_type = models.CharField(
        max_length=20, 
        choices=EVENT_TYPES, 
        default='meeting',
        verbose_name="Тип събитие"
    )
    start_datetime = models.DateTimeField(verbose_name="Начало")
    end_datetime = models.DateTimeField(verbose_name="Край")
    is_all_day = models.BooleanField(default=False, verbose_name="Цял ден")
    
    # Optional: Link to customer or employee
    customer = models.ForeignKey(
        'Customer',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Клиент"
    )
    employee = models.ForeignKey(
        'Employee',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Служител"
    )
    
    # Status and notes
    is_completed = models.BooleanField(default=False, verbose_name="Завършено")
    notes = models.TextField(blank=True, null=True, verbose_name="Бележки")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Създадено на")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновено на")
    
    class Meta:
        verbose_name = "Събитие"
        verbose_name_plural = "Събития"
        ordering = ['start_datetime']
        indexes = [
            models.Index(fields=['start_datetime', 'end_datetime']),
            models.Index(fields=['event_type']),
            models.Index(fields=['is_completed']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.start_datetime.strftime('%d.%m.%Y %H:%M')}"
    
    @property
    def duration_hours(self):
        """Calculate duration in hours"""
        delta = self.end_datetime - self.start_datetime
        return delta.total_seconds() / 3600
    
    @property
    def is_today(self):
        """Check if event is today"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_datetime.date() == today
    
    @property
    def is_past(self):
        """Check if event is in the past"""
        from django.utils import timezone
        now = timezone.now()
        return self.end_datetime < now


class Sklad(models.Model):
    """Warehouse/Inventory model for car service system"""
    
    # Article number (Артикул N)
    article_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Артикул N",
        help_text="Уникален номер на артикула"
    )
    
    # Product name (Наименование)
    name = models.CharField(
        max_length=255, 
        verbose_name="Наименование",
        help_text="Име на продукта"
    )
    
    # Unit of measure (Мр.)
    unit = models.CharField(
        max_length=20, 
        verbose_name="Мр.",
        help_text="Мерна единица (бр, кг, л, м, и т.н.)",
        default="бр"
    )
    
    # Quantity in stock (Наличност)
    quantity = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Наличност",
        help_text="Количество в наличност"
    )
    
    # Purchase price (Дост. цена)
    purchase_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        verbose_name="Дост. цена",
        help_text="Доставна цена за единица"
    )
    
    # Total value (Стойност) - calculated field
    @property
    def total_value(self):
        """Calculate total value (quantity * purchase_price)"""
        return self.quantity * self.purchase_price
    
    # Status
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Създаден на")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновен на")
    
    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склад"
        ordering = ['article_number']
        indexes = [
            models.Index(fields=['article_number']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.article_number} - {self.name}"
    
    def save(self, *args, **kwargs):
        """Override save to ensure article_number is uppercase"""
        self.article_number = self.article_number.upper()
        super().save(*args, **kwargs)
