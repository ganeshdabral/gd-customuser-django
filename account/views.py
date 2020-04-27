import hashlib
import random
import datetime
from django.utils import timezone
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser
from .forms import UserForm, LoginForm, UserUpdateForm, UserChangePasswordForm
from django.http import Http404
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.utils.crypto import get_random_string

def user_login(request):
    form = LoginForm(request.POST or None)
    context = {
        "form": form
    }
    if request.method == "POST":
        if form.is_valid():
            email = form.cleaned_data.get("email")
            password = form.cleaned_data.get("password")
            user_obj = authenticate(request, email=email, password=password)
            if user_obj:
                login(request, user_obj)
                return redirect("account:myaccount")
            else:
                messages.error(request,"User email or password incorect")
        else:
            messages.error(request, form.errors)
    return render(request, "account/login.html", context)

def user_listing(request):
    return render(request, "account/list.html", {})

def registration(request):
    '''
    registertion with email verification took help from this source
    https://stackoverflow.com/questions/24935271/django-custom-user-email-account-verification
    '''
    form = UserForm(request.POST or None, request.FILES or None)
    context = {
        "form": form
    }
    if request.method == "POST":
        if form.is_valid():
            user_obj = CustomUser.objects.create_user(
                username=form.cleaned_data.get("username"),
                password=form.cleaned_data.get("password"),
                email = form.cleaned_data.get("email"),
            )
            if request.FILES:
                user_obj.image = request.FILES['image']
            ######################### mail system ####################################
            user_obj.activation_key, user_obj.key_expires = generate_activation_key(user_obj.username)
            user_obj.save()
            sendEmail(user_obj)
            ##################################################################
            context["form"] = UserForm()
            messages.success(request, f'Your account has been created ! You are now able to log in')
        else:
            messages.error(request, form.errors)
    return render(request, "account/register.html", context)

def generate_activation_key(username):
    chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
    secret_key = get_random_string(20, chars)
    activation_key = hashlib.sha256(str(str(secret_key) + str(username)).encode('utf-8')).hexdigest()
    key_expires = timezone.now() + datetime.timedelta(2)
    return (activation_key, key_expires)

def sendEmail(user_object):
    htmly = get_template('account/register_email.html')
    link = "http://"+ str(settings.ALLOWED_HOSTS[0]) + ":" + str(settings.DEFAULT_PORT) + "/account/verification/" + str(user_object.activation_key) + "/"
    d = {'username': user_object.username, 'link': link}
    subject, from_email, to = 'welcome', settings.EMAIL_HOST_USER, user_object.email
    html_content = htmly.render(d)
    msg = EmailMultiAlternatives(subject, html_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()

@login_required(login_url='login/')
def update_user(request):
    user_obj = request.user
    context = {
        "update_form": UserUpdateForm(instance=user_obj),
        "change_password_form": UserChangePasswordForm()
    }

    if request.method == "POST":
        if request.POST.get("is_update") == "user":
            form = UserUpdateForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form_obj = form.save(commit=False)
                if request.FILES:
                    form_obj.image = request.FILES["image"]
                form_obj.save()
                messages.success(request, "successfuly update user info")
            else:
                messages.error(request, form.errors)
                context["update_form"] = form
        elif request.POST.get("is_update") == "password":
            form = UserChangePasswordForm(request.POST)
            if form.is_valid():
                email = user_obj.email
                old_password = form.cleaned_data.get("old_password")
                password = form.cleaned_data.get("password")
                pass_obj = authenticate(request, email=email, password=old_password)
                if pass_obj:
                    user_obj.set_password(password)
                    user_obj.save()
                    messages.success(request, "successfuly change password")
                else:
                    messages.error(request, "current password not match")
            else:
                messages.error(request, form.errors)
                context["change_password_form"] = form
    context["update_form"] = UserUpdateForm(instance=request.user)
    return render(request, "account/update.html", context)

def activation(request, key):
    context = {
        'already_verify': False,
        'expire': False
    }
    try:
        user_obj = CustomUser.objects.get(activation_key=key)
    except CustomUser.DoesNotExist:
        raise Http404
    if user_obj.is_verified == False:
        if timezone.now() < user_obj.key_expires:
            user_obj.is_verified = True
            user_obj.activation_key = None
            user_obj.key_expires = None
            user_obj.save()
        else:
            context['expire'] = True
            context['activation_key'] = key
    else:
        context['already_verify'] = True
    return render(request, "account/verification.html", context)

def new_activation(request, key):
    try:
        user_obj = CustomUser.objects.get(activation_key=key)
    except CustomUser.DoesNotExist:
        raise Http404

    if user_obj.is_verified == False:
        user_obj.activation_key, user_obj.key_expires = generate_activation_key(user_obj.username)
        user_obj.save()
        sendEmail(user_obj)
        return redirect("account:list")
    else:
        messages.success(request, f'Your account has been created ! You are now able to log in')

def logout_view(request):
    logout(request)
    return redirect("login")