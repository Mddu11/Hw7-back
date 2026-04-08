from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import User
from ..schemas import UserRegister, UserLogin, UserOut, LoginResponse
from ..dependencies import active_sessions

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.username == payload.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким username уже существует"
        )

    user = User(username=payload.username, password=payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=LoginResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or user.password != payload.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль"
        )

    active_sessions.add(user.id)

    return {
        "message": "Вход выполнен успешно",
        "user_id": user.id
    }


@router.post("/logout")
def logout_user(x_user_id: int | None = Header(default=None, alias="X-User-Id")):
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Передайте заголовок X-User-Id"
        )

    if x_user_id in active_sessions:
        active_sessions.remove(x_user_id)

    return {"message": "Выход выполнен успешно"}