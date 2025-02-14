import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import praw
from googleapiclient.discovery import build
from ticketpy import ApiClient
import yfinance as yf
from textblob import TextBlob
from pytrends.request import TrendReq
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd


load_dotenv()

# API Configurations
SPOTIPY_CLIENT_ID = os.getenv('SPOTIPY_CLIENT_ID')
SPOTIPY_CLIENT_SECRET = os.getenv('SPOTIPY_CLIENT_SECRET')
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
TICKETMASTER_API_KEY = os.getenv('TICKETMASTER_API_KEY')

# Initialize APIs
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=SPOTIPY_CLIENT_ID,
    client_secret=SPOTIPY_CLIENT_SECRET))

reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent='artist-analytics/1.0'
)

youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
pytrends = TrendReq(hl='en-US', tz=360)


class ArtistAnalytics:

    def __init__(self, artist_name):
        self.artist_name = artist_name
        self.spotify_artist = self._get_spotify_artist()
        self.youtube_channel = self._get_youtube_channel()
        self.TICKETMASTER_API_KEY = os.getenv("TICKETMASTER_API_KEY")
        # self.hybe_stock = yf.download('HYBE', period='1mo')

    def _get_spotify_artist(self):
        results = sp.search(q=self.artist_name, type='artist')
        return results['artists']['items'][0]

    def _get_youtube_channel(self):
        request = youtube.search().list(
            q=self.artist_name,
            part="snippet",
            type="channel",
            maxResults=1
        )
        response = request.execute()
        return response['items'][0] if response['items'] else None

    def get_spotify_data(self):
        top_tracks = sp.artist_top_tracks(self.spotify_artist['id'])
        return pd.DataFrame([{
            'name': track['name'],
            'popularity': track['popularity'],
            'duration_ms': track['duration_ms'],
            'release_date': track['album']['release_date']
        } for track in top_tracks['tracks']])

    def get_reddit_sentiment(self):
        submissions = reddit.subreddit('all').search(
            self.artist_name, limit=100)
        comments = []
        for sub in submissions:
            sub.comments.replace_more(limit=0)
            for comment in sub.comments.list():
                comments.append({
                    'body': comment.body,
                    'score': comment.score,
                    'created': datetime.fromtimestamp(comment.created_utc)
                })
        df = pd.DataFrame(comments)
        df['sentiment'] = df['body'].apply(
            lambda x: TextBlob(x).sentiment.polarity)
        return df

    def get_youtube_analytics(self):
        if not self.youtube_channel:
            return pd.DataFrame()
        channel_stats = youtube.channels().list(
            part="statistics",
            id=self.youtube_channel['id']['channelId']
        ).execute()
        return channel_stats['items'][0]['statistics']

    def get_ticketmaster_events(self):
        Client = ApiClient(self.TICKETMASTER_API_KEY)

        try:
            events = Client.events.find(
                keyword=self.artist_name,
                size=10
            )

            return pd.DataFrame([{
                'name': event.name,
                'date': event.dates.start.date if event.dates and event.dates.start else 'Unknown',
                'venue': event.venues[0].name if event.venues else 'Unknown',
                'city': event.venues[0].city.name if event.venues else 'Unknown'
            } for event in events])

        except Exception as e:
            print(f"Error fetching Ticketmaster events: {e}")
            return pd.DataFrame()

    def get_google_trends(self):
        pytrends.build_payload(
            kw_list=[self.artist_name],
            timeframe='today 3-m')
        return pytrends.interest_over_time().reset_index()






