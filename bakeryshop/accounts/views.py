from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.http import HttpResponse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from django.contrib.auth.forms import PasswordChangeForm
from django.utils import translation
from django.conf import settings

import logging

from .forms import (
    RegistrationForm, LoginForm, DeleteAccountForm, ConfirmPasswordForm,
    AvatarForm, ProfileEditForm, EmailForm, ChangePasswordForm
)
from .models import Profile

logger = logging.getLogger(__name__)

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            profile, created = Profile.objects.get_or_create(user=user)
            login(request, user)
            messages.success(request, "Регистрация прошла успешно!")
            return redirect('index')  # редирект на главную страницу
    else:
        form = RegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'accounts/login.html', {'error': 'Неверный логин или пароль'})
    else:
        return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def change_password(request):
    if request.method == 'POST' and 'new_password' in request.POST:
        password_form = ChangePasswordForm(request.user, request.POST)

        if password_form.is_valid():
            password_form.save()
            return redirect('confirm_old_password')

    else:
        password_form = ChangePasswordForm(request.user)

    return render(request, 'accounts/change_password.html', {'password_form': password_form})

def confirm_old_password(request):
    if request.method == 'POST':
        confirm_form = ConfirmPasswordForm(request.POST)

        if confirm_form.is_valid():
            current_password = confirm_form.cleaned_data['password']

            if request.user.check_password(current_password):
                messages.success(request, "Пароль успешно изменён!")
                return redirect('password_change_done')
            else:
                messages.error(request, "Неверный старый пароль.")

    else:
        confirm_form = ConfirmPasswordForm()

    return render(request, 'accounts/confirm_old_password.html', {'confirm_form': confirm_form})

def password_change_done(request):
    return render(request, 'accounts/password_change_done.html')


def delete_account(request):
    if not request.user.is_authenticated:
        return redirect('login')

    if request.method == 'POST':
        form = ConfirmPasswordForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = authenticate(username=request.user.username, password=password)

            if user is not None:
                request.user.delete()
                messages.success(request, "Ваш аккаунт был успешно удалён.")
                return redirect('index')
            else:
                messages.error(request, 'Неверный пароль. Попробуйте снова.')
    else:
        form = ConfirmPasswordForm()

    return render(request, 'accounts/delete_account.html', {'form': form})

def confirm_registration(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_user_model().objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Ваш аккаунт подтверждён! Вы можете войти.')
        return redirect('login')
    else:
        messages.error(request, 'Ссылка для подтверждения устарела или неверна.')
        return redirect('register')

def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлён.')
            return redirect('edit_profile')
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'accounts/edit_profile.html', {'form': form})

def change_avatar(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = AvatarForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Аватар успешно обновлён.')
            return redirect('edit_profile')
    else:
        form = AvatarForm(instance=profile)
    return render(request, 'accounts/change_avatar.html', {'form': form})

def send_test_email(request):
    if request.method == 'POST':
        form = EmailForm(request.POST)
        if form.is_valid():
            subject = 'Тестовое письмо от Django'
            message = 'Это тестовое письмо, отправленное из Django!'
            from_email = 'your_email@gmail.com'
            recipient_email = form.cleaned_data['email']
            try:
                send_mail(subject, message, from_email, [recipient_email])
                return HttpResponse(f'Тестовое письмо успешно отправлено на {recipient_email}')
            except Exception as e:
                logger.error(f"Ошибка при отправке письма: {str(e)}")
                messages.error(request, f'Ошибка при отправке письма: {str(e)}')
                return redirect('send_test_email')
    else:
        form = EmailForm()
    return render(request, 'accounts/send-test-email.html', {'form': form})
