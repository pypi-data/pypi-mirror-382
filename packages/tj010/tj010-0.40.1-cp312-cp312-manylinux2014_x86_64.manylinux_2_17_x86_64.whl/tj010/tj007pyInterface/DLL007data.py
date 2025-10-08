class UnitModel :
    def __init__(self) :
        self.NumberofNumerator = 0		# 分子系数的个数，没用，准备删掉 
        self.NumberofDenominator = 0		# 分母系数的个数，没用，准备删掉
        self.NumeratorCoefficient = []		# 分子系数  optional，可为空 
        self.DenominatorCoefficient = []		# 分母系数  optional，可为空 
        self.UnitStepRespLength = 0		# 阶跃序列长度，没用，准备删掉 
        self.UnitStepResponse = []		# 阶跃响应序列 
        self.delay = 0		# 纯滞后 
        self.StableGain = 0.0		# 稳态增益 对于积分环节，为稳态增益斜率 
        self.IntegralMark = 0		# 积分标志1：积分环节；0：非积分环节 

class InputVariable :
    def __init__(self) :
        self.MVType = 1		# default: 1  0: DV; 1: MV 
        self.Status = 1		# default: 1   0：检测出现故障；1：正常 
        self.ControlStatus = 0		# 控制状态 default: 0;  0: OFF；1：ON; 2: FeedForward 
        self.KeyVariable = 0		# 关键变量（没用）     default: 0  0: NO; 1: YES 
        self.HiLimit = 100.0		# 上限 
        self.LoLimit = 0.0		# 下限 
        self.PosSpeedLim = 10.0		# 2022-01-16新增 MV正速率限制  
        self.NegSpeedLim = 10.0		# 2022-01-16新增 MV负速率限制 
        self._IncrConstraint = 10.0		# 2022-01-16删除   增量约束(SpeedLimit)  
        self.IRVExpect = 0.0		# IRV期望值    default: 0 
        self.LinearWeight = 0.0		# 线性权重    default: 0 
        self.QuadraticWeight = 0.0		# 二次权重    default: 0 
        self.SoftHiLimit = 0.0		# 缓冲区上间距    default: 0 
        self.SoftLoLimit = 0.0		# 缓冲区下间距    default: 0 
        self.PRIWeight = 0.0		# 优先权重（没用）    default: 0 
        self.IncrementWeight = 1.0		# 增量权重    default: 1 
        self.ErrorWeight = 0.0		# 误差权重    default: 0 
        self.IntBlock = 15		# default: 15 
        self.DVPrd = []		# default: [], v0.28.1新增, 未来DV的预测数组(不包含当前值！) 
                                    # self.DVPrd = [] 表示未来的DV预测使用了默认方式：DVprd = [uk] 

        # 以下属性不记入TaiJiMPC4.0的ojp工程文件 
        # 即：仅允许用脚本修改，作为临时变量，脚本修改结果不存入.ojp的工程文件。
        self.SetNm = -1		# 修改MV的控制时域（非负整数），请慎重！
                                    # 默认: -1，表示启动控制器(Start Control)时/模型更换时使用内部默认值。
                                    # 注意：若要使用内部默认的控制时域，需要：(1)控制器重启(Stop control -> Start control)  或 在线更换模型, (2)SetNm<0 

        # v0.38新增
        self.EngHI = float('inf')        # 工程上限    default: inf
        self.EngLO = -float('inf')        # 工程下限    default: inf
        
        # v0.40新增
        self.OperatingRange = 1.0

