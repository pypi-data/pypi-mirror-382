from tjdcs.algorithm import utilities
from tjdcs.algorithm import MIMOSim2

def plt_model_stp(process_model_dict: dict, Ts = 1, plotLen = 300) -> None:
    return MIMOSim2.plot_model_stp(process_model_dict, Ts, plotLen)

def plot_model_stp(process_model_dict: dict, Ts = 1, plotLen = 300) -> None:
    print(f"This function is about to deprecated (maybe on 0.9.30), please use plt_model_stp instead.")
    return MIMOSim2.plot_model_stp(process_model_dict, Ts, plotLen)

def get_model_stp(process_model_dict: dict, Ts: int = 1, length: int = 300) -> dict:
    return MIMOSim2.get_model_stp(process_model_dict, Ts, length)

def tf2stp(process_model_dict, Ts = 1, plotLen = 300) -> dict:
    print(f"This function is about to deprecated (maybe on 0.9.30), please use get_model_stp instead.")
    return MIMOSim2.get_model_stp(process_model_dict, Ts, plotLen)

def dict2pairs(d:dict, path = ''):
    '''
    d = {'1':{'2':{'3':{'4':5},'6':7},'8':9}}
    >>> list(dict2pairs(d))
    [('1.2.3.4', 5), ('1.2.6', 7), ('1.8', 9)]
    ''' 
    return utilities.dict2pairs(d, path)

    
def pair2dict(pair:tuple, d:dict):
    '''
    pair2dict( ('SimLoop1.data.SP', 10), d )
    equals to
    d['SimLoop1']['data']['SP'] = 10
    若不存在分支，则创建。
    '''
    return utilities.pair2dict(pair, d)

def c2d(Gs_num, Gs_den, Gs_delay, Ts = 1, method = 'zoh'):
    # method: str, optional
    # Which method to use:
    # gbt: generalized bilinear transformation
    # bilinear: Tustin’s approximation (“gbt” with alpha=0.5)
    # euler: Euler (or forward differencing) method (“gbt” with alpha=0)
    # backward_diff: Backwards differencing (“gbt” with alpha=1.0)
    # zoh: zero-order hold (default)
    # foh: first-order hold (versionadded: 1.3.0)
    # impulse: equivalent impulse response (versionadded: 1.3.0)
    return utilities.c2d(Gs_num, Gs_den, Gs_delay, Ts, method)

def current_time_str():
    return utilities.current_time_str()

def str2xpyp(s:str):
    # 字符串转折线表
    # s = '0,0#100,10#200,15#300,20#5,25#500,27#600,27#700,27'
    # s = '2#0,0#100,10#200,15#300,20#400,25#500,27#600,27#700,27'
    # xp, yp = str2xpyp(s)
    # print(xp)
    # print(yp)
    return utilities.str2xpyp(s)

############################################################################################################
# from tjdcs.algorithm import tjModelMethod

# def plot_model_stp(process_model_dict, Ts = 1, plotLen = 300) -> None:
#     return tjModelMethod.plot_model_stp(process_model_dict, Ts, plotLen)


# def stp_stable_len(siso_stp, thr_pct=0.01) -> int:
#     return tjModelMethod.stp_stable_len(siso_stp, thr_pct)


# def stp2ipr(yu_model_stp) -> dict:
#     # 根据yu_model_stp创建yu_model_ipr
#     return tjModelMethod.stp2ipr(yu_model_stp)


# def get_ModelDict_tags(yu_model_dict, mode = 'list'):
#     '''
#     获取yu_model_dict字典中的全部位号

#     参数：
#         yu_model_dict: 嵌套字典，可以为yu_model_tf或yu_model_stp。
#         mode: 模式，支持填入'list'或'set'。
#     返回:
#         cv_tag_list: list或set，cv变量列表（集合）。
#         mv_tag_list: list或set，mv变量列表（集合）。
#     举例：
#         >>> model_CV_tag_list, model_MV_tag_list = tj010.get_model_tags(yu_model_tf)
#     '''
#     return tjModelMethod.get_ModelDict_tags(yu_model_dict, mode)


