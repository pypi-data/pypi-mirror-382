# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    :
# @Author  :
# @Email   :
# @FileName: simple_math_tool.py


from agentuniverse.agent.action.tool.tool import Tool, ToolInput


class AddTool(Tool):
    def execute(self, input: str):
        a, b = input.split(',')
        result = float(a) + float(b)
        return result

    async def async_execute(self, input: str):
        a, b = input.split(',')
        result = float(a) + float(b)
        return result


class SubtractTool(Tool):
    def execute(self, input: str):
        a, b = input.split(',')
        result = float(a) - float(b)
        return result

    async def async_execute(self, input: str):
        a, b = input.split(',')
        result = float(a) - float(b)
        return result


class MultiplyTool(Tool):
    def execute(self, input: str):
        a, b = input.split(',')
        result = float(a) * float(b)
        return result

    async def async_execute(self, input: str):
        a, b = input.split(',')
        result = float(a) * float(b)
        return result


class DivideTool(Tool):
    def execute(self, input: str):
        a, b = input.split(',')
        result = float(a) / float(b)
        return result

    async def async_execute(self, input: str):
        a, b = input.split(',')
        result = float(a) / float(b)
        return result