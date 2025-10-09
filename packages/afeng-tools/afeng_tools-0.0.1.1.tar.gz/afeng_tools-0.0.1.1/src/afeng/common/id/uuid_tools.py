"""
uuid相关的工具
"""
import uuid

def get_uuid():
    """
    获取一个uuid（36位）
    :return:
    """
    return str(uuid.uuid4())

def get_uuid32():
    """
    获取一个32位uuid
    :return:
    """
    return get_uuid().replace('-', '')


def get_uuid4():
    """
    获取一个4位uuid
    :return:
    """
    return get_uuid32()[:4]

def get_uuid8():
    """
    获取一个8位uuid
    :return:
    """
    return get_uuid32()[:8]

def get_uuid16():
    """
    获取一个16位uuid
    :return:
    """
    return get_uuid32()[:16]

