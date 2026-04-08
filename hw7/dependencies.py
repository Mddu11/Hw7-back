from fastapi import Header, HTTPException, Depends, status
from sqlalchemy.orm import Session

from .db import get_db
from .models import User

# простое хранилище "сессий" для учебного задания:
# если user_id есть в active_sessions -> считаем, что пользователь вошел
active_sessions: set[int] = set()


def get_current_user(
    x_user_id: int | None = Header(default=None, alias="X-User-Id"),
    db: Session = Depends(get_db),
):
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация. Передайте заголовок X-User-Id."
        )

    user = db.query(User).filter(User.id == x_user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )

    if x_user_id not in active_sessions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не авторизован"
        )

    return user