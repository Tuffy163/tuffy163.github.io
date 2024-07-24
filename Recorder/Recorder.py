from mcdreforged.api.types import PluginServerInterface,Info
from mcdreforged.api.command import *
from mcdreforged.api.all import *
import os
import requests

PLUGIN_METADATA = {
    'id': 'recorder',
    'version': '1.0.1',
    'name': 'Recorder',
    'author': 'Tuffy163'
}

data = []
version = '1.0.1'

def check_update(server):
    global version
    url_1 = 'https://tuffy163.github.io/Recorder/version.html'
    url_2 = 'https://tuffy163.github.io/Recorder/Recorder.py'
    myfile_1 = requests.get(url_1)
    myfile_2 = requests.get(url_2)
    server.say('§a当前版本为§r§c'+version+'§r§a，服务器版本为§r§c'+myfile_1.text[:-1])
    if myfile_1.text[:-1] != version:
        open('Recorder.py','wb').write(myfile_2.content)
        server.say('§e插件更新完成，请使用!!MCDR reload plugin重载插件')
    else :
        server.say('§e插件版本为最新版，不需要进行更新')

class Position:
    def __init__(self, name, x, y, z, dimension):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.dimension = dimension

    def __str__(self):
        return f"{self.name},{self.x},{self.y},{self.z},{self.dimension}"

    @staticmethod
    def from_str(s):
        parts = s.split(',')
        return Position(parts[0], parts[1], parts[2], parts[3], parts[4])

def save_positions_to_txt(positions, filename):
    with open(filename, 'w') as f:
        for position in positions:
            f.write(str(position) + '\n')

def load_positions_from_txt(filename):
    positions = []
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            pass
    with open(filename, 'r') as f:
        for line in f:
            positions.append(Position.from_str(line.strip()))
    return positions

def on_info(server: PluginServerInterface, info: Info):
    if info.is_user :
        args = info.content.split(' ')
        execute_arg(server,info,args);

def on_load(server: PluginServerInterface, prev_module):
    global data
    server.register_help_message('!!rec(order)','记录服务器地点坐标')
    data = load_positions_from_txt('positions.txt')

def get_color(dimension) :
    if dimension == '主世界':
        return RColor.dark_green
    elif dimension == '地狱':
        return RColor.dark_red
    elif dimension == '末地':
        return RColor.dark_purple
    else:
        return None

def get_format_name(dimension) :
    if dimension == '主世界':
        return 'minecraft:overworld'
    elif dimension == '地狱':
        return 'minecraft:the_nether'
    elif dimension == '末地':
        return 'minecraft:the_end'
    else:
        return None

