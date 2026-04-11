import os

from fastapi import HTTPException


def get_supabase_settings() -> tuple[str, str]:
    supabase_url = os.getenv("SUPABASE_URL")
    service_role_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_role_key:
        raise HTTPException(
            status_code=500,
            detail="Supabase credentials are not configured",
        )

    return supabase_url.rstrip("/"), service_role_key


def get_supabase_anon_key() -> str:
    anon_key = os.getenv("SUPABASE_ANON_KEY")
    if not anon_key:
        raise HTTPException(
            status_code=500,
            detail="Supabase anon key is not configured",
        )
    return anon_key


def get_app_url() -> str:
    app_url = os.getenv("APP_URL")
    if not app_url:
        raise HTTPException(
            status_code=500,
            detail="APP_URL is not configured",
        )
    return app_url.rstrip("/")
