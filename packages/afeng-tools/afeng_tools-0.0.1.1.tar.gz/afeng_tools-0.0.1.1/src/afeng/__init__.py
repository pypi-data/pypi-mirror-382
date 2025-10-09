try:
    import pydantic
except ImportError:
    print("请执行如下命令安装 pydantic：")
    print('pip install pydantic -i https://pypi.tuna.tsinghua.edu.cn/simple')
    exit(1)