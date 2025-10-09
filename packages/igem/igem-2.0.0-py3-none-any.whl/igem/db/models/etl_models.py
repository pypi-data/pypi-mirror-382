from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    BigInteger,
    Text,
)
from sqlalchemy.orm import relationship
from igem.db.base import Base


class DataSource(Base):
    __tablename__ = "datasource"
    id = Column(Integer, primary_key=True)
    data_source = Column(String(20), unique=True, nullable=False)
    description = Column(String(200))
    category = Column(String(20))
    website = Column(String(200))

    @classmethod
    def truncate(cls, engine):
        with engine.begin() as conn:
            conn.execute(f"TRUNCATE TABLE {cls.__tablename__} CASCADE")


class Connector(Base):
    __tablename__ = "connector"
    id = Column(Integer, primary_key=True)
    connector = Column(String(20), unique=True, nullable=False)
    data_source_id = Column(Integer, ForeignKey("datasource.id"), nullable=False)
    description = Column(String(200), default="")
    update_ds = Column(Boolean, default=True)
    source_path = Column(String(300), default="")
    source_web = Column(Boolean, default=True)
    source_compact = Column(Boolean, default=False)
    source_file_name = Column(String(200))
    source_file_format = Column(String(200))
    source_file_sep = Column(String(3), default=",")
    source_file_skiprow = Column(Integer, default=0)
    target_file_name = Column(String(200))
    target_file_format = Column(String(200))
    target_file_keep = Column(Boolean, default=False)

    datasource = relationship("Datasource", backref="connectors")

    @classmethod
    def truncate(cls, engine):
        with engine.begin() as conn:
            conn.execute(f"TRUNCATE TABLE {cls.__tablename__} CASCADE")


class PrefixOpc(Base):
    __tablename__ = "prefix_opc"
    pre_value = Column(String(5), primary_key=True)

    @classmethod
    def truncate(cls, engine):
        with engine.begin() as conn:
            conn.execute(f"TRUNCATE TABLE {cls.__tablename__} CASCADE")


class DSTColumn(Base):
    __tablename__ = "dst_column"
    id = Column(Integer, primary_key=True)
    connector_id = Column(Integer, ForeignKey("connector.id"))
    status = Column(Boolean, default=False)
    column_number = Column(Integer, default=0)
    column_name = Column(String(40), default="")
    pre_value_id = Column(String(5), ForeignKey("prefix_opc.pre_value"), default="None")
    single_word = Column(Boolean, default=False)

    connector = relationship("Connector", backref="columns")
    pre_value = relationship("PrefixOpc", backref="columns")

    @classmethod
    def truncate(cls, engine):
        with engine.begin() as conn:
            conn.execute(f"TRUNCATE TABLE {cls.__tablename__} CASCADE")


class WFControl(Base):
    __tablename__ = "wf_control"
    id = Column(Integer, primary_key=True)
    connector_id = Column(Integer, ForeignKey("connector.id"))
    last_update = Column(DateTime)
    source_file_version = Column(String(500), default="")
    source_file_size = Column(BigInteger, default=0)
    target_file_size = Column(BigInteger, default=0)
    chk_collect = Column(Boolean, default=False)
    chk_prepare = Column(Boolean, default=False)
    chk_map = Column(Boolean, default=False)
    chk_reduce = Column(Boolean, default=False)
    # igem_version = Column(String(15), default=v_version)
    status = Column(String(1), default="w")
    time_collect = Column(Integer, default=0)
    time_prepare = Column(Integer, default=0)
    time_map = Column(Integer, default=0)
    time_reduce = Column(Integer, default=0)
    row_collect = Column(Integer, default=0)
    row_prepare = Column(Integer, default=0)
    row_map = Column(Integer, default=0)
    row_reduce = Column(Integer, default=0)

    connector = relationship("Connector", backref="wf_controls")

    @classmethod
    def truncate(cls, engine):
        with engine.begin() as conn:
            conn.execute(f"TRUNCATE TABLE {cls.__tablename__} CASCADE")


class Logs(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True)
    process = Column(String(65))
    # igem_version = Column(String(15), default=v_version)
    created_at = Column(DateTime)
    status = Column(String(1), default="s")
    description = Column(Text, default=None)
