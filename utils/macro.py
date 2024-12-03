LOG_SEPARATOR = '=' * 15


class DictKey:
    """一些 key """
    # 经典的
    ID = 'id'
    TASK = 'task'

    # 经典推理的数据 key
    IMAGE_PATH = 'image_path'
    IMAGE_URL = 'image_url'
    CONTENT = 'content'
    PROMPT = 'prompt'
    RESPONSE_CONTENT = 'response_content'
    PROMPT_TOKENS = 'prompt_tokens'
    COMPLETION_TOKENS = 'completion_tokens'
    COST = 'cost'


    # 两轮推理要用的
    PROMPT1 = 'prompt1'
    PROMPT2 = 'prompt2'
    RESPONSE_CONTENT1 = 'response_content1'
    RESPONSE_CONTENT2 = 'response_content2'
    PROMPT_TOKENS1 = 'prompt_tokens1'
    PROMPT_TOKENS2 = 'prompt_tokens2'
    COMPLETION_TOKENS1 = 'completion_tokens1'
    COMPLETION_TOKENS2 = 'completion_tokens2'
    COST1 = 'cost1'
    COST2 = 'cost2'


class FilePath:
    # 写入的文件名
    TEMP_DIR = 'temp'
    DATA_DIR = 'data'
    TASKS_DIR = 'tasks'
    

class EventType:
    """交互类型"""
    BACK = 'back'
    CLICK = 'click'
    LONG_CLICK = 'long_click'
    INPUT = 'input'
    SWIPE = 'swipe'  # 划动
    DRAG = 'drag'  # 拖拽
    

class APPInfo:
    INTENT_MEITUAN = "com.sankuai.meituan/com.meituan.android.pt.homepage.activity.MainActivity"  # 美团
    INTENT_NOTE = "com.miui.notes/com.miui.notes.ui.NotesListActivity"  # 小米笔记


class STATE:
    """一些返回状态"""
    # 错误
    ERROR_OTHER_APP = -1  # 不在指定 app 中

    # 信息
    INFO_SKIP_NODE = 10  # 跳过节点
    INFO_MAX_DEPTH = 11  # 到达最大深度

    # 正常
    OK = 0  # 无事发生，继续运行
    SUCCESS = 1