from django import forms
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from .models import Customer, Car, Employee, DaysOff, Sklad, Order, OrderItem

class CustomerForm(forms.ModelForm):
    """Form for creating and editing customers"""
    
    class Meta:
        model = Customer
        fields = [
            'number', 'customer_name', 'customer_address_1', 'customer_address_2',
            'customer_mol', 'customer_taxno', 'customer_doctype', 'receiver',
            'receiver_details', 'customer_bulstat', 'telno', 'faxno', 'email',
            'res_address_1', 'res_address_2', 'eidate', 'include', 'active',
            'customer', 'supplier', 'contact', 'partida', 'bulstatletter'
        ]
    
        widgets = {
            'number': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Автоматично генериран',
                'readonly': True
            }),
            'customer_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Въведете име на клиента'
            }),
            'customer_address_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Основен адрес'
            }),
            'customer_address_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Допълнителен адрес'
            }),
            'customer_mol': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'МОЛ (Молимо отговорно лице)'
            }),
            'customer_taxno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ДДС номер'
            }),
            'customer_doctype': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'receiver': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Име на получател'
            }),
            'receiver_details': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Детайли за получателя'
            }),
            'customer_bulstat': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'БУЛСТАТ номер (9-11 цифри)',
                'pattern': r'\d{9,11}'
            }),
            'telno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Телефонен номер'
            }),
            'faxno': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Факс номер'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'имейл@example.com'
            }),
            'res_address_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Адрес за живеене 1'
            }),
            'res_address_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Адрес за живеене 2'
            }),
            'eidate': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Контактно лице'
            }),
            'partida': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0'
            }),
            'bulstatletter': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'БУЛСТАТ буква',
                'maxlength': '10'
            }),
            'include': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'customer': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'supplier': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        self.fields['customer_name'].required = True
        self.fields['customer_name'].widget.attrs['required'] = True
        
        # Auto-generate customer number for new customers
        if not self.instance.pk:  # Only for new customers
            last_customer = Customer.objects.order_by('-number').first()
            if last_customer:
                next_number = last_customer.number + 1
            else:
                next_number = 1
            self.fields['number'].initial = next_number
    
        # Set field labels
        self.fields['number'].label = 'Номер'
        self.fields['customer_name'].label = 'Име на клиент'
        self.fields['customer_address_1'].label = 'Адрес 1'
        self.fields['customer_address_2'].label = 'Адрес 2'
        self.fields['customer_mol'].label = 'МОЛ'
        self.fields['customer_taxno'].label = 'ДДС номер'
        self.fields['customer_doctype'].label = 'Тип документ'
        self.fields['receiver'].label = 'Получател'
        self.fields['receiver_details'].label = 'Детайли за получател'
        self.fields['customer_bulstat'].label = 'БУЛСТАТ'
        self.fields['telno'].label = 'Телефон'
        self.fields['faxno'].label = 'Факс'
        self.fields['email'].label = 'Имейл'
        self.fields['res_address_1'].label = 'Адрес за живеене 1'
        self.fields['res_address_2'].label = 'Адрес за живеене 2'
        self.fields['eidate'].label = 'Дата на влизане'
        self.fields['include'].label = 'Включен'
        self.fields['active'].label = 'Активен'
        self.fields['customer'].label = 'Клиент'
        self.fields['supplier'].label = 'Доставчик'
        self.fields['contact'].label = 'Контакт'
        self.fields['partida'].label = 'Партида'
        self.fields['bulstatletter'].label = 'БУЛСТАТ буква'
    
    def clean_customer_bulstat(self):
        """Validate BULSTAT format"""
        bulstat = self.cleaned_data.get('customer_bulstat')
        if bulstat and not bulstat.isdigit():
            raise ValidationError('БУЛСТАТ трябва да съдържа само цифри')
        if bulstat and len(bulstat) not in [9, 10, 11]:
            raise ValidationError('БУЛСТАТ трябва да бъде 9, 10 или 11 цифри')
        return bulstat
    
    def clean_number(self):
        """Validate unique number"""
        number = self.cleaned_data.get('number')
        if number:
            # Check if number already exists (excluding current instance if editing)
            existing = Customer.objects.filter(number=number)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError('Клиент с този номер вече съществува')
        return number

