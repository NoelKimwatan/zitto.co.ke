from django.contrib import admin
from .models import *



class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user","name","email","phone_number")
admin.site.register(Customer,CustomerAdmin)

class OrderAdmin(admin.ModelAdmin):
    list_display = ("id","customer","date_ordered","date_completed","status")
admin.site.register(Order,OrderAdmin)

class WalletAdmin(admin.ModelAdmin):
    list_display = ("customer","balance")
admin.site.register(Wallet,WalletAdmin)

class TransactionsAdmin(admin.ModelAdmin):
    list_display = ("customer","status","amount","date","type")
admin.site.register(Transactions,TransactionsAdmin)

class ShipmentAdmin(admin.ModelAdmin):
    list_display = ("name","description","batch_number","date_created","status")
admin.site.register(Shipment,ShipmentAdmin)

class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("customer","order","feedback")
admin.site.register(Feedback,FeedbackAdmin)

class MpesaPaymentAdmin(admin.ModelAdmin):
    list_display = ("customer","amount","phone_number","status","checkout_RequestID","reference","message","date_initiated")
admin.site.register(MpesaPayment,MpesaPaymentAdmin)

class OrderTimelineAdmin(admin.ModelAdmin):
    list_display = ("order","status","ship_request_created")
admin.site.register(OrderTimeline,OrderTimelineAdmin)

class BatchTimelineAdmin(admin.ModelAdmin):
    list_display = ("shipment","status")
admin.site.register(BatchTimeline,BatchTimelineAdmin)

class DeliveryDetailsAdmin(admin.ModelAdmin):
    list_display = ("order","county","town_location")
admin.site.register(DeliveryDetails,DeliveryDetailsAdmin)

class RejectPaymentRequestAdmin(admin.ModelAdmin):
    list_display = ("order","reason")
admin.site.register(RejectPaymentRequest,RejectPaymentRequestAdmin)

class GuestOrderAdmin(admin.ModelAdmin):
    list_display = ("id","name","identifier","description","link")
admin.site.register(GuestOrder,GuestOrderAdmin)





