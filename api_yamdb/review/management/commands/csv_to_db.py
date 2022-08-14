import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from review.models import (Category, Comment, Genre, GenresTitles, Review,
                           Title, User)

DIR_FILES = os.path.join(settings.BASE_DIR, 'static/data/')


path_file = {
    'User': DIR_FILES + 'users.csv',
    'Title': DIR_FILES + 'titles.csv',
    'Category': DIR_FILES + 'category.csv',
    'Genre': DIR_FILES + 'genre.csv',
    'GenreTitle': DIR_FILES + 'genre_title.csv',
    'Review': DIR_FILES + 'review.csv',
    'Comment': DIR_FILES + 'comments.csv',
}


def run_script():
    users = {}
    with open(path_file['User']) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                user = User.objects.create_user(
                    username=row['username'],
                    email=row['email'],
                    #role=row['role'], # TODO
                    bio=row['bio'],
                    first_name=row['first_name'],
                    last_name=row['last_name']
                )
                users[row['id']] = user
            except Exception:
                continue

    with open(path_file['Category'], encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                Category.objects.create(
                    name=row['name'],
                    slug=row['slug']
                )
            except Exception:
                continue

    with open(path_file['Title'], encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                category = Category.objects.get(pk=row['category'])
                Title.objects.create(
                    name=row['name'],
                    year=row['year'],
                    category=category,
                )
            except Exception:
                continue

    with open(path_file['Genre'], encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                Genre.objects.create(
                    name=row['name'],
                    slug=row['slug'],
                )
            except Exception:
                continue

    with open(path_file['GenreTitle'], encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                genre = Genre.objects.get(pk=row['genre_id'])
                title = Title.objects.get(pk=row['title_id'])
                GenresTitles.objects.create(
                    title=title,
                    genre=genre,
                )
            except Exception:
                continue

    with open(path_file['Review'], encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                title = Title.objects.get(pk=row['title_id'])
                author = users[row['author']]
                Review.objects.create(
                    title=title,
                    author=author,
                    text=row['text'],
                    score=row['score'],
                )
            except Exception:
                continue

    with open(path_file['Comment'], encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                review = Review.objects.get(pk=row['review_id'])
                author = users[row['author']]
                Comment.objects.create(
                    review=review,
                    author=author,
                    text=row['text'],
                )
            except Exception:
                continue


class Command(BaseCommand):
    help = 'Fills in the database for testing'

    def handle(self, *args, **options):
        run_script()
