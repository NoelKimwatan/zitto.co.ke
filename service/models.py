from django.db import models
from django.contrib.auth.models import User
from django.db.models.fields.related import OneToOneField
from requests.api import options

class Customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True,blank=True)
    manager_user = models.BooleanField(default=False)
    name = models.CharField(max_length=100,null=True)
    email = models.CharField(max_length=100,null=True)
    phone_number = models.IntegerField(null=True,blank=True)
    managed = models.BooleanField(default=False)

    def __str__(self):
        return self.email

class Shipment(models.Model):
    status_options = [
        ("CR","Created"),
        ("IT","In transit"),
        ("C","Complete"),
    ]
    name = models.CharField(max_length=100,null=True,blank=True)
    description = models.CharField(max_length=100,null=True,blank=True)
    batch_number = models.CharField(max_length=200,null=True,blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True,blank=True)
    status = models.CharField(max_length=2,choices=status_options,default="CR",null=False,blank=False)

    def __str__ (self):
        display = str(str(self.batch_number) + " -- " + self.name )
        return display

class GuestOrder(models.Model):
    name = models.CharField(max_length=100,null=False,blank=False)
    link = models.URLField(max_length=1000,null=False,blank=False)
    description = models.CharField(max_length=200,null=True,blank=True)
    identifier = models.CharField(max_length=300,null=True,blank=True)

    #-------------------User data-------------------
    first_name = models.CharField(max_length=200,null=True,blank=True)
    last_name = models.CharField(max_length=200,null=True,blank=True)
    phone_number = models.IntegerField(null=True,blank=True)
    email = models.CharField(max_length=100,null=True)


    def __str__(self):
        return self.name

class Order(models.Model):
    status_options = [
        ("I","Incomplete"),
        ("IR","In Review"),
        ("PP","Purchase Payment Pending"),
        ("TP"," To purchase"),
        ("P","Purchased"),
        ("R","Ready to Ship"),
        ("IT","In Transit"),
        ("LD","Landed. Pending delivery details"),
        ("DDE","Delivery details entered"),
        ("SPP","Shipping Payment Pending"),
        ("RD","Ready for Delivery"),
        ("D","Delivered"),
        ("RJ","Rejected")
    ]
    name = models.CharField(max_length=100,null=False,blank=False)
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE)
    date_ordered = models.DateTimeField(null=True,blank=True)
    date_completed = models.DateTimeField(null=True,blank=True)
    tracking_number = models.CharField(max_length=250,null=True,blank=True,unique=True)
    status = models.CharField(max_length=3, choices=status_options)


    link = models.URLField(max_length=1000,null=False,blank=False)
    description = models.CharField(max_length=200,null=True,blank=True)

    amount_in_purchase_currency = models.FloatField(blank=True,null=True)
    exchage_rate = models.FloatField(blank=True,null=True)
    amount = models.IntegerField(blank=True,null=True)

    estimated_weight = models.FloatField(blank=True,null=True)
    actual_weight = models.FloatField(blank=True,null=True)

    price_per_kg = models.FloatField(blank=True,null=True)

    shippingEstimate = models.IntegerField(blank=True,null=True)
    shipping = models.IntegerField(blank=True,null=True)

    delivery_fee = models.IntegerField(blank=True,null=True)

    shipment = models.ForeignKey(Shipment,on_delete=models.SET_NULL,null=True,blank=True)
    in_shipment = models.BooleanField(default=False)
    feedback_provided = models.BooleanField(default=False)


    def __str__(self):
        return self.name

    @property 
    def get_order_total(self):
        try:
            total = self.amount + self.shipping + self.delivery_fee
        except:
            total = "Error"
        return total

    @property 
    def get_order_shipping_and_delivery(self):
        try:
            total = self.shipping + self.delivery_fee
        except:
            total = "Error"
        return total

    @property 
    def get_order_estimated_total(self):
        try:
            total = self.amount + self.shippingEstimate
            return total
        except:
            total = "Erorr"

class OrderTimeline(models.Model):

    status_options = [
        ("SRC","Ship request created"),
        ("SRP","Ship request processed"),
        ("PPC","Purchase payment completed"),
        ("IP","Item purchased"),
        ("ETW","Enroute to warehouse"),
        ("RAW","Received at warehouse"),
        ("BPFOS","Being prepared for overseas shipping"),
        ("DFW","Departed from warehouse"),
        ("AAUSF","Arrived at US sort facility"),
        ("AADSF","Arrived at Dubai sort facility"),
        ("DTDA","Dispatched to destination airport"),
        ("AADA","Arrived at destination airport"),
        ("UIC","Undergoing import clearance"),
        ("PBPFD","Package being prepared for delivery"),
        ("DDE","Delivery details entered"),
        ("SPP","Shipping payment pending"),
        ("SPC","Shipping payment complete"),
        ("RFD","Ready for delivery"),
        ("OFD","Out for delivery"),
        ("D","Delivered"),
        ("RJ","Rejected")
    ]

    status = models.CharField(choices=status_options,max_length=6)
    order = models.OneToOneField(Order,on_delete=models.CASCADE,null=True,blank=True)

    ship_request_created = models.DateTimeField(auto_now_add=True)
    ship_request_processed = models.DateTimeField(null=True,blank=True)
    purchase_payment_completed = models.DateTimeField(null=True,blank=True)
    item_purchased = models.DateTimeField(null=True,blank=True)
    enroute_to_warehouse = models.DateTimeField(null=True,blank=True)
    received_at_warehouse = models.DateTimeField(null=True,blank=True)
    being_prepared_for_overseas_shipping = models.DateTimeField(null=True,blank=True)
    departed_from_warehouse = models.DateTimeField(null=True,blank=True)
    arrived_at_us_sort_facility = models.DateTimeField(null=True,blank=True)
    arrived_at_dubai_sort_facility = models.DateTimeField(null=True,blank=True)
    dispatched_to_destination_airport = models.DateTimeField(null=True,blank=True)
    arrived_at_destination_airport = models.DateTimeField(null=True,blank=True)
    undergoing_import_clearance = models.DateTimeField(null=True,blank=True)
    package_being_prepared_for_delivery = models.DateTimeField(null=True,blank=True)
    delivery_details_entered = models.DateTimeField(null=True,blank=True)
    shipping_price_reviewed = models.DateTimeField(null=True,blank=True) #Shipping payment pending
    shipping_payment_complete = models.DateTimeField(null=True,blank=True)
    ready_for_delivery = models.DateTimeField(null=True,blank=True)
    out_for_delivery = models.DateTimeField(null=True,blank=True)
    delivered = models.DateTimeField(null=True,blank=True)


