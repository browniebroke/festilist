from django.db import models
from django.contrib import admin


class SoundcloudAppli(models.Model):
    name = models.CharField(max_length=50)
    client_id = models.CharField(max_length=50)
    client_secret = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class SoundcloudAppliAdmin(admin.ModelAdmin):
    list_display = ('name', 'client_id', 'client_secret')

admin.site.register(SoundcloudAppli, SoundcloudAppliAdmin)


class Playlist(models.Model):
    name = models.CharField(max_length=100)
    author = models.CharField(max_length=100)
    author_id = models.CharField(max_length=100)
    url = models.CharField(max_length=1024)

    def __str__(self):
        return self.name

class PlaylistAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')

admin.site.register(Playlist, PlaylistAdmin)
