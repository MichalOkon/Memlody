import os
from dataclasses import dataclass

import spotipy
import plotly.express as px
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd
import datetime
from clustering import Clustering


class Application:
    def __init__(self):
        self.client_id = os.environ.get('SPOTIPY_CLIENT_ID')
        self.client_secret = os.environ.get('SPOTIPY_CLIENT_SECRET')
        self.redirect_uri = "http://localhost:1234"
        self.scope = "user-library-read"

        # Initialize the Spotify API client
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(self.client_id,
                                                            self.client_secret,
                                                            self.redirect_uri,
                                                            self.scope))
        self.data = None

    def get_data(self, load_data=True):

        if os.path.exists("data.csv") and load_data:
            self.data = pd.read_csv("data.csv")
        else:
            # Get the user's saved tracks and the total number of saved tracks
            results = self.sp.current_user_saved_tracks()
            total_tracks = results["total"]

            limit = 50
            offset = 0

            dates = []
            names = []
            genres = []
            artists = []
            # Retrieve the tracks in multiple requests
            while offset < total_tracks:
                results = self.sp.current_user_saved_tracks(limit=limit, offset=offset)
                saved_tracks = results["items"]

                # Extract the relevant information and store it in the lists
                for track in saved_tracks:
                    date = datetime.datetime.strptime(track["added_at"], "%Y-%m-%dT%H:%M:%SZ")
                    name = track["track"]["name"]
                    # Extract the primary genre of the track
                    artist = self.sp.artist(track["track"]["artists"][0]['id'])
                    artist_genres = artist["genres"]
                    if len(artist_genres) == 0:
                        artist_genres = ["unknown"]
                    for genre in artist_genres:
                        dates.append(date)
                        names.append(name)
                        artists.append(artist["name"])
                        genres.append(genre)
                # Increment the offset
                offset += limit

            # Create a pandas DataFrame from the lists
            self.data = pd.DataFrame({"date": dates, "name": names, "artist": artists, "genre": genres})

            # Add a column with the year and month of each date
            self.data["month"] = self.data["date"].dt.strftime("%Y-%m")

            self.data.to_csv("data.csv")

    def calculate_monthly_counts(self):
        # Group the data by month and count the number of songs added each month

        return self.data.groupby("month").size()

    def calculate_monthly_genre_counts(self):
        # Group the data by month and genre and count the number of songs in each group

        return self.data.groupby(["month", "genre"]).size().reset_index(name='counts')

    def plot_monthly_counts(self):
        # Use plotly to present the plot in an interactive way

        monthly_genre_counts = self.calculate_monthly_genre_counts()
        fig = px.bar(monthly_genre_counts, x="month", y="counts", color="genre",
                     hover_name=monthly_genre_counts["genre"] + ": " + monthly_genre_counts["counts"].astype(str))

        fig.update_layout(title="Number of songs added to library each month", xaxis_title="Month",
                          yaxis_title="Number of songs added", hoverlabel=dict(font=dict(size=10)))
        fig.show()

    def plot_artist_genre_heatmap(self):
        cl = Clustering(self.data)
        cl.create_genre_vectors()
        cl.create_genre_artist_heatmap()

    def cluster(self):
        cl = Clustering(self.data)
        cl.create_genre_vectors()
        cl.perform_hierarchical_clustering()


if __name__ == "__main__":
    app = Application()
    app.get_data()
    # app.plot_monthly_counts()
    # app.plot_artist_genre_heatmap()
    app.cluster()