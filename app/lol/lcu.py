import asyncio
import json
import os
import random

import aiohttp
import psutil
from aiohttp import BasicAuth

from app.common.signals import signal_bus
from app.common.utils import get_port_token

headers = {'Accept': 'application/json', 'Content-Type': 'application/json'}


class LcuWebsocket:
    def __init__(self, port, token):
        self.port = port
        self.token = token
        self.events = []
        self.subscribes = []

    def subscribe(self, event, uri: str = '', event_types: tuple = ('Update', 'Create', 'Delete')):
        def wrapper(func):
            if event not in self.events:
                self.events.append(event)
            self.subscribes.append({
                'uri': uri,
                'event_types': event_types,
                'callable': func
            })
            return func

        return wrapper

    def match_uri(self, data):
        for s in self.subscribes:
            if s['uri'] == data['uri'] and data['eventType'] in s['event_types']:
                asyncio.create_task(s['callable'](data))

    async def run_ws(self):
        self.session = aiohttp.ClientSession(auth=BasicAuth('riot', self.token), headers=headers)

        max_retries = 5
        retries = 0
        while retries < max_retries:
            try:
                self.ws = await self.session.ws_connect(f'wss://127.0.0.1:{self.port}', ssl=False)
                if self.ws:
                    break
            except:
                retries += 1
                await asyncio.sleep(1)

        print('ws started')
        for event in self.events:
            await self.ws.send_json([5, event])
        while True:
            msg = await self.ws.receive()
            if msg.type == aiohttp.WSMsgType.TEXT and msg.data != '':
                event = json.loads(msg.data)[1]
                data = json.loads(msg.data)[2]
                # print(event, data['eventType'], data['uri'], data['data'])
                self.match_uri(data)
            elif msg.type == aiohttp.WSMsgType.CLOSED:
                print('ws closed')
                break

        await self.session.close()

    async def start(self):
        if "OnJsonApiEvent" in self.events:
            raise AssertionError(
                "不应使用OnJsonApiEvent订阅所有事件，如需调试，注释此行/You should not use OnJsonApiEvent to subscribe to all events. If you wish to debug "
                "the program, comment out this line.")
        self.task = asyncio.create_task(self.run_ws())

    async def close(self):
        self.task.cancel()
        if self.session:
            await self.session.close()