class OutputVariable :
    def __init__(self) :
        self.Status = 1		# 状态  default: 1  0：检测出现故障；1：正常 
        self.ControlStatus = 0		# 控制状态 0(default): OFF; 1: ON; 2: PRD only;  
        self.KeyVariable = 0		# 关键变量（没用）     default: 0  0: NO; 1: YES 
        self.ControlType = 2		# 控制类型     1：设定值控制；2：区间控制(StickyRange); 3: 区间控制(FreeRange) 
        self.SetPoint = 0.0		# 设定值 (FTSPBias is included!) 
        self.HiRange = 100.0		# 区间上限 
        self.LoRange = 0.0		# 区间下限 
        self.ClsLpRsponseTime = 2.0		# 闭环响应时间
        self.IRVExpect = 0.0		# IRV期望值    default: 0 
        self.LinearWeight = 0.0		# 线性权重    default: 0 
        self.QuadraticWeight = 0.0		# 二次权重    default: 0 
        self.SoftHiLimit = 0.0		# 缓冲区上间距default: 0即为优化区域上限间距 
        self.SoftLoLimit = 0.0		# 缓冲区下间距default: 0即为优化区域下限间距 
        self.PRIWeight = 1.0		# 优先权重  default: 1 
        self.Priority = 1		# 优先级 
        self.ErrorWeight = 1.0		# 误差权重    default: 1 
        self.IncrementWeight = 100.0		# CV 增量权重 2021-09-04新增 
        self.DistAdaptiveSwt = 0		# 扰动自适应的开关; 0: OFF, 1: ON. 
        self.DistModelOrder = 0		# 干扰模型的阶次 
        self.DistPredHorizon = 6		# 使用干扰模型进行输出预测的长度 
        self.DistAdaptiveMode = 2		# 干扰模型的形式 {0:'', 1:'c0', 2:'c0c1', 3:'c0c1c2'} 
        self.DistAdaptiveDataLen = 3		# 估计干扰模型的数据长度 
        self.DistForgettingFactor = 1.0		# 估计干扰模型的遗忘因子 
        self.DistFilterCoef = 3.0		# 合并输出滤波系数 
        self.FTSPType = 0		# 0: None, 1:协调控制负荷斜坡, 2:协调控制滑压曲线, 3: 架空稳态层 
        self.FTSPRate = 0.0		# Slope Tag in Tai-Ji MPC 
        self.FTSPEnd = 0.0		# "End SP Tag" (FTSPBias is not included!) or "X Axis End Tag" in Tai-Ji MPC 
        self.FTSPNum = 0		# X Axis Cur. Tag in Tai-Ji MPC 
        self.FTSPXY = ""		# strFXY in Tai-Ji MPC  
        self.FTSPTau = 0.0		# Filter in Tai-Ji MPC 
        self.FTSPBias = 0.0		# Delta Tag in Tai-Ji MPC 
        self.FTSPHzn = 0		# Pred Horizon in Tai-Ji MPC
        
        # v0.40新增
        # DeltaErrorWeight准备重写，暂时保留
        # self.DeltaErrorWeight = 0.0		# 差分误差权重    default: 0 
        
        # v0.38新增
        self.SPFilterAlpha = 0.0        # 设定值滤波器的超前参数alpha    default: 0
        self.SPFilterTau = 0.0        # 设定值滤波器的时间常数tau(单位：秒)    default: 0
        self.EngHI = float('inf')        # 工程上限    default: inf
        self.EngLO = -float('inf')        # 工程下限    default: inf
        
        # v0.40新增
        self.OperatingRange = 1.0
        

        # 以下属性不记入TaiJiMPC4.0的ojp工程文件 
        # 即：仅允许用脚本修改，作为临时变量，脚本修改结果不存入.ojp的工程文件。 
        self.ErrWtRngFactor = 0.02		# 2023-03-05 仅在FreeRange条件下起作用。  
                                    # 区间内CV误差权重因子(ErrorWeightInRange = ErrWtRngFactor*ErrorWeight)  
        self.IncWtRngFactor = 0.02		# 2023-03-05 仅在FreeRange条件下起作用。  
                                    # 区间内CV增量权重因子(IncrementWeightInRange = IncWtRngFactor*IncrementWeight) 
        self.IntBlock = 200		# 修改CV的间隔块数（线性间隔），请慎重！ 
        self.SetNp = -1		# 修改CV的预测时域（非负整数），请慎重！ 
                                    # 默认: -1，表示启动控制器(Start Control)时/模型更换时使用内部默认值。 
                                    # 注意：若要使用内部默认的预测时域，需要：(1)控制器重启(Stop control -> Start control) 或 在线更换模型, (2)SetNp<0 

def registe_class():

    import zce

    zce.registe_class(UnitModel)

    zce.registe_class(InputVariable)

    zce.registe_class(OutputVariable)

