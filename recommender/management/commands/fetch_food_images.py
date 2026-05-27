"""Fetch missing food images using TheMealDB, then Spoonacular, then leave empty."""

import os
import re
import time
from pathlib import Path

import requests
from django.conf import settings
from django.core.management.base import BaseCommand

from recommender.models import Food


class Command(BaseCommand):
    help = 'Fetch missing food images from TheMealDB and Spoonacular'

    def __init__(self):
        super().__init__()
        self._local_image_index = None

    def handle(self, *args, **options):
        spoonacular_key = os.getenv('SPOONACULAR_KEY', 'd8a97829338a48c88faf9419faed3d46')
        foods = Food.objects.filter(imagepath='')

        if not foods.exists():
            self.stdout.write('No foods need image updates.')
            return

        for food in foods:
            image_url = self._fetch_image(food.name, spoonacular_key)

            if image_url:
                food.imagepath = image_url
                food.save(update_fields=['imagepath'])
                self.stdout.write(f'Updated: {food.name} -> {image_url}')
            else:
                self.stdout.write(f'Not found: {food.name}')

            time.sleep(0.5)

    def _normalize_key(self, value):
        return re.sub(r'[^a-z0-9]+', '', (value or '').lower())

    def _get_local_image_index(self):
        if self._local_image_index is not None:
            return self._local_image_index

        local_dir = Path(settings.BASE_DIR) / 'static' / 'images' / 'food'
        index = {}

        if local_dir.exists():
            for file_path in local_dir.iterdir():
                if not file_path.is_file() or file_path.suffix.lower() not in {'.jpg', '.jpeg', '.png', '.webp', '.gif'}:
                    continue

                index.setdefault(self._normalize_key(file_path.stem), f'/static/images/food/{file_path.name}')

        self._local_image_index = index
        return index

    def _build_query_variants(self, food_name):
        raw_name = (food_name or '').strip()
        if not raw_name:
            return []

        variants = [raw_name]

        without_parentheses = re.sub(r'\s*\([^)]*\)', '', raw_name).strip()
        if without_parentheses:
            variants.append(without_parentheses)

        first_comma_part = raw_name.split(',')[0].strip()
        if first_comma_part:
            variants.append(first_comma_part)

        comma_parts = [part.strip() for part in raw_name.split(',') if part.strip()]
        if len(comma_parts) >= 2:
            descriptor_first = f'{comma_parts[1]} {comma_parts[0]}'.strip()
            if descriptor_first:
                variants.append(descriptor_first)

        cleaned = raw_name
        cleaned = re.sub(r'\([^)]*\)', ' ', cleaned)
        cleaned = re.sub(
            r'\b(raw|cooked|frozen|canned|prepared|drained|with added vitamins?|with skin|lowfat|low fat|low moisture|part skim|part-skim|restaurant|commercial|instant|instantaneous|ready to eat|ready-to-eat|unsweetened|sweetened|plain|large|small|medium|dry roasted|boiled|baked|fried|fresh)\b',
            ' ',
            cleaned,
            flags=re.IGNORECASE,
        )
        cleaned = re.sub(r'[,/\-]', ' ', cleaned)
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        if cleaned:
            variants.append(cleaned)

        if first_comma_part:
            singularized = re.sub(r'\b([A-Za-z]+)s\b$', r'\1', first_comma_part)
            if singularized and singularized != first_comma_part:
                variants.append(singularized)

        return list(dict.fromkeys(variant for variant in variants if variant))

    def _fetch_image(self, food_name, spoonacular_key):
        local_image = self._fetch_local_image(food_name)
        if local_image:
            return local_image

        for query in self._build_query_variants(food_name):
            image_url = self._fetch_from_mealdb(query)
            if image_url:
                return image_url

            image_url = self._fetch_from_spoonacular(query, spoonacular_key)
            if image_url:
                return image_url

        return None

    def _fetch_local_image(self, food_name):
        local_image_index = self._get_local_image_index()

        for query in self._build_query_variants(food_name):
            image_url = local_image_index.get(self._normalize_key(query))
            if image_url:
                return image_url

        return None

    def _fetch_from_mealdb(self, food_name):
        """
        Layer 1: Fetch image from TheMealDB API
        """
        try:
            url = 'https://www.themealdb.com/api/json/v1/1/search.php'
            response = requests.get(url, params={'s': food_name}, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                meals = data.get('meals')
                
                if meals and len(meals) > 0:
                    image_url = meals[0].get('strMealThumb')
                    if image_url:
                        return image_url
        
        except Exception as e:
            self.stdout.write(f'    → TheMealDB error: {str(e)}')
        
        return None

    def _fetch_from_spoonacular(self, food_name, api_key):
        """
        Layer 2: Fetch image from Spoonacular API
        """
        try:
            url = 'https://api.spoonacular.com/food/ingredients/search'
            params = {
                'query': food_name,
                'number': 1,
                'apiKey': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                if results and len(results) > 0:
                    image_filename = results[0].get('image')
                    if image_filename:
                        return f'https://spoonacular.com/cdn/ingredients_250x250/{image_filename}'
            
        except Exception as e:
            self.stdout.write(f'Spoonacular error for {food_name}: {str(e)}')
        
        return None
