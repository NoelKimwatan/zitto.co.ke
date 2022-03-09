from multiprocessing import context
from django import http
from django.shortcuts import render,redirect
from django.http import HttpResponse, response
from django.contrib.auth import authenticate,login, logout
from django.contrib.auth.models import User
from service.models import *
from django.views.decorators.http import require_GET, require_POST

from django.contrib.auth.decorators import login_required
from django.http import Http404

from ShippingService.decorators import staff_required, superuser_required,not_staff_required
from django.contrib import messages
from datetime import datetime,timedelta
from django.utils import timezone
from django.conf import Settings, settings

#Mpesa
import requests
from requests.auth import HTTPBasicAuth 
import base64
from django.http import JsonResponse
import json

import os


from django.views.decorators.csrf import csrf_exempt
from . import tasks




# Create your views here.


def index(request):
    return render(request,'service/index.html')


def prohibited_items(request):    
    return render(request,'service/prohibited_items.html')

def pricing(request):
    return render(request,'service/pricing.html')

def terms_and_conditions(request):
    return render(request,'service/terms_and_conditions.html')

def FAQ(request):
    return render(request,'service/FAQ.html')

def contact_us(request):
    return render(request,'service/contact_us.html')


def signup_user(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            logout(request)
        return render(request,"service/signup.html")
    elif request.method == "POST": 
        print("Signup post")
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        full_name = first_name + " " + last_name
        email = request.POST["email"]
        phone_number = request.POST["phone_number"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if (len(password1) < 8) or (len(password2) < 8):
            error = "Your password should be atleats 8 characters long"
            context = {"error":error,"first_name":first_name,"last_name":last_name,"email":email,"phone_number":phone_number}
            return render(request,"service/signup.html",context)

        elif password1 != password2:
            error = "The passwords entered do not match"
            context = {"error":error,"first_name":first_name,"last_name":last_name,"email":email,"phone_number":phone_number}
            return render(request,"service/signup.html",context)

        elif password1 == password2:
            password = password1

            try:
                print("User created")
                user = User.objects.create_user(
                    username = email,
                    email = email,
                    password = password,
                    first_name =first_name,
                    last_name=last_name
                )
                user.save()

                print("Customer created")
                customer = Customer.objects.create(
                    user=user,
                    name=full_name,
                    email=email,
                    phone_number = phone_number,

                )
                customer.save()


                print("Email send function")
                print("Send email function")
                tasks.send_signup_email_function(name=first_name,email=email)
                login(request,user) 
            except:
                error = "Email already in use"
                context = {"error":error,"first_name":first_name,"last_name":last_name,"email":email,"phone_number":phone_number}
                return render(request,"service/signup.html",context)

            # user.save()
            # customer.save()
            return redirect("index")

    else:
        raise Http404  


def login_user(request):
    if request.method == "GET":
        if request.user.is_authenticated:
            logout(request)
        
        return render(request,"service/login.html")
    else:
        print("Login posted")
        print("Email",request.POST["email"])
        print("Password",request.POST["password"])
        email = request.POST["email"]
        user = authenticate(username = email, password = request.POST["password"])

        print("Authentication results",user)

        if user is not None:
            login(request,user)
            if "next" in request.POST:
                return redirect(request.POST["next"])
            else:
                return redirect("index")
        else:
            messages.add_message(request, messages.WARNING, 'The password or username entered is incorrect')
            if "next" in request.POST:
                return redirect(request.POST["next"])
            else:
                return render(request,"service/login.html")

@login_required
def logout_user(request):
    if request.method == "POST":
        logout(request)
        return redirect("index")
    else:
        raise Http404

def user_get_badge_context(request):
    current_user = request.user
    current_customer = current_user.customer

    all_orders = Order.objects.all().filter(customer=current_customer)
    orders_under_review = all_orders.filter(status="IR")
    orders_action_required = all_orders.filter(status__in=["PP","SPP","LD"])
    orders_orders = all_orders.filter(status__in=["TP","P","R","IT","DDE"])
    orders_ready_for_delivery = all_orders.filter(status="RD")
    orders_delivered = all_orders.filter(status="D")

    context = {"orders_under_review":orders_under_review,"orders_action_required":orders_action_required,"orders_orders":orders_orders,
               "orders_ready_for_delivery":orders_ready_for_delivery,"orders_delivered":orders_delivered }

    return context

def guest_order(request):
    if request.method == "GET":
        return render(request,"service/order_guest.html")
    elif request.method == "POST":
        value_no = int(request.POST["value_no"])
        print("Value no is:",value_no)
        print("Value no type is:",type(value_no))

        if value_no == 1:
            identifier = str(request.META.get("REMOTE_ADDR"))+ "_" + str(datetime.now().strftime("%m%d%Y%H%M%S"))
            item_link = request.POST["link"]
            item_description = request.POST["description"]
            item_name = request.POST["name"]

            guest_order = GuestOrder.objects.create(
                name=item_name,
                identifier = identifier,
                link = item_link,
                description = item_description
            )
            guest_order.save()

            context = {"identifier":identifier}

            messages.add_message(request, messages.SUCCESS, 'Details Saved Successfully')
            return render(request,"service/order_guest.html",context)

        elif value_no == 2:
            input_identifier = request.POST["identifier"]
            first_name = request.POST["guest_order_f_name"]
            last_name = request.POST["guest_order_l_name"]
            phone_number = request.POST["guest_order_phone_no"]
            email = request.POST["guest_order_email"]

            try:
                print("Trying to get user")
                user = User.objects.get(username=email)
                print("User exists")
                messages.add_message(request, messages.ERROR, 'A user with the entered email exists. Please login')
                print("Redirecting")
                return redirect("login")

            except:
                pass



            guest_order = GuestOrder.objects.get(identifier=input_identifier)
            guest_order.first_name = first_name
            guest_order.last_name = last_name
            guest_order.phone_number = phone_number
            guest_order.email = email
            guest_order.save()
            page = "Sign_Up"

            context = {"identifier":input_identifier,"first_name":first_name,"last_name":last_name,"phone_number":phone_number,"email":email,"page":page}
            return render(request,"service/order_guest.html",context)
        elif value_no == 3:
            input_identifier = request.POST["identifier"]
            next_step = request.POST["create_account_or_cancel"]
            guest_order = GuestOrder.objects.get(identifier=input_identifier)

            allowed_characters = 'abcdefghijklmnopABCDEFGHIJKLMNOP123456789.,!@#'
            created_password = User.objects.make_random_password(length=8,allowed_chars=allowed_characters)

            if next_step == "Create Account":
                first_name = guest_order.first_name
                print("First name",first_name)
                last_name = guest_order.last_name
                print("Last name",last_name)
                full_name = first_name + " " + last_name
                phone_number = guest_order.phone_number
                email = guest_order.email
                password = created_password

                user = User.objects.create_user(
                    username = email,
                    email = email,
                    password = password,
                    first_name =first_name,
                    last_name=last_name
                )
                user.save()

                customer = Customer.objects.create(
                    user=user,
                    name=full_name,
                    email=email,
                    phone_number = phone_number,
                )
                customer.save()

                order = Order.objects.create(
                    name = guest_order.name,
                    customer = customer,
                    date_ordered = timezone.now(),
                    status = "IR",
                    link = guest_order.link,
                    description = guest_order.description
                )
                order.save()

                timeline = OrderTimeline.objects.create(
                    order = order,
                    status = "SRC"
                )
                timeline.save()

                guest_order.delete()

                tasks.send_managed_user_account_created_email_function(name=first_name,email=email,password=created_password)
                messages.add_message(request, messages.SUCCESS, 'Your account has been created, and login credentials sent to your email')
                return redirect("index")
                

            elif next_step == "Cancel":
                first_name = guest_order.first_name
                last_name = guest_order.last_name
                full_name = first_name + " " + last_name
                phone_number = guest_order.phone_number
                email = guest_order.email
                password = created_password

                user = User.objects.create_user(
                    username = email,
                    email = email,
                    password = password,
                    first_name =first_name,
                    last_name=last_name
                )
                user.save()

                customer = Customer.objects.create(
                    user=user,
                    name=full_name,
                    email=email,
                    phone_number = phone_number,
                    managed = True
                )
                customer.save()

                order = Order.objects.create(
                    name = guest_order.name,
                    customer = customer,
                    date_ordered = timezone.now(),
                    status = "IR",
                    link = guest_order.link,
                    description = guest_order.description
                )
                order.save()

                timeline = OrderTimeline.objects.create(
                    order = order,
                    status = "SRC"
                )
                timeline.save()

                guest_order.delete()

                messages.add_message(request, messages.SUCCESS, 'Thank you, your order has been received. Our team will contact soon')
                return redirect("index")
            else:
                raise Http404


        else:
            raise Http404
    else:
        raise Http404

@login_required
def order(request):
    if request.method == "GET":
        main_path = "order"
        context = {"main_path":main_path}
        return render(request,"service/order.html",context)
    elif request.method == "POST":
        item_link = request.POST["link"]
        item_description = request.POST["description"]
        item_name = request.POST["name"]

        customer = request.user.customer

        order = Order.objects.create(customer=customer,name=item_name,description=item_description,link=item_link,status="IR")
        order.date_ordered = timezone.now()
        order.save()

        timeline = OrderTimeline.objects.create(
            order = order,
            status = "SRC"
        )
        timeline.save()


        return redirect("my_orders")


@login_required
def my_account(request):
    user = request.user
    customer = request.user.customer

    if request.method == "GET":
        main_path = request.path.split('/')[1]
        sub_path = "my_account"
        context = {"main_path":main_path,"sub_path":sub_path}
        return render(request,"service/my_account.html",context)
    elif request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        full_name = first_name + " " +last_name
        user = request.user
        customer = request.user.customer

        user.first_name = first_name
        user.last_name = last_name
        user.save()
        customer.name = full_name
        customer.save()

        messages.add_message(request, messages.SUCCESS, 'Details Changed Successfully')
        return render(request,"service/my_account.html")

@login_required
def change_password(request):
    if request.method == "GET":
        main_path = request.path.split('/')[1]
        sub_path = request.path.split('/')[2]
        context = {"main_path":main_path,"sub_path":sub_path}
        return render(request,"service/change_password.html",context)
    elif request.method =="POST":
        user = request.user
        password =  request.POST["password"]
        password1 = request.POST["password1"]
        password2 = request.POST["password2"]

        if password == user.password:
            value = CheckPassword(password1,password2)

            if value == 1:
                user.password = password1
                user.save()
            elif value == 2:
                messages.add_message(request, messages.ERROR, 'Passwords Entered Dont Match')
            elif value == 3:
                messages.add_message(request, messages.ERROR, 'Passwords Entered Dont Match')
            else:
                raise Http404
            
            return render(request,"service/change_password.html")
        else:
            messages.add_message(request, messages.ERROR, 'Previous Password Entered is Incorrect')
            return render(request,"service/change_password.html")

    else:
        raise Http404





@login_required
def my_orders(request):
    customer = request.user.customer

    if request.method == "GET":
        main_path = request.path.split('/')[1]
        sub_path = "dashboard"

        current_context = {"main_path":main_path,"sub_path":sub_path}
        returned_context = user_get_badge_context(request)

        combined_context = {**current_context,**returned_context}

        return render(request,"service/my_orders.html",combined_context)

    elif request.method == "POST":
        raise Http404



@login_required
def orders_under_review(request):
    customer = request.user.customer
    header = "Orders Under Review"
    orders = Order.objects.all().filter(status="IR",customer=customer).order_by("-date_ordered")

    main_path = request.path.split('/')[1]
    sub_path = request.path.split('/')[2]

    returned_context = user_get_badge_context(request)
    current_context = {"main_path":main_path,"sub_path":sub_path,"header":header,"orders":orders}

    combined_context = {**returned_context,**current_context}

    return render(request,"service/my_orders_detail_under_review.html",combined_context)

@login_required
def action_required(request):
    user = request.user
    customer = request.user.customer
    header = "Action Required"
    orders = Order.objects.all().filter(status__in=["PP","SPP","LD"],customer=customer).order_by("-date_ordered")

    main_path = request.path.split('/')[1]
    sub_path = request.path.split('/')[2]

    returned_context = user_get_badge_context(request)
    current_context = {"main_path":main_path,"sub_path":sub_path,"header":header,"orders":orders}

    combined_context = {**returned_context,**current_context}

    return render(request,"service/my_orders_detail_action_required.html",combined_context)

@login_required
def orders(request):
    customer = request.user.customer
    header = "Orders"
    orders = Order.objects.all().filter(customer=customer).filter(status__in=["TP","P","R","IT","DDE"]).order_by("-date_ordered")

    main_path = request.path.split('/')[1]
    sub_path = request.path.split('/')[2]

    returned_context = user_get_badge_context(request)
    current_context = {"main_path":main_path,"sub_path":sub_path,"header":header,"orders":orders}

    combined_context = {**returned_context,**current_context}

    return render(request,"service/my_orders_detail_orders.html",combined_context)

@login_required
def ready_for_delivery(request):
    customer = request.user.customer
    header = "Ready for Delivery"
    orders = Order.objects.all().filter(status="RD",customer=customer).order_by("-date_ordered")

    main_path = request.path.split('/')[1]
    sub_path = request.path.split('/')[2]

    returned_context = user_get_badge_context(request)
    current_context = {"main_path":main_path,"sub_path":sub_path,"header":header,"orders":orders}

    combined_context = {**returned_context,**current_context}

    return render(request,"service/my_orders_detail_ready_for_delivery.html",combined_context)

@login_required
def delivered(request):
    customer = request.user.customer
    header = "Delivered Orders"
    orders = Order.objects.all().filter(status="D",customer=customer).order_by("date_completed")

    main_path = request.path.split('/')[1]
    sub_path = request.path.split('/')[2]

    returned_context = user_get_badge_context(request)
    current_context = {"main_path":main_path,"sub_path":sub_path,"header":header,"orders":orders}

    combined_context = {**returned_context,**current_context}

    return render(request,"service/my_orders_detail_delivered.html",combined_context)


@login_required
def my_orders_detail(request,order_no):
    customer = request.user.customer

    if request.method == "GET":
        print("Getting path")
        main_path = request.path.split('/')[1]
        print("Path obtained")
        try:
            print("Obtaining order item")
            order = Order.objects.get(id=order_no,customer=customer)

            order_status = order.status

            if order_status == "IR":
                sub_path = "orders_under_review"
            elif order_status in ["PP","SPP","LD"]:
                sub_path = "action_required"
            elif order_status in ["TP","P","R","IT","DDE"]:
                sub_path = "orders"   
            elif order_status == "RD":
                sub_path = "ready_for_delivery" 
            elif order_status == "D":
                sub_path = "delivered" 

            current_context = {"order":order,"main_path":main_path,"sub_path":sub_path}
                    
            returned_context = user_get_badge_context(request)
            combined_context = {**current_context,**returned_context}



            return render(request,"service/my_orders_order_detail.html",combined_context)

        except:
            raise Http404



@login_required
def my_orders_delete_order(request,order_no):

    if request.method == "POST":
        order = Order.objects.get(id=order_no)
        order.delete()
    else:
        raise Http404

@login_required   
def enter_delivery_details(request,order_no):
    order = Order.objects.get(id=order_no)
    county = request.POST["county"]
    town_location = request.POST["town/location"]
    description = request.POST["description"]

    delivery,created = DeliveryDetails.objects.get_or_create(order=order)
    delivery.county = county
    delivery.town_location = town_location
    delivery.description = description
    delivery.save()

    order.status = "DDE"
    order.save()

    order_timeline = OrderTimeline.objects.get(order=order)
    order_timeline.delivery_details_entered = timezone.now()
    order_timeline.status = "DDE"
    order_timeline.save()


    return redirect(my_orders)

@login_required   
def approve_payment(request,order_no):
    customer = request.user.customer
    if request.method == "GET":
        raise Http404
    elif request.method == "POST":

        print("Trying approve")
        order = Order.objects.get(id=order_no)
        if order.status == "PP":
            print("Purchase Payment")
            amount = order.amount
            message = "Purchase Amount for {} ".format(order.name,order.id)
            reference = timezone.localtime(timezone.now()).strftime("%Y%m%d%H%M%S")


            #customer,type,amount,payment_mode,input_reference,identifier,message,status
            details = {
                "customer":customer,"type": "W","amount":amount,"payment_mode":"I","message":message,"reference":reference
            }
            print("Tring transactions")
            print("Transaction details:-->",details)
            value = transaction(details)
        elif order.status == "SPP":
            print("Shipping Payment")
            amount = order.get_order_shipping_and_delivery
            message = "Delivery and shipping cost for {}".format(order.name)
            reference = timezone.localtime(timezone.now()).strftime("%Y%m%d%H%M%S")

            #customer,type,amount,payment_mode,input_reference,identifier,message,status
            details = {
                "customer":customer,"type": "W","amount":amount,"payment_mode":"I","message":message,"reference":reference
            }
            value = transaction(details)
        
            


        if value == 1:
            #Payment Processed
            message = "Payment of {} Successful".format(amount)

            if order.status == "PP":
                order.status = "TP"
                order.save()

                timeline = OrderTimeline.objects.get(order=order)
                timeline.purchase_payment_completed = timezone.now()
                timeline.status = "PPC"
                timeline.save()

            elif order.status == "SPP":
                order.status = "RD"
                order.save()

                timeline = OrderTimeline.objects.get(order=order)
                timeline.shipping_payment_complete = timezone.now()
                timeline.status = "SPC"
                timeline.save()

            messages.add_message(request, messages.SUCCESS, message)
            return redirect(my_wallet)
        elif value == 2:
            #Insufficient Blanace
            message = ("Payment of {} Unsuccessful. Insufficient balance in your wallet").format(amount)

            messages.add_message(request, messages.ERROR, message)
            return redirect(my_wallet)
        else:
            raise Http404

@login_required  
def reject_payment(request,order_no):
    order = Order.objects.get(id=order_no)
    reject_payment_object = RejectPaymentRequest.objects.create(order=order,reason = request.POST['reason'])
    reject_payment_object.save()

    order.status = "RJ"
    order.save()

    order_timeline = order.ordertimeline
    order_timeline.status = "RJ"
    order_timeline.save()

    return redirect('my_orders')


@login_required  
def provide_feedback(request,order_no):
    feedback = request.POST["feedback"]

    order = Order.objects.get(id=order_no)

    customer = order.customer 
    feedback = Feedback.objects.create(order=order,feedback=feedback,customer=customer)
    feedback.save()
    return redirect(delivered)



@login_required
def my_wallet(request):
    user = request.user
    customer = request.user.customer

    wallet,created = Wallet.objects.get_or_create(customer=customer)
    transactions = Transactions.objects.all().filter(customer=customer).order_by("date")

    all_orders = Order.objects.all().filter(customer=customer)
    orders_action_required = all_orders.filter(status__in=["PP","SPP","LD"])

    main_path = request.path.split('/')[1]
    sub_path = 'my_wallet'

    if request.method == "GET":
        context = {"wallet":wallet,"transactions":transactions,"main_path":main_path,"sub_path":sub_path,"orders_action_required":orders_action_required}
        return render(request,"service/my_wallet.html",context)
    elif request.method == "POST":
        pass


@login_required
def deposit(request):
    user = request.user
    customer = request.user.customer
    wallet,created = Wallet.objects.get_or_create(customer=customer)
    header = "Add funds"
    action = "Deposit"
    main_path = request.path.split('/')[1]
    sub_path = request.path.split('/')[2]

    all_orders = Order.objects.all().filter(customer=customer)
    orders_action_required = all_orders.filter(status__in=["PP","SPP","LD"])

    if request.method == "GET":
        context = {"header":header,"action":action,"main_path":main_path,"sub_path":sub_path,"orders_action_required":orders_action_required}
        return render(request,"service/deposit_withdraw.html",context)
    elif request.method == "POST":
        amount = request.POST["deposit_amount"]
        mpesa_number = request.POST["mpesa_number"]
        deposit_mode = request.POST["deposit_mode"]
        reference = "None"

        if deposit_mode == "mpesa":
            response = processmpesapayment(customer,mpesa_number,amount)
            print("Payment Processed")

            try:
                #response_data = json.loads(response.text)
                print("Payment processing successful")
                response_data = response.json()
                print("Response data",response_data)

                CheckoutRequestID = response_data["CheckoutRequestID"]

                details = {
                    "customer":customer,"type":"D","amount":amount,"payment_mode":"M","identifier":CheckoutRequestID,"status":"P"
                }
                transaction(details)
            except:
                print("Payment processing successful")
                identifier = timezone.localtime(timezone.now()).strftime("%Y%m%d%H%M%S")
                response_data = response.json()
                error_message = response_data["errorMessage"]
                complete = True

                details = {
                    "customer":customer,"type":"D","amount":amount,"payment_mode":"M","message":error_message,"status":"F","complete":complete,"identifier":identifier
                }
                transaction(details)


            message = "Processing Deposit of Ksh"+ str(amount)+ ". Please enter your Mpesa pin on your mobile phone"
            messages.add_message(request, messages.SUCCESS, message)
            return redirect(my_wallet)
        elif deposit_mode == "card":
            pass
        else:
            raise Http404
    else:
        raise Http404



@login_required
def withdraw(request):
    user = request.user
    customer = request.user.customer
    wallet,created = Wallet.objects.get_or_create(customer=customer)
    header = "Withdraw"
    action = "Withdraw"
    main_path = request.path.split('/')[1]
    sub_path = request.path.split('/')[2]

    all_orders = Order.objects.all().filter(customer=customer)
    orders_action_required = all_orders.filter(status__in=["PP","SPP","LD"])

    if request.method == "GET":
        context = {"header":header,"action":action,"main_path":main_path,"sub_path":sub_path,"orders_action_required":orders_action_required}
        return render(request,"service/deposit_withdraw.html",context)

    elif request.method == "POST":
        amount = request.POST["withdraw_amount"]
        mpesa_number = request.POST["mpesa_number"]
        withdraw_mode = request.POST["withdraw_mode"]
        identifier = timezone.now()
        input_reference = timezone.now()
        message = "Successful"
        type = "W"

        if withdraw_mode == "mpesa":
            response = processmpesawithdrawal(customer,mpesa_number,amount)
        elif withdraw_mode == "bank":
            pass
        else:
            raise Http404

        details = {
            "customer":customer,"type":type,"amount":amount,"payment_mode":"M","status":"S","identifier":identifier,
            "input_reference":input_reference,"message":message
        }
        transaction(details)
        messages.add_message(request, messages.SUCCESS,"Processing payment please refresh this page")
        return redirect(my_wallet)


#customer,type,amount,payment_mode,input_reference,identifier,message,status

def transaction(details):
    payment_mode = details["payment_mode"]
    customer = details["customer"]

    wallet,created = Wallet.objects.get_or_create(customer=customer) 
    wallet_balance = wallet.balance

    #Mpesa payment
    if payment_mode == "M":
        status_options = details["status"]

        if status_options == "P":
            #"customer":customer,"type":"D","amount":amount,"payment_mode":"M","identifier":CheckoutRequestID,"status":"P"
            customer = details["customer"]
            type = details["type"]
            amount = details["amount"]
            identifier = details["identifier"]

            transaction_object = Transactions.objects.create(
                customer = customer,
                amount = amount,
                status = status_options,
                type = type,
                identifier = identifier,
                payment_mode = payment_mode
            )
            transaction_object.save()

        elif status_options == "S":
            #"customer":customer,"amount":amount,"input_reference":reference,"status":status,"message":Mpesa_message,"identifier":CheckoutId,"payment_mode":payment_mode,"type":type
            customer = details["customer"]
            amount = details["amount"]
            reference = details["input_reference"]
            message = details["message"]
            identifier = details["identifier"]
            type = details["type"]

            if type == "D":
                wallet.balance = wallet_balance + amount
                wallet.save()
                print("Transacrion is a deposit")


                transaction_object = Transactions.objects.get(customer=customer,identifier=identifier)
                transaction_object.amount = amount
                transaction_object.reference = reference
                transaction_object.message = message
                transaction_object.status = status_options
                transaction_object.complete = True
                transaction_object.save()
            
            elif type == "W":
                if wallet_balance > int(amount):
                    wallet.balance = wallet_balance - int(amount)
                    wallet.save()

                    print("Transacrion is a withdrawal")

                    transaction_object = Transactions.objects.create(customer=customer)
                    transaction_object.amount = amount
                    transaction_object.type = type
                    transaction_object.message = "Successful"
                    transaction_object.payment_mode = payment_mode
                    transaction_object.status = "Successful"
                    transaction_object.complete = True
                    transaction_object.save()
                else:
                    print("Withdrawal amount is above balance")
                    transaction_object = Transactions.objects.create(customer=customer)
                    transaction_object.amount = amount
                    transaction_object.type = type
                    transaction_object.message = "Failed. Insufficient Balance"
                    transaction_object.payment_mode = payment_mode
                    transaction_object.status = "Failed"
                    transaction_object.complete = True
                    transaction_object.save()


        elif status_options == "F":
            #From failed to send STK "customer":customer,"type":"D","amount":amount,"payment_mode":"M","message":"Failed to send STK push","status":"F"
                             
            customer = details["customer"]
            type = details["type"]
            amount = details["amount"]
            identifier = details["identifier"]
            message = details["message"]
            complete = details["complete"]

            if complete == True:
                transaction_object = Transactions.objects.create(
                    customer = customer,
                    amount = amount,
                    status = status_options,
                    type = type,
                    identifier = identifier,
                    reference = identifier,
                    payment_mode = payment_mode,
                    message = message

                )
                transaction_object.save()
            else:
                reference = details["input_reference"]

                transaction_object = Transactions.objects.get(
                    customer = customer,
                    identifier = identifier
                )

                transaction_object.reference = reference
                transaction_object.message = message
                transaction_object.status = status_options
                transaction_object.complete = True
                transaction_object.save()


    elif payment_mode == "C":
        pass
        
    elif payment_mode == "I":
        #"customer":customer,"type": "W","amount":amount,"payment_mode":"I","message":reference
        type = details["type"]
        amount = details["amount"]
        message = details["message"]
        reference = details["reference"]

        if type == "D":
            wallet.balance = wallet_balance + amount
            wallet.save()
            status = "S"

            transaction_object = Transactions.objects.create(
                customer = customer,
                amount = amount,
                type = type,
                reference = reference,
                payment_mode = payment_mode,
                message = message,
                status = status,
                complete = True
            )
            transaction_object.save()

            return 1

        elif type == "W":
            if wallet_balance < amount:
                return 2

            elif wallet_balance >= amount:
                wallet.balance = wallet_balance - amount
                wallet.save()

                status = "S"
                transaction_object = Transactions.objects.create(
                    customer = customer,
                    amount = amount,
                    type = type,
                    message = message,
                    payment_mode = payment_mode,
                    reference = reference,
                    complete = True,
                    status = status
                )
                transaction_object.save()
                return 1
    else:
        raise Http404

        



#---------------------------------------------------------Backend Admin Required---------------------------------------------------------
@staff_required
def admin_get_badge_context(request):
    all_users = User.objects.all()
    all_staff_users = User.objects.all().filter(is_staff=True,is_superuser=False)
    all_super_users = User.objects.all().filter(is_superuser=True)
    all_managed_users = Customer.objects.all().filter(managed=True)
    all_orders = Order.objects.all() #Do not return this
    all_shipments = Shipment.objects.all()

    orders_under_review = all_orders.filter(status="IR")
    orders_payment_pending = all_orders.filter(status__in=["PP","SPP"])
    items_to_purchase = all_orders.filter(status__in=["TP"])
    purchased_orders = all_orders.filter(status__in=["P"])
    orders_ready_to_ship = all_orders.filter(status="R",in_shipment = False)
    
    batches_created_it = all_shipments.filter(status__in=["CR","IT"])
    completed_batches = all_shipments.filter(status="C")

    orders_landed = all_orders.filter(status__in=["LD","DDE"])
    orders_ready_for_delivery = all_orders.filter(status="RD")
    orders_delivered = all_orders.filter(status="D")
    rejected_orders = all_orders.filter(status="RJ")

    context = {"all_users":all_users,"all_staff_users":all_staff_users,"all_super_users":all_super_users,"orders_under_review":orders_under_review,"orders_payment_pending":orders_payment_pending,"items_to_purchase":items_to_purchase,
        "purchased_orders":purchased_orders,"orders_ready_to_ship":orders_ready_to_ship,"batches_created_it":batches_created_it,
        "completed_batches":completed_batches,"orders_landed":orders_landed,"orders_ready_for_delivery":orders_ready_for_delivery,
        "orders_delivered":orders_delivered,"rejected_orders":rejected_orders,"all_managed_users":all_managed_users}

    return context

@staff_required
def staff_get_badge_context(request):
    all_orders = Order.objects.all() #Do not return this
    all_shipments = Shipment.objects.all()

    

    completed_batches = all_shipments.filter(status="C")

    orders_landed = all_orders.filter(status__in=["LD","DDE"])
    orders_ready_for_delivery = all_orders.filter(status="RD")
    orders_delivered = all_orders.filter(status="D")
    rejected_orders = all_orders.filter(status="RJ")

    context = {"completed_batches":completed_batches,"orders_landed":orders_landed,"orders_ready_for_delivery":orders_ready_for_delivery,
        "orders_delivered":orders_delivered,"rejected_orders":rejected_orders}

    return context


@staff_required
def my_admin(request):
    users = User.objects.all()

    new_users_this_week = User.objects.all().filter(date_joined__range=[(timezone.now() - timedelta(days=7)),timezone.now()])
    active_users_this_week = User.objects.all().filter(last_login__range=[(timezone.now() - timedelta(days=7)),timezone.now()])

    wallets = Wallet.objects.all()
    total_in_wallets = 0

    for wallet in wallets:
        total_in_wallets += wallet.balance


    orders = Order.objects.all()
    shipments = Shipment.objects.all()


    main_path = "main"
    sub_path = "main"

    if request.user.is_superuser:
        sufficient_permission = True
    else:
        sufficient_permission = False

    context = {"users":users,"total_in_wallets":total_in_wallets,"new_users_this_week":new_users_this_week,
    "active_users_this_week":active_users_this_week,"main_path":main_path,"sub_path":sub_path,"sufficient_permission":sufficient_permission}


    return render(request,"service/my_admin.html",context)


@staff_required
def admin_managed_accounts(request):
    header = "Managed Accounts"
    customers = Customer.objects.all().filter(managed=True)

    main_path = request.path.split('/')[2]
    sub_path = "main"

    context = {"header":header,"customers":customers,"main_path":main_path,"sub_path":sub_path}


    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        combined_context = {**context,**permission_context}


    if request.method == "GET":
        return render(request,"service/my_admin_managed_accounts.html",combined_context)
    elif request.method == "POST":
        print("This is a post request")
        customer_id = request.POST["customer_id"]
        customer = Customer.objects.get(id=customer_id)
        user = customer.user
        print("User details",user)
        print("Customer details",customer)

        if customer.managed == True:
            print("The account is a managed account")
            login(request,user)
            return redirect(index)
        else:
            print("The account is NOT managed account")
            messages.add_message(request, messages.WARNING, 'Error: The account entered is not a managed account')
            return render(request,"service/my_admin_managed_accounts.html",combined_context)

@staff_required
def admin_create_managed_accounts(request):
    header = "Managed Accounts"
    customers = Customer.objects.all().filter(managed=True)

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"header":header,"customers":customers,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        combined_context = {**context,**permission_context}



    if request.method == "GET":
        return render(request,"service/my_admin_create_managed_accounts.html",combined_context)
    elif request.method == "POST":
        first_name = request.POST["first_name"]
        last_name = request.POST["last_name"]
        phone_number = request.POST["phone_number"]
        email = request.POST["email"]

        allowed_characters = 'abcdefghijklmnopABCDEFGHIJKLMNOP123456789.,!@#'
        created_password = User.objects.make_random_password(length=8,allowed_chars=allowed_characters)
        print("Password created:",created_password)
        print("Created Email:",email)

        user = User.objects.create_user(
            username = email,
            email = email,
            password = created_password,
            first_name =first_name,
            last_name=last_name
        )
        user.save()


        customer = Customer.objects.create(
            user = user,
            name = first_name + " " + last_name,
            email = email,
            phone_number = phone_number,
            managed = True
        )
        customer.save()
        tasks.send_managed_user_account_created_email_function(name=first_name,email=email,password=created_password)

        return redirect(admin_managed_accounts)


@staff_required
def admin_orders(request):
    main_path = request.path.split('/')[2]
    sub_path = "main"

    context = {"main_path":main_path,"sub_path":sub_path}


    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}

    else:
        permission_context = {"sufficient_permission":True}
        admin_context = staff_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}

    return render(request,"service/my_admin_orders.html",combined_context)

    


