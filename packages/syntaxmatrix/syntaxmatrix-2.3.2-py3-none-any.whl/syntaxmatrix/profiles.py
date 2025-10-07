# syntaxmatrix/profiles.py
from openai import OpenAI
from google import genai
import anthropic

from syntaxmatrix.llm_store import list_profiles, load_profile

# Preload once at import-time
_profiles: dict[str, dict] = {}

def _refresh_profiles() -> None:
    _profiles.clear()
    for p in list_profiles():
        prof = load_profile(p["name"])
        if prof:
            _profiles[prof["purpose"]] = prof

def refresh_profiles_cache() -> None:
    _refresh_profiles()
            
def get_profile(purpose: str) -> dict:
    prof = _profiles.get(purpose)
    if prof:
        return prof
    _refresh_profiles()
    return _profiles.get(purpose)


def get_client(profile):
    
    provider = profile["provider"].lower()
    api_key = profile["api_key"]

    if provider == "google":    #1
        return  genai.Client(api_key=api_key)
    if provider == "openai":    #2
        return OpenAI(api_key=api_key)
    if provider == "xai":   #3
        return OpenAI(api_key=api_key, base_url="https://api.x.ai/v1")
    if provider == "deepseek":  #4
        return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    if provider == "moonshot":  #5
        return OpenAI(api_key=api_key, base_url="https://api.moonshot.ai/v1")
    if provider == "alibaba":   #6
        return OpenAI(api_key=api_key, base_url="https://dashscope-intl.aliyuncs.com/compatible-mode/v1",)
    if provider == "anthropic": #7
        return anthropic.Anthropic(api_key=api_key)
    
def drop_cached_profile_by_name(profile_name: str) -> bool:
    """
    Remove the cached profile with this name (if present) from the in-memory map.
    Returns True if something was removed.
    """
    removed = False
    for purpose, prof in list(_profiles.items()):
        if isinstance(prof, dict) and prof.get("name") == profile_name:
            _profiles.pop(purpose, None)
            removed = True
    return removed