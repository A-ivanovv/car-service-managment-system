from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone

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
    
    @property
    def customer_type(self):
        """Determine if customer is individual or company based on business fields"""
        if self.customer_bulstat or self.customer_mol or self.customer_taxno:
            return "Фирма"
        return "Частно лице"
    
    @property
    def customer_type_icon(self):
        """Get icon for customer type"""
        if self.customer_type == "Фирма":
            return "fas fa-building"
        return "fas fa-user"


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
    
    def save(self, *args, **kwargs):
        """Override save to ensure article_number is uppercase"""
        self.article_number = self.article_number.upper()
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.article_number} - {self.name}"


class Order(models.Model):
    """Order model for car service repairs"""
    
    ORDER_STATUS_CHOICES = [
        ('offer', 'Оферта'),
        ('invoice', 'Изготвена фактура'),
        ('order', 'Изготвена поръчка'),
    ]
    
    # Order basic information
    order_number = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="Номер на поръчката",
        help_text="Уникален номер на поръчката"
    )
    
    order_date = models.DateField(
        verbose_name="Дата на поръчката",
        help_text="Дата на създаване на поръчката"
    )
    
    # Car information (can be linked to existing car or standalone)
    car = models.ForeignKey(
        Car,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Кола",
        help_text="Изберете кола от базата данни"
    )
    
    # Standalone car information (if not linked to existing car)
    car_brand_model = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Марка и модел",
        help_text="Например: C4 Picasso"
    )
    car_vin = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="VIN/Шаси номер",
        help_text="Уникален номер на шасито"
    )
    car_plate_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Регистрационен номер",
        help_text="Например: СВ5602TK"
    )
    car_mileage = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="Изминати км",
        help_text="Текущ пробег на колата"
    )
    
    # Client information (can be linked to existing client or standalone)
    client = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Клиент",
        help_text="Изберете клиент от базата данни"
    )
    
    # Standalone client information (if not linked to existing client)
    client_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Име на клиента",
        help_text="Име на клиента"
    )
    client_address = models.CharField(
        max_length=500,
        blank=True,
        null=True,
        verbose_name="Адрес на клиента",
        help_text="Адрес на клиента"
    )
    client_phone = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Телефон на клиента",
        help_text="Телефонен номер на клиента"
    )
    
    # Employees working on this order
    employees = models.ManyToManyField(
        Employee,
        blank=True,
        verbose_name="Служители",
        help_text="Служители, които работят по тази поръчка"
    )
    
    # Order status and notes
    status = models.CharField(
        max_length=20,
        choices=ORDER_STATUS_CHOICES,
        default='pending',
        verbose_name="Статус"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        verbose_name="Бележки",
        help_text="Допълнителни бележки за поръчката"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Създадена на")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновена на")
    
    class Meta:
        verbose_name = "Поръчка"
        verbose_name_plural = "Поръчки"
        ordering = ['-order_date', '-created_at']
        indexes = [
            models.Index(fields=['order_number']),
            models.Index(fields=['order_date']),
            models.Index(fields=['status']),
            models.Index(fields=['car_vin']),
            models.Index(fields=['car_plate_number']),
        ]
    
    def __str__(self):
        return f"Поръчка {self.order_number} - {self.get_car_display()} - {self.get_client_display()}"
    
    def get_car_display(self):
        """Return car display name"""
        if self.car:
            return self.car.display_name
        elif self.car_brand_model:
            parts = [self.car_brand_model]
            if self.car_plate_number:
                parts.append(f"({self.car_plate_number})")
            elif self.car_vin:
                parts.append(f"VIN: {self.car_vin}")
            return " ".join(parts)
        return "Неизвестна кола"
    
    def get_client_display(self):
        """Return client display name"""
        if self.client:
            return self.client.customer_name
        elif self.client_name:
            return self.client_name
        return "Неизвестен клиент"
    
    @property
    def total_without_vat(self):
        """Calculate total without VAT"""
        return sum(item.total_price for item in self.order_items.all())
    
    @property
    def total_vat(self):
        """Calculate total VAT (20%) for items that include VAT"""
        return sum(item.total_vat for item in self.order_items.all())
    
    @property
    def total_with_vat(self):
        """Calculate total with VAT"""
        return sum(item.total_price_with_vat for item in self.order_items.all())
    
    @property
    def labor_total(self):
        """Calculate total labor costs"""
        return sum(item.total_price for item in self.order_items.filter(is_labor=True))


