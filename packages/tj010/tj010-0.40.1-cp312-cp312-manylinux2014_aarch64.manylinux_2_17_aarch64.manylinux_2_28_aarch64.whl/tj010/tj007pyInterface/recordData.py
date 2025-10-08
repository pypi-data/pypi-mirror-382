from collections import deque

class MV_Data:
    def __init__(self, tag_name = None, maxlen = 6000) -> None:
        self.tag_name = tag_name            # MV的标签
        self.u = deque(maxlen=maxlen)   # MV的值
        self.uStar = deque(maxlen=maxlen)  # MV的稳态值
        self.uLO = deque(maxlen=maxlen)  # MV的下界
        self.uHI = deque(maxlen=maxlen)  # MV的上界
        self.uControlStatus = deque(maxlen=maxlen)  # MV的运行状态（ON/OFF/FeedForward）
        self.uFuture = []

class CV_Data:
    def __init__(self, tag_name = None, maxlen = 6000) -> None:
        self.tag_name = tag_name            # CV的标签
        self.y = deque(maxlen=maxlen)   # CV的值
        self.yStar = deque(maxlen=maxlen)  # CV的稳态值
        self.ySP = deque(maxlen=maxlen)  # CV的设定值
        self.yLO = deque(maxlen=maxlen)  # CV的区间下界
        self.yHI = deque(maxlen=maxlen)  # CV的区间上界
        self.yControlType = deque(maxlen=maxlen)  # CV的控制类型（设定值or区间）
        self.yControlStatus = deque(maxlen=maxlen)  # CV的运行状态
        self.yPRD0 = []
        self.yPRD = []

class Other_Data:
    def __init__(self, tag_name = None, maxlen = 6000) -> None:
        self.tag_name = tag_name
        self.data = deque(maxlen=maxlen)


class LPV_Weighting_Data:
    def __init__(self, maxlen = 6000) -> None:
        self.WorkingVariable = deque(maxlen=maxlen)
        self.LocalModelWeight = {}
        for model_id in range(1,10):
            self.LocalModelWeight[model_id] = deque(maxlen=maxlen)



class MPCDataRecord:
    def __init__(self, cv_tag_list, mv_tag_list, maxlen = 6000) -> None:
        self.Samples = deque(maxlen=maxlen)
        self.RunTime = deque(maxlen=maxlen)
        self.MVs = {mv_tag: MV_Data(mv_tag, maxlen) for mv_tag in mv_tag_list}
        self.CVs = {cv_tag: CV_Data(cv_tag, maxlen) for cv_tag in cv_tag_list}
        self.LPV = LPV_Weighting_Data(maxlen = maxlen)