@staff_required
def admin_orders_to_review(request):
    user = request.user
    customer = request.user.customer
    header = "Orders to Review"
    orders = Order.objects.all().filter(status="IR").order_by("-date_ordered")

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"header":header,"orders":orders,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        admin_context = staff_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}

    return render(request,"service/my_admin_detail_orders_to_review.html",combined_context)

@staff_required
def admin_payment_pending(request):
    user = request.user
    customer = request.user.customer
    header = "Payment Pending"
    orders = Order.objects.all().filter(status__in=["PP","SPP"]).order_by("-date_ordered")

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"header":header,"orders":orders,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        admin_context = staff_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}

    return render(request,"service/my_admin_detail.html",combined_context)

@staff_required
def admin_items_to_purchase(request):
    customer = request.user.customer
    header = "Items to purchase"
    orders = Order.objects.all().filter(status="TP").order_by("-date_ordered")

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"header":header,"orders":orders,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        admin_context = staff_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}

    if request.method == "GET":
        return render(request,"service/my_admin_detail.html",combined_context)
    elif request.method == "POST":
        pass
    else:
        raise Http404

@staff_required
def admin_purchased_orders(request):
    customer = request.user.customer
    header = "Purchased orders"
    orders = Order.objects.all().filter(status="P").order_by("-date_ordered")
    post_view = "admin_purchased_orders"

    status_options = {
        "IP":"Item purchased",
        "ETW":"Enroute to warehouse",
        "RAW":"Received at warehouse",
        "BPFOS":"Being prepared for overseas shipping",
        "DFW":"Departed from warehouse",
        "AAUSF":"Arrived at US sort facility",
        "AADSF":"Arrived at Dubai sort facility",
    }

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"header":header,"orders":orders,"status_options":status_options,"post_view":post_view,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        admin_context = staff_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}

    if request.method == "GET":
        return render(request,"service/my_admin_detail.html",combined_context)
    elif request.method == "POST":
        order_id = request.POST["order_id"]
        key = request.POST["selected_status"]

        order = Order.objects.get(id=order_id)
        timeline = OrderTimeline.objects.get(order=order)
        timeline.status = key
        timeline.save()




        if key == "IP":#Item purchased
            pass
        elif key == "ETW":#Enroute to warehouse
            timeline.enroute_to_warehouse = timezone.now()
        elif key == "RAW":#Received at warehouse
            timeline.received_at_warehouse = timezone.now()
        elif key == "BPFOS":#Being prepared for overseas shipping
            timeline.being_prepared_for_overseas_shipping = timezone.now()
        elif key == "DFW":#Departed from warehouse
            timeline.departed_from_warehouse = timezone.now()
        elif key == "AAUSF":#Arrived at US sort facility
            timeline.arrived_at_us_sort_facility = timezone.now()
            order.status = "R"
            order.save()
        elif key == "AADSF":#Arrived at Dubai sort facility
            timeline.arrived_at_dubai_sort_facility = timezone.now()
            order.status = "R"
            order.save()
        else:
            raise Http404

        timeline.save()
        return render(request,"service/my_admin_detail.html",combined_context)

    else:
        raise Http404