class OrderItem(models.Model):
    """Order item model for parts and services used in orders"""
    
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="Поръчка"
    )
    
    # Part information (can be linked to existing sklad item or standalone)
    sklad_item = models.ForeignKey(
        Sklad,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Артикул от склад",
        help_text="Изберете артикул от склад"
    )
    
    # Standalone part information (if not linked to existing sklad item)
    article_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Артикул номер",
        help_text="Номер на артикула"
    )
    name = models.CharField(
        max_length=255,
        verbose_name="Наименование",
        help_text="Наименование на артикула или услугата"
    )
    unit = models.CharField(
        max_length=20,
        verbose_name="Мерна единица",
        help_text="бр, кг, л, м, норма, и т.н."
    )
    
    # Pricing information
    purchase_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Единична цена без ДДС",
        help_text="Цена за единица без ДДС"
    )
    price_with_vat = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        verbose_name="Единична цена с ДДС",
        help_text="Цена за единица с ДДС"
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Количество",
        help_text="Количество"
    )
    
    # Service type
    is_labor = models.BooleanField(
        default=False,
        verbose_name="Труд",
        help_text="Отметнете ако това е труд/услуга"
    )
    
    # VAT inclusion
    include_vat = models.BooleanField(
        default=True,
        verbose_name="Включи ДДС",
        help_text="Отметнете ако артикулът трябва да включва ДДС"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Създаден на")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновен на")
    
    class Meta:
        verbose_name = "Артикул от поръчка"
        verbose_name_plural = "Артикули от поръчка"
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['is_labor']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.quantity} {self.unit}"
    
    @property
    def calculated_price_with_vat(self):
        """Calculate price with VAT (20%) if include_vat is True"""
        from decimal import Decimal
        if self.include_vat:
            return self.purchase_price * Decimal('1.20')
        return self.purchase_price
    
    def get_price_with_vat(self):
        """Get price with VAT - use stored value if available, otherwise calculate"""
        if self.price_with_vat is not None:
            return self.price_with_vat
        return self.calculated_price_with_vat
    
    @property
    def total_price(self):
        """Calculate total price without VAT"""
        return self.purchase_price * self.quantity
    
    @property
    def total_vat(self):
        """Calculate total VAT (20%) if include_vat is True"""
        from decimal import Decimal
        if self.include_vat:
            return self.total_price * Decimal('0.20')
        return Decimal('0.00')
    
    @property
    def total_price_with_vat(self):
        """Calculate total price with VAT if include_vat is True"""
        return self.get_price_with_vat() * self.quantity


class ImportLog(models.Model):
    """Model to track import operations and their details"""
    
    PROVIDER_CHOICES = [
        ('starts94', 'Старс 94'),
        ('peugeot', 'Пежо'),
        ('nalichnosti', 'НАЛИЧНОСТИ'),
    ]
    
    provider = models.CharField(
        max_length=20,
        choices=PROVIDER_CHOICES,
        verbose_name="Доставчик"
    )
    
    invoice_date = models.DateField(
        verbose_name="Дата на фактурата",
        help_text="Дата от фактурата/документа"
    )
    
    invoice_number = models.CharField(
        max_length=100,
        verbose_name="Номер на фактурата",
        help_text="Уникален номер на фактурата/документа",
        blank=True,
        null=True
    )
    
    import_identifier = models.CharField(
        max_length=200,
        verbose_name="Идентификатор на импорта",
        help_text="Уникален идентификатор за предотвратяване на дублиране",
        unique=True,
        blank=True,
        null=True
    )
    
    import_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата на импорт"
    )
    
    file_name = models.CharField(
        max_length=255,
        verbose_name="Име на файла"
    )
    
    items_created = models.PositiveIntegerField(
        default=0,
        verbose_name="Създадени артикули"
    )
    
    items_updated = models.PositiveIntegerField(
        default=0,
        verbose_name="Обновени артикули"
    )
    
    errors_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Грешки"
    )
    
    skipped_count = models.PositiveIntegerField(
        default=0,
        verbose_name="Пропуснати редове"
    )
    
    total_processed = models.PositiveIntegerField(
        default=0,
        verbose_name="Общо обработени"
    )
    
    is_successful = models.BooleanField(
        default=True,
        verbose_name="Успешен импорт"
    )
    
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Съобщение за грешка"
    )
    
    affected_items = models.JSONField(
        blank=True,
        null=True,
        verbose_name="Засегнати артикули",
        help_text="JSON с детайли за създадените и обновените артикули"
    )
    
    class Meta:
        verbose_name = "Импорт лог"
        verbose_name_plural = "Импорт логове"
        ordering = ['-import_date']
    
    def __str__(self):
        return f"{self.get_provider_display()} - {self.invoice_date} ({self.import_date.strftime('%d.%m.%Y %H:%M')})"


