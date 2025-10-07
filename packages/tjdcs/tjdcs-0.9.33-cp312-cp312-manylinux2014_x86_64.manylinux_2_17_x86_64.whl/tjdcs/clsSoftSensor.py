import sys
import os
import time
import json
import math
import uuid
import importlib.util
import logging
import numpy as np
from pathlib import Path
from collections import deque, defaultdict
from collections.abc import Callable
from typing import Optional, Sequence
from dataclasses import dataclass, fields
# from tjdcs import sFilter, WatchDog
from tjdcs.algorithm.tjWatchDog import WatchDog
try:
    from OPCGatePy.opc_calc_task import OPCCalcTask
except ImportError:
    OPCCalcTask = None

from tjdcs.algorithm.tjSoftSensor import SoftSensorBiasUpdate, LabDataRecorder

# class SoftSensorBiasUpdate(tjSoftSensor.SoftSensorBiasUpdate):
#     r'''
#     软测量的偏差校正。
#     计算预测值(prd_data)与化验值(lab_data)的偏差。
#     '''
#     def __init__(self, name: str = 'SoftSensor', filter_tao: float = 5, abs_threshold: float = 1e-6, prd_len: int = 28800, const_len: int = 60) -> None:
#         r'''
#         parameters
#         ----------
#         name: str, name of the soft sensor
#         filter_tao: the returned bias is filtered by a one order filter which is denoted as 1/(filter_tao*s+1)
#             the time unit is sample
#             if filter_tao is zero, return the bias immediately
#         abs_threshold (float 1e-6 - inf): the bias renew only when abs(prd_data-lab_data)>=abs_threshold
#             otherwise the bias is hold (remain as the last return). 
#         prd_len: length of the storage of prd_data list
#         const_len (int >=0 ): bias update won't take active unless lab_data remain const for const_len
#             if const_len is zero, bias update will take active immediately.
#             the time unit is sample
#         '''
#         return super().__init__(name, filter_tao, abs_threshold, prd_len, const_len)
    
#     def get_name(self) -> str:      
#         r'''
#         return the name of the soft sensor
#         '''
#         return super().get_name()
    
#     def get_update_flag(self) -> bool:
#         r'''
#         return the flag of bias update
#         '''
#         return super().get_update_flag()
    
#     def get_bias(self) -> float:
#         r'''
#         return the bias
#         '''
#         return super().get_bias()
    
#     def get_lab_data(self) -> float:
#         r'''
#         return the lab_data
#         '''
#         return super().get_lab_data()
    
#     def get_lab_time(self) -> float:
#         r'''
#         return the lab_time
#         '''
#         return super().get_lab_time()
    
#     def get_prd_data_at_labtime(self) -> float:
#         r'''
#         return the prd_data at lab_time
#         '''
#         return super().get_prd_data_at_labtime()

#     def run(self, prd_data: float, lab_data: float, lab_time: float, prd_time: float = None) -> float:
#         r'''
#         软测量的偏差校正。
#         此函数应该在每个采样时刻运行，计算预测值(prd_data)与化验值(lab_data)的偏差。
#         将偏差返回值加入到预测值中，即可得到校正后的预测值。
#         在初始化时可设置滤波系数、化验值保持自定义时长后更新。        

#         parameters
#         ----------
#         prd_data: float, predict data, usually is the data that the soft sensor predict.
#         lab_data: float, usually is the analysis data from the laboratory.
#         lab_time: float, usually is the time that the laboratory gets the sample.
#         prd_time: optional, float, predict time, usually is the time that the soft sensor predict the prd_data
#             if prd_time is None, use time.time() instead.
        
#         returns
#         -------
#         filtered bias

#         Notes
#         -----
#         lab_time and prd_time should at the same time measured system
#         '''
#         return super().run(prd_data, lab_data, lab_time, prd_time)