class CustomerSearchForm(forms.Form):
    """Form for searching customers"""
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Търсене по име, номер, телефон, БУЛСТАТ...',
            'id': 'customer-search'
        }),
        label='Търсене'
    )
    
    active_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Само активни клиенти'
    )
    
    customer_type = forms.ChoiceField(
        choices=[
            ('', 'Всички'),
            ('customer', 'Клиенти'),
            ('supplier', 'Доставчици'),
            ('both', 'Клиенти и доставчици'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Тип'
    )


class CarForm(forms.ModelForm):
    """Form for creating and editing cars"""
    
    class Meta:
        model = Car
        fields = ['brand_model', 'vin', 'plate_number', 'year', 'color', 'engine_number', 'is_active']
        widgets = {
            'brand_model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: FIAT DUCATO (250) 120 Multijet 2,3 D'
            }),
            'vin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VIN/Шаси номер'
            }),
            'plate_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: CA1234AB'
            }),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1900',
                'max': '2030'
            }),
            'color': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: Бял, Черен, Син'
            }),
            'engine_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Номер на двигател'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        self.fields['brand_model'].required = True
        self.fields['brand_model'].widget.attrs['required'] = True


# Inline formset for cars
CarFormSet = inlineformset_factory(
    Customer, 
    Car, 
    form=CarForm,
    extra=1,  # Show 1 empty form by default
    can_delete=True,  # Allow deleting cars
    min_num=0,  # Minimum 0 cars
    validate_min=False,  # Don't validate minimum on form submission
)


class EmployeeForm(forms.ModelForm):
    """Form for creating and editing employees"""
    
    class Meta:
        model = Employee
        fields = [
            'first_name', 'last_name', 'hourly_rate',
            'hire_date', 'annual_leave_days', 'is_active', 'notes'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Име'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Фамилия'
            }),
            'hourly_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0'
            }),
            'hire_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'annual_leave_days': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'max': '50'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Допълнителни бележки за служителя'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        self.fields['first_name'].required = True
        self.fields['first_name'].widget.attrs['required'] = True
        self.fields['last_name'].required = True
        self.fields['last_name'].widget.attrs['required'] = True


class EmployeeSearchForm(forms.Form):
    """Form for searching employees"""
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Търси по име, фамилия...'
        }),
        label='Търсене'
    )
    
    active_only = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Само активни'
    )


