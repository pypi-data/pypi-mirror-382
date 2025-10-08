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
    detected_lang = re.sub("[^A-Za-z]", "", detected_lang).lower()
    detected_lang = Lang(detected_lang).name.lower()
    return detected_lang, confidence

def to_name(alpha2):
    return Lang(alpha2).name.lower()

def to_alpha2(name):
    return Lang(name).pt1