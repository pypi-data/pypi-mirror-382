from tjdcs.algorithm import tjFilter

class sFilter(tjFilter.sFilter):
    r'''
    输入参数为连续传递函数的滤波器，可给定初值。
    若给定初值，以初值为起点进行滤波。
    若未给定初值，以滤波器运行时输入的第一个值以及指定输出作为起点滤波。
    可进行单步滤波(__call__或run), 也可进行多步滤波run_multistep。
    '''
    def __init__(self, Bs = [1], As = [5, 1], Ts = 1, u_ini = None, y_ini = None):
        r'''
        初始化滤波器，输入参数为连续传递函数，需要指定采样时间进行离散化。
        若给定初值，滤波器运行时以初值为起点进行滤波。
        若未给定初值，在滤波器第一次运行时，以输入的第一个值以及指定输出作为起点。
        
        parameters
        ----------
        Bs: numerator coefficient of continuous filter 
        As: denominator coefficient of continuous filter 
        Ts: sampling time, default is 1
        u_ini: optional, float or None, initial value of the filter input
        y_ini: optional, float or None, initial value of the filter output
        '''
        super().__init__(Bs, As, Ts, u_ini, y_ini)

    def __call__(self, Ut, y_ini = 0.0):
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

    
    def run(self, Ut, y_ini = 0.0):
        r'''
        计算滤波器的单步输出
        (同__call__)

        parameters
        ----------
        Ut: input of the continuous filter
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

    def run_multistep(self, U_arr, y_ini = 0):   
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
    fil = sFilter(Bs = [1.0], As = [15, 1])
    N1, N2 = 100, 100
    u = np.hstack([np.random.randn(N1), 3*np.ones(N2)])
    y = []
    for k in range(0,N1+N2):
        yk = fil(u[k], y_ini=u[k])
        y.append(yk)

    plt.plot(u)
    plt.plot(y)
    plt.show()  