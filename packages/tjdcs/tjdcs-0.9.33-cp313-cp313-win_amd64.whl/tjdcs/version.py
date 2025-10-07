from datetime import datetime

__version__ = '0.9.33'

######################
# __version__ = '0.9.33'
# 软测量增加trigger触发功能

# __version__ = '0.9.32'
# 更新软测量的相关内容

# __version__ = '0.9.31'
# 修改了SoftSensorBiasUpdate类

# __version__ = '0.9.30'
# 1. 修改了LPVPlant中的bug

# __version__ = '0.9.29'
# 1. 增加ProcessSim类
# 2. MIMOSim类中增加get_model_dict, get_mv_list和get_cv_list方法
# 3. 增加LDLAG类
# 4. 增加AntiWindupLimter类

# __version__ = '0.9.28'
# 2024-02-14
# 1. 删除TJProcSim，仅保留TJProcSim2
# 2. 将TJProcSim2改名为MIMOSim，TJProcSim和TJProcSim2的名称仍然保留，内容指向MIMOSim
# 3. 移除SimBase和TJOpcGateSimTask
# 4. MIMOSim能够仿真积分过程
# 5. 增加SISOSim类
# 6. tjdcs包内的部分引用改为绝对引用

# __version__ = '0.9.27'
# 2024-02-14
# 1. 修改了模型仿真类，支持积分对象
# 2. 将部分间接引用改为绝对引用
# 3. 准备删除TJProcSim，仅保留TJProcSim2
#
# __version__ = '0.9.26'
# 2024-01-21
# 1. 修改了SoftSensorBiasUpdate
#
# __version__ = '0.9.24'
# 2023-10
# 1. 调整了代码结构
# 2. 增加一些注释
#
# __version__ = '0.9.23'
# 2023-10
# 1. 增加了SoftSensorBiasUpdate功能
# 2. 修改了ZFilter和SFilter
# 3. 为一些代码增加了注释
#
# __version__ = '0.9.22'
# 2023-7-15
# 1. 修改了Simulink框架, 将done, one_sample_simulation统一为task
#
# __version__ = '0.9.15'
# 2022-12-29
# 1. 新增LPVPlantSim类
#
# __version__ = '0.9.14'
# 2022-11-21
# 1. 新增了MIMOSim2类，通过scipy中的lfilter进行被控对象仿真
#
# __version__ = '0.9.13'
# 2022-09-13
# 1. 修改了测试信号模块
#
# __version__ = '0.9.12'
# 2022-05-27
# 1. 修改了PID模块
#
# __version__ = '0.9.11'
# 2022-04-16
# 1. 修改了PID模块
#
# __version__ = '0.9.10'
# 2022-04-02
# 1. 修改了PID模块
#
# __version__ = '0.9.9'
# 2022-03-31
# 1. 修改了PID模块
# 2. 将Simulink类建立独立文件clsSimulink.py
#
# __version__ = '0.9.8'
# 2022-03-28
# 1. 新增Simulink仿真框架
#
# __version__ = '0.9.7'
# 2022-01-05
# 1. 修正了ProcessSim中的名称显示
#
# __version__ = '0.9.6'
# 2021-12-31
# 1. 添加授权文件
#
# __version__ = '0.9.5'
# 2021-12-31
# 1. 修改了TJProcSim
# 2. 重新设计了接口
#
# __version__ = '0.9.4'
# 2021-12-21
# 修改了TJProcSim
#
# __version__ = '0.9.3'
# 2021-11-16
# 增加积分模型
#
##################################