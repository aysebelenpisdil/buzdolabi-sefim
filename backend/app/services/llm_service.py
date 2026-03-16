"""
LLM Service
Handles text generation using Google Gemini API
Provides explanations for recipe recommendations
"""

import logging
import re
import time
from typing import List, Optional, Dict, Any
from google import genai
from google.genai import types
from google.genai.errors import ClientError
from app.config import settings
from app.models.recipe import Recipe

# Setup logger
logger = logging.getLogger(__name__)


class LLMService:
    """
    Service for generating explanations using Google Gemini API
    Provides personalized recipe recommendation explanations
    """

    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.fallback_model = getattr(settings, "GEMINI_FALLBACK_MODEL", None)
        self.max_tokens = settings.GEMINI_MAX_TOKENS
        self.temperature = settings.GEMINI_TEMPERATURE
        self.enabled = settings.GEMINI_ENABLED
        self.client: Optional[genai.Client] = None
        self._model_loaded = False

    def _load_model(self):
        """Initialize Gemini API client"""
        if not self.enabled:
            logger.debug("LLM service is disabled")
            return

        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found in environment variables")
            logger.warning("LLM explanations will be disabled")
            self.enabled = False
            return

        if not self._model_loaded:
            try:
                logger.info(f"Initializing Gemini API: {self.model_name}")
                self.client = genai.Client(api_key=self.api_key)
                self._model_loaded = True
                logger.info(f"Gemini client initialized for model: {self.model_name}")
            except Exception as e:
                logger.error(f"Error initializing Gemini API: {e}", exc_info=True)
                logger.warning("LLM explanations will be disabled")
                self.enabled = False
                self._model_loaded = False
                raise

    def is_available(self) -> bool:
        """Check if LLM service is available and ready"""
        return self.enabled and self._model_loaded and self.client is not None

    def _try_generate_with_retry(self, prompt: str, config: types.GenerateContentConfig, max_retries: int = 1):
        """429 quota hatasında retry ve model fallback dene."""
        models_to_try = [self.model_name]
        if self.fallback_model and self.model_name != self.fallback_model:
            models_to_try.append(self.fallback_model)

        for model_name in models_to_try:
            for attempt in range(max_retries + 1):
                try:
                    return self.client.models.generate_content(
                        model=model_name,
                        contents=prompt,
                        config=config,
                    )
                except ClientError as e:
                    if e.code == 429:
                        msg = str(e)
                        if attempt < max_retries:
                            match = re.search(r'retry in (\d+(?:\.\d+)?)s', msg, re.I)
                            delay = min(float(match.group(1)) if match else 20, 60)
                            logger.warning(f"Gemini quota (429), {delay:.0f}s sonra tekrar deniyor...")
                            time.sleep(delay)
                        elif model_name != models_to_try[-1]:
                            logger.info(f"Ana model kota aşıldı, fallback ({self.fallback_model}) deneniyor...")
                            break
                        else:
                            logger.warning("Gemini API kota aşıldı (429)")
                            raise
                    else:
                        raise
                except Exception:
                    raise

    def _build_prompt(
        self,
        user_ingredients: List[str],
        recommended_recipes: List[Recipe],
        user_preferences: Optional[Dict[str, Any]] = None,
        excluded_ingredients: Optional[List[str]] = None
    ) -> str:
        """Build prompt for Gemini API"""
        system_prompt = """Sen bir mutfak danışmanısın. Kullanıcının elindeki malzemelere göre önerilen tarifleri kısaca özetle.

Kurallar:
- Türkçe yaz.
- Düz metin yaz, markdown işaretleri (###, **, * vb.) KULLANMA.
- En fazla 3-4 cümle yaz. Kısa ve öz ol.
- Tariflerin genel temasını özetle (örn. "sebze ağırlıklı", "pratik tarifler" vb.).
- Hangi ana malzemelerin eşleştiğini kısaca belirt.
- Her tarifi tek tek açıklama, genel bir özet ver.
"""

        context_parts = []
        context_parts.append(f"**Mevcut Malzemeler:** {', '.join(user_ingredients)}")

        if user_preferences:
            active_prefs = []
            if user_preferences.get('vegan'):
                active_prefs.append('Vegan')
            if user_preferences.get('vegetarian') and not user_preferences.get('vegan'):
                active_prefs.append('Vejetaryen')
            if user_preferences.get('glutenFree'):
                active_prefs.append('Glutensiz')
            if user_preferences.get('dairyFree'):
                active_prefs.append('Süt Ürünü İçermez')
            if user_preferences.get('nutAllergy'):
                active_prefs.append('Kuruyemiş İçermez')

            if active_prefs:
                context_parts.append(f"**Diyet Tercihleri:** {', '.join(active_prefs)}")

        if excluded_ingredients:
            context_parts.append(f"**Hariç Tutulan Malzemeler:** {', '.join(excluded_ingredients)}")

        recipes_text = "\n\nÖnerilen Tarifler:\n"
        for i, recipe in enumerate(recommended_recipes[:5], 1):
            ingredients_text = recipe.Cleaned_Ingredients or recipe.Ingredients
            ingredients_clean = ingredients_text.replace('[', '').replace(']', '').replace("'", '')
            recipes_text += f"\n{i}. {recipe.Title} - Malzemeler: {ingredients_clean[:200]}\n"

        prompt = f"""{system_prompt}
---

Kullanıcı Bilgisi:
{chr(10).join(context_parts)}
{recipes_text}

---

Bu tariflerin neden önerildiğini kısaca özetle. Düz metin yaz, markdown kullanma."""

        return prompt

    def generate_explanation(
        self,
        user_ingredients: List[str],
        recommended_recipes: List[Recipe],
        user_preferences: Optional[Dict[str, Any]] = None,
        excluded_ingredients: Optional[List[str]] = None
    ) -> Optional[str]:
        """Generate explanation for recipe recommendations using Gemini API"""
        if not recommended_recipes:
            logger.warning("No recipes provided for explanation generation")
            return None

        if not self.enabled:
            logger.debug("LLM service is disabled, skipping explanation generation")
            return None

        if not self.api_key:
            logger.debug("GEMINI_API_KEY not found, skipping explanation generation")
            return None

        try:
            if not self._model_loaded:
                self._load_model()

            if not self.is_available():
                logger.warning("LLM model could not be loaded, skipping explanation generation")
                return None

            prompt = self._build_prompt(
                user_ingredients=user_ingredients,
                recommended_recipes=recommended_recipes,
                user_preferences=user_preferences,
                excluded_ingredients=excluded_ingredients
            )

            logger.debug(f"Generating explanation for {len(recommended_recipes)} recipes")

            config = types.GenerateContentConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )
            response = self._try_generate_with_retry(prompt, config)
            explanation = response.text.strip()

            logger.debug(f"Explanation generated: {len(explanation)} characters")

            return explanation

        except ClientError as e:
            if e.code == 429:
                logger.warning("Gemini API kota aşıldı, açıklama atlanıyor")
            else:
                logger.error(f"Gemini API client error: {e}", exc_info=True)
            return None
        except Exception as e:
            logger.error(f"Error generating explanation: {e}", exc_info=True)
            logger.warning("Returning None for explanation")
            return None

    def generate_substitutions(
        self,
        recipe_title: str,
        missing_ingredients: List[str],
        available_ingredients: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Generate ingredient substitution suggestions using Gemini API.

        Returns a dict like:
            {"substitutions": {"süt": ["badem sütü", "yulaf sütü"]}, "explanation": "..."}
        or None on failure.
        """
        if not missing_ingredients:
            return {"substitutions": {}, "explanation": None}

        if not self.enabled or not self.api_key:
            logger.debug("LLM service unavailable, skipping substitution generation")
            return None

        try:
            if not self._model_loaded:
                self._load_model()
            if not self.is_available():
                return None

            subs_example = {ing: ["ikame1", "ikame2"] for ing in missing_ingredients[:2]}
            import json as _json
            example_str = _json.dumps({"substitutions": subs_example, "explanation": "Örnek açıklama"}, ensure_ascii=False)

            prompt = f"""Sen profesyonel bir Türk mutfağı şefisin. Sadece geçerli JSON döndür, başka metin yazma.

Tarif: {recipe_title}
Eksik malzemeler: {', '.join(missing_ingredients)}
Mevcut malzemeler: {', '.join(available_ingredients) if available_ingredients else 'Yok'}

Her eksik malzeme için 1-3 ikame öner (Türk mutfağına uygun). Örnek format:
{example_str}

Yanıtın SADECE bu JSON formatında olsun, tırnak ve virgüllere dikkat et."""

            # thinking_budget=0: JSON üretimi için thinking devre dışı — daha hızlı ve ucuz
            config = types.GenerateContentConfig(
                temperature=0.3,
                max_output_tokens=2048,
                thinking_config=types.ThinkingConfig(thinking_budget=0),
            )
            response = self._try_generate_with_retry(prompt, config)

            import json
            raw = response.text.strip()
            # Strip markdown code fences if present
            if raw.startswith("```"):
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                raw = raw[:-3].rstrip()
            if raw.startswith("json"):
                raw = raw[4:].lstrip()

            def _normalize_llm_json(text: str) -> str:
                """Python-style değerleri geçerli JSON'a çevir."""
                text = re.sub(r'\bNone\b', 'null', text)
                text = re.sub(r'\bTrue\b', 'true', text)
                text = re.sub(r'\bFalse\b', 'false', text)
                text = re.sub(r',\s*}', '}', text)
                text = re.sub(r',\s*]', ']', text)
                return text

            result = None
            try:
                result = json.loads(_normalize_llm_json(raw))
            except json.JSONDecodeError as parse_err:
                match = re.search(r'\{[\s\S]*\}', raw)
                if match:
                    try:
                        candidate = _normalize_llm_json(match.group(0))
                        result = json.loads(candidate)
                    except json.JSONDecodeError:
                        pass
                if result is None:
                    logger.warning(
                        f"LLM JSON parse failed ({parse_err}), raw response:\n{raw}\n"
                        "returning empty substitutions"
                    )
                    return {"substitutions": {}, "explanation": "İkame önerileri şu an yüklenemedi."}

            logger.debug(f"Substitutions generated for {len(missing_ingredients)} ingredients")
            return result

        except ClientError as e:
            if e.code == 429:
                logger.warning("Gemini API kota aşıldı, ikame önerileri boş döndürülüyor")
            else:
                logger.error(f"Gemini API client error: {e}", exc_info=True)
            return {"substitutions": {}, "explanation": None}
        except Exception as e:
            logger.error(f"Error generating substitutions: {e}", exc_info=True)
            return {"substitutions": {}, "explanation": None}

    def get_model_info(self) -> dict:
        """Get information about the LLM service"""
        return {
            "model_name": self.model_name,
            "loaded": self._model_loaded,
            "enabled": self.enabled,
            "has_api_key": bool(self.api_key),
            "max_tokens": self.max_tokens,
            "temperature": self.temperature
        }


# Singleton instance
llm_service = LLMService()
