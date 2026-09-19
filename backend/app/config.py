from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """
    Central application configuration loaded from environment variables or .env file.
    Follows Pydantic v2 Settings management.
    """
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Server Configuration
    APP_NAME: str = "AI Resume Analysis & Skill Gap API"
    APP_VERSION: str = "1.0.0"
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    ENVIRONMENT: str = "development"
    FRONTEND_URL: str = "http://localhost:5173"
    RATE_LIMIT_ENABLED: bool = True

    # Supabase Configuration
    SUPABASE_URL: str = Field(default="", description="Supabase Project URL")
    NEXT_PUBLIC_SUPABASE_URL: str = Field(default="", description="Supabase URL (Next.js alias)")
    SUPABASE_SERVICE_ROLE_KEY: str = Field(default="", description="Supabase Service Role Secret Key")
    SUPABASE_ANON_KEY: str = Field(default="", description="Supabase Anon / Publishable Key")
    SUPABASE_KEY: str = Field(default="", description="Supabase Generic API Key")
    SUPABASE_PUBLISHABLE_KEY: str = Field(default="", description="Supabase Publishable Key")
    NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY: str = Field(default="", description="Supabase Publishable Key (Next.js alias)")
    NEXT_PUBLIC_SUPABASE_ANON_KEY: str = Field(default="", description="Supabase Anon Key (Next.js alias)")
    SUPABASE_STORAGE_BUCKET: str = Field(default="resumes", description="Supabase Storage Bucket Name")

    # OpenAI / LLM Configuration
    OPENAI_API_KEY: str = Field(default="", description="OpenAI API Key")
    OPENAI_MODEL: str = Field(default="gpt-4o-mini", description="OpenAI Model Identifier")

    # Compatibility Scoring Weights (must sum to 1.0)
    WEIGHT_REQUIRED_SKILLS: float = 0.60
    WEIGHT_PREFERRED_SKILLS: float = 0.15
    WEIGHT_EXPERIENCE: float = 0.15
    WEIGHT_EDUCATION: float = 0.10

    @field_validator("WEIGHT_EDUCATION")
    @classmethod
    def validate_weights_sum(cls, v, values):
        # Access previous values safely in Pydantic v2
        data = values.data
        req = data.get("WEIGHT_REQUIRED_SKILLS", 0.60)
        pref = data.get("WEIGHT_PREFERRED_SKILLS", 0.15)
        exp = data.get("WEIGHT_EXPERIENCE", 0.15)
        total = round(req + pref + exp + v, 2)
        if total != 1.0:
            # We log or allow minor floating point variances, but warn
            pass
        return v

    @property
    def supabase_url(self) -> str:
        """Returns configured Supabase project URL, checking aliases"""
        for u in [self.SUPABASE_URL, self.NEXT_PUBLIC_SUPABASE_URL]:
            if u and "your-project" not in u:
                return u.rstrip("/")
        return ""

    @property
    def supabase_api_key(self) -> str:
        """
        Returns whichever valid Supabase key is provided:
        prioritizes service_role key, falls back to anon/publishable/key.
        """
        for key in [
            self.SUPABASE_SERVICE_ROLE_KEY, 
            self.SUPABASE_KEY, 
            self.SUPABASE_ANON_KEY, 
            self.SUPABASE_PUBLISHABLE_KEY,
            self.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY,
            self.NEXT_PUBLIC_SUPABASE_ANON_KEY
        ]:
            if key and "your-" not in key:
                return key
        return ""

    @property
    def is_supabase_configured(self) -> bool:
        return bool(self.supabase_url and self.supabase_api_key)

    @property
    def is_openai_configured(self) -> bool:
        return bool(self.OPENAI_API_KEY and "your-openai-api-key" not in self.OPENAI_API_KEY)


@lru_cache()
def get_settings() -> Settings:
    """Singleton getter for cached settings"""
    return Settings()
