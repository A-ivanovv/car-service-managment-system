from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.template.loader import render_to_string
from datetime import datetime, timedelta
import json
from .models import Customer, Car, Employee, DaysOff, Event, Sklad
from .forms import CustomerForm, CustomerSearchForm, CarFormSet, EmployeeForm, EmployeeSearchForm, DaysOffForm, SkladForm, SkladSearchForm

def dashboard(request):
    """Main dashboard view with 6 clickable boxes and weekly planner"""
    return render(request, 'dashboard/dashboard.html')

def klienti(request):
    """Clients page with list, search, and CRUD operations"""
    search_form = CustomerSearchForm(request.GET)
    customers = Customer.objects.all()
    
    # Apply search filters
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        active_only = search_form.cleaned_data.get('active_only')
        customer_type = search_form.cleaned_data.get('customer_type')
        
        if search_query:
            customers = customers.filter(
                Q(customer_name__icontains=search_query) |
                Q(number__icontains=search_query) |
                Q(telno__icontains=search_query) |
                Q(customer_bulstat__icontains=search_query) |
                Q(customer_taxno__icontains=search_query) |
                Q(cars__brand_model__icontains=search_query) |
                Q(cars__vin__icontains=search_query) |
                Q(cars__plate_number__icontains=search_query)
            ).distinct()
        
        if active_only:
            customers = customers.filter(active=True)
        
        if customer_type == 'customer':
            customers = customers.filter(customer=True, supplier=False)
        elif customer_type == 'supplier':
            customers = customers.filter(supplier=True, customer=False)
        elif customer_type == 'both':
            customers = customers.filter(Q(customer=True) | Q(supplier=True))
    
    # Pagination
    paginator = Paginator(customers, 20)  # 20 customers per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'customers': page_obj,
        'search_form': search_form,
        'total_customers': customers.count(),
        'active_customers': customers.filter(active=True).count(),
    }
    return render(request, 'dashboard/klienti.html', context)

def customer_create(request):
    """Create new customer with cars"""
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        car_formset = CarFormSet(request.POST)
        
        if form.is_valid() and car_formset.is_valid():
            customer = form.save()
            car_formset.instance = customer
            car_formset.save()
            messages.success(request, f'Клиент {customer.customer_name} е създаден успешно!')
            return redirect('klienti')
    else:
        form = CustomerForm()
        car_formset = CarFormSet()
    
    return render(request, 'dashboard/customer_form.html', {
        'form': form,
        'car_formset': car_formset,
        'title': 'Нов клиент',
        'action': 'Създай'
    })

