import time
from tjdcs.clsSimulink import Simulink
try:
    from OPCGatePy.opc_calc_task import OPCCalcTask
except ImportError:
    OPCCalcTask = None

class SimulinkOPCGateTask(OPCCalcTask if OPCCalcTask else object):
    '''
    将Simulink类型的仿真器映射到OPCGate上
    '''
    def __init__(self, ip: str = '127.0.0.1',              # opcgate所在的IP地址
                    port: int = 9999,                   # opcgate所在的端口
                    Simulator: Simulink = Simulink(),   # Simulink对象
                    group_tag: str = '',                # 额外添加的分组（如填写D1，可将内部位号CV1变为D1.CV1）
                    stop_time: int = float('inf'),          # 停止时间 
                    ) -> None:  
        '''
        初始化

        parameters
        ----------
        ip: str
        port: int
        Simulator: Simulink object
        grout_tag: str, optional, pre-string added before of Simulink tags
        stop_time: int, optional, the unit is samples.

        '''
        if OPCCalcTask is None:
            raise RuntimeError("需要安装 OPCGatePy 才能使用 SimulinkOPCGateTask")
        super().__init__(ip, port)
        self.Simulator = Simulator
        self.set_sampling_time(self.Simulator.get_sampling_time())
        self.SimulatorName = Simulator.__class__.__name__
        self.group_tag = group_tag+'.' if group_tag else group_tag
        self.write_and_create({self.group_tag + tag: value for tag,value in self.Simulator.get_data().items()})
        self._stop_time = stop_time
        self.display_flag = True
        time.sleep(1.0)


    def done(self):
        # 读取数据并输入仿真器
        if self.get_done_count() >= self._stop_time:
            self.stop()
        sim_data = self.Simulator.get_data()
        data_list = self.read_value([self.group_tag + tag for tag in sim_data])
        new_data_dict = dict(zip(sim_data, data_list))
        # 单步仿真，返回需要写入OPCGate的字典
        write_data_dict = self.Simulator.run(new_data=new_data_dict)
        # 写出数据
        if write_data_dict:
            self.write({self.group_tag + tag: value for tag, value in write_data_dict.items() if tag in self.Simulator.get_data()})
        # 打印信息
        if self.display_flag:
            print(f"{self.SimulatorName}.count = {self.Simulator.get_task_count()} -- {time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())}")

    def run(self):
        return super().run()
    
if __name__ == '__main__':
    import numpy as np
    from scipy import signal
    from tjdcs import MIMOSim

    sim_ini_dict = {'MV': 15, 'CV': 31, '__Random_CV_ONOFF': 0}
    plant_model = { 'CV': {'MV': {'mode': 'tf_z', 'num_z': [0, 1.0, 0.5], 'den_z': [1.0, -1.5, 0.7], 'iodelay_z': 0}}}
    class PIDSim(Simulink):
        def __init__(self, TS = 1) -> None:
            super().__init__(data = sim_ini_dict, TS = TS, max_record_length=0)
            self.plant = MIMOSim(plant_model, sim_ini_dict, TS)
            # 配置输出噪声序列 
            self.N = 10000
            np.random.seed(2)
            v1 = signal.lfilter([1], np.convolve([1, -0.95], [1, -0.95]), np.random.randn(self.N))
            self.v1 = 2.0*v1/np.std(v1)
        def task(self):
            data = self.get_data()
            # 获取CV的不可测干扰 (干扰的均值为0)
            if data['__Random_CV_ONOFF'] > 0:
                k = self.get_task_count() % self.N
                v_dict = {'CV': self.v1[k]}
            else:
                v_dict = {}
            # 获取MV
            mv_dict = {k:v for k,v in data.items() if k in {'MV'}}
            # 计算CV
            CV_dict = self.plant(u_Value_Dict = mv_dict, v_Value_Dict= v_dict)
            data.update(CV_dict)
            return CV_dict    
    
    s = SimulinkOPCGateTask('127.0.0.1', 9999, PIDSim(), group_tag='S2')
    s.run()