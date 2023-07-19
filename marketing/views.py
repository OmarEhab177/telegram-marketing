from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

from config.celery import app
from .models import TelegramAccount, Channel, Member
from .tasks import (
    add_telegram_account,
    verify_telegram_account,
    task_logout,
    get_all_channels,
    get_channels_participants,
    task_create_channel,
    task_invite_members,
    send_message_to_channel,
    task_request_to_join_channel
)

def setup(request):
    if request.method == "POST":
        # retreive data from form
        user_name = request.POST.get("user_name")
        phone_number = request.POST.get("phone_number")
        api_hash = request.POST.get("api_hash")
        api_id = request.POST.get("api_id")

        # Logout the currently authenticated user, if any
        if request.user.is_authenticated:
            tele_acc = TelegramAccount.objects.filter(username=request.user.username).first()
            if  tele_acc:

                result = task_logout.apply_async(
                    args=[
                        tele_acc.phone_number,
                        tele_acc.api_hash,
                        tele_acc.api_id
                    ]
                )
                task_result = app.AsyncResult(result.task_id).get()
                if task_result:
                    logout(request)

        # Save the data to the database
        tele_acc = TelegramAccount.objects.get_or_create(
            username=user_name,
            phone_number=phone_number,
            api_id=api_id,
            api_hash=api_hash,
        )
        tele_acc = tele_acc[0]
        # Call the Celery task asynchronously
        result = add_telegram_account.apply_async(args=[phone_number, api_hash, api_id])
        task_result = app.AsyncResult(result.task_id).get()
        # Wait for the task result and check if it's True
        if task_result == True:
            user = authenticate(request, username=user_name, password=tele_acc.password)
            if user:
                login(request, user)
            return render(
                request,
                "marketing/setup.html",
                {"message": "Account added successfully"},
            )
        else:
            tele_acc.phone_code_hash = task_result
            tele_acc.save()
            verification_link = reverse("marketing:verification")
            verification_link += "?phone_number=" + phone_number
            return redirect(verification_link)

    return render(request, "marketing/setup.html")


