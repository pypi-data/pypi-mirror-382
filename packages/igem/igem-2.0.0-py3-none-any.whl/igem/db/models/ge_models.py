from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Index
from sqlalchemy.orm import relationship
from igem.db.base import Base


class TermGroup(Base):
    __tablename__ = "term_group"
    id = Column(Integer, primary_key=True)
    term_group = Column(String(20), unique=True)
    description = Column(String(200))

    @classmethod
    def truncate(cls, engine):
        with engine.begin() as conn:
            conn.execute(f"TRUNCATE TABLE {cls.__tablename__} CASCADE")


class TermCategory(Base):
    __tablename__ = "term_category"
    id = Column(Integer, primary_key=True)
    term_category = Column(String(20), unique=True)
    description = Column(String(200))

    @classmethod
    def truncate(cls, engine):
        with engine.begin() as conn:
            conn.execute(f"TRUNCATE TABLE {cls.__tablename__} CASCADE")


class Term(Base):
    __tablename__ = "term"
    id = Column(Integer, primary_key=True)
    term = Column(String(40), unique=True)
    description = Column(String(400))
    term_group_id = Column(Integer, ForeignKey("term_group.id"))
    term_category_id = Column(Integer, ForeignKey("term_category.id"))

    term_group = relationship("TermGroup", backref="terms")
    term_category = relationship("TermCategory", backref="terms")

    @classmethod
    def truncate(cls, engine):
        with engine.begin() as conn:
            conn.execute(f"TRUNCATE TABLE {cls.__tablename__} CASCADE")


class TermHierarchy(Base):
    __tablename__ = "term_hierarchy"
    id = Column(Integer, primary_key=True)
    term_id = Column(Integer, ForeignKey("term.id"))
    term_parent_id = Column(Integer, ForeignKey("term.id"))

    term = relationship("Term", foreign_keys=[term_id], backref="children")
    term_parent = relationship("Term", foreign_keys=[term_parent_id], backref="parents")

    @classmethod
    def truncate(cls, engine):
        with engine.begin() as conn:
            conn.execute(f"TRUNCATE TABLE {cls.__tablename__} CASCADE")


class WordTerm(Base):
    __tablename__ = "word_term"
    id = Column(Integer, primary_key=True)
    word = Column(String(400), unique=True)
    term_id = Column(Integer, ForeignKey("term.id"))
    status = Column(Boolean, default=False)
    commute = Column(Boolean, default=False)

    term = relationship("Term", backref="word_terms")

    __table_args__ = (Index("ix_word_term_term_id", "term_id"),)

    @classmethod
    def truncate(cls, engine):
        with engine.begin() as conn:
            conn.execute(f"TRUNCATE TABLE {cls.__tablename__} CASCADE")


class WordMap(Base):
    __tablename__ = "word_map"
    id = Column(Integer, primary_key=True)
    cword = Column(String(15), unique=True)
    datasource_id = Column(Integer, ForeignKey("datasource.id"))
    connector_id = Column(Integer, ForeignKey("connector.id"))
    term_1_id = Column(Integer, ForeignKey("term.id"), nullable=True)
    term_2_id = Column(Integer, ForeignKey("term.id"), nullable=True)
    word_1 = Column(String(100))
    word_2 = Column(String(100))
    qtd_links = Column(Integer, default=0)

    datasource = relationship("Datasource")
    connector = relationship("Connector")
    term_1 = relationship("Term", foreign_keys=[term_1_id])
    term_2 = relationship("Term", foreign_keys=[term_2_id])

    @classmethod
    def truncate(cls, engine):
        with engine.begin() as conn:
            conn.execute(f"TRUNCATE TABLE {cls.__tablename__} CASCADE")


class TermMap(Base):
    __tablename__ = "term_map"
    ckey = Column(String(15), primary_key=True)
    connector_id = Column(Integer, ForeignKey("connector.id"))
    term_1_id = Column(Integer, ForeignKey("term.id"))
    term_2_id = Column(Integer, ForeignKey("term.id"))
    qtd_links = Column(Integer, default=0)

    connector = relationship("Connector")
    term_1 = relationship("Term", foreign_keys=[term_1_id])
    term_2 = relationship("Term", foreign_keys=[term_2_id])

    @classmethod
    def truncate(cls, engine):
        with engine.begin() as conn:
            conn.execute(f"TRUNCATE TABLE {cls.__tablename__} CASCADE")