@staff_required
def admin_ready_to_ship(request):
    customer = request.user.customer
    header = "Ready to Ship"
    orders = Order.objects.all().filter(status="R",in_shipment = False).order_by("-date_ordered")
    shipments = Shipment.objects.all().filter(status="CR")

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"header":header,"orders":orders,"main_path":main_path,"sub_path":sub_path,"shipments":shipments}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        admin_context = staff_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}

    if request.method == "GET":
        return render(request,"service/my_admin_detail.html",combined_context)
    elif request.method == "POST":
        shippmentName = request.POST["shippmentName"]
        batchNumber = request.POST["batchNumber"]
        description = request.POST["description"]
        page_source = request.POST["page_source"]

        newShipment = Shipment.objects.create(name=shippmentName,batch_number=batchNumber,description=description)
        newShipment.save()

        batchtimeline = BatchTimeline.objects.create(shipment=newShipment)
        batchtimeline.save()

        if page_source == "ready_to_ship":
            return render(request,"service/my_admin_detail.html",combined_context)
        elif page_source == "batches":
            return redirect("admin_batches")
        else:
            raise Http404
    else:
        raise Http404





@staff_required
def admin_batches(request):
    customer = request.user.customer
    header = "Batches"
    batches = Shipment.objects.all().filter(status__in=["CR","IT"]).order_by("-batch_number")
    
    status_options = {
        "CR":"Created",
        "DTDA":"Dispatched to destination airport",
        "AADA":"Arrived at destination airport",
        "UIC":"Undergoing import clearance",
        "C":"Complete",
    }

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"header":header,"batches":batches,"status_options":status_options,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        admin_context = staff_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}


    if request.method == "GET":
        return render(request,"service/my_admin_shipments.html",combined_context)
    elif request.method == "POST":
        shipment_id = request.POST["shipment_id"]
        key = request.POST["selected_shipment"]

        shipment = Shipment.objects.get(id=shipment_id)


        b_timeline = BatchTimeline.objects.get(shipment=shipment)


        if key == "CR": #Created
            b_timeline.status = "CR"
            b_timeline.save()
            shipment.status = "CR"
            shipment.save()

            orders = Order.objects.all().filter(shipment=shipment)
            for order in orders:
                order_timeline = OrderTimeline.objects.get(order=order)
                order_timeline.status = "AADSF"
                order_timeline.save()
                order.status = "R"
                order.save()

        elif key == "DTDA": #Dispatched to destination airport
            b_timeline.dispatched_to_destination_airport = timezone.now()
            b_timeline.status = "DTDA"
            b_timeline.save()
            shipment.status = "IT"
            shipment.save()

            orders = Order.objects.all().filter(shipment=shipment)
            for order in orders:
                order_timeline = OrderTimeline.objects.get(order=order)
                order_timeline.status = "DTDA"
                order_timeline.dispatched_to_destination_airport = timezone.now()
                order_timeline.save()

                
                order.status = "IT"
                order.save()
                

        elif key == "AADA": #Arrived at destination airport
            b_timeline.arrived_at_destination_airport = timezone.now()
            b_timeline.status = "AADA"
            b_timeline.save()
            shipment.status = "IT"
            shipment.save()

            orders = Order.objects.all().filter(shipment=shipment)
            for order in orders:
                order_timeline = OrderTimeline.objects.get(order=order)
                order_timeline.status = "AADA"
                order_timeline.arrived_at_destination_airport = timezone.now()
                order_timeline.save()

                
                order.status = "IT"
                order.save()
                

                

        elif key == "UIC": #Undergoing import clearance
            b_timeline.undergoing_import_clearance = timezone.now()
            b_timeline.status = "UIC"
            b_timeline.save()
            shipment.status = "IT"
            shipment.save()

            orders = Order.objects.all().filter(shipment=shipment)
            for order in orders:
                order_timeline = OrderTimeline.objects.get(order=order)
                order_timeline.status = "UIC"
                order_timeline.undergoing_import_clearance = timezone.now()
                order_timeline.save()

                
                order.status = "IT"
                order.save()
                

        elif key == "C":
            b_timeline.complete = timezone.now()
            b_timeline.status = "C"
            b_timeline.save()
            shipment.status = "C"
            shipment.date_completed = timezone.now()
            shipment.save()

            orders = Order.objects.all().filter(shipment=shipment)
            for order in orders:
                order_timeline = OrderTimeline.objects.get(order=order)
                order_timeline.status = "PBPFD"
                order_timeline.package_being_prepared_for_delivery = timezone.now()
                order_timeline.save()

                
                order.status = "LD"
                order.save()
                
        else:
            raise Http404
        
        
        return redirect(admin_batches)


