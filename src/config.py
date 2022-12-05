from fastapi_jwt_auth import AuthJWT
from pydantic import BaseSettings


class Config(BaseSettings):
    ENV: str = "local"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DATABASE_HOST: str = 'localhost'
    DATABASE_PORT: str = 5432
    DATABASE_NAME: str = 'abz'
    DATABASE_USER: str = 'abz'
    DATABASE_PASSWORD: str = 'abz'
    authjwt_secret_key: str = '(:'

    @property
    def DATABASE_URL(self):
        return (
            f"postgresql+asyncpg://{self.DATABASE_USER}:{self.DATABASE_PASSWORD}"
            f"@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@AuthJWT.load_config
def get_config():
    return Config()


app_config = Config()
