#!/usr/bin/env python
# -*- coding: utf-8 -*-
#  Copyright (c) [2019] [name of copyright holder]
#  [py3comtrade] is licensed under Mulan PSL v2.
#  You can use this software according to the terms and conditions of the Mulan
#  PSL v2.
#  You may obtain a copy of Mulan PSL v2 at:
#           http://license.coscl.org.cn/MulanPSL2
#  THIS SOFTWARE IS PROVIDED ON CFGAN "AS IS" BASIS, WITHOUT WARRANTIES OF ANY
#  KIND, EITHER EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
#  NON-INFRINGEMENT, MERCHANTABILITY OR FIT FOR A PARTICULAR PURPOSE.
#  See the Mulan PSL v2 for more details.
import copy
import json
import os
import struct
import warnings
import zipfile
from typing import Any, List, Union

import numpy as np
import pandas as pd
from pydantic import Field

from py3comtrade.computation.basic_calc import convert_primary_secondary, convert_raw_instant
from py3comtrade.model.analog import Analog
from py3comtrade.model.configure import Configure
from py3comtrade.model.digital import Digital
from py3comtrade.model.digital import StatusRecord
from py3comtrade.model.dmf import DMF
from py3comtrade.model.exceptions import ComtradeException
from py3comtrade.model.nrate import Nrate
from py3comtrade.model.type.analog_enum import PsType
from py3comtrade.model.type.data_file_type import DataFileType
from py3comtrade.model.type.mode_enum import SampleMode
from py3comtrade.model.type.types import ChannelType, IdxType, ValueType
from py3comtrade.utils.comtrade_file_path import ComtradeFilePath, generate_comtrade_path
from py3comtrade.utils.file_tools import zip_files
from py3comtrade.utils.result import Result


