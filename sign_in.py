import os
import requests
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def requests_get(url, use=False, referer=None, post_data=None, cookies=None):
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
    
    return response.text

def get_formhash(response_text):
    match = re.search(r'name="formhash" value="(.*?)"', response_text)
    if match:
        return match.group(1)
    else:
        exit('没有找到formhash')

def send_email(subject, body, from_email, to_email, smtp_server, smtp_port, smtp_user, smtp_password):
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    text = msg.as_string()
    server.sendmail(from_email, to_email, text)
    server.quit()

# 从环境变量中获取Cookies字符串
cookies_str = os.getenv('COOKIES')  # 论坛的Cookies字符串
# 将Cookies字符串解析为字典
cookies = {item.split('=')[0]: item.split('=')[1] for item in cookies_str.split('; ')}

base_url = os.getenv('BASE_URL')  # 论坛首页地址，结尾带上"/"

# 心情：开心，难过，郁闷，无聊，怒，擦汗，奋斗，慵懒，衰
qdxq = os.getenv('QDXQ', 'kx')  # 签到时使用的心情
todaysay = os.getenv('TODAYSAY', '开心~~~')  # 想说的话

# 邮件相关环境变量
smtp_server = os.getenv('SMTP_SERVER')
smtp_port = int(os.getenv('SMTP_PORT', 587))
smtp_user = os.getenv('SMTP_USER')
smtp_password = os.getenv('SMTP_PASSWORD')
from_email = os.getenv('FROM_EMAIL')
to_email = os.getenv('TO_EMAIL')

# 签到页面地址
sign_page_url = base_url + 'plugin.php?id=dsu_paulsign:sign'
# 签到信息提交地址
sign_submit_url = base_url + 'plugin.php?id=dsu_paulsign:sign&operation=qiandao&infloat=0&inajax=0'

print("Starting the sign-in process")

# 访问签到页面
response = requests_get(sign_page_url, use=True, cookies=cookies)
print(f"Sign page response: {response[:500]}")  # 打印前500个字符以避免过多输出

# 根据签到页面上的文字来判断今天是否已经签到
if '您今天已经签到过了或者签到时间还未开始' in response:
    result_str = "论坛今天已签过到\r\n"
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
    response = requests_get(sign_submit_url, use=True, post_data=post_data, cookies=cookies)
    print(f"Sign submit response: {response[:500]}")  # 打印前500个字符以避免过多输出

    if '签到成功' in response:
        result_str = "论坛签到成功\r\n!"
    else:
        result_str = "论坛签到失败!\r\n"

print(result_str)

# 发送邮件通知
subject = "论坛签到结果通知"
send_email(subject, result_str, from_email, to_email, smtp_server, smtp_port, smtp_user, smtp_password)
