if __name__ == '__main__':
    from algorithm.utilities import find_project_path
    prj_path = find_project_path(matker='setup.py')
    print(f"{prj_path = }")
    import sys
    sys.path.insert(0, prj_path)
    # sys.path.append(prj_path)


from tjdcs.algorithm import tjFilter


class zFilter(tjFilter.zFilter):
    r'''
    离散滤波器，可给定初值。
    若给定初值，以初值为起点进行滤波。
    若未给定初值，以滤波器运行时输入的第一个值以及指定输出作为起点滤波。
    可进行单步滤波(__call__或run), 也可进行多步滤波run_multistep。
    '''
    def __init__(self, Bz = [0, 0.1], Az = [1, -0.9], u_ini = None, y_ini = None):
        r'''
        初始化滤波器。
        若给定初值，滤波器运行时以初值为起点进行滤波。
        若未给定初值，在滤波器第一次运行时，以输入的第一个值以及指定输出作为起点。
        
        parameters
        ----------
        Bz: numerator coefficient of discrete filter 
        Az: denominator coefficient of discrete filter 
        u_ini: optional, float or None, initial value of the filter input
        y_ini: optional, float or None, initial value of the filter output
        '''
        return super().__init__(Bz, Az, u_ini, y_ini)

    def __call__(self, Ut: float, y_ini: float = 0.0) -> float:
        r'''
        计算滤波器的单步输出
        (同run)

        parameters
        ----------
        Ut: input of the discrete filter
        y_ini: initial value of the filter output, default is 0.0 

        returns
        -------
        Yt: float, filter output

        Notes
        -----
        Initial calculation takes effect for only one time.
        If u_ini is not assigned before, Ut will be the initial value when first call.
        '''
        return super().__call__(Ut, y_ini)

    
    def run(self, Ut: float, y_ini = 0.0) -> float:
        r'''
        计算滤波器的单步输出
        (同__call__)

        parameters
        ----------
        Ut: input of the discrete filter
        y_ini: initial value of the filter output, default is 0.0 

        returns
        -------
        Yt: float, filter output

        Notes
        -----
        Initial calculation takes effect for only one time.
        If u_ini is not assigned before, Ut will be the initial value when first call.
        '''
        return super().run(Ut, y_ini)

   
    def run_multistep(self, U_arr: list, y_ini: float = 0):   
        r'''
        计算滤波器的多步输出

        parameters
        ----------
        U_arr: array like, input sequence of filter
        y_ini: initial value of the filter output, default is 0.0

        returns
        -------
        Y_arr: array like, output sequence of filter

        Notes
        -----
        Initial calculation takes effect for only one time.
        If u_ini is not assigned before, Ut will be the initial value when first call.
        '''
        return super().run_multistep(U_arr, y_ini)


# demo
if __name__ == '__main__':
    import numpy as np
    import matplotlib.pyplot as plt
    fil = zFilter(Bz = [0, 1, 0.5], Az = [1, -1.5, 0.7])
    N1, N2 = 50, 50
    u = [30.0]+[31.0]*(N1-1)+[30.0]*N2
    y = []
    for k in range(0,N1+N2):
        yk = fil(u[k], y_ini=30)
        y.append(yk)

    fil2 = zFilter(Bz = [0, 1, 0.5], Az = [1, -1.5, 0.7])
    y_arr = fil2.run_multistep(u, y_ini=30)

    plt.plot(u)
    plt.plot(y)
    plt.plot(y_arr, '-.')
    plt.show()  

    

