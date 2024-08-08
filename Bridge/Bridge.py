from mcdreforged.api.types import PluginServerInterface,Info
from mcdreforged.api.command import *
from mcdreforged.api.all import *
from pywinauto.application import Application
from pywinauto.keyboard import send_keys
import threading
import pyperclip
import re
import queue
import os
import requests

PLUGIN_METADATA = {
    'id': 'bridge',
    'version': '1.0.1',
    'name': 'Bridge',
    'author': 'Tuffy163'
}

version = '1.0.1'

def check_update(server):
    global version
    url_1 = 'https://tuffy163.github.io/Bridge/version.html'
    url_2 = 'https://tuffy163.github.io/Bridge/Bridge.py'
    myfile_1 = requests.get(url_1)
    myfile_2 = requests.get(url_2)
    server.say('§a当前版本为§r§c'+version+'§r§a，云端版本为§r§c'+myfile_1.text[:-1])
    if myfile_1.text[:-1] != version:
        open('plugins/Bridge.py','wb').write(myfile_2.content)
        server.say('§e插件更新完成，请使用!!MCDR reload plugin重载插件')
    else :
        server.say('§e插件版本为最新版，不需要进行更新')

def is_time_format(time_str):
    pattern = r'^([0-2]?[0-9]):([0-5]?[0-9])$'
    match = re.match(pattern, time_str)
    if match:
        hour, minute = map(int, match.groups())
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return True
    return False

running = False
running2 = False
running3 = True
task = queue.Queue()

class Bind:
    def __init__(self, qq, id):
        self.qq = qq
        self.id = id

    def __str__(self):
        return f"{self.qq},{self.id}"

    @staticmethod
    def from_str(s):
        parts = s.split(',')
        return Bind(parts[0], parts[1])

def save(binds, filename):
    with open(filename, 'w') as f:
        for bind in binds:
            f.write(str(bind) + '\n')

def load(filename):
    binds = []
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            pass
    with open(filename, 'r') as f:
        for line in f:
            binds.append(Bind.from_str(line.strip()))
    return binds

def on_player_joined(server: PluginServerInterface, player: str, info: Info):
    if running3:
        binds = load('qqbinds.txt')
        find = False
        for bind in binds:
            if bind.id == player:
                find = True
        if not find and not player.startswith('bot_'):
            server.execute('kick '+player+' 请加入QQ群467581900添加白名单')

def on_info(server: PluginServerInterface, info: Info):
    if info.is_user :
        if info.content == '!!bridge listen' :
            if running == False:
                thread = threading.Thread(target=Receive,args=(server,))
                thread.start()
                server.say('§a监听线程启动成功')
            else :
                server.say('§c监听线程已经启动')
        if info.content == '!!bridge send' :
            if running2 == False:
                thread2 = threading.Thread(target=Send,args=(server,))
                thread2.start()
                server.say('§a发送线程启动成功')
            else :
                server.say('§c发送线程已经启动')
        if info.content == '!!bridge locate' :
            try:
                global app
                global dlg
                global chat_box
                global send_box
                global message
                explorer = Application(backend="uia").connect(path="explorer.exe")
                sys_tray = explorer.window(class_name="Shell_TrayWnd")
                sys_tray.child_window(title_re='( )?QQ:').click()
                app = Application(backend='uia').connect(title='QQ',timeout = 10)
                dlg = app.window(class_name = 'Chrome_WidgetWin_1',title='QQ')
                chat_box = dlg.child_window(title = '八方旅人|1.21|至夏',control_type = 'Edit')
                send_box = dlg.child_window(title = '发送',control_type = 'Button')
                message = dlg.child_window(title = '消息列表',control_type = 'Window')
                server.say('§a定位窗口成功')
            except:
                server.say('§c定位窗口失败')
        if info.content == '!!bridge whitelist' :
            if server.get_permission_level(info) <= 1:
                server.say('§e你没有足够的权限使用此命令')
            else :
                global running3
                running3 = not running3
                if running3:
                    server.say('§a白名单已开启')
                else:
                    server.say('§c白名单已关闭')
        if info.content == '!!bridge update' :
            if info.player == 'Tuffy163':
                check_update(server)
            else :
                server.say('§c只有开发者能够使用此命令')
        if info.content == '!!bridge state' :
            if running:
                server.say('§a监听线程状态为开启')
            else :
                server.say('§c监听线程状态为关闭')
            if running2:
                server.say('§a发送线程状态为开启')
            else :
                server.say('§c发送线程状态为关闭')
            if running3:
                server.say('§a白名单状态为开启')
            else :
                server.say('§c白名单状态为关闭')
        if info.content == '!!bridge' :
            server.say('§e!!bridge 查看帮助信息')
            server.say('§e!!bridge locate 定位窗口')
            server.say('§e!!bridge listen 启动监听线程')
            server.say('§e!!bridge send 启动发送线程')
            server.say('§e!!bridge state 查看状态')
            server.say('§e!!bridge whitelist 切换白名单状态')
        if not info.player == None and not info.content == None :
            task.put('[MC] ' + info.player + ' : ' + info.content)
    else :
        if 'joined the game' in info.content :
            task.put('[MC] ' + info.content)
        if 'left the game' in info.content :
            task.put('[MC] ' + info.content)

def Receive(server):
    global running
    running = True
    try:
        pre_message = ''
        while True:
            Group = message.children(control_type = 'Group')
            n = 0
            while True:
                n += 1
                Text = Group[n].children(control_type = 'Text')
                if len(Text) == 1:
                    if not is_time_format(Text[0].window_text()):
                        Last_message = Group[n-1].window_text() + ' : ' + Text[0].window_text()
                        break
            send_message = '[QQ] '+ Last_message
            if pre_message != send_message:
                if not Last_message.split(':',1)[1].startswith(' [MC]'):
                    server.say(send_message)
                if Text[0].window_text().startswith('/bind'):
                    task.put('bm'+Text[0].window_text()[6:])
                    task.put(Group[n-1])
                pre_message = send_message
    except:
        server.say('§e监听线程意外退出')
        running = False

def bind(qq_num,id):
    binds = load('qqbinds.txt')
    for bind in binds:
        if bind.id == id:
            task.put('此id已经绑定过了')
            return
        if bind.qq == qq_num:
            task.put('此qq已经绑定过了')
            return
    binds.append(Bind(qq_num,id))
    task.put('成功将'+id+'绑定到'+qq_num)
    save(binds,'qqbinds.txt')

def Send(server):
    global running2
    running2 = True
    task.queue.clear()
    try:
        while True:
            if not task.empty():
                content = task.get()
                if content.startswith('bm'):
                    group = task.get()
                    group.click_input()
                    qq = dlg.child_window(title_re = "QQ \\d+")
                    qq_num = qq.window_text()[3:]
                    id = content[2:]
                    send_keys('{ESC}')
                    bind(qq_num,id)
                else:
                    pyperclip.copy(content)
                    chat_box.type_keys('^v')
                    send_box.click()
    except:
        server.say('§e发送线程意外退出')
        running2 = False
