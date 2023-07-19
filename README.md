# Telegram Marketing Automation

This project is a Telegram Marketing Automation tool that allows users to manage their Telegram accounts, channels, and members. It utilizes Django and Celery for background task processing to perform actions asynchronously.

## Features

- User authentication and account setup
- Adding and verifying Telegram accounts
- Getting a list of channels and their participants
- Creating channels
- Inviting members to channels
- Sending messages to channels
- Requesting to join channels

## Setup

1. Install the required dependencies by running:

```
pip install -r requirements.txt
```

2. Setup the Django database:

```
python manage.py migrate
```

3. Create a superuser to access the Django admin interface:

```
python manage.py createsuperuser
```

4. Start the Celery worker to handle asynchronous tasks:

```
celery -A config worker --loglevel=info
```

5. Start the Django development server:

```
python manage.py runserver
```

6. Access the application in your web browser at http://127.0.0.1:8000/

## Usage

1. Register and login to the application.

2. Navigate to the "Setup" page and add a new Telegram account by providing the necessary details.

3. Once the account is added, you will receive a verification code via Telegram. Enter the verification code and set a password for the account.

4. After successful verification, you will be redirected to the "Dashboard" page, where you can see a list of your Telegram accounts and channels.

5. To create a new channel, click on the "Create Channel" button and enter the channel name.

6. To invite members to a channel, first, you need to get a list of all members by clicking on the "Get Members" button for a specific channel. Then, click on the "Invite Members" button and select the members you want to invite.

7. To send a message to a channel, click on the "Send Message" button for the desired channel and enter the message content.

8. To request to join a channel, click on the "Join Channel" button for the desired channel.

## Important Notes

- This project assumes you have already set up a Celery broker (e.g., RabbitMQ, Redis) and configured the Celery settings in the Django project.

- Make sure to handle the security and privacy aspects of using a Telegram API in a real-world scenario, such as securely storing API credentials and handling user data.

- For the sake of simplicity, this README only provides an overview of the features and setup process. You may need to further customize and improve the application according to your specific requirements and use cases.

## Conclusion

This Telegram Marketing Automation tool can be a helpful utility for managing Telegram accounts and channels, automating various tasks, and reaching out to the audience efficiently. Happy marketing!
