from sqlmodel import SQLModel

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class RefreshToken(SQLModel):
    refresh_token: str
    token_type: str = "bearer"


class Tokens(SQLModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str

# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None