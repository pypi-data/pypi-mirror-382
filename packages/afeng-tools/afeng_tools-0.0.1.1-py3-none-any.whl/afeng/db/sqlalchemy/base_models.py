import json
from datetime import datetime, date, time
from typing import Any, Dict

from sqlalchemy import Column, DateTime, func, BigInteger, Float, Boolean

from afeng.db.sqlalchemy.base import Base


class DBModel(Base):
    """数据库模型基类"""
    __abstract__ = True
    model_config = {"arbitrary_types_allowed": True}
    id = Column(BigInteger, comment='主键', primary_key=True, index=True, autoincrement=True)
    order_num = Column(Float, comment='排序值', default=100)
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime, comment='创建时间', default=func.now())
    created_by = Column(BigInteger, comment='创建人', default=None)
    updated_at = Column(DateTime, comment='修改时间', default=func.now(), onupdate=func.now())
    updated_by = Column(BigInteger, comment='修改人')
    is_deleted = Column(Boolean, comment='是否已经删除', default=False)
    delete_at = Column(DateTime, comment='删除时间', default=None)
    delete_by = Column(BigInteger,  comment='删除人', default=None)

    def model_dump(self):
        """为Pydantic兼容添加model_dump方法"""
        return self.to_dict()

    def model_dump_json(self):
        """为Pydantic兼容添加model_dump_json方法"""
        return self.to_json()


    def to_dict(self) -> Dict[str, Any]:
        """转换为字典，处理枚举类型和JSON字段"""
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            # 处理枚举类型
            if hasattr(value, 'value'):
                result[c.name] = value.value
            # 处理JSON字段
            elif c.name == 'options' and value is not None:
                # 如果options是字符串格式的JSON，尝试解析它
                if isinstance(value, str):
                    try:
                        result[c.name] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result[c.name] = value
                else:
                    result[c.name] = value
            # 处理其他JSON字段
            elif hasattr(c.type, 'python_type') and c.type.python_type == dict and value is not None:
                if isinstance(value, str):
                    try:
                        result[c.name] = json.loads(value)
                    except (json.JSONDecodeError, TypeError):
                        result[c.name] = value
                else:
                    result[c.name] = value
            else:
                result[c.name] = value
        return result

    def to_json(self, date_format="%Y-%m-%d", datetime_formate="%Y-%m-%d %H:%M:%S",
                time_formate="%H:%M:%S"):
        data_dict = self.to_dict()
        for key, value in data_dict.items():
            if isinstance(value, datetime):
                data_dict[key] = value.strftime(datetime_formate)
            elif isinstance(value, date):
                data_dict[key] = value.strftime(date_format)
            elif isinstance(value, time):
                data_dict[key] = value.strftime(time_formate)
        return data_dict

    def get_update_data(self):
        """获取更新字段
        使用示例：
        # 执行批量更新
        await session.execute(
            update(Model)
            .where(Model.id == new_model.id)
            .values(**update_data)
        )
        """
        return {k: v for k, v in self.__dict__.items()
                if not k.startswith('_') and k != 'id'}