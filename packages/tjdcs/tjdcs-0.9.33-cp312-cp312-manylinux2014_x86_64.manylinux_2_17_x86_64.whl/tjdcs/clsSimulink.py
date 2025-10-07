import copy
import time
from collections import deque
import numpy as np
from typing import Dict, List, Tuple


class Simulink():
    '''
    仿真器框架，以继承的方式使用。
    使用时覆盖task方法，使用run方法运行。
    '''
    def __init__(self, data: Dict[str, float] = {}, TS: int = 1, max_record_length: int = 10000) -> None:
        '''
        仿真器初始化

        parameters
        ----------
        data: Dict[str, float], all the data (input, output, tempvalue) used in the simulation should be included in the dict.
            example: data = {'MV1': 20.0, 'CV1': 40.6, 'SP1': 50.5, 'Var1': 80.1}
            The running simulation is based on self.__data. 
            One should not modify keys of __data durning running.
            self.__data prevent modify keys with enforcement in previous versions, it remove this property since 0.9.25. 
        TS: int, sampling time, default is 1. 
        max_record_length: int, default is 10000, max length of the record data.
            Simulation will record running data in self.record_data, which is a dict with same keys as self.__data.
            One can get previous data through self.record_data.
        '''
        self.__count = 0
        self.__TS = int(TS)
        self.__data: Dict[str, float] = copy.deepcopy(data)
        self.record_data: Dict[str, deque] = {'TimeStamp': deque([self.__count], maxlen = max_record_length)}
        self.record_data.update({key: deque([value], maxlen = max_record_length)
                                        for key, value in self.__data.items()})
        
    def get_sampling_time(self) -> int:
        '''
        获取采样时间
        '''
        return self.__TS

    def get_task_count(self) -> int:
        '''
        获取任务运行次数
        '''
        return self.__count
    
    def get_data(self) -> Dict[str, float]:
        '''
        获取仿真器数据字典的引用
        '''
        return self.__data
    
    def get_data_copy(self) -> Dict[str, float]:
        '''
        获取仿真器数据字典的拷贝
        '''
        return {k:v for k,v in self.__data.items()}
    
    def update_data(self, new_data: Dict[str, float] = {}):
        '''
        将外部数据输入仿真器
        注：有多种方式输入新数据
            如：d = self.get_data(); d.update(new_data);
                或run(new_data)
        '''
        self.__data.update(new_data)
    
    def task(self):
        '''
        仿真器单步计算内容（覆盖修改）
        可选字典型返回值, 以控制run函数的返回值
        所有数据修改需要使用self.__data.update方法更新

        returns
        -------
        None or Any(usually a dict), optional
        If the function returns None, the 'run function' auto returns a dict with changed items in self.__data.
        If the function returns not None, the 'run function' returns as it is. 
        '''
        pass

    def run(self, new_data: Dict[str, float] = {}) -> dict:
        '''
        仿真器单步执行，外部数据通过new_data输入仿真器。
        注：可能有多种方式输入新数据

        parameters
        ----------
        new_data: dict, new data pairs update to self.__data
            This is one way to change data in simulation from out side.

        returns
        -------
        dict or Any, it depends on the task returns.

        '''
        self.__count += 1
        if new_data:
            self.__data.update(new_data)
        data_save = copy.deepcopy(self.__data)
        task_return = self.task()
        if task_return is None:
            # self.task()返回None时替换为发生变化的数据字典
            task_return = {key: value for key, value in self.__data.items() if value != data_save[key]}
        self.record_data['TimeStamp'].append(self.__count)
        for key, value in self.__data.items():
            self.record_data[key].append(value)
        return task_return

    def export_csvdata(self, taglist: list = [], filename: str = ''):
        '''
        将self.record_data中的数据导出为CSV
        '''
        if len(taglist) == 0:
            taglist = list(self.record_data.keys())
        else:
            taglist.insert(0, 'TimeStamp')
        d = {key: value for key, value in self.record_data.items() if key in taglist}
        if len(d) == 0:
            return 
        data = np.array([np.array(dx, dtype= float) for dx in d.values()]).T
        header = ','.join(d.keys())
        fmt = ["%d"] + ["%f"]*(len(d) - 1)
        if not filename:
            filename = time.strftime("%Y_%m_%d_%H_%M_%S", time.localtime())+'.csv'
        with open(filename, 'wb') as csv_file:
            np.savetxt(csv_file, data, fmt = fmt, delimiter=",", header = header, comments="")


    def plot_record_data(self, taglist: list = []):
        if not taglist:
            taglist = [tag for tag in self.__data if '__' not in tag]
        import matplotlib.pyplot as plt        
        from matplotlib import gridspec 
        import matplotlib
        # plt.style.use('seaborn')
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']  
        plt.rcParams['axes.unicode_minus']=False
        FONT_SIZE = 11

        subfigNum = len(taglist)
        plt.figure(figsize=(8, 4*subfigNum), facecolor = 'w', tight_layout = True)
        gs = gridspec.GridSpec(subfigNum, 1)

        for num, tag in enumerate(taglist):
            ax = plt.subplot(gs[num])
            ax.plot(self.record_data['TimeStamp'], self.record_data[tag], '-', label=tag)
            ax.legend(loc='best', fontsize=FONT_SIZE)
            plt.yticks(fontsize=FONT_SIZE)
            plt.xticks(fontsize=FONT_SIZE)
            plt.title(f"", fontsize=FONT_SIZE)
            ax.grid(True)


    def plot_record_data_in_one_figure(self, taglist = []):
        '''
        将self.record_data中的数据绘制在一张图中
        
        '''
        if not taglist:
            taglist = [tag for tag in self.__data if '__' not in tag]
        import matplotlib.pyplot as plt        
        from matplotlib import gridspec 
        import matplotlib
        # plt.style.use('seaborn')
        matplotlib.rcParams['font.sans-serif'] = ['SimHei']  
        plt.rcParams['axes.unicode_minus']=False
        FONT_SIZE = 11

        subfigNum = 1
        plt.figure(figsize=(8, 5*subfigNum), facecolor = 'w', tight_layout = True)
        gs = gridspec.GridSpec(subfigNum, 1)
        ax = plt.subplot(gs[0])
        for tag in taglist:
            ax.plot(self.record_data['TimeStamp'], self.record_data[tag], '-', label=tag)
        ax.legend(loc='best', fontsize=FONT_SIZE)
        plt.yticks(fontsize=FONT_SIZE)
        plt.xticks(fontsize=FONT_SIZE)
        plt.title(f"", fontsize=FONT_SIZE)
        ax.grid(True)




