#--------Sending emails---------
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from .models import *
from eb_sqs_worker.decorators import task
from time import sleep


@task
def sleepy(**kwargs):
    items = dict(kwargs.items())
    duration = items["duration"]

    for i in range(duration):
        print("The number is:",i)

    sleep(duration)
    return "Hope it worked"

@task
def send_signup_email_function(**kwargs):
    items = dict(kwargs.items())

    print("Entered email sending function")
    customer_name = items["name"]
    customer_email = items["email"]
    print("Context placed")

    context = {"customer_name":customer_name,"customer_email":customer_email}

    html_message = render_to_string('service/email_templates/signup_email_template.html',context)

    print("Render to string complete")
    plain_message = strip_tags(html_message)
    print("Plain message complete")
    subject = 'Welcome to Zitto'
    from_email = 'info@zitto.co.ke'


    print("About to send email")
    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            [customer_email,],
            fail_silently = False,
            auth_user='info@zitto.co.ke',
            html_message=html_message,
        )
        print("Email sent successfully")
    except:
        print("Email sent failed")
        return None



@task
def send_managed_user_account_created_email_function(**kwargs):
    items = dict(kwargs.items())

    print("Entered email sending function")
    customer_name = items["name"]
    customer_email = items["email"]
    customer_password = items["password"]
    print("Context placed")

    context = {"customer_name":customer_name,"customer_email":customer_email,"customer_password":customer_password}

    html_message = render_to_string('service/email_templates/managed_user_created_email_template.html',context)
    print("Render to string complete")
    plain_message = strip_tags(html_message)
    print("Plain message complete")
    subject = 'Welcome to Zitto'
    from_email = 'info@zitto.co.ke'


    print("About to send email")
    try:
        send_mail(
            subject,
            plain_message,
            from_email,
            [customer_email,],
            fail_silently = False,
            auth_user='info@zitto.co.ke',
            html_message=html_message,
        )
        print("Email sent successfully")
    except:
        print("Email sent failed")