class OPCItem:
    def __init__(self, tag: str, 
                 description: str = '', 
                 time_shift: int = 0,  # time shift, if you want previous value
                 prefix: str = '', 
                 ini_value = float('nan'),  # value of OPCItem can be anything.
                 lo_limit: float = -float('inf'), 
                 hi_limit: float = float('inf'),
                 save_last_good_value: bool = False):
        self.tag = f"{prefix.strip('.')}.{tag}" if prefix else tag
        self.description = description
        self.time_shift = abs(time_shift)
        self.lo_limit = lo_limit
        self.hi_limit = hi_limit
        self.save_last_good_value = save_last_good_value

        if self.is_value_valid(ini_value):
            self._value = ini_value
        else:
            if self.save_last_good_value:
                self._value = 0.5*(self.lo_limit+self.hi_limit)
                if math.isnan(self._value):
                    self._value = 0.0
                assert self.is_value_valid(self._value)
            else:
                self._value = float('nan')

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, new_value):
        if self.is_value_valid(new_value):
            self._value = new_value
        else:
            if not self.save_last_good_value:
                self._value = np.nan
                


    def is_value_valid(self, v) -> bool:
        if isinstance(v, (int, float)):
            return self.lo_limit <= v <= self.hi_limit
        return True

    def __str__(self):
        return (f"Tag: {self.tag}, Desc: {self.description}, Shift: {self.time_shift}s, "
                f"Value: {self.value}, LO: {self.lo_limit}, HI: {self.hi_limit}")

    def __repr__(self):
        return f"OPCItem(tag='{self.tag}', value={self.value})"

    def to_dict(self):
        return {
            "tag": self.tag,
            "description": self.description,
            "value": self.value,
            "lo_limit": self.lo_limit,
            "hi_limit": self.hi_limit,
            "time_shift": self.time_shift
        }


def load_predict_module(file_path: str,
                        opclist_name: str = 'OPCItem_list',
                        predict_fun_name: str = 'predict',
                        ) -> tuple[Sequence[OPCItem], Callable[[], float]]:
    if not file_path or not os.path.exists(file_path):
        raise FileNotFoundError(f"Prediction module path not found: {file_path}")
    
    module_name = f"predict_{uuid.uuid4().hex}"  # 避免冲突
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    predict_module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = predict_module

    try:
        spec.loader.exec_module(predict_module)
    except Exception as e:
        raise ImportError(f"Failed to load module from {file_path}: {e}")

    if hasattr(predict_module, opclist_name):
        OPCItem_list = getattr(predict_module, opclist_name)
        if not isinstance(OPCItem_list, list) or not all(isinstance(item, OPCItem) for item in OPCItem_list):
            raise ValueError("OPCItem_list must be a list of OPCItem objects.")
    else:
        raise AttributeError(f"Missing required attribute '{opclist_name}' in module {file_path}")

    if hasattr(predict_module, predict_fun_name):
        predict_function = getattr(predict_module, predict_fun_name)
        if not callable(predict_function):
            raise TypeError(f"'{predict_fun_name}' is not callable in module {file_path}")
    else:
        raise AttributeError(f"Missing required attribute '{predict_fun_name}' in module {file_path}")
    
    return OPCItem_list, predict_function


