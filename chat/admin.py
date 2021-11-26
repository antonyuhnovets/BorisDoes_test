from django.contrib import admin
from .models import MessageModel, User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    fields = ('username', 'email', 'first_name', 'last_name')

class MessageModelAdmin(admin.ModelAdmin):
    list_filter = ('timestamp', 'author')
    fields = ('author', 'body')
    list_display = ('author', 'timestamp')


admin.site.register(User, UserAdmin)
admin.site.register(MessageModel, MessageModelAdmin)