class Lcu:

    async def start(self, pid, debug=False):
        self.debug = debug
        self.pid = pid
        self.port, self.token = get_port_token(psutil.Process(pid))
        self.auth = BasicAuth('riot', self.token)
        self.session = aiohttp.ClientSession(auth=BasicAuth('riot', self.token), headers=headers)
        print('lcu started')
        await self.run_ws_listener()

    async def close(self):
        await self.listener.close()
        if self.session:
            await self.session.close()

    async def run_ws_listener(self):
        self.listener = LcuWebsocket(self.port, self.token)

        @self.listener.subscribe(event='OnJsonApiEvent_lol-gameflow_v1_gameflow-phase',
                                 uri='/lol-gameflow/v1/gameflow-phase',
                                 event_types=('Update',))
        async def on_game_status_changed(event):
            signal_bus.game_status_changed.emit(event['data'])

        @self.listener.subscribe(event='OnJsonApiEvent_lol-champ-select_v1_session',
                                 uri='/lol-champ-select/v1/session',
                                 event_types=('Update',))
        async def on_champ_select_changed(event):
            signal_bus.champ_select_changed.emit(event['data'])

        @self.listener.subscribe(event='OnJsonApiEvent_lol-summoner_v1_current-summoner',
                                 uri='/lol-summoner/v1/current-summoner',
                                 event_types=('Update',))
        async def on_summoner_profile_changed(event):
            signal_bus.summoner_profile_changed.emit(await self.parse_summoner_info(event['data']))

        @self.listener.subscribe(event='OnJsonApiEvent_lol-inventory_v1_wallet',
                                 uri='/lol-inventory/v1/wallet/RP',
                                 event_types=('Update',))
        async def on_summoner_rp_changed(event):
            signal_bus.summoner_rp_changed.emit(event['data']['RP'])

        @self.listener.subscribe(event='OnJsonApiEvent_lol-inventory_v1_wallet',
                                 uri='/lol-inventory/v1/wallet/lol_blue_essence',
                                 event_types=('Update',))
        async def on_summoner_blue_changed(event):
            signal_bus.summoner_blue_changed.emit(event['data']['lol_blue_essence'])

        @self.listener.subscribe(event='OnJsonApiEvent_lol-inventory_v1_wallet',
                                 uri='/lol-inventory/v1/wallet/lol_orange_essence',
                                 event_types=('Update',))
        async def on_summoner_orange_changed(event):
            signal_bus.summoner_orange_changed.emit(event['data']['lol_orange_essence'])

        await self.listener.start()

    async def get_game_status(self):
        """获取游戏状态"""
        return await (await self.request('get', '/lol-gameflow/v1/gameflow-phase')).json()

    async def get_summoner_icon(self, icon_id):
        icon = f'app/resource/game/profile_icons/{icon_id}.jpg'

        if not os.path.exists(icon):
            if not os.path.exists(os.path.split(icon)[0]):
                os.makedirs(os.path.split(icon)[0])
            path = f'/lol-game-data/assets/v1/profile-icons/{icon_id}.jpg'
            resp = await self.request('get', path)
            with open(icon, "wb") as f:
                f.write(await resp.read())
        return icon

    async def parse_summoner_info(self, r):
        id = r['summonerId']
        puuid = r['puuid']
        name = r['gameName']
        tag = r['tagLine']
        icon_id = r['profileIconId']
        icon = await self.get_summoner_icon(icon_id)
        level = r['summonerLevel']
        xp = (r['xpSinceLastLevel'], r['xpUntilNextLevel'])
        privacy = r['privacy']
        return {'id': id, 'puuid': puuid, 'name': name, 'tag': tag, 'icon_id': icon_id, 'icon': icon, 'level': level,
                'xp': xp, 'privacy': privacy}

    async def get_curr_summoner(self):
        """获取玩家信息"""
        r = await self.request('get', '/lol-summoner/v1/current-summoner')
        while r.status == 404:
            r = await self.request('get', '/lol-summoner/v1/current-summoner')
        r = await r.json()
        return await  self.parse_summoner_info(r)

    async def get_summoner_rp(self):
        res = await self.request('get', '/lol-inventory/v1/wallet/RP')
        return (await res.json())['RP']  # 点券

    async def get_summoner_blue_essence(self):
        res = await self.request('get', '/lol-inventory/v1/wallet/lol_blue_essence')
        return (await res.json())['lol_blue_essence']  # 蓝色精粹

    async def get_summoner_orange_essence(self):
        res = await self.request('get', '/lol-inventory/v1/wallet/lol_orange_essence')
        return (await res.json())['lol_orange_essence']  # 橙色精粹

    async def play_again(self):
        await self.request('post', '/lol-lobby/v2/play-again')

    async def reconnect(self):
        await self.request('post', '/lol-gameflow/v1/reconnect')

    async def create_custom_lobby(self, lobby_name='5v5自定义', lobby_password=''):
        data = {
            "customGameLobby": {
                "configuration": {
                    "gameMode": "PRACTICETOOL",
                    "gameMutator": "",
                    "gameServerRegion": "",
                    "mapId": 11,
                    "mutators": {"id": 1},
                    "spectatorPolicy": "AllAllowed",
                    "teamSize": 5,
                },
                "lobbyName": lobby_name,
                "lobbyPassword": lobby_password,
            },
            "isCustom": True,
        }
        res = await self.request('post', "/lol-lobby/v2/lobby", data=data)
        return await res.json()

    async def add_bots(self, num, team_id):
        """
        5v5自定义添加机器人
        :param num: 机器人数量
        :param team_id: 队伍 100蓝色方  200红色方
        :return:
        """
        res = await self.get('/lol-lobby/v2/lobby/custom/available-bots')
        names = [r['name'] for r in res]
        bot_list = {
            r['name']: {'id': r['id'], 'name': r['name'], 'active': r['active'], 'difficulties': r['botDifficulties']}
            for r in res}
        random_names = random.sample(names, num)  # 随机选取 num 个英雄
        for name in random_names:
            bot = bot_list[name]
            data = {'botDifficulty': random.choice(bot['difficulties']),  # 随机难度
                    'championId': bot['id'],
                    'teamId': f'{team_id}'}
            await lcu.post('/lol-lobby/v1/lobby/custom/bots', data=data)

    async def add_blue_bots(self, num=4):
        await self.add_bots(num, 100)

    async def add_red_bots(self, num=5):
        await self.add_bots(num, 200)

    async def restart_client(self):
        await self.request('post', '/riotclient/kill-and-restart-ux')

    async def matchmaking_accept(self):
        resp = await self.request('post', '/lol-matchmaking/v1/ready-check/accept')
        return resp

    async def matchmaking_decline(self):
        await self.request('post', '/lol-matchmaking/v1/ready-check/decline')

    async def matchmaking_search(self):
        resp = await self.request('post', '/lol-lobby/v2/lobby/matchmaking/search')
        return resp

    async def matchmaking_search_cancel(self):
        resp = await self.request('delete', '/lol-lobby/v2/lobby/matchmaking/search')

    async def get_gameflow_session(self):
        res = await self.request('get', "/lol-gameflow/v1/session")
        return await res.json()

    async def get_champ_select_session(self):
        res = await self.request('get', "/lol-champ-select/v1/session")
        return await res.json()

    async def get_curr_select_champ(self):
        res = await self.request('get', "/lol-champ-select/v1/current-champion")
        return await res.json()

    async def get_curr_action_id(self):
        r = await self.get_champ_select_session()
        local_cell_id = r['localPlayerCellId']
        actions = r['actions'][0]
        for action in actions:
            if action['actorCellId'] == local_cell_id:
                return action['id']

    async def select_champ(self, action_id, champ_id, completed=False):
        data = {
            'championId': champ_id,
            'type': 'pick',
            'completed': completed,
        }
        res = await self.request('patch', f"/lol-champ-select/v1/session/actions/{action_id}", data=data)
        return await res.read()

    async def ban_champ(self, action_id, champ_id, completed=False):
        data = {
            'championId': champ_id,
            'type': 'ban',
            'completed': completed,
        }
        res = await self.request('patch', f"/lol-champ-select/v1/session/actions/{action_id}", data=data)
        return await res.read()

    async def reroll(self):
        res = await self.request('post', "/lol-champ-select/v1/session/my-selection/reroll")
        return await res.json()

    async def get_ready_check_status(self):
        res = await self.request('get', "/lol-matchmaking/v1/ready-check")

        return await res.json()

    async def get_champ_icons(self, champ_id):
        icon = f'app/resource/game/champ_icons/{champ_id}.png'
        if not os.path.exists(icon):
            if not os.path.exists(os.path.split(icon)[0]):
                os.makedirs(os.path.split(icon)[0])
            path = f"/lol-game-data/assets/v1/champion-icons/{champ_id}.png"
            resp = await self.request('get', path)
            with open(icon, "wb") as f:
                f.write(await resp.read())
        return icon

    async def get_champions(self):
        """获取所有英雄的信息  id 名称 别名 icon 分路"""
        r = await (await self.request('get', '/lol-game-data/assets/v1/champion-summary.json')).json()
        return [{'id': item['id'],
                 'name': item['name'],
                 'alias': item['alias'],
                 'icon_path': item['squarePortraitPath'],
                 'roles': item['roles'],
                 'icon': await self.get_champ_icons(item['id'])}
                for item in r]

    async def create_lobby(self, queue_id):
        await self.request('post', '/lol-lobby/v2/lobby', data={'queueId': queue_id})

    async def delete_lobby(self):
        await self.request('delete', '/lol-lobby/v2/lobby')

    async def get_lobby(self):
        resp = await self.request('get', '/lol-lobby/v2/lobby')
        if resp.status == 200:
            return (await resp.json())['gameConfig']['queueId']

    async def request(self, method, path, max_retries=5, **kwargs):
        if kwargs.get('data'):
            kwargs['data'] = json.dumps(kwargs['data'])

        retries = 0
        while retries < max_retries:
            try:
                return await self.session.request(method, f'https://127.0.0.1:{self.port}{path}', ssl=False, **kwargs)
            except:
                retries += 1
                await asyncio.sleep(1)

    async def get(self, path, **kwargs):
        res = await self.request('get', path, **kwargs)
        return await res.json()

    async def post(self, path, **kwargs):
        res = await self.request('post', path, **kwargs)
        return await res.json()

    async def patch(self, path, **kwargs):
        res = await self.request('patch', path, **kwargs)
        return await res.json()

    async def delete(self, path, **kwargs):
        res = await self.request('delete', path, **kwargs)
        return await res.json()


lcu = Lcu()