def customer_edit(request, pk):
    """Edit existing customer with cars"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        car_formset = CarFormSet(request.POST, instance=customer)
        
        if form.is_valid() and car_formset.is_valid():
            form.save()
            car_formset.save()
            messages.success(request, f'Клиент {customer.customer_name} е обновен успешно!')
            return redirect('klienti')
    else:
        form = CustomerForm(instance=customer)
        car_formset = CarFormSet(instance=customer)
    
    return render(request, 'dashboard/customer_form.html', {
        'form': form,
        'car_formset': car_formset,
        'customer': customer,
        'title': f'Редактиране на {customer.customer_name}',
        'action': 'Запази'
    })

def customer_delete(request, pk):
    """Delete customer"""
    customer = get_object_or_404(Customer, pk=pk)
    
    if request.method == 'POST':
        customer_name = customer.customer_name
        customer.delete()
        messages.success(request, f'Клиент {customer_name} е изтрит успешно!')
        return redirect('klienti')
    
    return render(request, 'dashboard/customer_confirm_delete.html', {
        'customer': customer
    })

def customer_detail(request, pk):
    """View customer details with cars"""
    customer = get_object_or_404(Customer, pk=pk)
    cars = customer.cars.filter(is_active=True)
    return render(request, 'dashboard/customer_detail.html', {
        'customer': customer,
        'cars': cars
    })

def fakturi(request):
    """Invoices page"""
    return render(request, 'dashboard/fakturi.html')

def poruchki(request):
    """Orders page"""
    return render(request, 'dashboard/poruchki.html')

def pregled_poruchki(request):
    """Order review page"""
    return render(request, 'dashboard/pregled_poruchki.html')

def slujiteli(request):
    """Employees page"""
    return render(request, 'dashboard/slujiteli.html')

def sklad(request):
    """Warehouse page"""
    return render(request, 'dashboard/sklad.html')

def get_weekly_planner(request):
    """API endpoint for weekly planner data"""
    from django.db.models import Q
    
    # Get the week from request parameters
    week_offset = int(request.GET.get('week', 0))
    
    # Calculate the start of the week (Monday)
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday()) + timedelta(weeks=week_offset)
    end_of_week = start_of_week + timedelta(days=6)
    
    # Bulgarian day names
    bulgarian_days = ['ПОН', 'ВТО', 'СРЯ', 'ЧЕТ', 'ПЕТ', 'СЪБ', 'НЕД']
    
    # Generate week days
    week_days = []
    for i in range(7):
        day = start_of_week + timedelta(days=i)
        week_days.append({
            'date': day.strftime('%Y-%m-%d'),
            'day_name': bulgarian_days[i],
            'day_number': day.day,
            'is_today': day.date() == today.date()
        })
    
    # Get employee days off for this week
    days_off = DaysOff.objects.filter(
        Q(start_date__lte=end_of_week.date()) & Q(end_date__gte=start_of_week.date()),
        is_approved=True
    ).select_related('employee')
    
    # Get events for this week
    from .models import Event
    events = Event.objects.filter(
        Q(start_datetime__date__lte=end_of_week.date()) & Q(end_datetime__date__gte=start_of_week.date())
    ).select_related('customer', 'employee')
    
    # Organize days off by date
    days_off_by_date = {}
    for day_off in days_off:
        current_date = day_off.start_date
        while current_date <= day_off.end_date:
            if start_of_week.date() <= current_date <= end_of_week.date():
                date_str = current_date.strftime('%Y-%m-%d')
                if date_str not in days_off_by_date:
                    days_off_by_date[date_str] = []
                
                days_off_by_date[date_str].append({
                    'id': day_off.id,
                    'employee_name': day_off.employee.full_name,
                    'type': day_off.get_day_off_type_display(),
                    'reason': day_off.reason or '',
                    'color': get_day_off_color(day_off.day_off_type),
                    'is_all_day': True
                })
            current_date += timedelta(days=1)
    
    # Organize events by date and time
    import pytz
    sofia_tz = pytz.timezone('Europe/Sofia')
    
    events_by_date = {}
    for event in events:
        # Convert to Sofia timezone for display
        start_local = event.start_datetime.astimezone(sofia_tz)
        end_local = event.end_datetime.astimezone(sofia_tz)
        event_date = start_local.date()
        
        if start_of_week.date() <= event_date <= end_of_week.date():
            date_str = event_date.strftime('%Y-%m-%d')
            if date_str not in events_by_date:
                events_by_date[date_str] = []
            
            events_by_date[date_str].append({
                'id': event.id,
                'title': event.title,
                'event_type': event.event_type,
                'type': event.get_event_type_display(),
                'start_date': event_date.strftime('%Y-%m-%d'),
                'start_time': start_local.strftime('%H:%M'),
                'end_time': end_local.strftime('%H:%M'),
                'is_all_day': event.is_all_day,
                'color': get_event_color(event.event_type),
                'customer': event.customer.customer_name if event.customer else None,
                'employee': event.employee.full_name if event.employee else None,
                'description': event.description or ''
            })
    
    return JsonResponse({
        'week_days': week_days,
        'current_week': week_offset == 0,
        'days_off': days_off_by_date,
        'events': events_by_date
    })


def get_day_off_color(day_off_type):
    """Get color for day off type"""
    colors = {
        'vacation': '#28a745',      # Green for vacation
        'sick': '#dc3545',          # Red for sick leave
        'personal': '#ffc107',      # Yellow for personal
        'holiday': '#6f42c1',      # Purple for holiday
        'other': '#17a2b8'          # Blue for other
    }
    return colors.get(day_off_type, '#6c757d')  # Default gray


def get_event_color(event_type):
    """Get color for event type"""
    colors = {
        'meeting': '#007bff',       # Blue for meetings
        'appointment': '#28a745',   # Green for appointments
        'maintenance': '#ffc107',   # Yellow for maintenance
        'inspection': '#fd7e14',    # Orange for inspections
        'delivery': '#6f42c1',      # Purple for deliveries
        'other': '#6c757d'          # Gray for other
    }
    return colors.get(event_type, '#6c757d')  # Default gray


@csrf_exempt
def create_event(request):
    """Create a new calendar event"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Parse datetime with timezone
            from datetime import datetime
            import pytz
            
            # Use Sofia timezone
            tz = pytz.timezone('Europe/Sofia')
            
            start_datetime = tz.localize(datetime.strptime(
                f"{data['start_date']} {data['start_time']}", 
                '%Y-%m-%d %H:%M'
            ))
            end_datetime = tz.localize(datetime.strptime(
                f"{data['start_date']} {data['end_time']}", 
                '%Y-%m-%d %H:%M'
            ))
            
            # Check for duplicate events (same title, date, and time)
            existing_event = Event.objects.filter(
                title=data['title'],
                start_datetime=start_datetime,
                end_datetime=end_datetime
            ).first()
            
            if existing_event:
                return JsonResponse({
                    'success': False,
                    'error': 'Събитие с това заглавие и време вече съществува!'
                })
            
            # Create event
            event = Event.objects.create(
                title=data['title'],
                event_type=data['event_type'],
                start_datetime=start_datetime,
                end_datetime=end_datetime,
                description=data.get('description', ''),
                is_all_day=data.get('is_all_day', False)
            )
            
            return JsonResponse({
                'success': True,
                'event_id': event.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


@csrf_exempt
def update_event(request):
    """Update an existing calendar event"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_id = data.get('id')
            
            if not event_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Event ID is required'
                })
            
            try:
                event = Event.objects.get(id=event_id)
            except Event.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Event not found'
                })
            
            # Parse datetime with timezone
            from datetime import datetime
            import pytz
            
            # Use Sofia timezone
            tz = pytz.timezone('Europe/Sofia')
            
            start_datetime = tz.localize(datetime.strptime(
                f"{data['start_date']} {data['start_time']}", 
                '%Y-%m-%d %H:%M'
            ))
            end_datetime = tz.localize(datetime.strptime(
                f"{data['start_date']} {data['end_time']}", 
                '%Y-%m-%d %H:%M'
            ))
            
            # Update event
            event.title = data['title']
            event.event_type = data['event_type']
            event.start_datetime = start_datetime
            event.end_datetime = end_datetime
            event.description = data.get('description', '')
            event.is_all_day = data.get('is_all_day', False)
            
            # Handle customer - try to find by name or set to None
            customer_name = data.get('customer', '')
            if customer_name:
                try:
                    customer = Customer.objects.get(customer_name=customer_name)
                    event.customer = customer
                except Customer.DoesNotExist:
                    # If customer doesn't exist, we'll leave it as None
                    # In a real app, you might want to create the customer
                    event.customer = None
            else:
                event.customer = None
                
            event.save()
            
            return JsonResponse({
                'success': True,
                'event_id': event.id
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


@csrf_exempt
def delete_event(request):
    """Delete a calendar event"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            event_id = data.get('id')
            
            if not event_id:
                return JsonResponse({
                    'success': False,
                    'error': 'Event ID is required'
                })
            
            try:
                event = Event.objects.get(id=event_id)
                event.delete()
                
                return JsonResponse({
                    'success': True,
                    'message': 'Event deleted successfully'
                })
                
            except Event.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Event not found'
                })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})


