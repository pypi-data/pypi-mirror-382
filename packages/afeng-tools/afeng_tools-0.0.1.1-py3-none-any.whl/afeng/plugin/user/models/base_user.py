from sqlalchemy import Boolean, Column, String, DateTime, BigInteger, UniqueConstraint, func

from afeng.common.id.code_generator import code_generator
from afeng.db.sqlalchemy import DBModel


class BaseUser(DBModel):
    """基础用户模型：存储用户基本信息"""
    __abstract__ = True
    __tablename__ = "tb_user"
    user_id = Column(BigInteger, comment="用户ID", nullable=False, unique=True, index=True, default=lambda: next(code_generator))
    username = Column(String, unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String, unique=True, index=True, nullable=False, comment="电子邮箱")
    hashed_password = Column(String, nullable=False, comment="加密密码")
    nick_name = Column(String, index=True, comment="昵称")
    avatar = Column(String, comment="头像")
    last_login_time = Column(DateTime, default=func.now(), comment="上次登录时间")
    is_active = Column(Boolean, default=False, comment="是否激活")
    active_time = Column(DateTime, comment="激活时间")
    active_reason = Column(String, comment="激活原因")
    # 关键：显式添加唯一约束，确保生成 UNIQUE (user_id)
    __table_args__ = (
        UniqueConstraint('user_id', name='uq_user_id'),  # 强制确保 user_id 唯一
    )