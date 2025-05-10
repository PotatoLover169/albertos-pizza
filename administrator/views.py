from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum, Count, Avg, F, ExpressionWrapper, DecimalField
from django.utils import timezone
from datetime import datetime, timedelta
from .models import (
    Category, MenuItem, MenuItemVariant, MenuItemAddon,
    Customer, Order, OrderItem, OrderItemAddon,
    DailySales, SiteSettings
)
from .forms import (
    CategoryForm, MenuItemForm, MenuItemVariantForm, MenuItemAddonForm,
    CustomerForm, OrderForm, OrderItemForm,
    SiteSettingsForm
)
from django.urls import reverse

# Helper Functions
def staff_required(user):
    return user.is_staff or user.is_superuser

# Dashboard View
@login_required
@user_passes_test(staff_required)
def dashboard_view(request):
    # Get basic statistics
    total_menu_items = MenuItem.objects.filter(is_available=True).count()
    today_orders = Order.objects.filter(created_at__date=timezone.now().date()).count()
    total_customers = Customer.objects.count()
    
    # Calculate today's revenue
    today_revenue = Order.objects.filter(
        created_at__date=timezone.now().date()
    ).aggregate(revenue=Sum('total_price'))['revenue'] or 0
    
    # Get recent orders for dashboard
    recent_orders = Order.objects.order_by('-created_at')[:5]
    
    context = {
        'total_menu_items': total_menu_items,
        'today_orders': today_orders,
        'total_customers': total_customers,
        'today_revenue': today_revenue,
        'recent_orders': recent_orders,
    }
    
    return render(request, 'administrator/dashboard.html', context)

# Menu Items Views
@login_required
@user_passes_test(staff_required)
def menu_items_view(request):
    categories = Category.objects.filter(is_active=True)
    menu_items = MenuItem.objects.select_related('category').all()
    
    context = {
        'categories': categories,
        'menu_items': menu_items,
    }
    
    return render(request, 'administrator/menu_items.html', context)

