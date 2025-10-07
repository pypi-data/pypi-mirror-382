from tjdcs.version import __version__
from tjdcs.clsSFilter import sFilter
from tjdcs.clsZFilter import zFilter
from tjdcs.clsSoftSensor import SoftSensorBiasUpdate, LabDataRecorder, OPCItem, load_predict_module, SSTaskConfig, SS_task

from tjdcs.clsInterface import ConstDect
from tjdcs.clsInterface import RateLimit
from tjdcs.clsInterface import WatchDog

from tjdcs.clsInterface import LPVPlantSim
from tjdcs.clsInterface import TestSignalGen
from tjdcs.clsInterface import MIMOSim
from tjdcs.clsInterface import SISOSim

from tjdcs.clsInterface import TJProcSim
from tjdcs.clsInterface import TJProcSim2
from tjdcs.clsInterface import LDLAG
from tjdcs.clsInterface import AntiWindupLimter
from tjdcs.clsPID import PID

from tjdcs.funInterface import current_time_str, dict2pairs, pair2dict, str2xpyp, c2d
from tjdcs.funInterface import plt_model_stp, get_model_stp
from tjdcs.funInterface import plot_model_stp
# from .funInterface import get_ModelDict_tags, tf2stp, stp2ipr, stp_stable_len, plot_model_stp

from tjdcs.clsSimulink import Simulink
from tjdcs.clsProcessSim import ProcessSim


from tjdcs.algorithm.utilities import is_OPCGatePy_installed
if is_OPCGatePy_installed():
    from tjdcs.clsSimulinkOPCGateTask import SimulinkOPCGateTask



