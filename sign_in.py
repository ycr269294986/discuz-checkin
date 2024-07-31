import os
import requests
import re

def requests_get(url, use=False, save=False, referer=None, post_data=None, cookies=None):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36'
    }
    session = requests.Session()
    if use and cookies:
        session.cookies.update(cookies)
    if referer:
        headers['Referer'] = referer

    if post_data:
        response = session.post(url, data=post_data, headers=headers)
    else:
        response = session.get(url, headers=headers)
    
    if save:
        cookies = session.cookies.get_dict()

    return response.text, cookies

def get_formhash(response_text):
    match = re.search(r'name="formhash" value="(.*?)"', response_text)
    if match:
        return match.group(1)
    else:
        exit('没有找到formhash')

# 账号信息和论坛地址
user = os.getenv('USERNAME')  # 用户名
pwd = os.getenv('PASSWORD')   # 密码
base_url = os.getenv('BASE_URL')  # 论坛首页地址，结尾带上"/"

# 心情：开心，难过，郁闷，无聊，怒，擦汗，奋斗，慵懒，衰
qdxq = os.getenv('QDXQ', 'kx')  # 签到时使用的心情
todaysay = os.getenv('TODAYSAY', '开心~~~')  # 想说的话

# 账号登录地址
login_page_url = base_url + 'member.php?mod=logging&action=login'
# 账号信息提交地址
login_submit_url = base_url + 'member.php?mod=logging&action=login&loginsubmit=yes&loginhash=LNvu3'
# 签到页面地址
sign_page_url = base_url + 'plugin.php?id=dsu_paulsign:sign'
# 签到信息提交地址
sign_submit_url = base_url + 'plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=0&inajax=0'

print("Starting the sign-in process")

# 访问论坛登录页面，保存Cookies
response, cookies = requests_get(login_page_url, save=True)
print(f"Login page response: {response[:500]}")  # 打印前500个字符以避免过多输出

# 获取DiscuzX论坛的formhash验证串
formhash = get_formhash(response)
print(f"Obtained formhash: {formhash}")

# 构建登录信息
login_data = {
    'username': user,
    'password': pwd,
    'referer': base_url,
    'questionid': 0,
    'answer': '',
    'formhash': formhash,
}

# 携带cookie提交登录信息
response, cookies = requests_get(login_submit_url, use=True, save=True, post_data=login_data, cookies=cookies)
print(f"Login submit response: {response[:500]}")  # 打印前500个字符以避免过多输出

if '欢迎您回来' in response:
    print("Login successful")
    # 访问签到页面
    response, cookies = requests_get(sign_page_url, use=True, save=True, cookies=cookies)
    print(f"Sign page response: {response[:500]}")  # 打印前500个字符以避免过多输出

    # 根据签到页面上的文字来判断今天是否已经签到
    if '您今天已经签到过了或者签到时间还未开始' in response:
        result_str = "今天已签过到\r\n"
    else:
        # 获取formhash验证串
        formhash = get_formhash(response)
        print(f"Sign formhash: {formhash}")

        # 构造签到信息
        post_data = {
            'qdmode': 1,
            'formhash': formhash,
            'qdxq': qdxq,
            'fastreply': 0,
            'todaysay': todaysay,
        }
        # 提交签到信息
        response, _ = requests_get(sign_submit_url, use=True, save=True, post_data=post_data, cookies=cookies)
        print(f"Sign submit response: {response[:500]}")  # 打印前500个字符以避免过多输出

        if '签到成功' in response:
            result_str = "签到成功\r\n"
        else:
            result_str = "签到失败\r\n"
else:
    result_str = "登陆失败\r\n"

print(result_str)
