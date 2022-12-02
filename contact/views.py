from django.shortcuts import render
from .models import User, Conversation, ConversationMessage, Notification
# Create your views here.
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from . import telegrambot


@login_required
def home(request):
    return render(request, 'notifications.html')


@login_required
def profile(request, user_id):

    cur_user = User.objects.get(id=user_id)

    Notification.objects.filter(created_by=cur_user).filter(is_read=False).filter(notification_type='new_join').update(is_read=True)

    return render(request, 'profile.html', {"cur_user": cur_user})



@login_required
def conversation(request, user_id):
    
    admin = User.objects.filter(is_superuser=True)[0]
    cur_user = User.objects.get(id=user_id)

    Notification.objects.filter(created_by=cur_user).filter(is_read=False).filter(notification_type='message').update(is_read=True)

    conversations = Conversation.objects.filter(users__in=[admin.id])
    conversations = conversations.filter(users__in=[user_id])

    if conversations.count() == 1:
        conversation = conversations[0]
    else:
        recipient = User.objects.get(id=user_id)
        conversation = Conversation.objects.create()
        conversation.users.add(admin)
        conversation.users.add(recipient)
        conversation.save()

    return render(request, 'conversation.html', {'conversation': conversation, 'cur_user': cur_user})



@login_required
def add_message(request):
    if request.is_ajax():

        msg = request.POST.get('msg')
        conversation_id = int(request.POST.get('conversation_id'))
        recipient = request.POST.get('recipient')

        conversation = Conversation.objects.get(id=conversation_id)
        admin = User.objects.filter(is_superuser=True)[0]
     

        message = ConversationMessage.objects.create(conversation=conversation, content=msg, created_by=admin)

      
        telegrambot.send_message(message=message.content, user_id=recipient)

        res = {
                'user': admin.first_name,
                'created_at': 'Now',
                'context': message.content
            }
        return JsonResponse({'data': res})

    return JsonResponse({})


@login_required
def notifications(request):

    return render(request, 'notifications.html')


@login_required
def filter_users(request):

    return render(request, 'filter_users.html')

def request_new_info(request):

    if request.is_ajax():

        username = request.POST.get('username')

        telegrambot.request_new_info(username)

        
        res = {
                'success': True           
              }

        
        return JsonResponse({'data': res})

    return JsonResponse({})



def search_results(request):

    if request.is_ajax():

        game = request.POST.get('game')

        results = User.objects.filter(Q(first_name__contains=game) | Q(last_name__contains=game)).exclude(is_superuser=True)[:20]

        if len(game) > 0:
            data = []
            for result in results:
                item = {
                    'id': result.id,
                    'first_name': result.first_name,
                    'last_name': result.last_name
                }
                data.append(item)
            res = data
        else:
            results = User.objects.all().exclude(is_superuser=True).order_by('first_name')
            data = []
            for result in results:
                item = {
                    'id': result.id,
                    'first_name': result.first_name,
                    'last_name': result.last_name
                }
                data.append(item)
            res = data
        return JsonResponse({'data': res})

    return JsonResponse({})



def group_filter(request):

    if request.is_ajax():

        keyword = request.POST.get('keyword')

        if keyword in ['International', 'Russian', 'CIS']:
            users = User.objects.filter(location=keyword).exclude(is_superuser=True)
        else:
            users = User.objects.filter(course=keyword).exclude(is_superuser=True)


        data = []

        for user in users:
            item = {
                    'id': user.id,
                    'first_name': user.first_name,
                    'last_name': user.last_name
                }
            data.append(item)
     
        return JsonResponse({'data': data})

    return JsonResponse({})



def multisend_message(request):

    if request.is_ajax():
        msg = request.POST.get('msg')
        recipients = request.POST.getlist('recipients[]')

        admin = User.objects.filter(is_superuser=True)[0]


        for id in recipients:

            recipient = User.objects.get(id=id)
        
            conversations = Conversation.objects.filter(users__in=[admin.id])
            conversations = conversations.filter(users__in=[id])

            if conversations.count() == 1:
                conversation = conversations[0]
            else:
                recipient = User.objects.get(id=id)
                conversation = Conversation.objects.create()
                conversation.users.add(admin)
                conversation.users.add(recipient)
                conversation.save()

        
            message = ConversationMessage.objects.create(conversation=conversation, content=msg, created_by=admin)

        
            telegrambot.send_message(message=message.content, user_id=recipient.username)
        
        return JsonResponse({'data': True})

    return JsonResponse({})
