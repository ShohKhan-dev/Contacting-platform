from django.contrib import admin
from .models import User, Conversation, ConversationMessage, Notification
# Register your models here.

admin.site.register(User)
admin.site.register(Conversation)
admin.site.register(ConversationMessage)
admin.site.register(Notification)