import re
import py3langid as langid
from iso639 import Lang


def detect_language(text, min_confidence=None):
    detector = langid.langid.LanguageIdentifier.from_pickled_model(
        langid.langid.MODEL_FILE, norm_probs=True
    )
    detected_lang, confidence = detector.classify(text)
    if min_confidence and confidence < min_confidence:
        return None, confidence
    detected_lang = to_name(detected_lang)
    return detected_lang, confidence

def to_name(alpha2):
    return Lang(alpha2).name

def to_alpha2(name):
    name = re.sub(r'\b\w+', lambda m: m.group(0).capitalize(), name)
    return Lang(name).pt1