if __name__ == '__main__':
    from tjdcs import MIMOSim
    from tjdcs import PID

    sim_ini_dict = {'MV': 15, 'CV': 31, 'SP': 31}
    plant_model = { 'CV': {'MV': {'mode': 'tf_z', 'num_z': [0, 1.0, 0.5], 'den_z': [1.0, -1.5, 0.7], 'iodelay_z': 0}}}

    class PIDSim(Simulink):
        def __init__(self) -> None:
            super().__init__(data = sim_ini_dict)
            self.plant = MIMOSim(plant_model, sim_ini_dict, Ts = 1)
            self.pid = PID()
            self.pid.setPIDParam(KP = 0.1, TI = 10.0, TD=2)
        def task(self):
            data = self.get_data()
            MV = self.pid.run(MODE=1, SP=data['SP'], PV=data['CV'], TV=data['MV'])
            data.update({'MV': MV})    
            CV_dict = self.plant(u_Value_Dict = {'MV': MV})
            data.update(CV_dict)    
    
    simulator = PIDSim()
    for k in range(0,200):
        sp_dict = {'SP': 32.0} if k == 0 else {} 
        simulator.run(sp_dict)

    simulator.plot_record_data_in_one_figure(taglist=['SP', 'CV'])
    simulator.plot_record_data(taglist=['MV'])

    import matplotlib.pyplot as plt
    plt.show()
