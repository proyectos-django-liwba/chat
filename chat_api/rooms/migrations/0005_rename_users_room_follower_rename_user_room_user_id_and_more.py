# Generated by Django 4.2.7 on 2023-12-16 20:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rooms', '0004_alter_room_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='room',
            old_name='users',
            new_name='follower',
        ),
        migrations.RenameField(
            model_name='room',
            old_name='user',
            new_name='user_id',
        ),
        migrations.AddField(
            model_name='room',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='room_images'),
        ),
        migrations.AddField(
            model_name='room',
            name='user_count',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
