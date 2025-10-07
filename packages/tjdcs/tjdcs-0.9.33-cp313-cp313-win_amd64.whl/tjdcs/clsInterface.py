from tjdcs.algorithm import tjConstDetector
from tjdcs.algorithm import tjRateLimit
from tjdcs.algorithm import tjWatchDog
from tjdcs.algorithm import tjTestSignal
from tjdcs.algorithm import MIMOSim2
from tjdcs.algorithm import tjLPVPlant
from tjdcs.algorithm import tjLDLAG
from tjdcs.algorithm import tjAntiWindupLimter

class AntiWindupLimter(tjAntiWindupLimter.AntiWindupLimter):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, u:float, HI = 100, LO = 0) -> float:
        return super().__call__(u, HI, LO)
    
    def run(self, u, HI = 100, LO = 0) -> float:
        return super().run(u, HI, LO)

class LDLAG(tjLDLAG.LDLAG):
    '''
    增益为1的一阶超前滞后滤波器, filter=(alpha*tao*s+1)/(tao*s+1)
    当alpha=0时, filter = 1/(tao*s+1)
    
    alpha的意义是滤波器单位阶跃响应的起点
    tao的意义是时间常数
    滤波器的参数alpha, tao可以随时改变
    '''
    
    def __init__(self, alpha=0.0, tao=5.0, Ts=1, u_ini=None, y_ini=None) -> None:
        super().__init__(alpha, tao, Ts, u_ini, y_ini)
        
    def __call__(self, u: float) -> float:
        return super().__call__(u)

    def run(self, u: float) -> float:
        return super().__call__(u)
        
    def multi_step(self, u: float) -> float:
        return super().multi_step(u)
    

class SISOSim(MIMOSim2.SISOSim):
    def __init__(self, gain, tao, delay=0, Ts=1, integralMark=0) -> None:
        super().__init__(gain, tao, delay, Ts, integralMark)
        

class MIMOSim(MIMOSim2.MIMOSim):
    def __init__(self, process_model_dict: dict, ini_value_dict: dict={}, Ts=1) -> None:
        super().__init__(process_model_dict, ini_value_dict, Ts)

    def __call__(self, u_Value_Dict={}, v_Value_Dict={}) -> dict:
        return super().__call__(u_Value_Dict=u_Value_Dict, v_Value_Dict=v_Value_Dict)

    def run(self, u_Value_Dict={}, v_Value_Dict={}) -> dict:
        return super().__call__(u_Value_Dict=u_Value_Dict, v_Value_Dict=v_Value_Dict)

    def reset(self):
        return super().reset()

    def get_process_tags(self):
        return super().get_process_tags()

    def get_output_data_dict(self):
        return super().get_output_data_dict()

    def get_input_data_dict(self):
        return super().get_input_data_dict()

    def get_all_data_dict(self):
        return super().get_all_data_dict()

    def plot_model_stp(self, plotLen=300):
        return super().plot_model_stp(plotLen)
    
    def get_cv_list(self):
        return super().get_cv_list()

    def get_mv_list(self):
        return super().get_mv_list()
    
    def get_model_dict(self):
        return super().get_model_dict()


class TJProcSim(MIMOSim):
    def __init__(self, process_model_dict: dict, ini_value_dict: dict={}, Ts=1) -> None:
        print('TJProcSim is deprecated, use MIMOSim instead')
        super().__init__(process_model_dict, ini_value_dict, Ts)

class TJProcSim2(MIMOSim):
    def __init__(self, process_model_dict: dict, ini_value_dict: dict={}, Ts=1) -> None:
        print('TJProcSim2 is deprecated, use MIMOSim instead')
        super().__init__(process_model_dict, ini_value_dict, Ts)


class LPVPlantSim(tjLPVPlant.LPVPlantSim):
    def __init__(self, ini_value_dict={}) -> None:
        super().__init__(ini_value_dict)

    def addPlant(self, plant_id: int, operating_point: float, yu_model_tf: dict, Ts: int) -> None:
        return super().addPlant(plant_id, operating_point, yu_model_tf, Ts)

    def delPlant(self, plant_id: int) -> None:
        return super().delPlant(plant_id)

    def run(self, operating_value: float, u_Value_Dict={}, v_Value_Dict={}) -> dict:
        return super().run(operating_value, u_Value_Dict, v_Value_Dict)

    def get_plant_dict(self):
        return super().get_plant_dict()

    def get_current_plant_weight_dict(self):
        return super().get_current_plant_weight_dict()


# class SISO_tfs_Model(tjProcessModel.SISO_tfs_Model):
#     def __init__(self, gain, tao, delay, Ts=1) -> None:
#         super().__init__(gain, tao, delay, Ts=Ts)

#     def update(self, gain, tao, delay):
#         return super().update(gain, tao, delay)


class WatchDog(tjWatchDog.WatchDog):
    '''
    看门狗，输出按调用次数自增循环。
    '''
    def __init__(self) -> None:
        super().__init__()

    def __call__(self, MaxOut=0) -> int:
        return super().__call__(MaxOut=MaxOut)


class RateLimit(tjRateLimit.RateLimit):
    def __init__(self, u_ini: float, Ts=1):
        super().__init__(u_ini, Ts=Ts)

    def __call__(self, u_end, PRLimPerMin=60, NRLimPerMin=None):
        return super().__call__(u_end, PRLimPerMin=PRLimPerMin, NRLimPerMin=NRLimPerMin)


class ConstDect(tjConstDetector.ConstDect):
    def __init__(self) -> None:
        super().__init__()

    def run(self, Ut, DectLen=10) -> bool:
        return super().__call__(Ut, DectLen=DectLen)
    
    def __call__(self, Ut, DectLen=10) -> bool:
        return super().__call__(Ut, DectLen=DectLen)


class TestSignalGen(tjTestSignal.TestSignal):
    def __init__(self, SEED=None):
        super().__init__(SEED)

    def set_ET(self, ET=10):
        return super().set_ET(ET)

    def get_ET(self):
        return super().get_ET()

    def set_amplitude(self, amp=1):
        return super().set_amplitude(amp)

    def get_amplitude(self):
        return super().get_amplitude()

    def __call__(self, t=None):
        return super().__call__(t)

    def run(self, t = None):
        return super().__call__(t)
