import os 
import re 
import sys 
import json
import requests 
from datetime import datetime, timedelta

# cookie_list = os.getenv("COOKIE_QUARK").split('\n|&&')  # 移到main函数中通过get_env获取

# Telegram 通知功能
def send(title, message):
    # 获取当前 UTC 时间，并转换为北京时间（+8小时）
    now = datetime.utcnow()
    beijing_time = now + timedelta(hours=8)
    formatted_time = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
    
    # 打印调试信息
    print(f"{title}: {message}")
    
    # 直接嵌入 Telegram 配置
    bot_token = "8193671460:AAHg4KToSp9beDByiBg9WWbZVrjBTwAW2bM"
    chat_id = "7761148097"
    
    # 如果 Telegram Bot Token 和 Chat ID 都配置了，则发送消息
    if bot_token and chat_id:
        try:
            # 构建消息内容
            message_text = f"<b>执行时间:</b> {formatted_time}\n\n<b>{title}</b>\n{message}"
            
            # 构造按钮的键盘布局
            keyboard = {
                "inline_keyboard": [
                    [
                        {
                            "text": "夸克网盘",
                            "url": "https://pan.quark.cn/"
                        }
                    ]
                ]
            }
            
            # 发送消息的 URL
            send_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            # 构造请求数据
            payload = {
                "chat_id": chat_id,
                "text": message_text,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(keyboard)
            }
            
            # 发送请求
            response = requests.post(send_url, data=payload)
            response.raise_for_status()
            print(f"✅ Telegram 通知发送成功")
        except Exception as e:
            print(f"❌ 发送 Telegram 消息时发生错误: {str(e)}")

# 获取环境变量 
def get_env(): 
    # 判断 COOKIE_QUARK是否存在于环境变量 
    if "COOKIE_QUARK" in os.environ: 
        # 读取系统变量以 \n 或 && 分割变量 
        cookie_list = re.split('\n|&&', os.environ.get('COOKIE_QUARK')) 
    else: 
        # 标准日志输出 
        print('❌未添加COOKIE_QUARK变量') 
        send('夸克自动签到', '❌未添加COOKIE_QUARK变量') 
        # 脚本退出 
        sys.exit(0) 

    return cookie_list 

# 其他代码...

