# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description:
# @Time   : 2023-05-28 18:40
# @Author : 毛鹏

from pydantic import BaseModel

from mangoautomation.enums import ElementOperationEnum
from mangotools.models import MysqlConingModel, MethodModel


class EnvironmentConfigModel(BaseModel):
    id: int
    test_object_value: str
    db_c_status: bool
    db_rud_status: bool
    mysql_config: MysqlConingModel | None = None


class ElementListModel(BaseModel):
    exp: int
    loc: str
    sub: int | None = None
    is_iframe: int | None


class ElementModel(BaseModel):
    id: int
    type: ElementOperationEnum
    name: str | None
    elements: list[ElementListModel] = []
    sleep: int | None
    ope_key: str | None
    ope_value: list[MethodModel] | None = None
    sql_execute: list[dict] | None = None
    custom: list[dict] | None = None
    condition_value: dict | None = None
    func: str | None = None


class ElementListResultModel(BaseModel):
    loc: str | None = None
    exp: int | None = None
    ele_quantity: int = 0
    element_text: str | None = None
    sub: int | None = None
    is_iframe: int | None


class ElementResultModel(BaseModel):
    id: int
    name: str | None = None
    sleep: int | None = None

    type: int
    ope_key: str | None = None
    ope_value: list[MethodModel] | None = None
    sql_execute: list[dict] | None = None
    custom: list[dict] | None = None
    condition_value: dict | None = None
    ass_msg: str | None = None

    elements: list[ElementListResultModel] = []
    status: int = 0
    error_message: str | None = None
    picture_path: str | None = None
    picture_name: str | None = None

    next_node_id: int | None = None
