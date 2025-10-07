from tjdcs.algorithm import PIDalgorithm

class PID(PIDalgorithm.PID):
    '''
    PID控制器，实现公式:
    OP = KP{1 + 1/(TI*s) + TD*s/[(TD/N)*s + 1]} * (SP - PV)
        离散化:   
        1/s = TS/(1-z^{-1})   
        其中:
        TS 为采样时间，单位: 秒，默认为1秒。

    控制器参数:   
    KP:      默认为1.0；PID控制器增益，实数，正数表示“反作用”，负数表示“正作用”。  
    TI:      默认为60.0；PID控制器积分时间，TI>=0。  
    TD:      默认为0.0；PID控制器微分时间，TD>=0。  
    N:       默认为10.0；PID控制器微分滤波系数，N>0。  
    OP_HI:    默认为100.0；OP输出高限  
    OP_LO:    默认为0.0；OP输出低限  
    TS:      默认为1；采样时间

    MODE:     模式；跟踪模式: MODE = 0，自动模式: MODE = 1。 
    SP:     设定值  
    PV:     被控变量  
    FF:     前馈变量（OP偏置）  
    TV:     跟踪变量。TV必须连接“实际阀位指令”，初始化时OP = TV。  
    OP:     操作变量，连接下游  

    PID控制器模式:    
    跟踪模式: MODE = 0，OP跟踪TV。
    自动模式: MODE = 1，根据公式计算OP。
    
    *注: OP输出始终受到OP_HI和OP_LO的约束。
    '''
    def __init__(self, TS:int=1):
        '''
        PID控制器初始化

        parameters
        ----------
        TS: int, sampling time
        '''
        super().__init__(TS)

    def getPIDForm(self):
        return super().getPIDForm()
    
    def getPIDParam(self):
        return super().getPIDParam()
    
    def getInnerSaveState(self):
        return super().getInnerSaveState()
    
    def getOPHighLowLimit(self):
        return super().getOPHighLowLimit()
    
    def setOPHighLowLimit(self, OP_HI=100.0, OP_LO=0.0):
        '''
        设置PID的输出(OP)上下界

        parameters
        ----------
        OP_HI: float, the high limit of OP
        OP_LO: float, the low limit of OP
        '''
        return super().setOPHighLowLimit(OP_HI, OP_LO)
    
    def setPIDParam(self, KP=1.0, TI=60.0, TD=0.0, N=10.0):
        '''
        设置PID的参数

        parameters
        ----------
        KP: the proportion of the PID (could be positive or negative)
        TI: the integral time of PID, the unit is second
        TD: the derivative time of PID, the unit is second
        N: the derivative filter time of PID, the unit is second 
        '''
        return super().setPIDParam(KP, TI, TD, N)
    
    def run(self, MODE: float, SP: float, PV: float, TV: float, FF: float = 0) -> float:
        '''
        单步运行PID，计算OP

        parameters
        ----------
        MODE: control mode of PID, (0 is tracting mode, 1 is auto mode)
        SP: the setpoint value of the current control loop
        PV: the process value of the current control loop, also known as control variable (CV)
        TV: the tracking value of the current control loop, if MODE == 0, the function returns the value of TV 
        FF: the feedforward value of the current control loop, also known as the bias of OP
        
        returns
        -------
        OP: the output of PID for the current control loop, also known as manipulate variable (MV) 
        '''
        return super().run(MODE, SP, PV, TV, FF)