@login_required
@user_passes_test(staff_required)
def add_menu_item_view(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Menu item added successfully.")
            return redirect('menu_items')
    else:
        form = MenuItemForm()
    
    context = {
        'form': form,
        'title': 'Add Menu Item',
    }
    
    return render(request, 'administrator/menu_item_form.html', context)

@login_required
@user_passes_test(staff_required)
def edit_menu_item_view(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            form.save()
            messages.success(request, "Menu item updated successfully.")
            return redirect('menu_items')
    else:
        form = MenuItemForm(instance=menu_item)
    
    variants = MenuItemVariant.objects.filter(menu_item=menu_item)
    
    context = {
        'form': form,
        'title': 'Edit Menu Item',
        'menu_item': menu_item,
        'variants': variants,
    }
    
    return render(request, 'administrator/menu_item_form.html', context)

@login_required
@user_passes_test(staff_required)
def delete_menu_item_view(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    
    if request.method == 'POST':
        menu_item.delete()
        messages.success(request, "Menu item deleted successfully.")
        return redirect('menu_items')
    
    context = {
        'menu_item': menu_item,
    }
    
    return render(request, 'administrator/confirm_delete.html', context)

# Orders Views
@login_required
@user_passes_test(staff_required)
def orders_view(request):
    orders = Order.objects.select_related('customer').order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    
    return render(request, 'administrator/orders.html', context)

@login_required
@user_passes_test(staff_required)
def order_detail_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    order_items = OrderItem.objects.filter(order=order).select_related('menu_item', 'variant')
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    
    return render(request, 'administrator/order_detail.html', context)

@login_required
@user_passes_test(staff_required)
def update_order_status_view(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Order.STATUS_CHOICES):
            order.status = new_status
            order.save()
            messages.success(request, f"Order status updated to {dict(Order.STATUS_CHOICES)[new_status]}.")
        else:
            messages.error(request, "Invalid status.")
            
        return redirect('order_detail', order_id=order_id)
        
    return redirect('orders')

# Customers Views
@login_required
@user_passes_test(staff_required)
def customers_view(request):
    customers = Customer.objects.all()
    
    context = {
        'customers': customers,
    }
    
    return render(request, 'administrator/customers.html', context)

@login_required
@user_passes_test(staff_required)
def customer_detail_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    customer_orders = Order.objects.filter(customer=customer).order_by('-created_at')
    
    # Calculate customer statistics
    total_spent = customer_orders.aggregate(total=Sum('total_price'))['total'] or 0
    avg_order = customer_orders.aggregate(avg=Avg('total_price'))['avg'] or 0
    
    # Get last order date
    last_order = None
    if customer_orders.exists():
        last_order = customer_orders.first().created_at.date()
    
    context = {
        'customer': customer,
        'customer_orders': customer_orders,
        'total_spent': total_spent,
        'avg_order': avg_order,
        'last_order': last_order,
    }
    
    return render(request, 'administrator/customer_detail.html', context)

@login_required
@user_passes_test(staff_required)
def add_customer_view(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer added successfully.")
            return redirect('customers')
    else:
        form = CustomerForm()
    
    context = {
        'form': form,
        'title': 'Add Customer',
    }
    
    return render(request, 'administrator/customer_form.html', context)

@login_required
@user_passes_test(staff_required)
def edit_customer_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            messages.success(request, "Customer updated successfully.")
            return redirect('customers')
    else:
        form = CustomerForm(instance=customer)
    
    context = {
        'form': form,
        'title': 'Edit Customer',
        'customer': customer,
    }
    
    return render(request, 'administrator/customer_form.html', context)

@login_required
@user_passes_test(staff_required)
def delete_customer_view(request, customer_id):
    customer = get_object_or_404(Customer, id=customer_id)
    
    if request.method == 'POST':
        customer.delete()
        messages.success(request, "Customer deleted successfully.")
        return redirect('customers')
    
    context = {
        'customer': customer,
    }
    
    return render(request, 'administrator/confirm_delete.html', context)

# Reports Views
@login_required
@user_passes_test(staff_required)
def reports_view(request):
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Filter by date range if provided
    if request.GET.get('start_date') and request.GET.get('end_date'):
        try:
            start_date = datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
            end_date = datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
        except ValueError:
            messages.error(request, "Invalid date format.")
    
    # Get daily sales data
    daily_sales = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('created_at__date').annotate(
        date=F('created_at__date'),
        total_sales=Sum('total_price'),
        total_orders=Count('id'),
        average_order_value=ExpressionWrapper(
            Sum('total_price') / Count('id'),
            output_field=DecimalField()
        )
    ).order_by('date')
    
    # Get aggregate metrics
    metrics = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).aggregate(
        total_sales=Sum('total_price') or 0,
        total_orders=Count('id'),
        avg_order_value=Avg('total_price') or 0,
    )
    
    total_sales = metrics['total_sales']
    total_orders = metrics['total_orders']
    avg_order_value = metrics['avg_order_value']
    
    # Calculate growth vs previous period
    period_length = (end_date - start_date).days
    prev_start_date = start_date - timedelta(days=period_length)
    prev_end_date = start_date - timedelta(days=1)
    
    prev_metrics = Order.objects.filter(
        created_at__date__gte=prev_start_date,
        created_at__date__lte=prev_end_date
    ).aggregate(
        prev_sales=Sum('total_price') or 0,
        prev_orders=Count('id'),
        prev_aov=Avg('total_price') or 0,
    )
    
    prev_period_sales = prev_metrics['prev_sales']
    prev_period_orders = prev_metrics['prev_orders']
    prev_period_aov = prev_metrics['prev_aov']
    
    # Calculate growth percentages
    sales_growth = 0
    if prev_period_sales and prev_period_sales > 0:
        sales_growth = ((total_sales - prev_period_sales) / prev_period_sales) * 100
        
    orders_growth = 0
    if prev_period_orders and prev_period_orders > 0:
        orders_growth = ((total_orders - prev_period_orders) / prev_period_orders) * 100
        
    aov_growth = 0
    if prev_period_aov and prev_period_aov > 0:
        aov_growth = ((avg_order_value - prev_period_aov) / prev_period_aov) * 100
    
    # Get top menu items
    top_items = OrderItem.objects.filter(
        order__created_at__date__gte=start_date,
        order__created_at__date__lte=end_date
    ).values('menu_item__name').annotate(
        total_orders=Count('id'),
        total_revenue=Sum(F('price') * F('quantity'))
    ).order_by('-total_revenue')[:5]
    
    # Get order status counts
    status_counts = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('status').annotate(count=Count('id'))
    
    status_labels = []
    status_data = []
    for status in status_counts:
        status_name = dict(Order.STATUS_CHOICES)[status['status']]
        status_labels.append(status_name)
        status_data.append(status['count'])
    
    # Get category revenue
    category_revenue = OrderItem.objects.filter(
        order__created_at__date__gte=start_date,
        order__created_at__date__lte=end_date
    ).values('menu_item__category__name').annotate(
        revenue=Sum(F('price') * F('quantity'))
    ).order_by('-revenue')
    
    category_labels = []
    category_data = []
    for category in category_revenue:
        if category['menu_item__category__name']:  # Check for None values
            category_labels.append(category['menu_item__category__name'])
            category_data.append(float(category['revenue']))
    
    # Prepare chart data
    date_labels = []
    sales_data = []
    
    # Create date range for all days in the period
    current_date = start_date
    while current_date <= end_date:
        date_labels.append(current_date.strftime('%b %d'))
        
        # Find sales for this date
        day_sale = next((item for item in daily_sales if item['date'] == current_date), None)
        if day_sale:
            sales_data.append(float(day_sale['total_sales']))
        else:
            sales_data.append(0)
        
        current_date += timedelta(days=1)
    
    context = {
        'start_date': start_date,
        'end_date': end_date,
        'daily_sales': daily_sales,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'avg_order_value': avg_order_value,
        'prev_period_sales': prev_period_sales,
        'prev_period_orders': prev_period_orders,
        'prev_period_aov': prev_period_aov,
        'sales_growth': sales_growth,
        'orders_growth': orders_growth,
        'aov_growth': aov_growth,
        'top_items': top_items,
        'date_labels': date_labels,
        'sales_data': sales_data,
        'status_labels': status_labels,
        'status_data': status_data,
        'category_labels': category_labels,
        'category_data': category_data,
    }
    
    return render(request, 'administrator/reports.html', context)

# Settings View
@login_required
@user_passes_test(staff_required)
def settings_view(request):
    # Get or create site settings
    settings, created = SiteSettings.objects.get_or_create(
        id=1,
        defaults={
            'site_name': "Alberto's Pizza",
            'contact_email': 'info@albertospizza.com',
            'contact_phone': '555-123-4567',
            'address': '123 Main Street, Pizza City',
            'opening_hours': 'Monday - Friday: 11am - 10pm\nSaturday - Sunday: 12pm - 11pm'
        }
    )
    
    if request.method == 'POST':
        form = SiteSettingsForm(request.POST, request.FILES, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, "Settings updated successfully.")
            return redirect('settings')
    else:
        form = SiteSettingsForm(instance=settings)
    
    # Get system information for the template
    import django
    from django.db import connections
    from django.contrib.auth.models import User
    
    db_info = connections['default'].vendor
    
    # Get all categories
    categories = Category.objects.all()
    
    # Count database objects
    user_count = User.objects.count()
    total_orders = Order.objects.count()
    total_menu_items = MenuItem.objects.count()
    total_customers = Customer.objects.count()
    
    context = {
        'form': form,
        'categories': categories,
        'django_version': django.get_version(),
        'database_info': db_info,
        'user_count': user_count,
        'total_orders': total_orders,
        'total_menu_items': total_menu_items,
        'total_customers': total_customers,
    }
    
    return render(request, 'administrator/settings.html', context)

# Home View (For landing page)
def home_view(request):
    # Get featured menu items for homepage
    featured_items = MenuItem.objects.filter(is_featured=True, is_available=True)[:3]
    
    # Get site settings
    site_settings, created = SiteSettings.objects.get_or_create(id=1)
    
    context = {
        'featured_items': featured_items,
        'site_settings': site_settings,
    }
    
    return render(request, 'login/home.html', context)

# Categories Views
@login_required
@user_passes_test(staff_required)
def categories_view(request):
    # This view is no longer used but kept for compatibility
    return redirect('settings')

@login_required
@user_passes_test(staff_required)
def add_category_view(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES)
        if form.is_valid():
            category = form.save()
            
            # Check if this is a quick add request (AJAX)
            if request.GET.get('quick') == 'true':
                return JsonResponse({
                    'success': True,
                    'category': {
                        'id': category.id,
                        'name': category.name
                    }
                })
            
            messages.success(request, "Category added successfully.")
            return redirect(f"{reverse('settings')}#categories")
        elif request.GET.get('quick') == 'true':
            return JsonResponse({
                'success': False,
                'error': "Invalid form data"
            })
    else:
        form = CategoryForm()
    
    context = {
        'form': form,
        'title': 'Add Category',
    }
    
    return render(request, 'administrator/category_form.html', context)

@login_required
@user_passes_test(staff_required)
def edit_category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, request.FILES, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated successfully.")
            return redirect(f"{reverse('settings')}#categories")
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'form': form,
        'title': 'Edit Category',
        'category': category,
    }
    
    return render(request, 'administrator/category_form.html', context)

@login_required
@user_passes_test(staff_required)
def delete_category_view(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    
    if request.method == 'POST':
        # Check if there are menu items associated with this category
        if MenuItem.objects.filter(category=category).exists():
            messages.error(request, "Cannot delete category because there are menu items associated with it.")
            return redirect(f"{reverse('settings')}#categories")
        
        category.delete()
        messages.success(request, "Category deleted successfully.")
        return redirect(f"{reverse('settings')}#categories")
    
    context = {
        'category': category,
        'is_category': True,  # To differentiate in the delete confirmation template
    }
    
    return render(request, 'administrator/confirm_delete.html', context)