# def tf2stp(yu_model_tf, Ts=1, plotLen=0) -> dict:
#     '''
#     将yu_model_tf模型转换为yu_model_stp

#     参数：
#         yu_model_tf: 三层嵌套字典，参数化模型接口（原始输入模型）。可用于仿真器、MPC的模型接收。
#             根据需求，yu_model_tf允许填入 “全部模型_ALL” 或 “部分模型_SUB” 。
#             yu_model_tf为三层嵌套字典，第一层为CV标签，第二层为MV标签，第三层为对应模型的参数。
#             模型允许6种模型表达方式(mode)：'tf_s', 'tf_z', 'stp', 'stpfx', 'None', 不填。不同mode中的详细参数不同。
#             例如：
#             yu_model_tf = {'CV1': {'MV1': {'mode': 'tf_s', 'num_s': [0, 1], 'den_s': [20, 1], 'iodelay_s': 2},
#                                 'MV2': {'mode': 'stp', 'stp': [0,0,1,1,0,0,4,4,4,7,8,9,4,3,3,3,4,5,4,3,3,3,3]}},
#                         'CV2': {'MV1': {'mode': 'tf_z', 'num_z': [-0.02], 'den_z': [1, -0.95],     'iodelay_z': 5},
#                                 'DV1': {'mode': 'stpfx', 'x': [0, 10, 100, 350, 400, 600],  'y': [0, 0, 3, 9, 7, 7]},
#                                 'MV2': {'mode': 'None'}}}
#             #### 特别约定 ####
#             # 录入yu_model_tf时，标签中“出现但未赋值”的模型视为None。
#             # 即录入模型时，必须给出标签中的所有模型。
#             # 例如：
#             # yu_model_tf = {'CV1': {'MV2': {'mode': 'tf_s', 'num_s': [0, 1],  'den_s': [50, 1], 'iodelay_s': 1}},
#             #                'CV2': {'MV1': {'mode': 'tf_s', 'num_s': [0, 2],  'den_s': [60, 1], 'iodelay_s': 2},
#             #                        'MV2': {'mode': 'tf_s', 'num_s': [0, 3],  'den_s': [70, 1], 'iodelay_s': 2}}}
#             # 上述表达中，模型'CV1'-'MV1'为None
#             # 如果系统中存在MV3和CV3，那么和MV3、CV3相关的模型不发生改变。
#         Ts: int, 采样时间，单位为秒，默认值为1。
#         plotLen: int, 生成stp序列的指定长度, 若plotLen = 0则自适应生成。

#     返回:
#         yu_model_stp, 三层嵌套字典，模型的阶跃响应序列，单位为采样点。一般用于绘图。
#             yu_model_stp 为三层嵌套字典，第一层为CV标签，第二层为MV标签，第三层为对应模型的阶跃响应序列(List)。
#             yu_model_stp 由函数tj010.tf2stp(yu_model_tf, Ts, plotLen)获得。不建议用其它方式生成。  

#     举例:
#         >>> yu_model_tf = {'CV1': {'MV1': {'mode': 'tf_s', 'num_s': [0, 1],     'den_s': [20, 1],        'iodelay_s': 2},
#                                 'MV2': {'mode': 'stp', 'stp': [0,0,1,1,0,0,4,4,4,7,8,9,4,3,3,3,4,5,4,3,3,3,3]}},
#                         'CV2': {'MV1': {'mode': 'tf_z', 'num_z': [-0.02], 'den_z': [1, -0.95],     'iodelay_z': 5},
#                                 'DV1': {'mode': 'stpfx', 'x': [0, 10, 100, 350, 400, 600],  'y': [0, 0, 3, 9, 7, 7]},
#                                 'MV2': {'mode': 'None'}}}

#         >>> yu_model_stp = tj010.tf2stp(yu_model_tf, Ts = 1, plotLen = 0)  
#     '''
#     return tjModelMethod.tf2stp(yu_model_tf, Ts, plotLen)

