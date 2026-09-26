from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy import DateTime, Integer, String, Text, create_engine, delete, desc, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    keywords_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), default="COMPLETED", nullable=False)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "filename": self.filename,
            "raw_text": self.raw_text,
            "summary": self.summary,
            "keywords": json.loads(self.keywords_json) if self.keywords_json else {},
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status,
        }


class DatabaseManager:
    def __init__(self, db_path: str = "smartdoc.db") -> None:
        self.db_path = db_path
        self.engine = create_engine(f"sqlite:///{self.db_path}", echo=False)
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        self.init_db()

    def init_db(self) -> None:
        Base.metadata.create_all(self.engine)

    def save_document(
        self,
        filename: str,
        raw_text: str,
        summary: Optional[str] = None,
        keywords_data: Optional[dict[str, Any]] = None,
        status: str = "COMPLETED",
    ) -> Document:
        serialized_keywords = json.dumps(keywords_data or {}, ensure_ascii=False)
        with self.session_factory() as session:
            doc = Document(
                filename=filename,
                raw_text=raw_text,
                summary=summary,
                keywords_json=serialized_keywords,
                status=status,
                created_at=datetime.now(timezone.utc),
            )
            session.add(doc)
            session.commit()
            session.refresh(doc)
            return doc

    def get_all_documents(self) -> list[Document]:
        with self.session_factory() as session:
            stmt = select(Document).order_by(desc(Document.created_at))
            return list(session.scalars(stmt).all())

    def get_document_by_id(self, doc_id: int) -> Optional[Document]:
        with self.session_factory() as session:
            return session.get(Document, doc_id)

    def delete_document_by_id(self, doc_id: int) -> bool:
        with self.session_factory() as session:
            stmt = delete(Document).where(Document.id == doc_id)
            result = session.execute(stmt)
            session.commit()
            return bool(result.rowcount > 0)


# Global default instance
db_manager = DatabaseManager()
