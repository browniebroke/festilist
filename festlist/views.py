"""
The application views defined here
"""
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseServerError
from models import SoundcloudAppli, Playlist
import soundcloud
import random
import simplejson


def set_cookie(response, key, value, days_expire=1):
    max_age = days_expire * 24 * 60 * 60
    response.set_cookie(key, value, max_age=max_age)


def home(request):
    apps = SoundcloudAppli.objects.all()
    print "running home view '%s'" % apps
    return render(request, 'index.html', {'setup_ok': (len(apps) > 0),
                                          'setup_warn': (len(apps) > 1),
                                          'authorised': ('access_token' in request.COOKIES)})


def authorise(request):
    if 'access_token' in request.COOKIES:
        #App has already been authorised: skip this
        return redirect('create')
    app = SoundcloudAppli.objects.all()[0]
    print app
    print app.client_id
    create_uri = request.build_absolute_uri('/create')
    client = soundcloud.Client(
        client_id=app.client_id,
        client_secret=app.client_secret,
        redirect_uri=create_uri,
        display='popup'
    )
    return redirect(client.authorize_url())


def create(request):
    app = SoundcloudAppli.objects.all()[0]
    code = request.GET.get('code', '')
    response = render(request, 'create.html')
    if code and 'access_token' not in request.COOKIES:
        create_uri = request.build_absolute_uri('/create')
        client = soundcloud.Client(
            client_id=app.client_id,
            client_secret=app.client_secret,
            redirect_uri=create_uri
        )
        access_token = client.exchange_token(code)
        print("about to set the cookie")
        set_cookie(response, 'access_token', access_token.access_token)
    return response


def generate_playlist(request):
    print(request.POST.keys())
    artists = request.POST.get("artists").replace('/', '\n').split('\n')
    if artists:
        client = soundcloud.Client(access_token=request.COOKIES['access_token'])
        print(artists)
        all_tracks = []
        for artist in artists:
            artist = artist.strip()
            print artist
            tracks = client.get('/tracks', q=artist, limit=20)
            short_tracks = []
            count = 0
            for track in tracks:
                max_tracks = int(request.POST.get("max_tracks"))
                if count > max_tracks:
                    break
                max_length = int(request.POST.get("max_length"))
                if max_length == 0 or track.duration < (max_length * 60 * 1000):
                    #Skip ones longer than max_length mins
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
        # FIXME: timeout more than ~400 sounds in total
        print("Creating Playlist...")
        ret = client.post('/playlists', playlist={
            'title': request.POST.get("title"),
            'sharing': "public", #TODO: cutomize this viw a tickbox
            'tracks': all_tracks_ids
        })
        try:
            user = client.get('/me')
            plst = Playlist(name=ret.title, author=user.username, author_id=user.uri, url=ret.permalink_url)
            plst.save()
        except Exception as exc:
            print("++ ERROR while trying to save the playlist: %s" % exc)
        print("Created %s available at: %s!" % (ret.title, ret.permalink_url))
        return HttpResponse(simplejson.dumps({"link": ret.permalink_url, "title": ret.title}), content_type="application/json")
    else:
        print("no artists found!")
        return HttpResponseServerError()

