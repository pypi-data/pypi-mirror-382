if __name__ == '__main__':
    from algorithm.utilities import find_project_path
    prj_path = find_project_path(matker='setup.py')
    print(f"{prj_path = }")
    import sys
    sys.path.insert(0, prj_path)
    # sys.path.append(prj_path)

import copy
from tjdcs import Simulink, MIMOSim

class ProcessSim(Simulink):
    def __init__(self, plant_dict: dict, sim_ini_dict: dict, disturb_dict: dict, TS = 1) -> None:
        super().__init__(data = sim_ini_dict, TS = TS)
        self.plant = MIMOSim(plant_dict, sim_ini_dict, TS)
        self.disturb_dict = copy.deepcopy(disturb_dict)
        try:
            self.N = len(next(iter(self.disturb_dict.values())))
        except:
            self.N = 10000
            
    def get_plant(self):
        return self.plant
            
    def task(self):
        data = self.get_data()
        input_list = self.plant.get_mv_list()
        output_list = self.plant.get_cv_list()
        
        _count = self.get_task_count() % self.N
        dv_dict = {k:v[_count] for k,v in self.disturb_dict.items() if k in input_list}
        data.update(dv_dict)
        
        cv_noise_dict = {k:v[_count] for k,v in self.disturb_dict.items() if k in output_list}
        
        y_data = self.plant.run(u_Value_Dict = data, v_Value_Dict=cv_noise_dict)
        data.update(y_data)
        
if __name__ == '__main__':
    import numpy as np
    # 被控对象传递函数
    plant_model = { 'CV1': {'MV1': {'mode': 'tf_s', 'num_s': [0.6], 'den_s': [20.0, 1.0], 'iodelay_s': 3},
                            'DV1': {'mode': 'tf_s', 'num_s': [2.6], 'den_s': [10.0, 1.0], 'iodelay_s': 1}}}

    # 定义仿真初值（必须包含所有位号）
    sim_ini_dict = {'MV1': 15,
                    'CV1': 31,
                    'DV1': 10}
    
    N = 10000
    disturb_dict = {'CV1': np.random.randn(N), 'DV1': np.random.randn(N)}
    
    
    p = ProcessSim(plant_model, sim_ini_dict, disturb_dict = disturb_dict, TS = 1)
    
    for k in range(100):
        if k == 50:
            p.get_data()['DV1'] = 20
        p.run()
        print(p.get_data())