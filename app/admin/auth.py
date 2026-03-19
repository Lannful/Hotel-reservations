from datetime import datetime, timezone
from jose import JWTError, jwt
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app.config import settings
from app.exceptions import IncorrectEmailOrPasswordException
from app.users.auth import authenticate_user, create_access_token
from app.users.dao import UsersDAO


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form["username"], form["password"]
            
        user = await authenticate_user(email, password)
        if not user:
            return False
        
        access_token = create_access_token({"sub": str(user.id)})
        request.session.update({"token": access_token})
        return True

    async def logout(self, request: Request) -> bool:
        # Usually you'd want to just clear the session
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("token")

        if not token:
            return RedirectResponse(request.url_for("admin:login"), status_code=302)
        
        try:
            payload = jwt.decode(
                token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
            )
            # jwt.decode автоматически проверяет exp, но для явности оставляем проверку
            expire: int | None = payload.get("exp")
            if expire and datetime.fromtimestamp(expire, tz=timezone.utc) < datetime.now(timezone.utc):
                return RedirectResponse(request.url_for("admin:login"), status_code=302)
            user_id = payload.get("sub")
            if not user_id:
                return RedirectResponse(request.url_for("admin:login"), status_code=302)
            user = await UsersDAO.find_by_id(int(user_id))
            if not user:
                return RedirectResponse(request.url_for("admin:login"), status_code=302)
        except (JWTError, ValueError, TypeError):
            return RedirectResponse(request.url_for("admin:login"), status_code=302)

        return True


authentication_backend = AdminAuth(secret_key=settings.SECRET_KEY)
