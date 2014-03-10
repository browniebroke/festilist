"""
The application views defined here
"""
from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse
import soundcloud
import random
from django.core.context_processors import csrf
import simplejson

YOUR_CLIENT_ID = '2ae265cd2702984b68b72f786c2cf1e5'
YOUR_CLIENT_SECRET = '6ff01cbec17b9dd3887ff7d17fce9a58'

def home(request):
    return render(request, 'index.html')


def authorise(request):
    create_uri = request.build_absolute_uri('/create')
    client = soundcloud.Client(
        client_id=YOUR_CLIENT_ID,
        client_secret=YOUR_CLIENT_SECRET,
        redirect_uri=create_uri,
        display='popup'
    )
    return redirect(client.authorize_url())


def create(request):
    code = request.GET.get('code', '')
    if code:
        create_uri = request.build_absolute_uri('/create')
        client = soundcloud.Client(
            client_id=YOUR_CLIENT_ID,
            client_secret=YOUR_CLIENT_SECRET,
            redirect_uri=create_uri
        )
        access_token = client.exchange_token(code)
        request.session['access_token'] = access_token.access_token
        #client.get('/me').username
        c = {}
        c.update(csrf(request))
        return render(request, 'create.html', c)


def generate_playlist(request):
    print(request.POST.keys())
    artists = request.POST.get("artists").split('\n')
    if artists:
        client = soundcloud.Client(access_token=request.session['access_token'])
        print(artists)
        all_tracks = []
        for artist in artists:
            print artist
            tracks = client.get('/tracks', q=artist, limit=20)
            short_tracks = []
            count = 0
            for track in tracks:
                if count > 5:
                    break
                if track.duration < (10 * 60 * 1000):
                    #Skip ones longer than 10 mins
                    count += 1
                    short_tracks.append(track)
            all_tracks.extend(track.id for track in short_tracks)
            print len(all_tracks)

        if request.POST.get("randomize"):
            print("Randomize = true")
            random.shuffle(all_tracks)

        # create an array of track ids
        all_tracks_ids = map(lambda id: dict(id=id), all_tracks)

        # create the playlist
        print("Creating Playlist...")
        ret = client.post('/playlists', playlist={
            'title': request.POST.get("title"),
            'sharing': "public",
            'tracks': all_tracks_ids
        })
        print("Created %s available at: %s!" % (ret.title, ret.permalink_url))
        return HttpResponse(simplejson.dumps({"link": ret.permalink_url, "title": ret.title}), content_type="application/json")
    else:
        print("no artists found!")
        return HttpResponse()