class RejectPaymentRequest(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE)
    reason = models.CharField(max_length=1000,blank=True,null=True)


class DeliveryDetails(models.Model):
    order = models.OneToOneField(Order,on_delete=models.CASCADE,null=True,blank=True)
    county = models.CharField(max_length=100,null=True,blank=True)
    town_location = models.CharField(max_length=100,null=True,blank=True)
    description = models.CharField(max_length=1000,null=True,blank=True)

class BatchTimeline(models.Model):

    status_options = [
        ("CR","Created"),
        ("DTDA","Dispatched to destination airport"),
        ("AADA","Arrived at destination airport"),
        ("UIC","Undergoing import clearance"),
        ("C","Complete"),
    ]

    status = models.CharField(choices=status_options,max_length=6,default="CR")
    shipment = models.OneToOneField(Shipment,on_delete=models.CASCADE,null=True,blank=True)

    time_created = models.DateTimeField(auto_now_add=True)
    dispatched_to_destination_airport = models.DateTimeField(null=True,blank=True)
    arrived_at_destination_airport = models.DateTimeField(null=True,blank=True)
    undergoing_import_clearance = models.DateTimeField(null=True,blank=True)
    complete = models.DateTimeField(null=True,blank=True)


class OrderItem(models.Model):
    status_options = [
        ("I","Incomplete"),
        ("IR","In Review"),
        ("PP","Payment Pending"),
        ("R","Ready to Ship"),
        ("IT","In Transit"),
        ("RD","Ready for Delivery"),
        ("D","Delivered"),
    ]
    order = models.ForeignKey(Order,on_delete=models.CASCADE)
    shipment = models.ForeignKey(Shipment,on_delete=models.SET_NULL,null=True,blank=True)
    link = models.URLField(max_length=1000)
    description = models.CharField(max_length=200)
    date_added = models.DateTimeField(auto_now_add = True)
    amount = models.IntegerField(blank=True,null=True)
    tax = models.IntegerField(blank=True,null=True)
    shipping = models.IntegerField(blank=True,null=True)
    in_shipment = models.BooleanField(default=False)
    status = models.CharField(max_length=2, choices=status_options)


    def __str__(self):
        return self.description

    @property
    def get_total(self):
        if self.tax != None and self.shipping != None and self.amount != None:
            total = int(self.tax) + int(self.shipping) + int(self.amount)
            return total
        elif self.tax == None and self.shipping != None and self.amount != None:
            total = int(self.shipping) + int(self.amount)
            return total
        elif self.tax != None and self.shipping == None and self.amount != None:
            total = int(self.tax) + int(self.amount)
            return total
        elif self.tax != None and self.shipping != None and self.amount == None:
            total = int(self.tax) + int(self.shipping)
            return total
        else:
            return 0


class Wallet(models.Model):
    customer =models.OneToOneField(Customer,on_delete=models.CASCADE,null=False,blank=False)
    balance = models.IntegerField(default=0)

class Transactions(models.Model):
    transaction_options =[
        ("D","Deposit"),
        ("W","Withdraw")
    ]
    payment_mode =[
        ("M","Mpesa"),
        ("C","Card"),
        ("I","Internal")
    ]
    status_options =[
        ("P","Processing"),
        ("S","Successful"),
        ("F","Failed")
    ]

    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,null=True,blank=True)
    amount = models.IntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1,choices=status_options,null=False,blank=True)
    type = models.CharField(max_length=1,choices=transaction_options,null=False,blank=True)
    reference = models.CharField(max_length=300,null=True,blank=True)
    payment_mode = models.CharField(max_length=1,choices=payment_mode,null=True,blank=True)
    message = models.CharField(max_length=100,null=True,blank=True)
    identifier = models.CharField(max_length=300,null=True,blank=True)
    complete = models.BooleanField(default=False)

class MpesaPayment(models.Model):
    status_options =[
        ("P","Processing"),
        ("S","Successful"),
        ("F","Failed")
    ]
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,null=True,blank=True)
    amount = models.BigIntegerField(blank=True,null=True)
    phone_number = models.BigIntegerField(null=True,blank=True)
    checkout_RequestID = models.CharField(max_length=100,blank=True,null=True)
    reference = models.CharField(max_length=100,blank=True,null=True)
    message = models.CharField(max_length=100,blank=True,null=True)
    date_initiated = models.DateTimeField(auto_now_add=True)
    date_completed = models.DateTimeField(null=True)
    status = models.CharField(max_length=2,choices=status_options,null=True,blank=True)

class Feedback(models.Model):

    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,null=True,blank=True)
    order = models.ForeignKey(Order,on_delete=models.CASCADE,null=True,blank=True)
    feedback = models.CharField(max_length=500,null=True,blank=True)