@staff_required
def admin_completed_batches(request): 
    customer = request.user.customer
    header = "Completed Batches"
    batches = Shipment.objects.all().filter(status="C").order_by("batch_number")

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"header":header,"batches":batches,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":True}
        admin_context = staff_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}

    return render(request,"service/my_admin_shipments.html",combined_context)

@staff_required
def admin_shipments_detail(request,shipment_no): 
    customer = request.user.customer
    shipment = Shipment.objects.get(id=shipment_no)

    orders = Order.objects.all().filter(in_shipment=True,shipment=shipment).order_by("-tracking_number")

    context = {"shipment":shipment,"orders":orders} 

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        combined_context = {**context,**permission_context}

    if request.method == "GET":
        return render(request,"service/my_admin_shipments_detail.html",combined_context)
    elif request.method == "POST":
        shipment = Shipment.objects.get(id=shipment_no)
        batchName = request.POST["shippmentName"]
        batchNumber = request.POST["batchNumber"]
        description = request.POST["description"]

        shipment.name = batchName
        shipment.batch_number = batchNumber
        shipment.description = description
        shipment.save()
        return redirect(admin_shipments_detail,shipment_no)

@staff_required
def admin_landed(request):
    customer = request.user.customer
    header = "Orders Landed"

    orders = Order.objects.all().filter(status__in=["LD","DDE"]).order_by("-tracking_number")

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"header":header,"orders":orders,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":True}
        admin_context = staff_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}

    return render(request,"service/my_admin_detail.html",combined_context)

