import os
import base64
from openai import OpenAI
from django.conf import settings
from django.core.management.base import BaseCommand
from movie.models import Movie
from dotenv import load_dotenv


class Command(BaseCommand):
    help = "Generate images with OpenAI and update movie image field"

    def handle(self, *args, **kwargs):
        load_dotenv(os.path.join(settings.BASE_DIR, 'openAI.env'))

        client = OpenAI(
            api_key=os.environ.get('openai_apikey'),
        )
        images_folder = 'media/movie/images/'
        os.makedirs(images_folder, exist_ok=True)

        movies = Movie.objects.all()
        self.stdout.write(f"Found {movies.count()} movies")

        for movie in movies:
            try:
                image_relative_path = self.generate_and_download_image(client, movie.title, images_folder)

                movie.image = image_relative_path
                movie.save()
                self.stdout.write(self.style.SUCCESS(f"Saved and updated image for: {movie.title}"))

            except Exception as e:
                self.stderr.write(f"Failed for {movie.title}: {e}")

            break

        self.stdout.write(self.style.SUCCESS("Process finished (only first movie updated)."))

    def generate_and_download_image(self, client, movie_title, save_folder):
        prompt = f"Movie poster of {movie_title}"

        # dall-e-2 fue retirado de la API; esta cuenta solo expone la familia gpt-image
        response = client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            quality="low",
            n=1,
        )
        image_b64 = response.data[0].b64_json

        image_filename = f"m_{movie_title}.png"
        image_path_full = os.path.join(save_folder, image_filename)

        with open(image_path_full, 'wb') as f:
            f.write(base64.b64decode(image_b64))

        return os.path.join('movie/images', image_filename)
