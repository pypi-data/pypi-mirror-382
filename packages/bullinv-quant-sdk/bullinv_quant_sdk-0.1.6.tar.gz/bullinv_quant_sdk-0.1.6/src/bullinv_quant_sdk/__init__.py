import os
from dotenv import load_dotenv

# 获取用户当前工作目录
current_dir = os.getcwd()

# 尝试从用户当前工作目录加载.env文件
dotenv_path = os.path.join(current_dir, '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)
else:
    # 如果在当前目录找不到，尝试默认加载（可能在包目录或其他位置）
    load_dotenv()

# 导出主要类和函数，使它们可以直接从包中导入
from .quote import BullinvQuote, INDICATORS

# 检查必要的环境变量
def check_environment():
    """检查必要的环境变量是否已设置"""
    required_vars = [
        "CLICKHOUSE_HOST",
        "CLICKHOUSE_PORT",
        "CLICKHOUSE_USER",
        "CLICKHOUSE_PASSWORD",
        "CLICKHOUSE_DATABASE"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# 在导入时执行环境检查
check_environment()

__all__ = ['BullinvQuote', 'INDICATORS']

