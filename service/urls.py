from django.urls import path
from . import views
from django.conf.urls import  handler404



urlpatterns = [
    path("",views.index,name="index"),
    path("signup",views.signup_user, name="signup"),
    path("login",views.login_user,name="login"),
    path("logout",views.logout_user,name="logout"),
    path("order",views.order,name="order"),
    path("guest_order",views.guest_order,name="guest_order"),
    path("pricing",views.pricing,name="pricing"),
    path("terms_and_conditions",views.terms_and_conditions,name="terms_and_conditions"),
    path("FAQ",views.FAQ,name="FAQ"),
    path("prohibited_items",views.prohibited_items,name="prohibited_items"),
    path("my_admin",views.my_admin,name="my_admin"),
    path("my_wallet",views.my_wallet,name="my_wallet"),
    path("my_account",views.my_account,name="my_account"),
    path("my_orders",views.my_orders,name="my_orders"),
    path("contact_us",views.contact_us,name="contact_us"),
    path("checkmpesaspaymentstatus", views.checkmpesaspaymentstatus, name="checkmpesaspaymentstatus"),

    #--------------------------Wallet----------------------
    path("my_wallet/deposit",views.deposit,name="deposit"),
    path("my_wallet/withdraw",views.withdraw,name="withdraw"),


    path("my_account/change_password",views.change_password,name="change_password"),


    path("my_orders/orders_under_review",views.orders_under_review,name="orders_under_review"),
    path("my_orders/action_required/",views.action_required,name="action_required"),
    path("my_orders/orders",views.orders,name="orders"),
    path("my_orders/ready_for_delivery",views.ready_for_delivery,name="ready_for_delivery"),
    path("my_orders/delivered",views.delivered,name="delivered"),

    path("my_orders/order_detail/<int:order_no>",views.my_orders_detail,name="my_orders_detail"),
    path("my_orders_delete_order/<int:order_no>",views.my_orders_delete_order,name="my_orders_delete_order"),
    path("my_orders/approve_payment/<int:order_no>",views.approve_payment, name="approve_payment"),
    path("my_orders/reject_payment/<int:order_no>",views.reject_payment, name="reject_payment"),
    path("my_orders/enter_delivery_details/<int:order_no>",views.enter_delivery_details, name="enter_delivery_details"),
    path("my_orders/provide_feedback/<int:order_no>",views.provide_feedback, name="provide_feedback"),


    #-----------------------------------------My Admin---------------------------------------

    

    path("my_admin/managed_accounts",views.admin_managed_accounts,name="admin_managed_accounts"),
    path("my_admin/managed_accounts/create_managed_accounts",views.admin_create_managed_accounts,name="admin_create_managed_accounts"),
    path("my_admin/orders",views.admin_orders,name="admin_orders"),
    path("my_admin/orders/orders_to_review", views.admin_orders_to_review, name ="admin_orders_to_review"),
    path("my_admin/orders/payment_pending",views.admin_payment_pending, name="admin_payment_pending"),
    path("my_admin/orders/items_to_purchase", views.admin_items_to_purchase, name ="admin_items_to_purchase"),
    path("my_admin/orders/purchased_orders", views.admin_purchased_orders, name ="admin_purchased_orders"),
    path("my_admin/orders/ready_to_ship", views.admin_ready_to_ship, name ="admin_ready_to_ship"),
    
    

    path("my_admin/orders/batches", views.admin_batches, name ="admin_batches"),
    path("my_admin/orders/batch_detail/<int:shipment_no>", views.admin_shipments_detail, name ="admin_shipments_detail"),
    path("my_admin/orders/completed_batches", views.admin_completed_batches, name="admin_completed_batches"),
    path("my_admin/orders/landed", views.admin_landed, name="admin_landed"),
    path("my_admin/orders/ready_for_delivered", views.admin_ready_for_delivered, name="admin_ready_for_delivered"),
    path("my_admin/orders/delivered", views.admin_delivered, name="admin_delivered"),
    path("my_admin/orders/rejected_orders", views.admin_rejected_orders, name="admin_rejected_orders"),


    path("my_admin/users", views.admin_users, name="admin_users"),
    path("my_admin/users/staff_users", views.admin_staff_users, name="admin_staff_users"),
    path("my_admin/users/super_users", views.admin_super_users, name="admin_super_users"),
    path("my_admin/users/managed_users", views.admin_managed_users, name="admin_managed_users"),
    path("my_admin/users/users_detail/<int:user_id>", views.admin_users_details, name="admin_users_details"),
    path("my_admin/order_detail/<int:order_no>", views.admin_orders_detail, name ="admin_orders_detail"),



    #-------------------------------------Backend Operations-----------------------------------
    path("my_admin/set_shipped/<int:order_no>", views.admin_set_shipped, name="admin_set_shipped"),
    path("my_admin/set_purchased/<int:order_no>", views.admin_set_purchased, name="admin_set_purchased"),
    path("my_admin/update_order_status", views.admin_update_order_status, name="admin_update_order_status"),
    path("my_admin/add_to_shipment", views.add_to_shipment, name="add_to_shipment"),
    path("my_admin/remove_from_batch/<int:order_no>", views.remove_from_batch, name="remove_from_batch"),
    path("my_admin/shipments/set_shipment_in_transit/<int:shipment_no>", views.admin_set_shipment_in_transit, name="admin_set_shipment_in_transit"),
    path("my_admin/set_delivered/<int:order_no>", views.admin_set_delivered, name="admin_set_delivered"),
    #path("my_admin/<str:detail_one>",views.my_admin_detail_one,name="my_admin_detail_one"),


    #----------------------------Payments----------------------------



]