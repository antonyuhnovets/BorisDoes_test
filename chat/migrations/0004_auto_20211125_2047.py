# Generated by Django 3.2.9 on 2021-11-25 18:47

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_alter_user_email'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'ordering': ('-date_time',), 'verbose_name': 'message'},
        ),
        migrations.RemoveField(
            model_name='message',
            name='title',
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=60)),
                ('members', models.ManyToManyField(to=settings.AUTH_USER_MODEL, verbose_name='Участник')),
            ],
        ),
        migrations.AddField(
            model_name='message',
            name='chat_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, to='chat.chat'),
        ),
    ]