@dataclass
class SSTaskConfig:
    # 软测量名称，用于标识任务
    ss_name: str = 'SS_Test'
    
    # 软测量模型预测脚本的路径
    ss_predict_file_path: str = r".\predict.py"
    
    # 预测脚本中的 OPC 位号列表名称
    ss_predict_opcitem_list_name: str = 'OPCItem_list'
    
    # 预测脚本中的预测函数名称
    ss_predict_function_name: str = 'predict'
    
    # 软测量输出的 OPC 位号（包含偏差校正）
    ss_output_tag: str = 'Demo.Tag4'
    
    # 原始输出的 OPC 位号（未经过偏差校正），可选
    ss_output_tag0: Optional[str] = 'Demo.Tag5'
    
    # 看门狗 OPC 位号，用于连接状态检测，可选
    ss_watchdog_tag: Optional[str] = 'Demo.Tag6'
    
    # 输出的上限值（用于裁剪结果）
    ss_output_hilim: float = 9999
    
    # 输出的下限值
    ss_output_lolim: float = -9999

    # 软测量的采样周期（单位：秒）
    sampling_time: int = 1

    # gRPC 服务端 IP 地址
    grpc_server_ip: str = 'localhost'
    
    # gRPC 服务端端口号
    grpc_server_port: int = 9999

    # 化验数据的 OPC 位号，用于偏差校正
    ss_labdata_tag: Optional[str] = 'Demo.Tag1'
    
    # 化验数据的有效上限（用于异常值剔除）
    ss_labdata_hilim: float = 9999
    
    # 化验数据的有效下限
    ss_labdata_lolim: float = -9999

    # 化验数据时间戳的 OPC 位号 (必须为时间戳)
    ss_labtime_tag: Optional[str] = 'Demo.Tag2'
    
    # 偏差更新的滤波时间常数（单位：采样点）
    filter_tao_sample: int = 10
    
    # 偏差更新触发的绝对误差阈值
    abs_threshold: float = 1e-4
    
    # 偏差更新所需的历史数据长度（单位：采样点）
    data_storage_len: int = 172800  # 相当于两天的数据
    
    # 判断偏差保持恒定所需的持续时间（单位：采样点）
    const_time_sample: int = 10
    
    # 偏差更新触发信号的 OPC 位号（0和1）
    ss_bias_update_trigger_tag: Optional[str] = 'Demo.Tag7'

    @staticmethod
    def from_json(path: str) -> 'SSTaskConfig':
        if not os.path.exists(path):
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 获取所有字段名
        expected_fields = {f.name for f in fields(SSTaskConfig)}
        actual_fields = set(data.keys())

        missing = expected_fields - actual_fields
        extra = actual_fields - expected_fields

        if missing:
            raise ValueError(f"Missing fields in config: {sorted(missing)}")
        if extra:
            raise ValueError(f"Unexpected fields in config: {sorted(extra)}")

        return SSTaskConfig(**data)

    def __post_init__(self):
        self.ss_predict_file_path = os.path.abspath(self.ss_predict_file_path)


