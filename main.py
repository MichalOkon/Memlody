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

# Retrieve the tracks in multiple requests
while offset < total_tracks:
    results = sp.current_user_saved_tracks(limit=limit, offset=offset)
    saved_tracks = results["items"]

    # Extract the relevant information and store it in the lists
    for track in saved_tracks:
        dates.append(datetime.datetime.strptime(track["added_at"], "%Y-%m-%dT%H:%M:%SZ"))
        names.append(track["track"]["name"])

    # Increment the offset
    offset += limit

# Use pandas to extract month from dates
df = pd.DataFrame({"date": dates})
df["month"] = df["date"].dt.to_period("M")

# Group the data by month and count the number of songs added each month
monthly_counts = df.groupby("month").size()

# Use plotly to present the plot in an interactive way
fig = px.bar(x=monthly_counts.index.strftime("%Y-%m"), y=monthly_counts.values)
fig.update_layout(title="Number of songs added to library each month", xaxis_title="Month", yaxis_title="Number of songs added")
fig.show()