class DaysOffForm(forms.ModelForm):
    """Form for creating and editing days off"""
    
    class Meta:
        model = DaysOff
        fields = ['employee', 'start_date', 'end_date', 'day_off_type', 'reason', 'notes', 'is_approved']
        widgets = {
            'employee': forms.Select(attrs={
                'class': 'form-select'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'day_off_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'reason': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Причина за отпуска'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Допълнителни бележки'
            }),
            'is_approved': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        self.fields['employee'].required = True
        self.fields['employee'].widget.attrs['required'] = True
        self.fields['start_date'].required = True
        self.fields['start_date'].widget.attrs['required'] = True
        self.fields['end_date'].required = True
        self.fields['end_date'].widget.attrs['required'] = True
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError('Началната дата не може да бъде след крайната дата.')
        
        return cleaned_data


class SkladForm(forms.ModelForm):
    """Form for creating and editing warehouse items"""
    
    class Meta:
        model = Sklad
        fields = ['article_number', 'name', 'unit', 'quantity', 'purchase_price', 'is_active']
        widgets = {
            'article_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: 0003001001',
                'style': 'text-transform: uppercase;'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Наименование на продукта'
            }),
            'unit': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'бр, кг, л, м, и т.н.'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }
        labels = {
            'article_number': 'Артикул N',
            'name': 'Наименование',
            'unit': 'Мр.',
            'quantity': 'Наличност',
            'purchase_price': 'Дост. цена',
            'is_active': 'Активен',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        self.fields['article_number'].required = True
        self.fields['article_number'].widget.attrs['required'] = True
        self.fields['name'].required = True
        self.fields['name'].widget.attrs['required'] = True
        self.fields['unit'].required = True
        self.fields['unit'].widget.attrs['required'] = True
        self.fields['quantity'].required = True
        self.fields['quantity'].widget.attrs['required'] = True
        self.fields['purchase_price'].required = True
        self.fields['purchase_price'].widget.attrs['required'] = True
    
    def clean_article_number(self):
        """Validate and format article number"""
        article_number = self.cleaned_data.get('article_number')
        if article_number:
            article_number = article_number.upper().strip()
            # Check if article number already exists (excluding current instance if editing)
            existing = Sklad.objects.filter(article_number=article_number)
            if self.instance.pk:
                existing = existing.exclude(pk=self.instance.pk)
            if existing.exists():
                raise ValidationError('Артикул с този номер вече съществува')
        return article_number
    
    def clean_quantity(self):
        """Validate quantity"""
        quantity = self.cleaned_data.get('quantity')
        if quantity is not None and quantity < 0:
            raise ValidationError('Количеството не може да бъде отрицателно')
        return quantity
    
    def clean_purchase_price(self):
        """Validate purchase price"""
        price = self.cleaned_data.get('purchase_price')
        if price is not None and price < 0:
            raise ValidationError('Цената не може да бъде отрицателна')
        return price


class SkladSearchForm(forms.Form):
    """Form for searching warehouse items"""
    
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Търсене по артикул, наименование...',
            'id': 'sklad-search'
        }),
        label='Търсене'
    )
    
    active_only = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Само активни артикули'
    )
    
    unit_filter = forms.ChoiceField(
        choices=[],  # Will be populated dynamically
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Мерна единица'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Populate unit choices from database
        from .models import Sklad
        units = Sklad.objects.values_list('unit', flat=True).distinct().order_by('unit')
        unit_choices = [('', 'Всички мерни единици')] + [(unit, unit) for unit in units if unit]
        self.fields['unit_filter'].choices = unit_choices


class OrderForm(forms.ModelForm):
    """Form for creating and editing orders"""
    
    class Meta:
        model = Order
        fields = [
            'car', 'car_brand_model', 'car_vin', 
            'car_plate_number', 'car_mileage', 'client', 'client_name', 
            'client_address', 'client_phone', 'employees', 'notes'
        ]
        widgets = {
            'car': forms.Select(attrs={
                'class': 'form-select',
                'id': 'car-select'
            }),
            'car_brand_model': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: C4 Picasso',
                'id': 'car-brand-model'
            }),
            'car_vin': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'VIN/Шаси номер',
                'id': 'car-vin'
            }),
            'car_plate_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Например: СВ5602TK',
                'id': 'car-plate-number'
            }),
            'car_mileage': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Изминати км',
                'min': '0',
                'id': 'car-mileage'
            }),
            'client': forms.Select(attrs={
                'class': 'form-select',
                'id': 'client-select'
            }),
            'client_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Име на клиента',
                'id': 'client-name'
            }),
            'client_address': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Адрес на клиента',
                'id': 'client-address'
            }),
            'client_phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Телефон на клиента',
                'id': 'client-phone'
            }),
            'employees': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'id': 'employees-select'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Допълнителни бележки за поръчката',
                'id': 'order-notes'
            }),
        }
        labels = {
            'car': 'Кола от базата данни',
            'car_brand_model': 'Марка и модел',
            'car_vin': 'VIN/Шаси номер',
            'car_plate_number': 'Регистрационен номер',
            'car_mileage': 'Изминати км',
            'client': 'Клиент от базата данни',
            'client_name': 'Име на клиента',
            'client_address': 'Адрес на клиента',
            'client_phone': 'Телефон на клиента',
            'employees': 'Служители',
            'notes': 'Бележки',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add autocomplete attributes for JavaScript
        self.fields['car_vin'].widget.attrs.update({
            'data-autocomplete-url': '/poruchki/autocomplete/car-vin/',
            'autocomplete': 'off'
        })
        self.fields['car_plate_number'].widget.attrs.update({
            'data-autocomplete-url': '/poruchki/autocomplete/car-plate/',
            'autocomplete': 'off'
        })
        self.fields['client_name'].widget.attrs.update({
            'data-autocomplete-url': '/poruchki/autocomplete/client/',
            'autocomplete': 'off'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        car = cleaned_data.get('car')
        car_brand_model = cleaned_data.get('car_brand_model')
        car_vin = cleaned_data.get('car_vin')
        car_plate_number = cleaned_data.get('car_plate_number')
        
        client = cleaned_data.get('client')
        client_name = cleaned_data.get('client_name')
        
        # Validate that either car is selected or car info is provided
        if not car and not car_brand_model:
            raise ValidationError('Моля изберете кола от базата данни или въведете марка и модел.')
        
        # Validate that either client is selected or client info is provided
        if not client and not client_name:
            raise ValidationError('Моля изберете клиент от базата данни или въведете име на клиента.')
        
        return cleaned_data


class OrderItemForm(forms.ModelForm):
    """Form for creating and editing order items"""
    
    class Meta:
        model = OrderItem
        fields = ['sklad_item', 'article_number', 'name', 'unit', 'purchase_price', 'quantity', 'include_vat']
        widgets = {
            'sklad_item': forms.Select(attrs={
                'class': 'form-select',
                'id': 'sklad-item-select'
            }),
            'article_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Артикул номер',
                'id': 'article-number'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Наименование',
                'id': 'item-name'
            }),
            'unit': forms.Select(attrs={
                'class': 'form-select',
                'id': 'item-unit'
            }),
            'purchase_price': forms.NumberInput(attrs={
                'class': 'form-control price-input',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'id': 'purchase-price'
            }),
            'quantity': forms.NumberInput(attrs={
                'class': 'form-control quantity-input',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00',
                'id': 'quantity'
            }),
            'include_vat': forms.CheckboxInput(attrs={
                'class': 'form-check-input include-vat-checkbox',
                'id': 'include-vat'
            }),
        }
        labels = {
            'sklad_item': 'Артикул от склад',
            'article_number': 'Артикул номер',
            'name': 'Наименование',
            'unit': 'Мерна единица',
            'purchase_price': 'Единична цена без ДДС',
            'quantity': 'Количество',
            'include_vat': 'Включи ДДС',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Mark required fields
        self.fields['name'].required = True
        self.fields['unit'].required = True
        self.fields['purchase_price'].required = True
        self.fields['quantity'].required = True
        
        # Populate unit choices from database
        from .models import Sklad
        units = Sklad.objects.values_list('unit', flat=True).distinct().order_by('unit')
        unit_choices = [('', 'Избери мерна единица')] + [(unit, unit) for unit in units if unit]
        self.fields['unit'].choices = unit_choices
    
    def clean(self):
        cleaned_data = super().clean()
        sklad_item = cleaned_data.get('sklad_item')
        article_number = cleaned_data.get('article_number')
        name = cleaned_data.get('name')
        
        # Validate that either sklad_item is selected or standalone info is provided
        if not sklad_item and not (article_number and name):
            raise ValidationError('Моля изберете артикул от склад или въведете артикул номер и наименование.')
        
        return cleaned_data


class OrderSearchForm(forms.Form):
    """Form for searching orders"""
    
    search = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Търсене по номер, клиент, кола, VIN...',
            'id': 'order-search'
        }),
        label='Търсене'
    )
    
    status_filter = forms.ChoiceField(
        choices=[('', 'Всички статуси')] + Order.ORDER_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        label='Статус'
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='От дата'
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='До дата'
    )


# Inline formset for order items
OrderItemFormSet = inlineformset_factory(
    Order,
    OrderItem,
    form=OrderItemForm,
    extra=1,  # Show 1 empty form by default
    can_delete=True,  # Allow deleting items
    min_num=0,  # Minimum 0 items
    validate_min=False,  # Don't validate minimum on form submission
)
