import plotly.express as px
import pandas as pd


class Clustering:
    def __init__(self, data):
        self.data = data
        self.artist_indices = None
        self.genre_vectors = None

    def create_genre_vectors(self):
        # Get a list of unique genres and artists
        unique_genres = self.data["genre"].unique()
        unique_artists = self.data["artist"].unique()

        # Create a dictionary to map each genre to a set of artists
        genre_to_artists = {genre: set() for genre in unique_genres}

        # Iterate over the data and add the artists to the appropriate genre sets
        for i, row in self.data.iterrows():
            genre = row["genre"]
            artist = row["artist"]
            genre_to_artists[genre].add(artist)

        # Create a dictionary to map each artist to an index
        self.artist_indices = {artist: index for index, artist in enumerate(unique_artists)}

        # Create a dictionary to map each genre to a vector
        genre_vectors = {genre: [0] * len(unique_artists) for genre in unique_genres}

        # Fill in the vectors
        for genre, artists in genre_to_artists.items():
            for artist in artists:
                index = self.artist_indices[artist]
                genre_vectors[genre][index] = 1

        self.genre_vectors = genre_vectors

    def create_genre_artist_heatmap(self):
        # Create a pandas DataFrame from the genre_vectors dictionary
        df = pd.DataFrame(self.genre_vectors)

        # Set the indices of the DataFrame to the actual artist names
        df.index = self.artist_indices.keys()

        # Plot the genre vectors using a heatmap
        fig = px.imshow(df, color_continuous_scale='reds', labels={'x': 'Genres', 'y': 'Artists'})
        fig.show()
