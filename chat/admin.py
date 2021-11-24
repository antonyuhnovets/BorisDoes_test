from django.contrib import admin
from .models import Message, User

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    fields = ('username', 'email', 'first_name', 'last_name')

class MessageAdmin(admin.ModelAdmin):
    list_filter = ('date_time', 'author')
    fields = ('title', 'author', 'body')
    list_display = ('title', 'author', 'date_time')


admin.site.register(User, UserAdmin)
admin.site.register(Message, MessageAdmin)