@staff_required
def admin_ready_for_delivered(request):
    customer = request.user.customer
    header = "Orders Ready For Delivery"

    orders = Order.objects.all().filter(status="RD").order_by("-tracking_number")
    post_view = "admin_ready_for_delivered"
    

    status_options = {
        "SPC":"Shipping payment complete",
        "RFD":"Ready for delivery",
        "OFD":"Out for delivery",
        "D":"Delivered",
    }

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"header":header,"orders":orders,"post_view":post_view,"status_options":status_options,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":True}
        admin_context = staff_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}


    if request.method == "GET":
        return render(request,"service/my_admin_detail.html",combined_context)
    elif request.method == "POST":
        order_id = request.POST["order_id"]
        key = request.POST["selected_status"]

        order = Order.objects.get(id=order_id)
        order.status = "RD"
        order.save()

        timeline = OrderTimeline.objects.get(order=order)
        timeline.status = key
        timeline.save()



        if key == "SPC":#Enroute to warehouse
            pass
        elif key == "RFD":#Received at warehouse
            timeline.ready_for_delivery = timezone.now()
        elif key == "OFD":#Being prepared for overseas shipping
            timeline.out_for_delivery = timezone.now()
        elif key == "D":#Arrived at Dubai sort facility
            timeline.delivered = timezone.now()
            order.status = "D"
            order.date_completed = timezone.now()
            order.save()
        else:
            raise Http404
        timeline.save()
        return redirect(admin_ready_for_delivered)
    else:
        raise Http404

    


