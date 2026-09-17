import os
import numpy as np
from django.conf import settings
from django.shortcuts import render
from openai import OpenAI
from dotenv import load_dotenv
from movie.models import Movie


def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


def recommend(request):
    prompt = request.GET.get('prompt', '')
    recommended_movie = None
    similarity_score = None
    error = None

    if prompt:
        try:
            load_dotenv(os.path.join(settings.BASE_DIR, 'openAI.env'))
            client = OpenAI(api_key=os.environ.get('openai_apikey'))

            response = client.embeddings.create(
                input=[prompt],
                model="text-embedding-3-small",
            )
            prompt_emb = np.array(response.data[0].embedding, dtype=np.float32)

            best_movie = None
            max_similarity = -1

            for movie in Movie.objects.all():
                movie_emb = np.frombuffer(movie.emb, dtype=np.float32)
                similarity = cosine_similarity(prompt_emb, movie_emb)

                if similarity > max_similarity:
                    max_similarity = similarity
                    best_movie = movie

            recommended_movie = best_movie
            similarity_score = max_similarity

        except Exception as e:
            error = str(e)

    return render(request, 'recommend.html', {
        'prompt': prompt,
        'recommended_movie': recommended_movie,
        'similarity_score': similarity_score,
        'error': error,
    })