class SS_task(OPCCalcTask if OPCCalcTask else object):
    def __init__(self, 
                 config: SSTaskConfig,
                 logger: Optional[logging.Logger] = None,
                 ss_signal = None,  # 计算完成信号pyqtBoundSignal
                 ):
        
        if OPCCalcTask is None:
            raise RuntimeError("需要安装 OPCGatePy 才能使用 SS_task")        
        super().__init__(config.grpc_server_ip, config.grpc_server_port)

        # 接收 logger 或 fallback
        self.logger = logger or logging.getLogger(__name__)
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('[%(asctime)s] %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)
            
        self.set_sampling_time(config.sampling_time)
        self.module_name = config.ss_name
        self.ss_signal = ss_signal
        self.OPCItem_list, self.predict_function  = load_predict_module(config.ss_predict_file_path,
                                                                        opclist_name=config.ss_predict_opcitem_list_name,
                                                                        predict_fun_name=config.ss_predict_function_name)
        self.file_dir = Path(config.ss_predict_file_path).parent.resolve()
        self.ss_opcitem = OPCItem(config.ss_output_tag, 
                                    f"SoftSensor Output", 
                                    lo_limit=config.ss_output_lolim, 
                                    hi_limit=config.ss_output_hilim)
        
        if config.ss_output_tag0:
            self.ss0_opcitem = OPCItem(config.ss_output_tag0, f"Raw SoftSensor Output")
        else:
            self.ss0_opcitem = None

        if config.ss_labdata_tag:
            self.labdata_opcitem = OPCItem(config.ss_labdata_tag, 
                                        f"LabData",
                                        lo_limit=config.ss_labdata_lolim,
                                        hi_limit=config.ss_labdata_hilim)
        else:
            self.labdata_opcitem = None
            
        if config.ss_labtime_tag:
            self.labtime_opcitem = OPCItem(config.ss_labtime_tag,
                                        f"LabTime")
        else:
            self.labtime_opcitem = None
            
        if config.ss_watchdog_tag:
            self.watchdog_opcitem = OPCItem(config.ss_watchdog_tag, f"WatchDog")
            self.watchdog_obj = WatchDog()
        else:
            self.watchdog_opcitem = None
            
        if config.ss_bias_update_trigger_tag:
            self.bias_update_trigger_opcitem = OPCItem(config.ss_bias_update_trigger_tag, 
                                                       f"BiasUpdateTrigger")
        else:
            self.bias_update_trigger_opcitem = None

        self.bias_update_obj = SoftSensorBiasUpdate(name=config.ss_name,
                                                    filter_tao=config.filter_tao_sample, 
                                                    abs_threshold=config.abs_threshold,
                                                    prd_len=config.data_storage_len, # 2days
                                                    const_len=config.const_time_sample)

        self.labdata_recorder = LabDataRecorder(name=config.ss_name,
                                                abs_threshold=config.abs_threshold,
                                                const_len=config.const_time_sample,
                                                csv_dir=self.file_dir)

        # 软测量的labdata和labtime可能通过读OPC位号获取，也可能通过直接传入
        # labdata和labtime不能是nan等非法值
        # 读OPC位号获取需要传入OPCItem对象，如果没有初始值，默认为0.0
        if isinstance(self.labdata_opcitem, OPCItem) and np.isfinite(self.labdata_opcitem.value):
            self._labdata_value = self.labdata_opcitem.value
        else:
            self._labdata_value = 0.0
        
        # 读取化验时间位号时，化验时间需要转换为时间戳格式，默认初始值为当前时间  
        if isinstance(self.labtime_opcitem, OPCItem) and np.isfinite(self.labtime_opcitem.value):
            # labtime的值需要转换为时间戳格式  
            self._labtime_value = self.set_lab_time(self.labtime_opcitem.value)
        else:
            self._labtime_value = time.time()

            
        self.logger.info(f"🐛 SoftSensor task {self.module_name} started.")
            

    def read_sequence_OPCItem(self, items: list[OPCItem]):
        if not items:
            return
        
        if len(items) == 1:
            self.read_single_OPCItem(items[0])
            return

        tag_set = set(item.tag for item in items)
        if len(tag_set) > 1:
            raise ValueError(f"❌ {self.module_name} OPCItems contain multiple tags: {tag_set}")

        tag = tag_set.pop()

        for item in items:
            item.value = np.nan
            
        # 收集所有 time_shift，并算出最早（最大）那一个
        shifts = sorted({item.time_shift for item in items})
        if any(shift < 0 for shift in shifts):
            self.logger.error(f"❌ {self.module_name} invalid negative time_shift found: {shifts}")
            return
        min_shift = shifts[0]
        max_shift = shifts[-1]
        length = max_shift - min_shift + 1

        # 一次性读序列：从 -max_shift 秒 开始，读 max_shift+1 个点
        try:
            rst = self.read(tag, start=-max_shift, length=length)
        except Exception as e:
            self.logger.error(f"❌ {self.module_name} {tag} read failed: {e}")
            return
            
        if not rst:
            self.logger.error(f"❌ {self.module_name} failed to read historical data for tag {tag}")
            return

        # 3. 根据索引映射到对应的 time_shift
        #    rst[0] 对应 time_shift=max_shift，rst[-1] 对应 time_shift=0
        shift_map = {
            max_shift - idx: (_value, _quality)
            for idx, (_name, _value, _quality, _timestamp) in enumerate(rst)
        }

        # 4. 将值写回每个 OPCItem
        for item in items:
            tup = shift_map.get(abs(item.time_shift))
            if tup is None:
                self.logger.error(f"❌ {self.module_name} {tag} missing data for shift {item.time_shift}")
                continue
            _value, _quality = tup
            if _quality == 'Good':
                # 不在这里进行工程上下限判断，OPCItem内部会自动判断该值的写入是否合法
                item.value = _value
            else:
                self.logger.error(
                    f"❌ {self.module_name} {tag}@{item.time_shift}s read error: quality={_quality}, value={_value}"
                )


    def read_single_OPCItem(self, item: Optional[OPCItem] = None):
        if not item:
            return
        
        if item.time_shift < 0:
            self.logger.error(f"❌ {self.module_name} {item.tag} has invalid negative time_shift: {item.time_shift}")
            return

        # 将值置为 NaN，读到正确的值再覆盖
        item.value = np.nan
        try:
            rst = self.read(item.tag, start = -item.time_shift, length = 1)
        except Exception as e:
            self.logger.error(f"❌ {self.module_name} {item.tag}@{item.time_shift}s read failed: {e}")
            rst = None
            
        if rst and len(rst) >= 1:
            _name, _value, _quality, _timestamp = rst[0]
            if _quality == 'Good':
                # 不在这里进行工程上下限判断，OPCItem内部会自动判断该值的写入是否合法
                item.value = _value   
            else:
                self.logger.error(f"❌ {self.module_name} {item.tag}@{item.time_shift}s read error: {_quality = }, {_value = }")
        else:
            self.logger.error(f"❌ {self.module_name} failed to read data for tag {item.tag}@{item.time_shift}s")


    def read_zero_shift_OPCItems(self, zero_shift_items: Optional[list[OPCItem]] = None):
        if not zero_shift_items:
            return
        
        if not all(item.time_shift == 0 for item in zero_shift_items):
            raise ValueError(f"❌ {self.module_name} all OPCItems must have time_shift=0")
                
        # 所有初值设为 NaN
        for item in zero_shift_items:
            item.value = np.nan

        tags = [item.tag for item in zero_shift_items]
        
        try:
            rst = self.read(tags, start=0, length=1)
        except Exception as e:
            self.logger.error(f"❌ [{self.module_name}] Batch read failed for zero-shift tags: {tags} -> {e}")
            return

        if not rst or len(rst) < len(zero_shift_items):
            self.logger.error(f"❌ [{self.module_name}] Expected {len(zero_shift_items)} results, got {len(rst) if rst else 0}")
            return

        for item, (_name, _value, _quality, _timestamp) in zip(zero_shift_items, rst):
            if _quality == 'Good':
                item.value = _value
            else:
                self.logger.error(
                    f"❌ [{self.module_name}] {item.tag}@{item.time_shift}s bad quality: quality={_quality}, value={_value}"
                )

    
    def _read_OPCItems_backup(self, opc_read_list: list[OPCItem] = None):
        if not opc_read_list:
            return
        
        for item in opc_read_list:
            if isinstance(item, OPCItem):
                self.read_single_OPCItem(item)


    def read_OPCItems_auto(self, opc_list: Optional[list[OPCItem]]) -> None:
        if not opc_list:
            return

        # 防止错误配置
        for item in opc_list:
            if item.time_shift < 0:
                self.logger.error(f"❌ [{self.module_name}] Invalid time_shift < 0: {item.tag}@{item.time_shift}s")
                return

        # 所有项先设为 NaN
        for item in opc_list:
            item.value = np.nan

        # 拆出 time_shift=0 的项，分为：
        # - 多 tag（可批量）
        # - 其余（按 tag 分组再处理）
        zero_shift_items = [item for item in opc_list if item.time_shift == 0]
        other_items = [item for item in opc_list if item.time_shift != 0]

        # 尝试批量读取多个 tag 的 time_shift=0 项
        if zero_shift_items:
            self.read_zero_shift_OPCItems(zero_shift_items)
            
        # 对其余项：按 tag 分组
        tag_groups = defaultdict(list)
        for item in other_items:
            tag_groups[item.tag].append(item)

        for tag, items in tag_groups.items():
            if len(items) == 1:
                # 单项：直接读
                self.read_single_OPCItem(items[0])
            else:
                # 多项：按 time_shift 排序并分组（是否连续）
                items.sort(key=lambda x: x.time_shift)
                shift_groups = []
                group = [items[0]]
                for prev, curr in zip(items, items[1:]):
                    if curr.time_shift == prev.time_shift + 1:
                        group.append(curr)
                    else:
                        shift_groups.append(group)
                        group = [curr]
                shift_groups.append(group)

                # 每组用 sequence 方法读取（内部会判断长度是否为1）
                for group in shift_groups:
                    self.read_sequence_OPCItem(group)

            
    def write_OPC(self, OPCItem_list: list[OPCItem]):
        d = {}
        for item in OPCItem_list:
            if item.tag and item.lo_limit <= item.value <= item.hi_limit:
               d[item.tag] = item.value
        if d:
            self.write(d)

            
    def set_lab_data(self, lab_data: float):
        if np.isfinite(lab_data):
            self._labdata_value = lab_data

    
    def set_lab_time(self, lab_data_time: float):
        # 输入的lab_data_time需要是时间戳格式
        if np.isfinite(lab_data_time):
            self._labtime_value = lab_data_time
 
 
    def export_csv(self):
        # 获取数据
        lab_data = self.bias_update_obj.get_lab_data()
        lab_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.bias_update_obj.get_lab_time()))
        prd_at_labtime = self.bias_update_obj.get_prd_data_at_labtime()
        export_time_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        store_data = f'{export_time_str},{lab_time},{lab_data},{prd_at_labtime}\n'
        # 写入或追加数据
        csv_file = self.file_dir / f'{self.module_name}_SoftSensorLabData.csv'
        file_exists = csv_file.exists()
        with open(csv_file, 'a', encoding='utf-8') as f:
            if not file_exists:
                header = "ExportTime,LabTime,LabData,SoftSensorPrd0\n"
                f.write(header)
            f.write(store_data)


    def done(self):
        # 读取OPC位号
        self.read_OPCItems_auto(self.OPCItem_list)     
        if self.labdata_opcitem:
            self.read_single_OPCItem(self.labdata_opcitem)
            self.set_lab_data(self.labdata_opcitem.value)
        if self.labtime_opcitem:
            self.read_single_OPCItem(self.labtime_opcitem)
            self.set_lab_time(self.labtime_opcitem.value)
        if self.bias_update_trigger_opcitem:
            self.read_single_OPCItem(self.bias_update_trigger_opcitem)
            _bias_update_trigger = self.bias_update_trigger_opcitem.value
        else:
            _bias_update_trigger = None

        # 记录化验数据
        self.labdata_recorder.run(self._labdata_value, self._labtime_value)
        
        # 执行软测量预测函数
        try:
            _ss0_value = self.predict_function()
        except Exception as e:
            self.logger.error(f"❌ {self.module_name} SS0 Predict Error: {e}")
            _ss0_value = np.nan
            
        if not np.isfinite(_ss0_value):
            self.logger.error(f"❌ {self.module_name} SS0 Predict Error: {_ss0_value = }")
            return
        
        # 预测值叠加偏差
        _prd_time = time.time()
        _ss0_auto_bias = self.bias_update_obj.run(_ss0_value, self._labdata_value, self._labtime_value, _prd_time, _bias_update_trigger)
        if self.bias_update_obj.get_update_flag():
            # 检测到有新的化验值，[化验时间、化验值、化验时间的预测值]写入文件
            self.logger.info(f"🎉 Bias update has been applied. New bias = {self.bias_update_obj.get_bias()}")
            self.export_csv()

        _ss_value = _ss0_value + _ss0_auto_bias        
        
        self.ss_opcitem.value = _ss_value
        opc_output_list = [self.ss_opcitem]
        
        if self.ss0_opcitem:
            # 软测量原始值输出
            self.ss0_opcitem.value = _ss0_value
            opc_output_list.append(self.ss0_opcitem)
            
        if self.watchdog_opcitem:
            self.watchdog_opcitem.value = self.watchdog_obj(MaxOut=1)
            opc_output_list.append(self.watchdog_opcitem)
        

        self.write_OPC(opc_output_list)


        # 发射信号, 配套ss_gui使用
        if self.ss_signal:
            self.ss_signal.emit(_ss_value, _ss0_value, _prd_time)


if __name__ == '__main__':
    import time
    import numpy as np
    bs_obj = SoftSensorBiasUpdate(name = 'SoftSensorTest', const_len=3, filter_tao=5)

    lab_value = 0
    lab_time = 0
    for k in range(0,10):
        prd_value = 0.2
        prd_time = float(k)
        if k == 5:
            lab_value = 6.0
        lab_time = k
        print(f"{k = }, {prd_value = }, {prd_time = }, {lab_value = }, {lab_time = }")
        bias = bs_obj.run(prd_value, lab_data=lab_value, lab_time = lab_time, prd_time=prd_time)
        if bs_obj.get_update_flag():
            print(f"New bias is updated.")
            print(f"{bs_obj.get_bias() = }")
            print(f"{bs_obj.get_lab_data() = }")
            print(f"{bs_obj.get_lab_time() = }")
            print(f"{bs_obj.get_prd_data_at_labtime() = }")
        
        print(f"fixed_prd = {prd_value + bias}, {bias = }, {bs_obj.get_update_flag() = }")
        time.sleep(0.3)