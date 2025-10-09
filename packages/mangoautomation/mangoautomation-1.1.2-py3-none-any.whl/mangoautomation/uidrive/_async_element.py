# -*- coding: utf-8 -*-
# @Project: 芒果测试平台
# @Description: 
# @Time   : 2025-04-12 15:53
# @Author : 毛鹏
import asyncio
import os
import random
import traceback
from typing import Optional

from playwright._impl._errors import TargetClosedError, Error

from mangotools.assertion import MangoAssertion
from mangotools.decorator import async_retry
from mangotools.enums import StatusEnum
from ..enums import ElementOperationEnum, DriveTypeEnum
from ..exceptions import MangoAutomationError
from ..exceptions.error_msg import *
from ..models import ElementResultModel, ElementModel, ElementListResultModel
from ..uidrive.android import AndroidDriver
from ..uidrive.web.async_web import AsyncWebDevice, AsyncWebAssertion


class AsyncElement(AsyncWebDevice, AndroidDriver):

    def __init__(self, base_data, drive_type: int, ):
        super().__init__(base_data)
        self.drive_type = drive_type
        self.element_model: Optional[ElementModel | None] = None
        self.element_result_model: Optional[ElementResultModel | None] = None
        self.element_list_model: Optional[list[ElementModel] | None] = None
        self.test_data = self.base_data.test_data

    async def open_device(self, is_open: bool = False):
        if self.drive_type == DriveTypeEnum.WEB.value:
            await self.open_url(is_open)
        elif self.drive_type == DriveTypeEnum.ANDROID.value:
            self.open_app()
        elif self.drive_type == DriveTypeEnum.DESKTOP.value:
            pass
        else:
            self.base_data.log.debug(f'不存在这个类型，如果是非管理员看到这种提示，请联系管理员')
            raise Exception('不存在的设备类型')

    async def element_main(self,
                           element_model: ElementModel,
                           element_list_model: list[ElementModel] | None = None) -> ElementResultModel:
        self.element_model = element_model
        self.element_list_model = element_list_model
        self.element_result_model = ElementResultModel(
            id=self.element_model.id,
            name=self.element_model.name,
            sleep=self.element_model.sleep,

            type=self.element_model.type.value,
            ope_key=self.element_model.ope_key,
            sql_execute=self.element_model.sql_execute,
            custom=self.element_model.custom,

            status=StatusEnum.FAIL.value,
        )
        try:
            await self.init_element()
            await self.__main()
            if self.element_model.sleep:
                await asyncio.sleep(self.element_model.sleep)
            self.element_result_model.status = StatusEnum.SUCCESS.value
            self.element_result_model.error_message = None
        except MangoAutomationError as error:
            self.base_data.log.debug(f'操作元素异常-1，类型：{type(error)}，失败详情：{error}')
            await self.__error(error.msg)
        except TargetClosedError as error:
            self.base_data.setup()
            self.base_data.log.debug(
                f'操作元素异常-2，类型：{type(error)}，失败详情：{error}，失败明细：{traceback.format_exc()}')
            await self.__error(ERROR_MSG_0010[1], False)
        except Error as error:
            self.base_data.log.error(
                f'操作元素异常-3，类型：{type(error)}，失败详情：{error}，失败明细：{traceback.format_exc()}')
            await self.__error(f'未知错误失败，请检查测试数据，如果需要明确的提示请联系管理员，提示：{error.message}')
        except Exception as error:
            error_msg = f'未知错误失败，请检查测试数据，如果需要明确的提示请联系管理员，提示：{error.args}'
            if hasattr(error, 'msg'):
                error_msg = error.msg
            self.base_data.log.error(
                f'操作元素异常-4，类型：{type(error)}，失败详情：{error}，失败明细：{traceback.format_exc()}')
            await self.__error(error_msg)
        return self.element_result_model

    @async_retry()
    async def __main(self):
        self.base_data.verify_equipment(self.drive_type)
        if self.element_model.type == ElementOperationEnum.OPE:
            await self.__ope()
        elif self.element_model.type == ElementOperationEnum.ASS:
            await self.__ass()
        elif self.element_model.type == ElementOperationEnum.SQL:
            await self.__sql()
        elif self.element_model.type == ElementOperationEnum.CUSTOM:
            await self.__custom()
        elif self.element_model.type == ElementOperationEnum.CONDITION:
            await self.__condition()
        elif self.element_model.type == ElementOperationEnum.PYTHON_CODE:
            await self.__python_code()
        else:
            raise MangoAutomationError(*ERROR_MSG_0015)

    async def init_element(self):
        try:
            for i in self.element_model.elements:
                i.loc = self.base_data.test_data.replace(i.loc)
                i.sub = self.base_data.test_data.replace(i.sub)
            self.element_model.sleep = self.base_data.test_data.replace(self.element_model.sleep)
            self.element_result_model.sleep = self.element_model.sleep

        except MangoAutomationError as error:
            self.base_data.log.error(f'操作元素解析数据失败，类型：{type(error)}, 详情：{error}')
            raise MangoAutomationError(error.code, error.msg)

    async def __ope(self):
        method_name = getattr(self.element_model, 'ope_key', None)
        if not method_name:
            self.base_data.log.debug('操作失败-1，ope_key 不存在或为空')
            raise MangoAutomationError(*ERROR_MSG_0048)
        if not hasattr(self, method_name):
            self.base_data.log.debug(f'操作失败-2，方法不存在: {method_name}')
            raise MangoAutomationError(*ERROR_MSG_0048)
        if not callable(getattr(self, method_name)):
            self.base_data.log.debug(f'操作失败-3，属性不可调用: {method_name}')
            raise MangoAutomationError(*ERROR_MSG_0048)
        if self.element_model.ope_value is None:
            raise MangoAutomationError(*ERROR_MSG_0054)
        await self.__ope_value()
        if self.drive_type == DriveTypeEnum.WEB.value:
            await self.web_action_element(
                self.element_model.name,
                self.element_model.ope_key,
                {i.f: i.v for i in self.element_model.ope_value}
            )
        elif self.drive_type == DriveTypeEnum.ANDROID.value:
            self.a_action_element(
                self.element_model.name,
                self.element_model.ope_key,
                {i.f: i.v for i in self.element_model.ope_value}
            )
        else:
            pass
        self.element_result_model.ope_value = self.element_model.ope_value
        for i in self.element_result_model.ope_value:
            if not isinstance(i.v, str):
                i.v = str(i.v)

    async def __ass(self, _ope_value: dict | None = None):
        if self.element_model.ope_value is None:
            raise MangoAutomationError(*ERROR_MSG_0054)
        await self.__ope_value(True)
        ope_value = {i.f: i.v for i in self.element_model.ope_value}
        if _ope_value is not None:
            ope_value.update(_ope_value)
        try:
            if self.drive_type == DriveTypeEnum.WEB.value:
                self.element_result_model.ass_msg = await self.web_assertion_element(
                    self.element_model.name,
                    self.element_model.ope_key,
                    ope_value
                )
            elif self.drive_type == DriveTypeEnum.ANDROID.value:
                self.element_result_model.ass_msg = self.a_assertion_element(
                    self.element_model.name,
                    self.element_model.ope_key,
                    ope_value
                )
            else:
                pass
        except MangoAutomationError as error:
            self.element_result_model.ass_msg = error.msg
            raise error
        self.element_result_model.ope_value = self.element_model.ope_value
        for i in self.element_result_model.ope_value:
            if not isinstance(i.v, str):
                i.v = str(i.v)

    async def __sql(self):
        async def run(sql, key_list):
            result_list: list[dict] = self.base_data.mysql_connect.condition_execute(sql)
            self.base_data.log.debug(f'sql参数->key:{sql}，value:{result_list}')
            if not isinstance(result_list, list) and not len(result_list) > 0:
                raise MangoAutomationError(*ERROR_MSG_0036, value=(self.element_model.sql_execute,))
            self.base_data.test_data.set_sql_cache(key_list, result_list[0])

        if self.base_data.mysql_connect:
            for i in self.element_model.sql_execute:
                await run(i.get('sql'), i.get('key_list'))

    async def __custom(self):
        for i in self.element_model.custom:
            self.base_data.test_data.set_cache(i.get('key'), self.base_data.test_data.replace(i.get('value')))

    async def __condition(self):
        error_list = []
        for i in self.element_list_model:
            try:
                condition_value = self.base_data.test_data.replace(i.condition_value)
                self.base_data.log.debug(f'执行条件判断数据：{self.element_model.id}，{condition_value}')
                await self.__ass(condition_value)
                self.element_result_model.next_node_id = i.id
                return
            except Exception as error:
                self.base_data.log.debug(f'节点判断中-错误：{error}，明细：{traceback.print_exc()}')
                error_list.append(error)
        raise error_list[0]

    async def __python_code(self):
        self.base_data.log.debug(f'执行python函数：{self.element_model.func}')
        global_namespace = {}
        exec(self.element_model.func, global_namespace)
        global_namespace['func'](self)

    async def __ope_value(self, is_ass: bool = False):
        try:
            ope_key = 'actual' if is_ass else 'locating'
            for i in self.element_model.ope_value:
                if i.f == ope_key and self.element_model.elements:
                    random_element = random.randint(0, len(self.element_model.elements) - 1)
                    find_params = {
                        'name': self.element_model.name,
                        '_type': self.element_model.type,
                        'exp': self.element_model.elements[random_element].exp,
                        'loc': self.element_model.elements[random_element].loc,
                        'sub': self.element_model.elements[random_element].sub
                    }
                    if self.drive_type == DriveTypeEnum.WEB.value:
                        loc, ele_quantity, element_text = await self.web_find_ele(
                            **find_params, is_iframe=self.element_model.elements[random_element].is_iframe)
                    elif self.drive_type == DriveTypeEnum.ANDROID.value:
                        loc, ele_quantity, element_text = self.a_find_ele(**find_params)
                    else:
                        loc, ele_quantity, element_text = None, 0, None
                    new_element = ElementListResultModel(
                        exp=self.element_model.elements[random_element].exp,
                        loc=self.element_model.elements[random_element].loc,
                        sub=self.element_model.elements[random_element].sub,
                        ele_quantity=ele_quantity,
                        element_text=element_text,
                        is_iframe=self.element_model.elements[random_element].is_iframe
                    )

                    element_exists = any(
                        existing.exp == new_element.exp and
                        existing.loc == new_element.loc and
                        existing.sub == new_element.sub and
                        existing.is_iframe == new_element.is_iframe
                        for existing in self.element_result_model.elements
                    )

                    if not element_exists:
                        self.element_result_model.elements.append(new_element)
                    if is_ass:
                        if callable(getattr(AsyncWebAssertion, self.element_model.ope_key, None)):
                            i.v = loc
                        elif callable(getattr(MangoAssertion(), self.element_model.ope_key, None)):
                            i.v = element_text
                    else:
                        i.v = loc
                i.v = self.base_data.test_data.replace(i.v)

        except AttributeError as error:
            self.base_data.log.debug(
                f'获取操作值失败-1，类型：{type(error)}，失败详情：{error}，失败明细：{traceback.format_exc()}')
            raise MangoAutomationError(*ERROR_MSG_0027)

    async def __error(self, msg: str, is_screenshot: bool = True):
        try:
            self.element_result_model.status = StatusEnum.FAIL.value
            self.element_result_model.error_message = msg
            self.base_data.log.debug(
                f"""
                元素操作失败----->
                元 素 对 象：{self.element_model.model_dump() if self.element_model else self.element_model}
                元素测试结果：{
                self.element_result_model.model_dump() if self.element_result_model else self.element_result_model}
                """
            )
            if is_screenshot:
                file_name = f'失败截图-{self.element_model.name}{self.base_data.test_data.get_time_for_min()}.jpg'
                file_path = os.path.join(self.base_data.screenshot_path, file_name)
                await self.__error_screenshot(file_path)
                self.element_result_model.picture_path = file_path
                self.element_result_model.picture_name = file_name
        except MangoAutomationError as error:
            self.element_result_model.error_message += f'执行过程中发生失败，准备截图时截图失败，失败原因：{error.msg}'
        except Exception as error:
            self.base_data.log.error(
                f'截图失败未知异常-1，类型：{type(error)}，失败详情：{error}，失败明细：{traceback.format_exc()}')

    async def __error_screenshot(self, file_path):
        if self.drive_type == DriveTypeEnum.WEB.value:
            await self.w_screenshot(file_path)
        elif self.drive_type == DriveTypeEnum.ANDROID.value:
            self.a_screenshot(file_path)
        else:
            pass