class Quark:
    '''
    Quark类封装了签到、领取签到奖励的方法
    '''
    def __init__(self, user_data):
        '''
        初始化方法
        :param user_data: 用户信息，用于后续的请求
        '''
        self.param = user_data

    def convert_bytes(self, b):
        '''
        将字节转换为 MB GB TB
        :param b: 字节数
        :return: 返回 MB GB TB
        '''
        units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = 0
        while b >= 1024 and i < len(units) - 1:
            b /= 1024
            i += 1
        return f"{b:.2f} {units[i]}"

    def get_growth_info(self):
        '''
        获取用户当前的签到信息
        :return: 返回一个字典，包含用户当前的签到信息
        '''
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/info"
        querystring = {
            "pr": "ucpro",
            "fr": "android",
            "kps": self.param.get('kps'),
            "sign": self.param.get('sign'),
            "vcode": self.param.get('vcode')
        }
        response = requests.get(url=url, params=querystring).json()
        #print(response)
        if response.get("data"):
            return response["data"]
        else:
            return False

    def get_growth_sign(self):
        '''
        获取用户当前的签到信息
        :return: 返回一个字典，包含用户当前的签到信息
        '''
        url = "https://drive-m.quark.cn/1/clouddrive/capacity/growth/sign"
        querystring = {
            "pr": "ucpro",
            "fr": "android",
            "kps": self.param.get('kps'),
            "sign": self.param.get('sign'),
            "vcode": self.param.get('vcode')
        }
        data = {"sign_cyclic": True}
        response = requests.post(url=url, json=data, params=querystring).json()
        #print(response)
        if response.get("data"):
            return True, response["data"]["sign_daily_reward"]
        else:
            return False, response["message"]

    def queryBalance(self):
        '''
        查询抽奖余额
        '''
        url = "https://coral2.quark.cn/currency/v1/queryBalance"
        querystring = {
            "moduleCode": "1f3563d38896438db994f118d4ff53cb",
            "kps": self.param.get('kps'),
        }
        response = requests.get(url=url, params=querystring).json()
        # print(response)
        if response.get("data"):
            return response["data"]["balance"]
        else:
            return response["msg"]

    def do_sign(self):
        '''
        执行签到任务
        :return: 返回一个字符串，包含签到结果
        '''
        log = ""
        # 每日领空间
        growth_info = self.get_growth_info()
        if growth_info:
            user_type = "<b>88VIP用户</b>" if growth_info['88VIP'] else "普通用户"
            log += (
                f"📌 {user_type} {self.param.get('user', '未知用户')}\n"
                f"💾 <b>网盘总容量</b>：{self.convert_bytes(growth_info['total_capacity'])}\n"
                f"📈 <b>签到累计容量</b>：")
            if "sign_reward" in growth_info['cap_composition']:
                log += f"{self.convert_bytes(growth_info['cap_composition']['sign_reward'])}\n"
            else:
                log += "0 MB\n"
            if growth_info["cap_sign"]["sign_daily"]:
                log += (
                    f"✅ <b>签到状态</b>: 今日已签到\n"
                    f"📊 <b>获得容量</b>: +{self.convert_bytes(growth_info['cap_sign']['sign_daily_reward'])}\n"
                    f"🔥 <b>连签进度</b>: {growth_info['cap_sign']['sign_progress']}/{growth_info['cap_sign']['sign_target']}\n"
                )
            else:
                sign, sign_return = self.get_growth_sign()
                if sign:
                    log += (
                        f"✅ <b>签到状态</b>: 签到成功\n"
                        f"📊 <b>获得容量</b>: +{self.convert_bytes(sign_return)}\n"
                        f"🔥 <b>连签进度</b>: {growth_info['cap_sign']['sign_progress'] + 1}/{growth_info['cap_sign']['sign_target']}\n"
                    )
                else:
                    log += f"❌ <b>签到状态</b>: 签到异常 - {sign_return}\n"
        else:
            # log += f"❌ 签到异常: 获取成长信息失败\n"
            raise Exception("❌ 签到异常: 获取成长信息失败")  # 适用于单账号情形，当 cookie 值失效后直接报错，方便通过 github action 的操作系统来进行提醒 如果你使用的是多账号签到的话，不要跟进此更新

        return log


def main():
    '''
    主函数
    :return: 返回一个字符串，包含签到结果
    '''
    msg = ""
    global cookie_quark
    cookie_quark = get_env()

    total_accounts = len(cookie_quark)
    print(f"✅ 检测到共 {total_accounts} 个夸克账号\n")
    
    # 添加总览信息
    msg += f"📋 共检测到 {total_accounts} 个夸克账号\n\n"

    i = 0
    while i < len(cookie_quark):
        try:
            # 获取user_data参数
            user_data = {}  # 用户信息
            for a in cookie_quark[i].replace(" ", "").split(';'):
                if not a == '':
                    user_data.update({a[0:a.index('=')]: a[a.index('=') + 1:]})
            
            # 开始任务
            msg += f"🔹 <b>第{i + 1}个账号</b>\n"
            # 登录
            log = Quark(user_data).do_sign()
            msg += log + "\n"
            
        except Exception as e:
            msg += f"❌ 账号 {i + 1} 处理异常: {str(e)}\n\n"
        finally:
            i += 1

    # 优化消息结尾
    if msg.endswith("\n"):
        msg = msg[:-1]

    try:
        send('夸克自动签到', msg)
    except Exception as err:
        print(f'{str(err)}\n❌ 错误，请查看运行日志！')

    return msg


if __name__ == "__main__":
    print("----------夸克网盘开始签到----------")
    main()
    print("----------夸克网盘签到完毕----------")