@staff_required
def admin_delivered(request):
    header = "Delivered Orders"
    orders = Order.objects.all().filter(status="D").order_by("date_completed")

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"header":header,"orders":orders,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":True}
        admin_context = staff_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}


    return render(request,"service/my_admin_detail_date_delivered.html",combined_context)

@staff_required
def admin_rejected_orders(request):
    header = "Rejected Orders"
    orders = Order.objects.all().filter(status="RJ").order_by("-date_ordered")

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"header":header,"orders":orders,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        admin_context = staff_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}


    return render(request,"service/my_admin_detail.html",combined_context)

@staff_required
def admin_orders_detail(request,order_no):
    user = request.user
    customer = request.user.customer
    order = Order.objects.get(id=order_no)
    shipments = Shipment.objects.all().filter(status="CR")

    context = {"order":order,"shipments":shipments}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        combined_context = {**context,**permission_context}



    if request.method == "GET": 
        return render(request,"service/my_admin_order_detail.html",combined_context)
    elif request.method == "POST":
        order = Order.objects.get(id=order_no)

        if order.status == "IR":
            estimated_weight = request.POST["estimatedWeight"]
            price_per_kg = request.POST["price_per_kg"]
            estimated_shipping_amount = request.POST["shippingEstimate"]
            

            purchase_amount_in_original_currency = request.POST["purchaseAmountOriginalCurrency"]
            exchage_rate = request.POST["exchangeRate"]
            purchase_amount = request.POST["purchaseAmount"]

            
            order.amount_in_purchase_currency = purchase_amount_in_original_currency
            order.exchage_rate = exchage_rate
            order.amount = purchase_amount
            order.estimated_weight = estimated_weight
            order.price_per_kg = price_per_kg
            order.shippingEstimate = estimated_shipping_amount
            order.save()


        elif order.status == "DDE":
            shipping_amount = request.POST["shipping"]
            delivery_amount = request.POST["delivery_fee"]
            order.shipping = shipping_amount
            order.delivery_fee = delivery_amount
            order.save()

        elif order.status == "R" or order.status == "P":
            try:
                trackingNumber = request.POST["trackingNumber"]
                order.tracking_number = trackingNumber
                order.save()

            except:
                messages.error(request,"Failed: Please ensure the tracking number is unique")
                return redirect(admin_orders_detail,order_no)


        
        if request.POST["submit"] == "Save":
            messages.success(request,"Details Saved Succesfully")
            return redirect(admin_orders_detail,order_no)
        elif request.POST["submit"] == "Submit Review":
            order.status = "PP"
            order.save()

            timeline = OrderTimeline.objects.get(order=order)
            timeline.ship_request_processed = timezone.now()
            timeline.status = "SRP"
            timeline.save()

            return redirect(admin_orders_to_review)

        elif request.POST["submit"] == "Set shipping and delivery":
            order.status = "SPP"
            order.save()

            timeline = OrderTimeline.objects.get(order=order)
            timeline.shipping_price_reviewed = timezone.now()
            timeline.status = "SPP"
            timeline.save()

            return redirect(admin_landed)
        elif request.POST["submit"] == "Save Tracking Number":
            if order.status == "R":
                return redirect(admin_ready_to_ship)
            elif order.status == "P":
                messages.success(request,"Details Saved Succesfully")
                return redirect(admin_orders_detail,order_no)