def verification(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        verification_code = request.POST.get("verification_code")
        password = request.POST.get("password")

        phone_number = phone_number if phone_number[0] == "+" else"+" + phone_number.strip()

        # Retrieve the account from the database based on the phone number
        telegram_account = TelegramAccount.objects.filter(phone_number=phone_number).first()
        if telegram_account:
            # Call the Celery task asynchronously
            result = verify_telegram_account.apply_async(
                args=[phone_number, verification_code, telegram_account.api_hash, telegram_account.api_id, telegram_account.phone_code_hash, password]
            )
            task_result = app.AsyncResult(result.task_id).get()
            if task_result:
                if not telegram_account.password:
                    telegram_account.set_password(password)
                    telegram_account.save()
                user = authenticate(request, username=telegram_account.username, password=password)
                if user:
                    login(request, user)
                return redirect("marketing:dashboard")
            else:
                # TODO: return message show that the verification code or password is wrong
                verification_link = reverse("marketing:verification")
                verification_link += "?phone_number=" + phone_number
                return redirect(verification_link)
        else:
            # TODO: return message show that the account is not found or not added
            return redirect("marketing:setup")

    phone_number = request.GET.get("phone_number")
    return render(request, "marketing/verification.html", {"phone_number": phone_number})


@login_required(login_url="marketing:setup")  # Redirect to setup page if the user is not authenticated
def dashboard(request):
    # Retrieve the list of Telegram accounts from the database
    accounts = TelegramAccount.objects.all()
    accounts_paginator = Paginator(accounts, 10)  # Display 10 accounts per page
    accounts_page_number = request.GET.get("acc_page")
    accounts = accounts_paginator.get_page(accounts_page_number)

    # Retrieve the list of channels from the database
    current_user = TelegramAccount.objects.filter(username=request.user.username).first()
    current_user_channels = []
    if current_user:
        current_user_channels = current_user.channels.all()
        current_user_channels_paginator = Paginator(current_user_channels, 10)
        current_user_channels_page_number = request.GET.get("user_channels_page")
        current_user_channels = current_user_channels_paginator.get_page(current_user_channels_page_number)

    # Retrieve the list of all channels from the database
    channels = Channel.objects.exclude(telegram_account__username=request.user.username).all()
    channel_paginator = Paginator(channels, 10)  # Display 10 channels per page
    channel_page_number = request.GET.get("channels_page")
    channels = channel_paginator.get_page(channel_page_number)

    context = {
        "accounts": accounts,
        "channels": channels,
        "current_user_channels": current_user_channels,
    }

    return render(request, "marketing/dashboard.html", context)

def logout_view(request):
    if request.method == "POST":
        tele_acc = TelegramAccount.objects.filter(username=request.user.username).first()
        if  tele_acc:

            result = task_logout.apply_async(
                args=[
                    tele_acc.phone_number,
                    tele_acc.api_hash,
                    tele_acc.api_id
                ]
            )
            task_result = app.AsyncResult(result.task_id).get()
            if task_result:
                logout(request)
                return redirect("marketing:setup")
    else:
        return HttpResponse("Method not allowed")


def get_channels(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        telegram_account = TelegramAccount.objects.filter(phone_number=phone_number).first()
        if telegram_account:
            result = get_all_channels.apply_async(
                args=[
                    telegram_account.phone_number,
                    telegram_account.api_hash,
                    telegram_account.api_id,
                ]
            )
            task_result = app.AsyncResult(result.task_id).get()
            if task_result:
                channels = task_result
                for channel in channels:
                    channel_exist = Channel.objects.filter(channel_id=channel["id"]).first()
                    if not channel_exist:
                        Channel.objects.create(
                            channel_id=channel["id"],
                            title=channel["title"],
                            name=channel["name"],
                            is_channel=channel["is_channel"],
                            is_group=channel["is_group"],
                            telegram_account=telegram_account,
                        )
            elif task_result == []:
                # TODO implement message no channel found
                print("no channel found")
                return redirect("marketing:dashboard")
    return redirect("marketing:dashboard")


def get_members(request):
    if request.method == "POST":
        channel_id = request.POST.get("channel_id")
        channel = Channel.objects.filter(channel_id=channel_id).first()
        telegram_account = TelegramAccount.objects.filter(username=request.user.username).first()

        if not channel:
            chanel_result = get_channel_info.apply_async(
                args=[
                    telegram_account.phone_number,
                    telegram_account.api_hash,
                    telegram_account.api_id,
                    channel_id,
                ]
            )
            channel_task_result = app.AsyncResult(chanel_result.task_id).get()
            if channel_task_result:
                channel = Channel.objects.create(
                    channel_id=channel_task_result["id"],
                    title=channel_task_result["title"],
                    name=channel_task_result["name"],
                    is_channel=channel_task_result["is_channel"],
                    is_group=channel_task_result["is_group"],
                    telegram_account=telegram_account,
                )


        result = get_channels_participants.apply_async(
            args=[
                telegram_account.phone_number,
                telegram_account.api_hash,
                telegram_account.api_id,
                channel_id,
            ]
        )
        task_result = app.AsyncResult(result.task_id).get()
        if task_result:
            members = task_result
            for member in members:
                member_exist = Member.objects.filter(member_id=member["id"]).first()
                if not member_exist:
                    member = Member.objects.create(
                        member_id=member["id"],
                        username=member["username"],
                        first_name=member["first_name"],
                        last_name=member["last_name"],
                        phone=member["phone"],
                    )
                    if channel:
                        member.channels.add(channel)
                else:
                    if channel:
                        member_exist.channels.add(channel)

        elif task_result == []:
            # TODO implement message no member found
            print("no member found")
        return redirect("marketing:dashboard")

    # TODO message "method not allowed"
    redirect("marketing:dashboard")


def create_channel(request):
    if request.method == "POST":
        phone_number = request.POST.get("phone_number")
        channel_name = request.POST.get('channel_name')
        phone_number = phone_number if phone_number[0] == "+" else"+" + phone_number.strip()
        tele_acc = TelegramAccount.objects.filter(phone_number=phone_number).first()
        if not tele_acc:
            # TODO message "account with this phone number not found"
            return redirect("marketing:dashboard")

        result = task_create_channel.apply_async(
            args=[
                phone_number,
                tele_acc.api_hash,
                tele_acc.api_id,
                channel_name,
            ]
        )
        task_result = app.AsyncResult(result.task_id).get()
        if task_result:
            channel = Channel.objects.create(
                channel_id=task_result["id"],
                title=channel_name,
                name=channel_name,
                is_channel=True,
                telegram_account=tele_acc,
            )
            # TODO: return message show that the channel is created successfully
            return redirect("marketing:dashboard")
        else:
            # TODO: return message show that the channel is not created
            return redirect("marketing:dashboard")

def invite_members_to_channel(request):
    if request.method == "POST":
        channel_id = request.POST.get("channel_id")
        telegram_account = TelegramAccount.objects.filter(username=request.user.username).first()
        if int(channel_id) not in telegram_account.channels.all().values_list("channel_id", flat=True):
            # TODO: message that the logged in user in not the owner of the channel
            return redirect("marketing:dashboard")
        # get all members ids
        members_ids = Member.objects.all().values_list("member_id", flat=True)
        members_ids = list(members_ids)
        result = task_invite_members.apply_async(
            args=[
                telegram_account.phone_number,
                telegram_account.api_hash,
                telegram_account.api_id,
                channel_id,
                members_ids
            ]
        )
        task_result = app.AsyncResult(result.task_id).get()

        if task_result:
            # sucess message that members are invited
            return redirect("marketing:dashboard")
        return redirect("marketing:dashboard")


def send_message(request, channel_id):
    if request.method == "POST":
        message = request.POST.get('message')
        telegram_account = Channel.objects.get(channel_id=channel_id).telegram_account
        result = send_message_to_channel.apply_async(
            args=[
                telegram_account.phone_number,
                telegram_account.api_hash,
                telegram_account.api_id,
                channel_id,
                message,
            ]
        )
        task_result = app.AsyncResult(result.task_id).get()
        if task_result:
            # TODO: message that the message is sent successfully
            return redirect("marketing:dashboard")
        else:
            # TODO: message that the message is not sent
            return redirect("marketing:send-message", channel_id=channel_id)

    return render(request, 'marketing/send-message.html', {'channel_id': channel_id})

def request_to_join_channel(request):
    # Not implemented yet
    if request.method == "POST":
        channel_id = request.POST.get("channel_id")
        telegram_account = TelegramAccount.objects.filter(username=request.user.username).first()
        task = task_request_to_join_channel.apply_async(
            args=[
                telegram_account.phone_number,
                telegram_account.api_hash,
                telegram_account.api_id,
                channel_id,
            ]
        )
        task_result = app.AsyncResult(task.task_id).get()
        if task_result:
            telegram_account.channels.add(Channel.objects.get(channel_id=channel_id))
            # TODO: message that the request is sent successfully
            return redirect("marketing:dashboard")
        else:
            # TODO: message that the request is not sent
            return redirect("marketing:dashboard")
