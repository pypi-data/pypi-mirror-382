"""
pip install SQLAlchemy -i https://pypi.tuna.tsinghua.edu.cn/simple
"""
try:
    import sqlalchemy
except ImportError:
    print("请执行如下命令安装 SQLAlchemy：")
    print('pip install SQLAlchemy -i https://pypi.tuna.tsinghua.edu.cn/simple')
    exit(1)
from .base import Base
from .base_models import DBModel