# Employee Views
def slujiteli(request):
    """Employee list with search and pagination"""
    employees = Employee.objects.all()
    search_form = EmployeeSearchForm(request.GET)
    
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        active_only = search_form.cleaned_data.get('active_only')
        
        if search_query:
            employees = employees.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query)
            )
        
        if active_only:
            employees = employees.filter(is_active=True)
    
    # Pagination
    paginator = Paginator(employees, 20)  # 20 employees per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'employees': page_obj,
        'search_form': search_form,
        'total_employees': employees.count(),
        'active_employees': employees.filter(is_active=True).count(),
    }
    return render(request, 'dashboard/slujiteli.html', context)


def employee_create(request):
    """Create new employee"""
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            employee = form.save()
            messages.success(request, f'Служител {employee.full_name} е създаден успешно!')
            return redirect('slujiteli')
    else:
        form = EmployeeForm()
    
    return render(request, 'dashboard/employee_form.html', {
        'form': form,
        'title': 'Нов служител',
        'action': 'Създай'
    })


def employee_edit(request, pk):
    """Edit existing employee"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, f'Служител {employee.full_name} е обновен успешно!')
            return redirect('slujiteli')
    else:
        form = EmployeeForm(instance=employee)
    
    return render(request, 'dashboard/employee_form.html', {
        'form': form,
        'employee': employee,
        'title': f'Редактиране на {employee.full_name}',
        'action': 'Запази'
    })


def employee_delete(request, pk):
    """Delete employee"""
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        employee_name = employee.full_name
        employee.delete()
        messages.success(request, f'Служител {employee_name} е изтрит успешно!')
        return redirect('slujiteli')
    
    return render(request, 'dashboard/employee_confirm_delete.html', {
        'employee': employee
    })


def employee_detail(request, pk):
    """View employee details with days off"""
    from datetime import date
    
    employee = get_object_or_404(Employee, pk=pk)
    days_off = employee.days_off.all().order_by('-start_date')
    current_year = date.today().year
    
    return render(request, 'dashboard/employee_detail.html', {
        'employee': employee,
        'days_off': days_off,
        'current_year': current_year
    })


def days_off_create(request):
    """Create new days off request"""
    if request.method == 'POST':
        form = DaysOffForm(request.POST)
        if form.is_valid():
            days_off = form.save()
            messages.success(request, f'Заявка за отпуск е създадена успешно!')
            return redirect('employee_detail', pk=days_off.employee.pk)
    else:
        form = DaysOffForm()
    
    return render(request, 'dashboard/days_off_form.html', {
        'form': form,
        'title': 'Нова заявка за отпуск',
        'action': 'Създай'
    })


def days_off_edit(request, pk):
    """Edit days off request"""
    days_off = get_object_or_404(DaysOff, pk=pk)
    
    if request.method == 'POST':
        form = DaysOffForm(request.POST, instance=days_off)
        if form.is_valid():
            form.save()
            messages.success(request, f'Заявка за отпуск е обновена успешно!')
            return redirect('employee_detail', pk=days_off.employee.pk)
    else:
        form = DaysOffForm(instance=days_off)
    
    return render(request, 'dashboard/days_off_form.html', {
        'form': form,
        'days_off': days_off,
        'title': f'Редактиране на заявка за отпуск',
        'action': 'Запази'
    })


def days_off_delete(request, pk):
    """Delete days off request"""
    days_off = get_object_or_404(DaysOff, pk=pk)
    employee_pk = days_off.employee.pk
    
    if request.method == 'POST':
        days_off.delete()
        messages.success(request, f'Заявка за отпуск е изтрита успешно!')
        return redirect('employee_detail', pk=employee_pk)
    
    return render(request, 'dashboard/days_off_confirm_delete.html', {
        'days_off': days_off
    })


@csrf_exempt
def cleanup_duplicate_events(request):
    """Clean up duplicate events from the database"""
    if request.method == 'POST':
        try:
            # Find duplicate events (same title, start_datetime, end_datetime)
            from django.db.models import Count
            
            duplicates = Event.objects.values('title', 'start_datetime', 'end_datetime').annotate(
                count=Count('id')
            ).filter(count__gt=1)
            
            removed_count = 0
            
            for duplicate in duplicates:
                # Get all events with this combination
                events = Event.objects.filter(
                    title=duplicate['title'],
                    start_datetime=duplicate['start_datetime'],
                    end_datetime=duplicate['end_datetime']
                ).order_by('id')
                
                # Keep the first one, delete the rest
                events_to_delete = events[1:]
                for event in events_to_delete:
                    event.delete()
                    removed_count += 1
            
            return JsonResponse({
                'success': True,
                'removed_count': removed_count,
                'message': f'Премахнати са {removed_count} дублирани събития.'
            })
            
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid method'})
def sklad(request):
    """Warehouse/Inventory page with list, search, and CRUD operations"""
    search_form = SkladSearchForm(request.GET)
    items = Sklad.objects.all()
    
    # Apply search filters
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        active_only = search_form.cleaned_data.get('active_only')
        unit_filter = search_form.cleaned_data.get('unit_filter')
        
        if search_query:
            items = items.filter(
                Q(article_number__icontains=search_query) |
                Q(name__icontains=search_query)
            ).distinct()
        
        if active_only:
            items = items.filter(is_active=True)
        
        if unit_filter:
            items = items.filter(unit=unit_filter)
    
    # Pagination
    paginator = Paginator(items, 20)  # 20 items per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Calculate total value
    total_value = sum(item.total_value for item in items if item.is_active)
    
    # Check if this is an AJAX request
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.GET.get('ajax'):
        # Return JSON response for AJAX requests
        table_html = render_to_string('dashboard/sklad_table.html', {
            'page_obj': page_obj,
        })
        
        pagination_html = render_to_string('dashboard/sklad_pagination.html', {
            'page_obj': page_obj,
            'request': request,
        })
        
        return JsonResponse({
            'table_html': table_html,
            'pagination_html': pagination_html,
            'stats': {
                'total_items': items.count(),
                'active_items': items.filter(is_active=True).count(),
                'total_value': float(total_value),
                'total_pages': paginator.num_pages,
            }
        })
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_value': total_value,
        'total_items': items.count(),
        'active_items': items.filter(is_active=True).count(),
    }
    
    return render(request, 'dashboard/sklad.html', context)


def sklad_create(request):
    """Create new warehouse item"""
    if request.method == 'POST':
        form = SkladForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Артикулът е създаден успешно!')
            return redirect('sklad')
    else:
        form = SkladForm()
    
    return render(request, 'dashboard/sklad_form.html', {
        'form': form,
        'title': 'Създаване на нов артикул',
        'action': 'Създай'
    })


def sklad_detail(request, pk):
    """View warehouse item details"""
    item = get_object_or_404(Sklad, pk=pk)
    return render(request, 'dashboard/sklad_detail.html', {
        'item': item
    })


def sklad_edit(request, pk):
    """Edit warehouse item"""
    item = get_object_or_404(Sklad, pk=pk)
    
    if request.method == 'POST':
        form = SkladForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            messages.success(request, 'Артикулът е обновен успешно!')
            return redirect('sklad_detail', pk=item.pk)
    else:
        form = SkladForm(instance=item)
    
    return render(request, 'dashboard/sklad_form.html', {
        'form': form,
        'item': item,
        'title': 'Редактиране на артикул',
        'action': 'Запази'
    })


def sklad_delete(request, pk):
    """Delete warehouse item"""
    item = get_object_or_404(Sklad, pk=pk)
    
    if request.method == 'POST':
        item.delete()
        messages.success(request, 'Артикулът е изтрит успешно!')
        return redirect('sklad')
    
    return render(request, 'dashboard/sklad_confirm_delete.html', {
        'item': item
    })


def sklad_autocomplete(request):
    """API endpoint for autocomplete suggestions"""
    query = request.GET.get('q', '').strip()
    field = request.GET.get('field', 'article_number')  # 'article_number' or 'name'
    
    if not query or len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    # Validate field parameter
    if field not in ['article_number', 'name']:
        field = 'article_number'
    
    # Search for matching items
    items = Sklad.objects.filter(
        **{f'{field}__icontains': query}
    ).values('id', 'article_number', 'name', 'unit', 'quantity', 'purchase_price')[:10]
    
    suggestions = []
    for item in items:
        suggestions.append({
            'id': item['id'],
            'article_number': item['article_number'],
            'name': item['name'],
            'unit': item['unit'],
            'quantity': float(item['quantity']),
            'purchase_price': float(item['purchase_price']),
            'display_text': f"{item['article_number']} - {item['name']}"
        })
    
    return JsonResponse({'suggestions': suggestions})
