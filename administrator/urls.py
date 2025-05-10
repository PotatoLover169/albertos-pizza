from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard_view, name='dashboard'),
    
    # Categories URLs - Keep processing routes but redirect to settings page
    path('categories/add/', views.add_category_view, name='add_category'),
    path('categories/edit/<int:category_id>/', views.edit_category_view, name='edit_category'),
    path('categories/delete/<int:category_id>/', views.delete_category_view, name='delete_category'),
    
    # Menu Items URLs
    path('menu-items/', views.menu_items_view, name='menu_items'),
    path('menu-items/add/', views.add_menu_item_view, name='add_menu_item'),
    path('menu-items/edit/<int:item_id>/', views.edit_menu_item_view, name='edit_menu_item'),
    path('menu-items/delete/<int:item_id>/', views.delete_menu_item_view, name='delete_menu_item'),
    
    # Orders URLs
    path('orders/', views.orders_view, name='orders'),
    path('orders/<int:order_id>/', views.order_detail_view, name='order_detail'),
    path('orders/<int:order_id>/update-status/', views.update_order_status_view, name='update_order_status'),
    
    # Customers URLs
    path('customers/', views.customers_view, name='customers'),
    path('customers/<int:customer_id>/', views.customer_detail_view, name='customer_detail'),
    path('customers/add/', views.add_customer_view, name='add_customer'),
    path('customers/edit/<int:customer_id>/', views.edit_customer_view, name='edit_customer'),
    path('customers/delete/<int:customer_id>/', views.delete_customer_view, name='delete_customer'),
    
    # Reports URLs
    path('reports/', views.reports_view, name='reports'),
    
    # Settings URLs
    path('settings/', views.settings_view, name='settings'),
]
