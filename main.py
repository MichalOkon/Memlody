import os

import spotipy
import plotly.express as px
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import datetime

client_id = os.environ.get('SPOTIPY_CLIENT_ID')
client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
redirect_uri = "http://localhost:1234"
scope = "user-library-read"

# Initialize the Spotify API client
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id,
                                               client_secret,
                                               redirect_uri,
                                               scope))

# Get the user's saved tracks and the total number of saved tracks
results = sp.current_user_saved_tracks()
total_tracks = results["total"]

limit = 50
offset = 0

# Initialize lists to store the tracks and their dates
dates = []
names = []
genres = []
# Retrieve the tracks in multiple requests
while offset < total_tracks:
    results = sp.current_user_saved_tracks(limit=limit, offset=offset)
    saved_tracks = results["items"]

    # Extract the relevant information and store it in the lists
    for track in saved_tracks:
        dates.append(datetime.datetime.strptime(track["added_at"], "%Y-%m-%dT%H:%M:%SZ"))
        names.append(track["track"]["name"])
        # Extract the primary genre of the track
        artist = sp.artist(track["track"]["artists"][0]['id'])
        if len(artist["genres"]) > 0:
            genre = artist["genres"][0]
        else:
            genre = "unknown"
        genres.append(genre)
    # Increment the offset
    offset += limit

# Create a pandas DataFrame from the lists
df = pd.DataFrame({"date": dates, "name": names, "genre": genres})

# Add a column with the year and month of each date
df["month"] = df["date"].dt.strftime("%Y-%m")

# Group the data by month and count the number of songs added each month
monthly_counts = df.groupby("month").size()


# Group the data by month and genre and count the number of songs in each group
monthly_genre_counts = df.groupby(["month", "genre"]).size().reset_index(name='counts')

# Use plotly to present the plot in an interactive way
fig = px.bar(monthly_genre_counts, x="month", y="counts", color="genre",
             hover_name=monthly_genre_counts["genre"] + ": " + monthly_genre_counts["counts"].astype(str))

fig.update_layout(title="Number of songs added to library each month", xaxis_title="Month",
                  yaxis_title="Number of songs added", hoverlabel=dict(font=dict(size=10)))
fig.show()
