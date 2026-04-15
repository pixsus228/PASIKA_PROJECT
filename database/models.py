from sqlalchemy import BigInteger, String, ForeignKey, DateTime, Integer, Boolean, Text, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from datetime import datetime, timezone


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    username: Mapped[str] = mapped_column(String(50), nullable=True)

    # Дані профілю
    age: Mapped[int] = mapped_column(Integer, nullable=True)
    gender: Mapped[str] = mapped_column(String(10), nullable=True)
    city: Mapped[str] = mapped_column(String(100), default="Ромни")
    bio: Mapped[str] = mapped_column(Text, nullable=True)

    # Медіа-контент (фото/відео)
    # Зберігаю список об'єктів: [{'type': 'photo', 'file_id': '...'}, ...]
    media_content: Mapped[list] = mapped_column(JSON, default=list)

    is_military: Mapped[bool] = mapped_column(Boolean, default=False)

    # Фільтри пошуку
    interest_gender: Mapped[str] = mapped_column(String(10), nullable=True)
    min_age: Mapped[int] = mapped_column(Integer, default=18)
    max_age: Mapped[int] = mapped_column(Integer, default=100)

    # Економіка Вулика
    honey_balance: Mapped[int] = mapped_column(Integer, default=0)
    trust_level: Mapped[int] = mapped_column(Integer, default=10)
    is_ghost: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Гігієна та активність
    last_active: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    is_banned: Mapped[bool] = mapped_column(Boolean, default=False)

    # Зв'язки
    sent_likes: Mapped[list["Match"]] = relationship(
        "Match", foreign_keys="Match.from_user_id", back_populates="from_user"
    )
    received_likes: Mapped[list["Match"]] = relationship(
        "Match", foreign_keys="Match.to_user_id", back_populates="to_user"
    )


class Match(Base):
    __tablename__ = 'matches'

    id: Mapped[int] = mapped_column(primary_key=True)
    from_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    to_user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))

    is_like: Mapped[bool] = mapped_column(Boolean, default=True)
    is_mutual: Mapped[bool] = mapped_column(Boolean, default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    from_user: Mapped["User"] = relationship("User", foreign_keys=[from_user_id], back_populates="sent_likes")
    to_user: Mapped["User"] = relationship("User", foreign_keys=[to_user_id], back_populates="received_likes")