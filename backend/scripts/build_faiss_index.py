import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.recipe_service import recipe_service
from app.services.embedding_service import embedding_service
from app.services.faiss_service import faiss_service

def main():
    recipe_service._load_recipes()
    recipes = recipe_service.recipes
    if not recipes:
        print("No recipes loaded")
        return
    print(f"Encoding {len(recipes)} recipes...")
    embeddings = embedding_service.encode_recipes_batch(recipes, batch_size=32)
    faiss_service.build_index(embeddings, recipes)
    print(f"FAISS index built for {len(recipes)} recipes")

if __name__ == "__main__":
    main()
