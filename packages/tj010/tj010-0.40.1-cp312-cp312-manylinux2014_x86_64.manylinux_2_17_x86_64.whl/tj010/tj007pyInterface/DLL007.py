import logging
import functools
import traceback
import time
from typing import List, Tuple
from tj010.tj007pyInterface.Controller007 import Controller
from tj010.tj007pyInterface.DLL007data import InputVariable, OutputVariable, UnitModel

logger = logging.getLogger('tj010')

def tryWrapper(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            value = func(*args, **kwargs)
            return value
        except Exception as e:
            logger.error(traceback.format_exc())
    return wrapper

class ControllerInterface(Controller):
    def __init__(self) -> None:
        super().__init__()

    @tryWrapper
    def save_mpcobj(self, *args, **kargs) -> None:
        self._save_mpcobj()

    @tryWrapper
    def save_mpcmodel(self, *args, **kargs) -> None:
        self._save_mpcmodel()


    @tryWrapper
    def ControllerFlagInitialization(self, 
                                     path: str = '',    # mpc工程文件的路径与文件名 
                                     ControlInterval: int = 1,  # mpc采样时间，单位秒
                                     *args, **kargs) -> None: 
        self._ControllerFlagInitialization(path=path, ControlInterval=ControlInterval)

    @tryWrapper
    def SetupModel(self, 
                    InputNum: int,    # 输入变量总数        
                    OutputNum: int,   # 输出变量总数
                    ControlModel: List[UnitModel],     # 控制模型 typModel结构的二维数组
                                                       # 维数：（int输出变量总数, int输入变量总数），用于模型预测
                    PlantModel: List[UnitModel],    #工厂模型 typModel结构的二维数组
                                                    # 维数：（int输出变量总数, int输入变量总数），用于仿真时的工厂模型递推。
                    ControlModelFlag: int,  # 控制模型标志    
                                            # 为1，表示模型预测时使用的阶跃响应序列由传递函数计算得来
                                            # 为0，表示模型预测直接使用客户程序给定的阶跃响应序列
                    PlantModelFlag: int,    # 工厂模型标志    
                                            # 为1，表示仿真时工厂模型递推使用的阶跃响应序列由传递函数计算得来
                                            # 为0，表示仿真时工厂模型递推直接使用客户程序给定的阶跃响应序列
                    ControlInterval: int,   # 控制周期, 要与客户程序生成阶跃响应序列时使用的控制周期一致
                    InputTagName: List[str],    # 输入输出变量名称数组，分别存放于InputTagName和OutputTagName
                    OutputTagName: List[str],
                    **kargs
                    ) -> None:
        self._SetupModel(InputNum, OutputNum, ControlModel, PlantModel, ControlModelFlag, PlantModelFlag,
                         ControlInterval, InputTagName, OutputTagName,  **kargs)


    @tryWrapper
    def use_basic_MPCmodel(self) -> None:
        self._use_basic_MPCmodel()

    @tryWrapper
    def use_interp_LPVmodel(self,
                            working_value: float  # 工作点变量的值
                            ) -> None:
        self._use_interp_LPVmodel(working_value)

    @tryWrapper
    def SetupLPVModelPy(self, 
                        model_id: int, 
                        working_point: float, 
                        yu_model_tf: dict
                        ) -> None:
        self._SetupLPVModelPy(model_id, working_point, yu_model_tf)

    @tryWrapper
    def SetupLPVModel(self, 
                       model_id: int,                  # 模型ID
                       working_point: float,           # 工作点
                       InputNum: int,                  # 输入变量总数        
                       OutputNum: int,                 # 输出变量总数
                       ControlModel: List[UnitModel],  # 控制模型 typModel结构的二维数组
                                                       # 维数：（int输出变量总数, int输入变量总数），用于模型预测
                       InputTagName: List[str],        # 输入变量名称数组
                       OutputTagName: List[str],       # 输出变量名称数组
                       **kargs                         # 输入输出变量名称数组，分别存放于InputTagName和OutputTagName
                       ) -> None:
        self._SetupLPVModel(model_id, working_point, InputNum, OutputNum, ControlModel, InputTagName, OutputTagName,  **kargs)

    @tryWrapper
    def DeleteLPVModel(self, 
                       model_id: int    # 根据id删除工作点模型
                       ) -> None:
        self._DeleteLPVModel(model_id)
    
    @tryWrapper
    def SetupModelPy(self, 
                     yu_model_tf: dict
                     ) -> None:
        self._SetupModelPy(yu_model_tf)

    @tryWrapper
    def ProcessVariableInitializationPy(self):
        self._ProcessVariableInitializationPy()

    @tryWrapper
    def ProcessVariableInitialization(self,
                                      InputVar: List[InputVariable],    # typInputVariable结构的一维数组，长度InputNum 
                                      OutputVar: List[OutputVariable],      # typOutputVariable结构的一维数组 长度OutputNum
                                      **kargs   # 输入输出变量名称数组，分别存放于InputTagName和OutputTagName
                                      ) -> None:
        self._ProcessVariableInitialization(InputVar, OutputVar, **kargs)

    @tryWrapper
    def ModifyInputVariablePy(self, 
                              mvtag, 
                              InputVar: InputVariable
                              ) -> None:
        self._ModifyInputVariablePy(mvtag, InputVar)

    @tryWrapper
    def ModifyInputVariable(self,
                            VarIndex: int,  # 变量下标：取值范围[1，nu]    
                            InputVar: InputVariable,   # 变量内容：标量，类型：typInputVariable
                            ) -> None:
        self._ModifyInputVariable(VarIndex, InputVar)
    
    @tryWrapper    
    def ModifyMutiInputVariables(self, VarIndexList: list[int], InputVarList: list[InputVariable]) -> None:
        for VarIndex, InputVar in zip(VarIndexList, InputVarList):
            self._ModifyInputVariable(VarIndex, InputVar)

    @tryWrapper            
    def ModifyOutputVariablePy(self, 
                               cvtag, 
                               OutputVar: OutputVariable
                               ) -> None:
        self._ModifyOutputVariablePy(cvtag, OutputVar)

    @tryWrapper
    def ModifyOutputVariable(self,
                             VarIndex: int,   # 变量下标：取值范围[1，ny]    
                             OutputVar: OutputVariable,   # 变量内容：标量，类型：typOutputVariable 
                             ) -> None:
        self._ModifyOutputVariable(VarIndex, OutputVar)

    @tryWrapper
    def ModifyMutiOutputVariables(self, VarIndexList: list[int], OutputVarList: list[OutputVariable]) -> None:
        for VarIndex, OutputVar in zip(VarIndexList, OutputVarList):
            self._ModifyOutputVariable(VarIndex, OutputVar)

    @tryWrapper
    def ModifyGainFactor(self, 
                         GainFactor1DList: list # GainFactor 1维数组
                         ) -> None:   
        self._ModifyGainFactor(GainFactor1DList)

    @tryWrapper
    def ModifyGainFactorPy(self, 
                           cvtag, 
                           mvtag, 
                           gainFactor: float = 1.0):
        self._ModifyGainFactorPy(cvtag, mvtag, gainFactor)

    @tryWrapper        
    def DynamicMatrixCreationandBlockDesign(self) -> None:
        self._DynamicMatrixCreationandBlockDesign()

    @tryWrapper        
    def PlantRecursion(self,
                       InputValue: List[float],     # 输入变量值，一维数组 长度InputNum
                       OutputValue: List[float]     # 输出变量值，一维数组 长度OutputNum
                       ) -> List[float]:     # 输出变量值，一维数组 长度OutputNum 
        OutputSim = self._PlantRecursion(InputValue, OutputValue)
        return OutputSim
    
    @tryWrapper
    def PlantRecursionPy(self, data_dict: dict) -> dict:
        return super()._PlantRecursionPy(data_dict)

    @tryWrapper
    def ModelPrediction(self,
                        InputValue: List[float],     # 输入变量值，一维数组 长度InputNum
                        OutputValue: List[float]     # 输出变量值，一维数组 长度OutputNum
                        ) -> None:
        self._ModelPrediction(InputValue, OutputValue)

    @tryWrapper
    def ControllerCalculationPy(self, data: dict) -> dict:
        MV_DV_action_dict = self._ControllerCalculationPy(data)
        return MV_DV_action_dict

    def ControllerCalculation(self, 
                              InputValue: List[float],         # 输入变量值，一维数组 长度InputNum
                              OutputValue: List[float],        # 输出变量值，一维数组 长度OutputNum
                              m: int = 20,
                              ) -> Tuple[List[float], List[float], List[float], List[float], List[float], List[float],
                                         List[float], List[float], List[float], List[float]]:
        try:
            result = self._ControllerCalculation(InputValue, OutputValue, m=m)
        except Exception as e:
            logger.error(traceback.format_exc())
            result = self._errorControllerCalculationReturn(InputValue, OutputValue, m=m)
        finally:
            (InputPredVal, InputSSVal, InputPredHorizon, 
             OutputPredVal, OutputSSVal, OutputPredHorizon, 
             InputErrPct, InputIncPct, 
             OutputErrPct, OutputIncPct, 
             InputMaxDeltaPrd, OutputMaxDeltaPrd) = result
        return (InputPredVal,        # 返回值，m*InputNum * 1, MV、DV预测值
                InputSSVal,            # 返回值，InputNum * 1, MV、DV稳态值
                InputPredHorizon,    # 返回值，InputNum * 1, MV、DV模型时域
                OutputPredVal,      # 返回值，m*OutputNum* 1, CV预测值
                OutputSSVal,        # 返回值，OutputNum* 1, CV稳态值
                OutputPredHorizon,   # 返回值，OutputNum* 1, CV模型时域
                InputErrPct,        # 返回值，InputNum* 1, MV、DV误差百分比
                InputIncPct,        # 返回值，InputNum* 1, MV、DV增量百分比
                OutputErrPct,       # 返回值，OutputNum* 1, CV误差百分比
                OutputIncPct,       # 返回值，OutputNum* 1, CV增量百分比
                InputMaxDeltaPrd,  # 返回值，InputNum* 1, MV、DV预测值最大变化量
                OutputMaxDeltaPrd, # 返回值，OutputNum* 1, CV预测值最大变化量
                )

    @tryWrapper
    def getLPVmodelStatus(self) -> dict:
        '''
        返回值，dict，存储LPV模型的状态信息
            d = {'LPV_SW': 0 or 1,   # LPV模型开关，0表示关闭，1表示开启 
                 'working_value': float,  # 工作点变量的当前值
                 'model_id': list[int],  # LPV模型ID
                 'working_point': list[float],  # ID对应模型的工作点列表
                 'current_weight': list[float],  # ID对应模型的权重列表
                 }
        
        '''
        return self._get_LPVmodel_status()
    
    @tryWrapper
    def StopControl(self) -> None:
        self._StopControl()

    @tryWrapper
    def getResultMVCVDict(self):
        ResMVDict, ResCVDict = self._getResultMVCVDict()
        return ResMVDict, ResCVDict



