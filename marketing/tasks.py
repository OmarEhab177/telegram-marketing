from celery import shared_task
from telethon.sync import TelegramClient
from telethon.errors import ChatAdminRequiredError, SessionPasswordNeededError
from telethon.tl.types import InputPeerChannel
from telethon.tl.functions.channels import CreateChannelRequest

@shared_task
def get_phone_code_hash(phone_number, api_hash, api_id):
    client = TelegramClient(phone_number, api_id, api_hash)
    client.connect()
    sent_code = client.send_code_request(phone_number)
    phone_code_hash = sent_code.phone_code_hash
    return client, phone_code_hash


@shared_task
def add_telegram_account(phone_number, api_hash, api_id):
    client, phone_code_hash = get_phone_code_hash(phone_number, api_hash, api_id)
    if not client.is_user_authorized():
        return phone_code_hash
    else:
        return True

@shared_task
def verify_telegram_account(phone_number, verification_code, api_hash, api_id, phone_code_hash, password):
    client = TelegramClient(phone_number, api_id, api_hash)
    client.connect()
    try:
        client.sign_in(phone_number, code=verification_code, phone_code_hash=phone_code_hash)
    except SessionPasswordNeededError:
        client.sign_in(phone_number, password=password)
        return True
    except:
        return False


@shared_task
def login_telegram_account(phone_number, password, api_hash, api_id):
    """ Need to be implemented"""
    # client, phone_code_hash = get_phone_code_hash(phone_number, api_hash, api_id)
    client = TelegramClient(phone_number, api_id, api_hash)
    client.connect()
    client.sign_in(phone_number, password)
    return True
    # try:
    #     client.sign_in(phone_number, password=password)
    #     return True
    # except:
    #     return False

@shared_task
def get_all_channels(phone_number, api_hash, api_id):
    client = TelegramClient(phone_number, api_id, api_hash)
    client.connect()
    channels = []
    dialogs = client.get_dialogs()
    for dialog in dialogs:
        if dialog.is_channel or dialog.is_group:
            channels.append({
                'id': dialog.id,
                'title': dialog.title,
                'name': dialog.name,
                'is_channel': dialog.is_channel,
                'is_group': dialog.is_group
            })
    return channels

@shared_task
def get_channels_participants(phone_number, api_hash, api_id, channel_id):
    client = TelegramClient(phone_number, api_id, api_hash)
    client.connect()
    participants_data = []
    try:
        participants = client.get_participants(int(channel_id))
        for participant in participants:
            try:
                participant_data = {
                    'id': participant.id,
                    'first_name': participant.first_name,
                    'last_name': participant.last_name,
                    'username': participant.username,
                    'phone': participant.phone,
                    'access_hash': participant.access_hash,
                }
                participants_data.append(participant_data)
            except:
                pass
    except ChatAdminRequiredError:
        participants_data = []
    return participants_data


@shared_task
def task_create_channel(phone_number, api_hash, api_id, channel_name):
    client = TelegramClient(phone_number, api_id, api_hash)
    client.connect()
    # try:
    result = client(CreateChannelRequest(channel_name, channel_name, megagroup=False))
    print(result.__dict__)
    channel = {
        'id': result.chats[0].id,
    }
    return channel
    # except:
    #     return False