def execute_arg(server,info,args) :
    global data
    if (args[0] == '!!recorder' or args[0] == '!!rec') and len(args) >= 2:
        if args[1] == 'add' and (len(args) == 7 or len(args) == 8):
            if len(args) == 7:
                if data != []:
                    pos = Position(args[2],args[3],args[4],args[5],args[6])
                    data.append(pos)
                    server.reply(info,'§a添加成功')
                    save_positions_to_txt(data, 'positions.txt')
                else :
                    server.reply(info,'§c警告：检测到未储存任何位置，可能有以下两种情况')
                    server.reply(info,'§e情况一：服务器第一次使用此插件，还未储存任何位置')
                    server.reply(info,'§e在这种情况下，请输入 §r§a!!rec '+info.content.split(' ',1)[1]+' --force§r§e 来强制添加位置')
                    server.reply(info,'§e情况二：已经储存过位置，但是插件未能读取到位置')
                    server.reply(info,'§e在这种情况下，请输入 §r§a!!rec load§r§e 来读取位置')
            if len(args) == 8:
                if args[7] == '--force':
                    pos = Position(args[2],args[3],args[4],args[5],args[6])
                    data.append(pos)
                    server.reply(info,'§a添加成功')
                    save_positions_to_txt(data, 'positions.txt')

        if args[1] == 'delete'and len(args) == 3:
            for pos in data:
                if pos.name == args[2]:
                    data.remove(pos)
                    server.reply(info,'§a删除成功')
                    save_positions_to_txt(data, 'positions.txt')

        if args[1] == 'list' and len(args) == 2:
            for pos in data:
                texts = RTextList(RText(pos.name+' 在 ',RColor.green),RText(pos.dimension,get_color(pos.dimension)),RText(' 的 '+pos.x+', '+pos.y+', '+pos.z+' ',RColor.green))
                coord = RText('[分享]', RColor.red).h('点击将位置信息填充到聊天栏').c(RAction.suggest_command, pos.name+' 在 '+pos.dimension+' 的 '+pos.x+', '+pos.y+', '+pos.z)
                texts.append(coord)
                if server.get_permission_level(info) >= 2:
                    coord2 = RText('[传送]', RColor.blue).h('点击将传送指令填充到聊天栏').c(RAction.suggest_command, '!!rec teleport '+pos.name)
                    texts.append(coord2)
                server.reply(info,texts)

        if args[1] == 'find' and len(args) == 3:
            for pos in data:
                if pos.name == args[2]:
                    texts = RTextList(RText(pos.name+' 在 ',RColor.green),RText(pos.dimension,get_color(pos.dimension)),RText(' 的 '+pos.x+', '+pos.y+', '+pos.z+' ',RColor.green))
                    coord = RText('[分享]', RColor.red).h('点击将位置信息填充到聊天栏').c(RAction.suggest_command, pos.name+' 在 '+pos.dimension+' 的 '+pos.x+', '+pos.y+', '+pos.z)
                    texts.append(coord)
                    if server.get_permission_level(info) >= 2:
                        coord2 = RText('[传送]', RColor.blue).h('点击将传送指令填充到聊天栏').c(RAction.suggest_command, '!!rec teleport '+pos.name)
                        texts.append(coord2)
                    server.reply(info,texts)

        if args[1] == 'save' and len(args) == 2:
            save_positions_to_txt(data, 'positions.txt')
            server.reply(info,'§a保存成功')

        if args[1] == 'load' and len(args) == 2:
            data = load_positions_from_txt('positions.txt')
            server.reply(info,'§a读取成功')

        if args[1] == 'teleport' and len(args) == 3:

            if server.get_permission_level(info) <= 1:
                server.reply(info,'§c你没有足够的权限使用此命令')

            else :
                for pos in data:
                    if pos.name == args[2]:
                        n = info.player
                        d = get_format_name(pos.dimension)
                        server.execute('/execute as '+n+' in '+d+' run tp '+pos.x+' '+pos.y+' '+pos.z)

        if args[1] == 'update' and len(args) == 2:
            if info.player == 'Tuffy163':
                check_update(server)
            else :
                server.reply(info,'§c只有Tuffy163能够使用此命令')

        if args[1] == 'help' and len(args) == 2:
            server.reply(info,'§a====================Rec Help Documentation========================')
            server.reply(info,'§a!!rec(order) add <name> <x> <y> <z> <dimension> [--force] 添加位置')
            server.reply(info,'§a!!rec(order) delete <name> 删除位置')
            server.reply(info,'§a!!rec(order) list 查看所有位置')
            server.reply(info,'§a!!rec(order) find <name> 寻找位置')
            server.reply(info,'§a!!rec(order) save 保存位置')
            server.reply(info,'§a!!rec(order) load 读取位置')
            server.reply(info,'§a!!rec(order) teleport <name> 传送位置 (仅限Owner,Admin,Helper使用)')
            server.reply(info,'§a!!rec(order) update 更新插件 (仅限Tuffy163使用)')
            server.reply(info,'§a!!rec(order) help 查看帮助信息')
            server.reply(info,'§a!!rec(order) 查看帮助信息')
            server.reply(info,'§a====================Programmed by Tuffy163========================')

    if (args[0] == '!!recorder' or args[0] == '!!rec') and len(args) == 1:
        server.reply(info,'§a====================Rec Help Documentation========================')
        server.reply(info,'§a!!rec(order) add <name> <x> <y> <z> <dimension> [--force] 添加位置')
        server.reply(info,'§a!!rec(order) delete <name> 删除位置')
        server.reply(info,'§a!!rec(order) list 查看所有位置')
        server.reply(info,'§a!!rec(order) find <name> 寻找位置')
        server.reply(info,'§a!!rec(order) save 保存位置')
        server.reply(info,'§a!!rec(order) load 读取位置')
        server.reply(info,'§a!!rec(order) teleport <name> 传送位置 (仅限Owner,Admin,Helper使用)')
        server.reply(info,'§a!!rec(order) update 更新插件 (仅限Tuffy163使用)')
        server.reply(info,'§a!!rec(order) help 查看帮助信息')
        server.reply(info,'§a!!rec(order) 查看帮助信息')
        server.reply(info,'§a====================Programmed by Tuffy163========================')