@staff_required
def admin_users(request):
    users = User.objects.all()
    header = "All Users"

    main_path = request.path.split('/')[2]
    sub_path = "main"

    context = {"users":users,"header":header,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        combined_context = {**context,**permission_context}

    return render(request,"service/my_admin_users.html",combined_context)

@staff_required
def admin_staff_users(request):
    users = User.objects.all().filter(is_staff=True, is_superuser=False)
    header = "Staff Users"

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"users":users,"header":header,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        combined_context = {**context,**permission_context}

    return render(request,"service/my_admin_users.html",combined_context)

@staff_required
def admin_super_users(request):
    users = User.objects.all().filter(is_superuser=True)
    header = "Super Users"

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"users":users,"header":header,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        combined_context = {**context,**permission_context}

    return render(request,"service/my_admin_users.html",combined_context)


@staff_required
def admin_managed_users(request):
    users = User.objects.all().filter(customer__managed=True)
    header = "Managed Users"

    main_path = request.path.split('/')[2]
    sub_path = request.path.split('/')[3]

    context = {"users":users,"header":header,"main_path":main_path,"sub_path":sub_path}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        combined_context = {**context,**permission_context}

    return render(request,"service/my_admin_users.html",combined_context)


@staff_required
def admin_users_details(request,user_id):
    try:
        user = User.objects.get(id=user_id)
    except:
        raise Http404
    customer = user.customer
    transactions = Transactions.objects.all().filter(customer=customer)
    wallet,created = Wallet.objects.get_or_create(customer=customer)

    context = {"user":user,"customer":customer,"transactions":transactions,"wallet":wallet}

    if request.user.is_superuser:
        permission_context = {"sufficient_permission":True}
        admin_context = admin_get_badge_context(request)
        combined_context = {**context,**admin_context,**permission_context}
    else:
        permission_context = {"sufficient_permission":False}
        combined_context = {**context,**permission_context}

    if request.method == "GET":
        return render(request,"service/my_admin_users_details.html",combined_context)
    elif request.method == "POST":
        if request.POST["admin_user_modal"] == "change_state":
            if user.is_superuser:
                messages.add_message(request, messages.WARNING, 'Error: The above user is a superuser')
                return redirect(admin_users_details,user_id)
            elif user.is_staff:
                messages.add_message(request, messages.SUCCESS, 'Success: Staff Privilages have been removed from '+ str(user.first_name))
                user.is_staff = False
                user.save()
                return redirect(admin_users_details,user_id)
            else:
                messages.add_message(request, messages.SUCCESS, 'Success: Staff Privilages have been given to '+ str(user.first_name))
                user.is_staff = True
                user.save()
                return redirect(admin_users_details,user_id)
        elif request.POST["admin_user_modal"] == "email":
            messages.add_message(request, messages.WARNING, 'Error: This feature is currently in development')
            context = {"user":user,"customer":customer,"transactions":transactions,"wallet":wallet}
            return redirect(admin_users_details,user_id)
        elif request.POST["admin_user_modal"] == "text":
            messages.add_message(request, messages.WARNING, 'Error: his feature is currently in development')
            context = {"user":user,"customer":customer,"transactions":transactions,"wallet":wallet}
            return redirect(admin_users_details,user_id)
    else:
        raise Http404




@staff_required
def admin_set_shipped(request,order_no):
    order = Order.objects.get(id=order_no)
    order.status = "S"
    order.save()

    timeline = OrderTimeline.get(order=order)
    timeline.arrived_at_destination_airport = timezone.now()
    timeline.status = "AADA"
    timeline.save()
    
    return redirect("admin_ready_to_ship")


@staff_required
def admin_set_purchased(request,order_no):
    order = Order.objects.get(id=order_no)
    order.status = "P"
    order.save()

    timeline = OrderTimeline.objects.get(order=order)
    timeline.item_purchased = timezone.now()
    timeline.status = "IP"
    timeline.save()


    return redirect("admin_items_to_purchase")

@staff_required
def admin_update_order_status(request):

    if request.method == "POST":
        order_id = request.POST["order_id"]
        key = request.POST["selected_status"]

        order = Order.objects.get(id=order_id)
        timeline = OrderTimeline.objects.get(order=order)
        timeline.status = key


        if key == "IP":#Item purchased
            timeline.item_purchased = timezone.now()
        elif key == "ETW":#Enroute to warehouse
            timeline.enroute_to_warehouse = timezone.now()
        elif key == "RAW":#Received at warehouse
            timeline.received_at_warehouse = timezone.now()
        elif key == "BPFOS":#Being prepared for overseas shipping
            timeline.being_prepared_for_overseas_shipping = timezone.now()
        elif key == "DFW":#Departed from warehouse
            timeline.departed_from_warehouse = timezone.now()
        elif key == "AADSF":#Arrived at Dubai sort facility
            timeline.arrived_at_dubai_sort_facility = timezone.now()
            order.status = "R"
            order.save()
        else:
            raise Http404

        timeline.save()

    else:
        raise Http404

    return redirect("admin_purchased_orders")



@staff_required  
def admin_set_shipment_in_transit(request,shipment_no):
    selected_shipment = Shipment.objects.get(id=shipment_no)

    associated_orders = Order.objects.all().filter(shipment=selected_shipment)
    if len(associated_orders) == 0:
        messages.add_message(request, messages.WARNING, 'Error: Shipment is empty')
        return redirect("admin_batches")

    selected_shipment.status = "IT"
    selected_shipment.save()

    orders = Order.objects.all().filter(shipment=selected_shipment,in_shipment=True)
    for order in orders:
        order.status = "IT"
        order.save()



    return redirect("admin_batches")



def add_to_shipment(request):
    print("Adding to shipment section")
    shipment_no_selected = request.POST["selected_shipment"]
    selected_shipment = Shipment.objects.get(id=shipment_no_selected)


    order_no = request.POST["order"]
    order = Order.objects.get(id=order_no)

    if not order.tracking_number:
        try:
            tracking_no = request.POST["trackingNumber"]
            order.tracking_number = tracking_no
            order.in_shipment = True
            order.shipment = selected_shipment
            order.save()
            print("Try passed")
        except:
            messages.error(request,"Failed: Please ensure the tracking number is unique")
            return redirect(admin_ready_to_ship)
    else:
        print("Tracking number section skipped")
        order.in_shipment = True
        order.shipment = selected_shipment
        order.save()
        
    return redirect(admin_ready_to_ship)

def remove_from_batch(request,order_no):
    order = Order.objects.get(id=order_no) 
    shipment_id = order.shipment.id
    order.shipment = None
    order.in_shipment = False
    order.save()
    return redirect(admin_shipments_detail,shipment_id)   


def admin_set_delivered(request,order_no):
    order = Order.objects.get(id=order_no)
    order.date_completed = timezone.now()
    order.status = "D"
    order.save()

    timeline = OrderTimeline.objects.get(order=order)
    timeline.delivered = timezone.now()
    timeline.status = "D"
    timeline.save()

    return redirect("admin_ready_for_delivered")
        

#-----------------------------------------------------Administrative---------------------------------------
def CheckPassword(password1,password2):
    if (len(password1) < 8) or (len(password2) < 8):
        return 3 #Password Not longer than 8

    elif password1 != password2:
        return 2 #Passwords Dont Match

    elif password1 == password2:
        return 1 #Password OK Successful

#------------------------------------------------------Error View------------------------------------------

def handler404(request,exception):
    return render(request,"service/404.html")


def processmpesapayment(customer,mpesa_number,amount):
        total = amount
        raw_phonenumber = mpesa_number
        phonenumber = "254" + raw_phonenumber[-9:]
        print("Stripped phone number",phonenumber)

        #--------------------------------------------------Need to Hide-------------------------------------------------
        consumer_key = settings.CONSUMER_KEY
        consumer_secret = settings.CONSUMER_SECRET
        BusinessShortCode = settings.BUSINESS_SHORT_CODE
        lipa_na_mpesa_passkey = settings.LIPA_NA_MPESA_PASSKEY
        phonenumber = str(phonenumber)

        access_token_api_URL = settings.ACCESS_TOKEN_API_URL
        stk_push_api_URL = settings.PROCESS_REQUEST_API_URL

        r = requests.get(access_token_api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        print("R response",r.json)
        input_access_token = r.json()["access_token"] ########################
        print("Input access token",input_access_token)

        print("Time now:",timezone.now())
        Timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        print("Time Stamp",Timestamp)
        Data_to_encode = BusinessShortCode + lipa_na_mpesa_passkey + Timestamp
        Encoded_data = base64.b64encode(Data_to_encode.encode())
        Decoded_data = Encoded_data.decode("utf8")
        print("Password",Decoded_data)

        def lipa_na_mpesa():
            access_token = input_access_token
            api_url = stk_push_api_URL
            headers = { "Authorization": "Bearer %s" % access_token }
            request = {
                "BusinessShortCode": BusinessShortCode ,#Need to hide
                "Password": Decoded_data,
                "Timestamp": Timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": total,
                "PartyA": phonenumber, #Need to hide
                "PartyB": settings.BUSINESS_SHORT_CODE, #Need to hide
                "PhoneNumber": phonenumber, #Need to hide
                "CallBackURL": settings.CALL_BACK_URL,
                "AccountReference": customer.email,
                "TransactionDesc": "Ratanga"
            }

            response = requests.post(api_url, json = request, headers=headers)

            return response



        response = lipa_na_mpesa()
        print("The callback url is --------",settings.CALL_BACK_URL)
        print("---------------------------------The response--------------------------------")
        print(response)

        try:
            print("Trying payment")
        
            response_data = response.json()
            print("----------------------------------The response",response_data)
        
            #response_data = json.loads(response.text)
            #response_data = json.loads(response)

            CheckoutRequestID = response_data["CheckoutRequestID"]
            print("Obtained Request ID-->",CheckoutRequestID)

            mpesa_object = MpesaPayment.objects.create(
                customer = customer,
                amount = amount,
                phone_number = mpesa_number,
                checkout_RequestID = CheckoutRequestID,
                status = "P"

            )
            mpesa_object.save()

        except:
            print("Exception Occured")
            

        return response  

def processmpesawithdrawal(customer,mpesa_number,amount):
        total = amount
        raw_phonenumber = mpesa_number
        phonenumber = "254" + raw_phonenumber[-9:]
        print("Stripped phone number",phonenumber)

        #--------------------------------------------------Need to Hide-------------------------------------------------
        consumer_key = settings.CONSUMER_KEY
        consumer_secret = settings.CONSUMER_SECRET
        BusinessShortCode = settings.BUSINESS_SHORT_CODE
        lipa_na_mpesa_passkey = settings.LIPA_NA_MPESA_PASSKEY
        phonenumber = str(phonenumber)

        access_token_api_URL = settings.ACCESS_TOKEN_API_URL
        b2c_proxy_URL = settings.B2C_PROXY_URL

        r = requests.get(access_token_api_URL, auth=HTTPBasicAuth(consumer_key, consumer_secret))
        print("R response",r.json)
        input_access_token = r.json()["access_token"] ########################
        print("Input access token",input_access_token)

        print("Time now:",timezone.now())
        Timestamp = timezone.now().strftime("%Y%m%d%H%M%S")
        print("Time Stamp",Timestamp)
        Data_to_encode = BusinessShortCode + lipa_na_mpesa_passkey + Timestamp
        Encoded_data = base64.b64encode(Data_to_encode.encode())
        Decoded_data = Encoded_data.decode("utf8")
        print("Password",Decoded_data)

        def mpesa_withdrawal():
            access_token = input_access_token
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer %s' % access_token
            }

            payload = {
                "InitiatorName": "NOEL",
                "SecurityCredential": lipa_na_mpesa_passkey,
                "CommandID": "BusinessPayment",
                "Amount": amount,
                "PartyA": BusinessShortCode,
                "PartyB": phonenumber,
                "Remarks": "Withdrawal from zitto wallet",
                "QueueTimeOutURL": "https://zitto.co.ke/b2c/queue",
                "ResultURL": "https://zitto.co.ke/b2c/result",
                "Occassion": "",
            }
            request = {
                "BusinessShortCode": BusinessShortCode ,#Need to hide
                "Password": Decoded_data,
                "Timestamp": Timestamp,
                "TransactionType": "CustomerPayBillOnline",
                "Amount": total,
                "PartyA": phonenumber, #Need to hide
                "PartyB": settings.BUSINESS_SHORT_CODE, #Need to hide
                "PhoneNumber": phonenumber, #Need to hide
                "CallBackURL": settings.CALL_BACK_URL,
                "AccountReference": customer.email,
                "TransactionDesc": "Ratanga"
            }

            response = requests.request("POST", b2c_proxy_URL, headers = headers, data = payload)
            print(response.text.encode('utf8'))

            return response

        response = mpesa_withdrawal()
        print(response)




@csrf_exempt
def checkmpesaspaymentstatus(request):
    if request.method == "GET":
        print("CheckMpesaPayment Status Get Request Failed")
        return render(request,'service/404.html')
    elif request.method == "POST":
        print("----------------------------------------------Mpesa Callback-----------------------------------------------")
        data = json.loads(request.body)
        print(data["Body"])
        CheckoutId = data["Body"]["stkCallback"]["CheckoutRequestID"]
        ResultsCode = data["Body"]["stkCallback"]["ResultCode"]

        mpesa_object = MpesaPayment.objects.get(checkout_RequestID=CheckoutId)


        if ResultsCode == 0:

            try:
                Payed_Amount = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]
                Mpesa_receiptnumber = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][1]["Value"]
                Mpesa_time = str(data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][3]["Value"])
                Mpesa_phonenumber = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][4]["Value"]
                
                Mpesa_date = datetime.strptime(Mpesa_time,"%Y%m%d%H%M%S")
                Mpesa_message = data["Body"]["stkCallback"]["ResultDesc"]
            except:
                Payed_Amount = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][0]["Value"]
                Mpesa_receiptnumber = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][1]["Value"]
                Mpesa_time = str(data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][2]["Value"])
                Mpesa_phonenumber = data["Body"]["stkCallback"]["CallbackMetadata"]["Item"][3]["Value"]
                
                Mpesa_date = datetime.strptime(Mpesa_time,"%Y%m%d%H%M%S")
                Mpesa_message = data["Body"]["stkCallback"]["ResultDesc"]


            
            mpesa_object.reference = Mpesa_receiptnumber
            mpesa_object.phone_number = Mpesa_phonenumber
            mpesa_object.date_completed = Mpesa_date
            mpesa_object.amount = Payed_Amount
            mpesa_object.message = Mpesa_message
            mpesa_object.status = "S"
            mpesa_object.save()
            status = "S"
            

        else:
            Mpesa_message = data["Body"]["stkCallback"]["ResultDesc"]


            mpesa_object.message = Mpesa_message
            mpesa_object.reference = timezone.localtime(timezone.now()).strftime("%Y%m%d%H%M%S")
            mpesa_object.date_completed = timezone.now()
            mpesa_object.status = "F"
            mpesa_object.save()
            status = "F"

        customer = mpesa_object.customer
        amount = mpesa_object.amount
        reference = mpesa_object.reference
        print("Printing reference",reference)
        payment_mode = "M" #Mpesa
        type = "D"
        complete = False

        if reference is None:
            reference = timezone.localtime(timezone.now()).strftime("%Y%m%d%H%M%S")
            print("Reference is None")
        else:
            print("Printing is not None")
        



        details = {"customer":customer,"amount":amount,"input_reference":reference,"status":status,"message":Mpesa_message,"identifier":CheckoutId,"payment_mode":payment_mode,"type":type,"complete":complete}
        transaction(details)

    return redirect(index)