class Invoice(models.Model):
    """Invoice model for storing invoice information"""
    
    INVOICE_STATUS_CHOICES = [
        ('sent', 'Изпратена'),
        ('paid', 'Платена'),
        ('overdue', 'Просрочена'),
        ('cancelled', 'Отказана'),
    ]
    
    # Basic invoice information
    invoice_number = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="Номер на фактура",
        help_text="Уникален номер на фактурата"
    )
    
    # Related order
    order = models.OneToOneField(
        'Order',
        on_delete=models.CASCADE,
        related_name='invoice',
        verbose_name="Свързана поръчка",
        help_text="Поръчката, от която е създадена фактурата"
    )
    
    # Invoice dates
    invoice_date = models.DateField(
        verbose_name="Дата на фактура",
        help_text="Дата на издаване на фактурата"
    )
    due_date = models.DateField(
        verbose_name="Краен срок за плащане",
        help_text="Дата до която трябва да бъде платена фактурата"
    )
    
    # Client information (copied from order for historical accuracy)
    client_name = models.CharField(
        max_length=255,
        verbose_name="Име на клиент",
        help_text="Име на клиента"
    )
    client_address = models.TextField(
        verbose_name="Адрес на клиент",
        help_text="Адрес на клиента",
        blank=True
    )
    client_phone = models.CharField(
        max_length=20,
        verbose_name="Телефон на клиент",
        help_text="Телефонен номер на клиента",
        blank=True
    )
    client_tax_number = models.CharField(
        max_length=50,
        verbose_name="ДДС номер на клиент",
        help_text="ДДС номер на клиента",
        blank=True
    )
    
    # Car information (copied from order for historical accuracy)
    car_brand_model = models.CharField(
        max_length=255,
        verbose_name="Марка и модел на кола",
        help_text="Марка и модел на автомобила",
        blank=True
    )
    car_plate_number = models.CharField(
        max_length=20,
        verbose_name="Регистрационен номер",
        help_text="Регистрационен номер на автомобила",
        blank=True
    )
    car_vin = models.CharField(
        max_length=17,
        verbose_name="VIN номер",
        help_text="VIN номер на автомобила",
        blank=True
    )
    
    # Financial information
    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Междинна сума",
        help_text="Сума преди ДДС"
    )
    vat_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="ДДС сума",
        help_text="Сума на ДДС"
    )
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Обща сума",
        help_text="Обща сума с ДДС"
    )
    
    # Status and metadata
    status = models.CharField(
        max_length=20,
        choices=INVOICE_STATUS_CHOICES,
        default='sent',
        verbose_name="Статус",
        help_text="Статус на фактурата"
    )
    
    notes = models.TextField(
        verbose_name="Бележки",
        help_text="Допълнителни бележки за фактурата",
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Създадена на",
        help_text="Дата и час на създаване"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Обновена на",
        help_text="Дата и час на последно обновяване"
    )
    
    class Meta:
        verbose_name = "Фактура"
        verbose_name_plural = "Фактури"
        ordering = ['-invoice_date', '-created_at']
    
    def __str__(self):
        return f"Фактура {self.invoice_number} - {self.client_name} ({self.total_amount} лв.)"
    
    @property
    def is_overdue(self):
        """Check if invoice is overdue"""
        if self.status == 'paid':
            return False
        return self.due_date < timezone.now().date()
    
    @property
    def days_until_due(self):
        """Calculate days until due date"""
        if self.status == 'paid':
            return 0
        delta = self.due_date - timezone.now().date()
        return delta.days
    
    def save(self, *args, **kwargs):
        # Auto-generate invoice number if not provided
        if not self.invoice_number:
            last_invoice = Invoice.objects.order_by('-id').first()
            if last_invoice and last_invoice.invoice_number.isdigit():
                self.invoice_number = str(int(last_invoice.invoice_number) + 1)
            else:
                self.invoice_number = '1'
        
        # Set due date if not provided (30 days from invoice date)
        if not self.due_date and self.invoice_date:
            from datetime import timedelta
            self.due_date = self.invoice_date + timedelta(days=30)
        
        super().save(*args, **kwargs)