class Comtrade(Configure, DMF):
    file_path: ComtradeFilePath = Field(default=None, description="录波文件路径")
    fault_point: int = Field(default=0, description="故障时刻采样点")
    sample_point: List[int] = Field(default_factory=list, description="采样点号")
    sample_time: List[int] = Field(default_factory=list, description="采样时间")
    digital_change: List[Digital] = Field(default_factory=list, description="变位开关量通道记录")

    @property
    def self(self) -> 'Comtrade':
        """返回类本身实例，支持链式调用"""
        return self

    def remove_fields(self, fields: Union[str, List[str]]) -> 'Comtrade':
        """
        移除指定的属性字段

        :param fields: 要移除的字段名或字段名列表
        :return: 类本身实例，支持链式调用
        """
        if isinstance(fields, str):
            fields = [fields]

        for field in fields:
            field_info = self.model_fields[field]
            if hasattr(field_info, 'default'):
                # 设置为默认值或 None
                setattr(self, field, field_info.default)
            else:
                setattr(self, field, None)
        return self

    def model_post_init(self, context: Any) -> None:
        """
        在模型初始化完成后自动执行
        """
        # 在这里执行初始化后的逻辑
        self.fault_point = self.get_zero_point()

    def filter(self,
                idx_type: str = "INDEX",
                analog_ids: list[int] = None,
                digital_ids: list[int] = None,
                is_values: bool = False,
                start_point: int = 0,
                end_point: int = None) -> 'Comtrade':
        """
        Comtrade过滤器，根据指定参数筛选数据通道,包含完整的通道参数和采样数值

        参数：
            idx_type: 索引类型，可选值：INDEX、CFGAN，默认值为INDEX
            analog_ids: 模拟通道标识列表，默认值为None
            digital_ids: 数字通道标识列表，默认值为None
            is_values: 是否返回通道值，默认值为False
            start_point: 起始采样点，默认值为0
            end_point: 结束采样点，默认值为None
        返回值：
            Comtrade对象，包含筛选后的通道数据  
        """
        if idx_type.upper() == "INDEX":
            idx_type = IdxType.INDEX
        elif idx_type.upper() == "CFGAN":
            idx_type = IdxType.CFGAN
        else:
            raise ComtradeException("索引参数错误")
        analogs = self.get_analog_selector(analog_ids=analog_ids, idx_type=idx_type, is_values=is_values)
        digitals = self.get_digital_selector(digital_ids=digital_ids, idx_type=idx_type, is_values=is_values)
        sample = self.cut_samples_points(start_point, end_point)

        return Comtrade(file_path=self.file_path,
                        sample_point=self.sample_point[start_point:end_point],
                        sample_time=self.sample_time[start_point:end_point],
                        digital_change=self.digital_change,
                        channel_num=self.channel_num,
                        analogs=analogs,
                        digitals=digitals,
                        sample=sample,
                        file_start_time=self.file_start_time,
                        fault_time=self.fault_time)

    def get_channel_data_range(self, channel_idx: Union[int, list[int]] = None,
                               idx_type: str = "INDEX",
                               channel_type: str = "ANALOG",
                               start_point: int = 0,
                               end_point: int = None,
                               cycle_num: float = None,
                               mode: str = "FORWARD",
                               output_value_type: str = "INSTANT",
                               output_primary: bool = False) -> Union[Analog, Digital, list[Digital], list[Analog]]:
        """
        根据指定通道标识获取指定采样范围内通道数据

        参数:
            channel_idx(int,list[int]) 通道索引值（index）、通道标识（cfgan）、通道索引值列表或通道标识列表
            idx_type: 索引类型，可选值：INDEX、CFGAN，默认值为INDEX
            channel_type:(str)通道类型，可选值：ANALOG、DIGITAL，默认值为ANALOG
            start_point(int) 开始采样点号，默认为0，标识第一个采样点
            end_point(int) 结束采样点号，默认为None，表示取所有采样点
            cycle_num(float)取周波数量，当该参数不为空时，end_point无效
            mode（str）取值方式，可选值：FORWARD、BACKWARD、CENTERED，默认向时间轴后方取值FORWARD
            output_value_type（str）输出值类型，可选值：INSTANT、RAW，默认值为INSTANT
            output_primary（bool）输出值是否为一次值，可选值：True、False，默认值为False
        返回值:
            选择的模拟量、开关量对象或列表，含采样数据
        """
        # 根据传入的采样值范围确定开始采样值点和结束采样点
        start_point, end_point, _ = self.get_cursor_sample_range(start_point, end_point, cycle_num, mode)
        # 根据通道索引值获取模拟量通道对象
        chanels = self.get_channel_obj(channel_idx, channel_type, idx_type)

        if not isinstance(chanels, list):
            chanels = [chanels]
        cns = []
        for channel in chanels:
            # 拷贝对象避免影响原始对象采样数值
            channel_new = copy.copy(channel)
            vs = channel.values[start_point:end_point + 1]

            # 如果是开关量通道，则直接返回原始采样值
            if channel_type.upper() == "DIGITAL":
                channel_new.values = vs
                cns.append(channel_new)
            else:
                # 如果是非开关量通道，需要判断输入和输出的格式是否一致，不一致则需要进行转换
                input_primary = channel.ps == PsType.P
                # 文件数值格式为原始采样值，输出格式为瞬时值
                # output_value_type = ValueType.INSTANT if output_value_type == "INSTANT" else ValueType.RAW
                if self.sample.value_type == ValueType.RAW and output_value_type.upper() == "INSTANT":
                    channel_new.values = convert_raw_instant(vs, channel.a, channel.b, channel.primary,
                                                             channel.secondary, channel.ps.value, output_primary)
                # 文件数值格式为瞬时值，输出格式为原始采样值
                elif self.sample.value_type == ValueType.INSTANT and output_value_type.upper() == "RAW":
                    channel_new.values = convert_raw_instant(vs, channel.a, channel.b, channel.primary,
                                                             channel.secondary, input_primary, output_primary,
                                                             to_instant=False)
                # 格式一致，判断文件模拟量数值类型和输出数值类型的一次值还是二次值是否一致
                else:
                    channel_new.values = convert_primary_secondary(vs, channel.primary, channel.secondary,
                                                                   input_primary, output_primary)
                cns.append(channel_new)

        return cns

    def get_channel_raw_data_range(self, channel_idx: Union[int, list[int]] = None,
                                   idx_type: IdxType = IdxType.INDEX,
                                   channel_type: ChannelType = ChannelType.ANALOG,
                                   start_point: int = 0,
                                   end_point: int = None) -> Union[list[Digital], list[Analog]]:
        """
        【不推荐使用】根据指定通道标识获取指定采样范围内通道原始采样值

        参数:
            channel_idx(int,list[int]) 通道索引值或通道索引值列表
            idx_type:(IdxType)通道标识类型，默认使用INDEX，支持按照通道数组索引值和cfg通道标识an两种方式
            channel_type(ChannelTyep)通道类型，默认模拟量ANALOG，支持模拟量和开关量两种类型
            start_point(int) 开始采样点，默认值0，包含该点。
            end_point(int) 结束采样点，默认值为None，为录波文件最大采样点，不包含该点。
        返回值:
            通道对象数组
        """
        warnings.warn(
            "get_channel_raw_data_range()方法已弃用，请使用get_channel_data_range()方法代替",
            DeprecationWarning,
            stacklevel=2
        )
        channel_type = channel_type.get_code()
        idx_type = idx_type.get_code()
        return self.get_channel_data_range(channel_idx, idx_type, channel_type, start_point, end_point,
                                           output_value_type="RAW")

    def get_channel_instant_data_range(self, channel_idx: Union[int, list[int]] = None,
                                       idx_type: IdxType = IdxType.INDEX,
                                       channel_type: ChannelType = ChannelType.ANALOG,
                                       start_point: int = 0,
                                       end_point: int = None,
                                       output_primary: bool = False) -> Union[list[Analog], list[Digital]]:
        """
        【不推荐使用】根据指定通道标识获取指定采样范围内模拟量瞬时采样值

        参数:
            channel_idx(int,list[int]) 通道索引值或通道索引值列表
            idx_type:(IdxType)通道标识类型，默认使用INDEX，支持按照通道数组索引值和cfg通道标识an两种方式
            channel_type(ChannelTyep)通道类型，默认模拟量ANALOG，支持模拟量和开关量两种类型
            start_point(int) 开始采样点，默认值0，包含该点。
            end_point(int) 结束采样点，默认值为None，为录波文件最大采样点，不包含该点。
            output_primary(bool)输出值是否是一次值
        返回值:
            通道对象数组
        """
        warnings.warn(
            "get_channel_instant_data_range()方法已弃用，请使用get_channel_data_range()方法代替",
            DeprecationWarning,
            stacklevel=2
        )
        channel_type = channel_type.get_code()
        idx_type = idx_type.get_code()
        return self.get_channel_data_range(channel_idx=channel_idx, idx_type=idx_type, channel_type=channel_type,
                                           start_point=start_point, end_point=end_point,
                                           output_value_type="INSTANT", output_primary=output_primary)

    def get_digital_change(self) -> list[Digital]:
        """
        获取所有发生变位的开关量
        """
        if self.digital_change is None:
            self.analyze_digital_change_status()
        return self.digital_change

    def analyze_digital_change_status(self):
        """
        根据开关量采样值计算变化点号及幅值
        """
        self.digital_change = []
        for digital in self.digitals:
            value = np.array(digital.values)
            digital.change_status.append(StatusRecord(sample_point=self.sample_point[0],
                                                      timestamp=self.sample_time[0],
                                                      status=value[0].item()))
            if value.min() != value.max():
                # 找出变化点：当前值与前一个值不同
                change_indices = np.where(value[:-1] != value[1:])[0] + 1
                # 获取变化后的值
                change_vs = value[change_indices]
                for i in range(len(change_vs)):
                    digital.change_status.append(StatusRecord(sample_point=change_indices[i].item(),
                                                              timestamp=self.sample_time[change_indices[i].item()],
                                                              status=change_vs[i].item()))
                self.digital_change.append(digital)

    def _update_configure(self, 
                        analogs: List[Analog] = None, 
                        diagitals: List[Digital] = None,
                          nrates: List[Nrate] = None,
                          data_file_type: str = None
                          ):
        """更新配置文件参数
        参数:
            analogs(List[Analog]) 模拟量通道对象数组
            diagitals(List[Digital]) 开关量通道对象数组
            nrates(List[Nrate]) 采样段
            data_file_type(str) 文件格式,可选值："BINARY"、"ASCII"，默认值为"BINARY"
        """
        # TODO: 增加校验功能，要验证通道数量、采样点数量和通道对象是否一致
        # 更新文件格式
        if data_file_type is not None:
            self.sample.data_file_type = DataFileType.from_string(data_file_type)
        if  analogs is not None:
            # 更新模拟量通道对象
            self.analogs = [analog for analog in analogs if analog.values is not None and analog.selected]
            self.channel_num.analog_num = len(self.analogs)
        if diagitals is not None:
            # 更新开关量通道对象
            self.digitals = [digital for digital in diagitals if digital.values is not None and digital.selected]
            self.channel_num.digital_num = len(self.digitals)
        # 更新采样信息
        self.sample.channel_num = self.channel_num
        # 更新采样频率
        if nrates is not None:
            self.sample.nrate_num = len(nrates)
            self.sample.nrates = nrates
            self.sample.calc_sampling()

    def save_comtrade(self,
                      file_path: str,
                      data_file_type: str = "BINARY",
                      compress: bool = False):
        """
        将comtrade对象保存为文件
        参数:
            file_path(str) 保存路径,后缀名可选
            data_file_type(str) 保存格式,默认保存为二进制文件
            compress(bool) 是否压缩为zip文件,默认为False
        返回:
            ComtradeFilePath对象或压缩文件路径
        """
        cfp = generate_comtrade_path(file_path)
        # 更换configure参数
        self._update_configure(data_file_type=data_file_type)
        # 写入cfg文件
        super().write_cfg_file(str(cfp.cfg_path))
        if data_file_type.upper() == "ASCII":
            self._write_ascii_file(str(cfp.dat_path))
        else:
            self._write_binary_file(str(cfp.dat_path))

        if compress:
            zip_file_path = f"{cfp.cfg_path.stem}.zip"
            zip_file = zip_files([str(cfp.cfg_path), str(cfp.dat_path)],zip_file_path)
            return Result(msg="文件保存成功",data=zip_file)
        return Result(msg="文件保存成功",data=cfp)

    def _write_ascii_file(self, output_file_path: str):
        """
        将数据写入ASCII格式文件

        参数:
            output_file_path: 输出文件路径
        """
        analog_datas = self.get_channel_data_range(output_value_type="INSTANT")
        analog_values = np.array([analog.values for analog in analog_datas])
        digital_values = np.array([digital.values for digital in self.digitals])
        # 组合数据
        data = np.column_stack((
            self.sample_point,
            self.sample_time,
            analog_values.T,
            digital_values.T
        ))

        # 写入CSV文件
        pd.DataFrame(data).to_csv(output_file_path, header=False, index=False)

    def _write_binary_file(self, output_file_path: str):
        """
        将数据写入二进制格式文件，符合COMTRADE标准格式

        参数:
            output_file_path: 输出文件路径
        """
        # 获取数据并转置，使每行代表一个采样点
        analog_datas = self.get_channel_data_range(output_value_type="INSTANT")
        analog_values = np.array([analog.values for analog in analog_datas]).T
        digital_values = np.array([digital.values for digital in self.digitals]).T
        # 根据数据类型确定模拟量格式
        if self.sample.data_file_type == DataFileType.BINARY32:
            analog_fmt = '<i'  # 4个字节小端序有符号整数
        elif self.sample.data_file_type == DataFileType.FLOAT32:
            analog_fmt = '<f'  # 4个字节小端序浮点数
        else:
            analog_fmt = '<h'  # 2个字节小端序有符号短整数

        with open(output_file_path, 'wb') as f:
            # 遍历每个采样点
            for i in range(len(self.sample_point)):
                # 1. 写入采样点号 (4个字节小端序有符号整数)
                sample_point_bytes = struct.pack('<i', int(self.sample_point[i]))
                f.write(sample_point_bytes)

                # 2. 写入采样时间 (4个字节小端序浮点数)
                sample_time_bytes = struct.pack('<f', float(self.sample_time[i]))
                f.write(sample_time_bytes)

                # 3. 写入模拟量数据
                for j in range(len(self.analogs)):  # 遍历每个模拟通道
                    if i < analog_values.shape[0] and j < analog_values.shape[1]:
                        analog_value = int(analog_values[i, j])
                    else:
                        analog_value = 0
                    analog_bytes = struct.pack(analog_fmt, analog_value)
                    f.write(analog_bytes)

                # 4. 写入数字量数据 (将最多16个数字量通道状态打包成2个字节)
                for word_idx in range(int(self.sample.digital_sampe_word / 2)):
                    digital_word = 0
                    # 处理当前16位字中的每一位
                    for bit_idx in range(16):
                        channel_idx = word_idx * 16 + bit_idx
                        # 检查是否还有数字量通道需要处理
                        if channel_idx < len(self.digitals):
                            if i < digital_values.shape[0] and channel_idx < digital_values.shape[1]:
                                digital_status = int(digital_values[i, channel_idx])
                                if digital_status != 0:
                                    digital_word |= (1 << bit_idx)

                    # 将16位数字量状态打包成2个字节无符号短整数
                    digital_bytes = struct.pack('<H', digital_word)
                    f.write(digital_bytes)

    def to_json(self, file_path: str=None) -> dict:
        """
        将comtrade对象转换为JSON格式

        参数：
            file_path(str): 文件保存路径,当路径为空输出json对象
        返回值:
            JSON对象
        """
        comtrade_json =  self.model_dump_json(by_alias=True,exclude_none=True,round_trip=True)
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(comtrade_json, f, ensure_ascii=False,indent=2)
                return Result(msg=f"文件写入成功",data=file_path)
            except Exception as e:
                return Result(code=500, msg=f"{file_path}文件写入失败",data=e)
        return comtrade_json

    def to_csv(self,
               file_path: str,
               samp_point_num_title: bool = True,
               sample_time_title: bool = True
               ):
        """
        将comtrade对象保存为csv文件

        参数：
            file_path(str): 文件保存路径
            samp_point_num_title(bool):是否添加采样点号行,默认添加
            sample_time_title(bool):是否添加采样时间行,默认为添加
        返回值:
            ComtradeFilePath对象
        """
        try:
            with open(file_path, 'w', encoding='gbk') as f:
                if samp_point_num_title:
                    f.write(f'采样点号,{",".join(map(str, self.sample_point))}\n')
                if sample_time_title:
                    f.write(f'采样时间,{",".join(map(str, self.sample_time))}\n')
                for analog in self.analogs:
                    if analog.values is not None:
                        f.write(f'{analog.name},{",".join(map(str, analog.values))}\n')
                for digital in self.digitals:
                    if digital.values is not None:
                        f.write(f'{digital.name},{",".join(map(str, digital.values))}\n')
            return Result(code=200, msg=f"文件写入成功",data=file_path)
        except Exception as e:
            return Result(code=500, msg=f"{file_path}文件写入失败",data=e)
    
    def to_excel(self,
               file_path: str,
               samp_point_num_title: bool = True,
               sample_time_title: bool = True
               ):
        """
        将comtrade对象保存为excel文件

        参数：
            file_path(str): 文件保存路径
            samp_point_num_title(bool):是否添加采样点号行,默认添加
            sample_time_title(bool):是否添加采样时间行,默认为添加
        返回值:
            ComtradeFilePath对象
        """
        try:
            # 创建DataFrame
            data_dict = {}

            # 添加采样点号
            if samp_point_num_title:
                data_dict['采样点号'] = self.sample_point

            # 添加采样时间
            if sample_time_title:
                data_dict['采样时间'] = self.sample_time

            # 添加模拟量通道数据
            for analog in self.analogs:
                if analog.values is not None:
                    data_dict[analog.name] = analog.values

            # 添加开关量通道数据
            for digital in self.digitals:
                if digital.values is not None:
                    data_dict[digital.name] = digital.values

            # 创建DataFrame并保存为Excel
            df = pd.DataFrame(data_dict)
            df.to_excel(file_path, index=False)

            return Result(code=200, msg=f"文件写入成功",data=file_path)
        except Exception as e:
            return Result(code=500, msg=f"{file_path}文件写入失败",data=e)
