import os
import numpy as np
from django.conf import settings
from django.core.management.base import BaseCommand
from movie.models import Movie
from openai import OpenAI
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Generate and store embeddings for all movies in the database"

    def handle(self, *args, **kwargs):
        load_dotenv(os.path.join(settings.BASE_DIR, 'openAI.env'))
        client = OpenAI(api_key=os.environ.get('openai_apikey'))

        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies in the database")

        def get_embedding(text):
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return np.array(response.data[0].embedding, dtype=np.float32)

        for movie in movies:
            try:
                emb = get_embedding(movie.description)
                movie.emb = emb.tobytes()
                movie.save()
                self.stdout.write(self.style.SUCCESS(f"Embedding stored for movie id {movie.id}"))
            except Exception as e:
                self.stderr.write(f"Failed to generate embedding for movie id {movie.id}: {e}")

        self.stdout.write(self.style.SUCCESS("Finished generating embeddings for all movies"))
