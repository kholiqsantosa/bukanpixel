import asyncio
import base64
import json
import os
import random
import re
import datetime
from multiprocessing.util import debug
from time import time
from urllib.parse import unquote, quote

import brotli
import aiohttp
from aiohttp_proxy import ProxyConnector
from better_proxy import Proxy
from pyrogram import Client
from pyrogram.errors import Unauthorized, UserDeactivated, AuthKeyUnregistered
from pyrogram.raw import types
from pyrogram.raw.functions.messages import RequestAppWebView

from bot.config import settings

from bot.utils import logger
from bot.exceptions import InvalidSession
from .headers import headers, headers_squads

from random import randint, choices

from .image_checker import get_cords_and_color, template_to_join, inform, boost_record
from ..utils.firstrun import append_line_to_file


class Tapper:
    def __init__(self, tg_client: Client, first_run: bool):
        self.tg_client = tg_client
        self.first_run = first_run
        self.session_name = tg_client.name
        self.start_param = ''
        self.main_bot_peer = 'notpixel'
        self.squads_bot_peer = 'notgames_bot'
        self.joined = None
        self.balance = 0
        self.template_to_join = 0
        self.user_id = 0

    async def get_tg_web_data(self, proxy: str | None, ref:str, bot_peer:str, short_name:str) -> str:
        if proxy:
            proxy = Proxy.from_str(proxy)
            proxy_dict = dict(
                scheme=proxy.protocol,
                hostname=proxy.host,
                port=proxy.port,
                username=proxy.login,
                password=proxy.password
            )
        else:
            proxy_dict = None

        self.tg_client.proxy = proxy_dict

        try:
            if not self.tg_client.is_connected:
                try:
                    await self.tg_client.connect()

                except (Unauthorized, UserDeactivated, AuthKeyUnregistered):
                    raise InvalidSession(self.session_name)
            peer = await self.tg_client.resolve_peer(bot_peer)

            if bot_peer == self.main_bot_peer and not self.first_run:
                if self.joined is False:
                    web_view = await self.tg_client.invoke(RequestAppWebView(
                        peer=peer,
                        platform='android',
                        app=types.InputBotAppShortName(bot_id=peer, short_name=short_name),
                        write_allowed=True,
                        start_param=f"f{self.template_to_join}_t"
                    ))
                    self.joined = True
                else:
                    web_view = await self.tg_client.invoke(RequestAppWebView(
                        peer=peer,
                        platform='android',
                        app=types.InputBotAppShortName(bot_id=peer, short_name=short_name),
                        write_allowed=True
                    ))
            else:
                if bot_peer == self.main_bot_peer:
                    logger.info(f"🆕 {self.session_name} | Memulai dengan refferal 🙇")
                    self.first_run = False
                    await append_line_to_file(self.session_name)
                web_view = await self.tg_client.invoke(RequestAppWebView(
                    peer=peer,
                    platform='android',
                    app=types.InputBotAppShortName(bot_id=peer, short_name=short_name),
                    write_allowed=True,
                    start_param=ref
                ))

            auth_url = web_view.url

            tg_web_data = unquote(
                string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))

            start_param = re.findall(r'start_param=([^&]+)', tg_web_data)

            user = re.findall(r'user=([^&]+)', tg_web_data)[0]
            self.user_id = json.loads(user)['id']

            init_data = {
                'auth_date': re.findall(r'auth_date=([^&]+)', tg_web_data)[0],
                'chat_instance': re.findall(r'chat_instance=([^&]+)', tg_web_data)[0],
                'chat_type': re.findall(r'chat_type=([^&]+)', tg_web_data)[0],
                'hash': re.findall(r'hash=([^&]+)', tg_web_data)[0],
                'user': quote(user),
            }

            if start_param:
                start_param = start_param[0]
                init_data['start_param'] = start_param
                self.start_param = start_param

            ordering = ["user", "chat_instance", "chat_type", "start_param", "auth_date", "hash"]

            auth_token = '&'.join([var for var in ordering if var in init_data])

            for key, value in init_data.items():
                auth_token = auth_token.replace(f"{key}", f'{key}={value}')

            await asyncio.sleep(10)

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()

            return auth_token

        except InvalidSession as error:
            raise error

        except Exception as error:
            logger.error(f"{self.session_name} | Error saat otorisasi: {error} ⚠️")
            await asyncio.sleep(delay=3)

    async def join_squad(self, http_client, tg_web_data: str, user_agent):
        custom_headers = headers_squads
        custom_headers['User-Agent'] = user_agent
        bearer_token = None
        try:
            custom_headers["Host"] = "api.notcoin.tg"
            custom_headers["bypass-tunnel-reminder"] = "x"
            custom_headers["TE"] = "trailers"

            if tg_web_data is None:
                logger.error(f"{self.session_name} | Error Invalid web_data, gabisa join squad ⚠️")
            custom_headers['Content-Length'] = str(len(tg_web_data) + 18)
            custom_headers['x-auth-token'] = "Bearer null"
            qwe = f'{{"webAppData": "{tg_web_data}"}}'
            r = json.loads(qwe)
            login_req = await http_client.post("https://api.notcoin.tg/auth/login", json=r, headers=custom_headers)

            login_req.raise_for_status()

            login_data = await login_req.json()

            bearer_token = login_data.get("data", {}).get("accessToken", None)
            if not bearer_token:
                raise Exception
            logger.success(f"{self.session_name} | Masuk ke NotGames 🎮")
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when logging in to NotGames: {error} ⚠️")

        custom_headers["Content-Length"] = "26"
        custom_headers["x-auth-token"] = f"Bearer {bearer_token}"


        try:
            logger.info(f"{self.session_name} | Join ke squad... 🎳")
            join_req = await http_client.post("https://api.notcoin.tg/squads/absolateA/join",
                                              json=json.loads('{"chatId": -1002312810276}'), headers=custom_headers)

            join_req.raise_for_status()
            logger.success(f"{self.session_name} | Join ke squad 🎳")
        except Exception as error:
            logger.error(f"{self.session_name} | Error saat join squad: {error} ⚠️")


    async def login(self, http_client: aiohttp.ClientSession):
        try:

            response = await http_client.get("https://notpx.app/api/v1/users/me")
            response.raise_for_status()
            response_json = await response.json()
            return response_json

        except Exception as error:
            logger.error(f"{self.session_name} | Error saat login: {error} ⚠️")
            logger.warning(f"{self.session_name} | Bot overload, mencoba lagi... 🙇")
            await asyncio.sleep(delay=randint(3, 7))
            await self.login(http_client)

    async def check_proxy(self, http_client: aiohttp.ClientSession, service_name, proxy: Proxy) -> None:
        try:
            response = await http_client.get(url='https://ipinfo.io/json', timeout=aiohttp.ClientTimeout(20))
            response.raise_for_status()

            response_json = await response.json()
            ip = response_json.get('ip', 'NO')
            region = response_json.get('region', 'NO')

            logger.info(f"{self.session_name} | IP {ip} - {region} 🌏")
        except Exception as error:
            logger.error(f"{self.session_name} | Proxy: {proxy} | Error: {error} ⚠️")

    async def join_tg_channel(self, link: str):
        if not self.tg_client.is_connected:
            try:
                await self.tg_client.connect()
            except Exception as error:
                logger.error(f"{self.session_name} | Error while TG connecting: {error}")

        try:
            parsed_link = link.split('/')[-1]
            logger.info(f"{self.session_name} | Joining tg channel {parsed_link}")

            await self.tg_client.join_chat(parsed_link)

            logger.success(f"{self.session_name} | Joined tg channel {parsed_link}")

            if self.tg_client.is_connected:
                await self.tg_client.disconnect()
        except Exception as error:
            logger.error(f"{self.session_name} | Error while join tg channel: {error}")
            await asyncio.sleep(delay=3)

    async def get_balance(self, http_client: aiohttp.ClientSession):
        try:
            balance_req = await http_client.get('https://notpx.app/api/v1/mining/status')
            balance_req.raise_for_status()
            balance_json = await balance_req.json()
            
            # Menghapus desimal dari balance
            balance = int(balance_json.get('userBalance', 0))
            return balance
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when processing balance: {error} ⚠️")
            await asyncio.sleep(delay=3)

    async def tasks(self, http_client: aiohttp.ClientSession):
        try:
            stats = await http_client.get('https://notpx.app/api/v1/mining/status')
            stats.raise_for_status()
            stats_json = await stats.json()
            done_task_list = stats_json['tasks'].keys()
            #logger.debug(done_task_list)
            if randint(0, 5) == 3:
                league_statuses = {"bronze": [], "silver": ["leagueBonusSilver"], "gold": ["leagueBonusSilver", "leagueBonusGold"], "platinum": ["leagueBonusSilver", "leagueBonusGold", "leagueBonusPlatinum"]}
                possible_upgrades = league_statuses.get(stats_json["league"], "Unknown")
                if possible_upgrades == "Unknown":
                    logger.warning(f"{self.session_name} | Unknown league: {stats_json['league']} ⚠️")
                else:
                    for new_league in possible_upgrades:
                        if new_league not in done_task_list:
                            tasks_status = await http_client.get(f'https://notpx.app/api/v1/mining/task/check/{new_league}')
                            tasks_status.raise_for_status()
                            tasks_status_json = await tasks_status.json()
                            status = tasks_status_json[new_league]
                            if status:
                                logger.success(f"{self.session_name} | League upgrade ke {new_league}. 🎉")
                                current_balance = await self.get_balance(http_client)
                                logger.info(f"{self.session_name} | Saldo: {current_balance} PX 🔳")
                            else:
                                logger.warning(f"{self.session_name} | League belum layak. ⚠️")
                            await asyncio.sleep(delay=randint(10, 20))
                            break

            for task in settings.TASKS_TO_DO:
                if task not in done_task_list:
                    if task == 'paint20pixels':
                        repaints_total = stats_json['repaintsTotal']
                        if repaints_total < 20:
                            continue
                    if ":" in task:
                        entity, name = task.split(':')
                        task = f"{entity}?name={name}"
                        if entity == 'channel':
                            if not settings.JOIN_TG_CHANNELS:
                                continue
                            await self.join_tg_channel(name)
                            await asyncio.sleep(delay=3)
                    tasks_status = await http_client.get(f'https://notpx.app/api/v1/mining/task/check/{task}')
                    tasks_status.raise_for_status()
                    tasks_status_json = await tasks_status.json()
                    status = (lambda r: all(r.values()))(tasks_status_json)
                    if status:
                        logger.success(f"{self.session_name} | Task {task} komplit. 🎉")
                        current_balance = await self.get_balance(http_client)
                        logger.info(f"{self.session_name} | Saldo: <e>{current_balance}</e> PX 🔳")
                    else:
                        logger.warning(f"{self.session_name} | Task {task} belum komplit ⚠️")
                    if randint(0, 1) == 1:
                        break
                    await asyncio.sleep(delay=randint(10, 20))

        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when processing tasks: {error} ⚠️")

    async def make_paint_request(self, http_client: aiohttp.ClientSession, yx, color, delay_start, delay_end):
        paint_request = await http_client.post('https://notpx.app/api/v1/repaint/start',
                                                json={"pixelId": int(yx), "newColor": color})
        paint_request.raise_for_status()
        paint_request_json = await paint_request.json()
        cur_balance = paint_request_json.get("balance", self.balance)
        change = cur_balance - self.balance
        if change <= 0:
            change = 0
        self.balance = cur_balance
        logger.success(f"{self.session_name} | 🗺️ {yx} | 🎨: {color} | <e>+{change:.2f}</e> PX 🔳")
        await asyncio.sleep(delay=randint(delay_start, delay_end))

    async def paint(self, http_client: aiohttp.ClientSession, retries=20):
        try:
            stats = await http_client.get('https://notpx.app/api/v1/mining/status')
            stats.raise_for_status()
            stats_json = await stats.json()
            charges = stats_json.get('charges', 24)
            self.balance = stats_json.get('userBalance', 0)
            maxCharges = stats_json.get('maxCharges', 24)
            logger.info(f"{self.session_name} | Energi: <e>{charges}/{maxCharges}</e> ⚡")
            for _ in range(charges - 1):
                try:
                    q = await get_cords_and_color(user_id=self.user_id, template=self.template_to_join)
                except Exception as error:
                    logger.info(f"{self.session_name} | No pixels to paint ⚠️")
                    return
                coords = q["coords"]
                color3x = q["color"]
                yx = coords
                await self.make_paint_request(http_client, yx, color3x, 5, 10)

        except Exception as error:
            await asyncio.sleep(delay=10)
            if retries > 0:
                await self.paint(http_client=http_client, retries=retries-1)

    async def upgrade(self, http_client: aiohttp.ClientSession):
        try:
            status_req = await http_client.get('https://notpx.app/api/v1/mining/status')
            status_req.raise_for_status()
            status = await status_req.json()
            boosts = status['boosts']
            boosts_max_levels = {
                "energyLimit": settings.ENERGY_LIMIT_MAX_LEVEL,
                "paintReward": settings.PAINT_REWARD_MAX_LEVEL,
                "reChargeSpeed": settings.RECHARGE_SPEED_MAX_LEVEL,
            }
            await boost_record(user_id=self.user_id, boosts=boosts, max_level=boosts_max_levels)
            for name, level in sorted(boosts.items(), key=lambda item: item[1]):
                while name not in settings.IGNORED_BOOSTS and level < boosts_max_levels[name]:
                    try:
                        upgrade_req = await http_client.get(f'https://notpx.app/api/v1/mining/boost/check/{name}')
                        upgrade_req.raise_for_status()
                        logger.success(f"{self.session_name} | Boost: {name} diupgrade 🎉")
                        level += 1
                        await asyncio.sleep(delay=randint(2, 5))
                    except Exception as error:
                        logger.warning(f"{self.session_name} | Gada saldo buat upgrade boost. 🙇")
                        await asyncio.sleep(delay=randint(5, 10))
                        return
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when upgrading: {error} ⚠️")
            await asyncio.sleep(delay=3)

    async def claim(self, http_client: aiohttp.ClientSession):
        try:
            logger.info(f"{self.session_name} | Klaim Minning 💸")
            response = await http_client.get(f'https://notpx.app/api/v1/mining/status')
            response.raise_for_status()
            response_json = await response.json()
            await asyncio.sleep(delay=5)
            for _ in range(2):
                try:
                    response = await http_client.get(f'https://notpx.app/api/v1/mining/claim')
                    response.raise_for_status()
                    response_json = await response.json()
                except Exception as error:
                    logger.info(f"{self.session_name} | Gagal nih, coba lagi ah...")
                    await asyncio.sleep(delay=randint(20,30))
                else:
                    break

            return response_json['claimed']
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when claiming reward: {error} ⚠️")
            await asyncio.sleep(delay=3)

    async def in_squad(self, http_client: aiohttp.ClientSession):
        try:
            logger.info(f"{self.session_name} | Cek squad...")
            stats_req = await http_client.get(f'https://notpx.app/api/v1/mining/status')
            stats_req.raise_for_status()
            stats_json = await stats_req.json()
            league = stats_json["league"]
            squads_req = await http_client.get(f'https://notpx.app/api/v1/ratings/squads?league={league}')
            squads_req.raise_for_status()
            squads_json = await squads_req.json()
            squad_id = squads_json.get("mySquad", {"id": None}).get("id", None)
            return True if squad_id else False
        except Exception as error:
            logger.error(f"{self.session_name} | Unknown error when checking squad reward: {error} ⚠️")
            await asyncio.sleep(delay=3)
            return True

    async def notpx_template(self, http_client: aiohttp.ClientSession):
        try:
            stats_req = await http_client.get(f'https://notpx.app/api/v1/image/template/my')
            stats_req.raise_for_status()
            cur_template = await stats_req.json()
            cur_template = cur_template["id"]
            return cur_template
        except Exception as error:
            return 0

    async def j_template(self, http_client: aiohttp.ClientSession, template_id):
        try:
            resp = await http_client.put(f"https://notpx.app/api/v1/image/template/subscribe/{template_id}")
            resp.raise_for_status()
            await asyncio.sleep(randint(1, 3))
            return resp.status == 204
        except Exception as error:
            logger.error(f"Unknown error upon joining a template: {error} ⚠️")
            return False

    async def join_template(self, http_client: aiohttp.ClientSession):
        try:
            tmpl = await self.notpx_template(http_client)
            self.template_to_join = await template_to_join(tmpl)
            return str(tmpl) != self.template_to_join
        except Exception as error:
            pass
        return False

    def generate_random_string(self, length=8):
        characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
        random_string = ''
        for _ in range(length):
            random_index = int((len(characters) * int.from_bytes(os.urandom(1), 'big')) / 256)
            random_string += characters[random_index]
        return random_string


    async def run(self, user_agent: str, proxy: str | None) -> None:
        access_token_created_time = 0
        proxy_conn = ProxyConnector().from_url(proxy) if proxy else None
        headers["User-Agent"] = user_agent

        async with aiohttp.ClientSession(headers=headers, connector=proxy_conn, trust_env=True) as http_client:
            if proxy:
                await self.check_proxy(http_client=http_client, service_name="NotPixel", proxy=proxy)

            ref = settings.REF_ID
            link = get_link(ref)

            delay = randint(settings.START_DELAY[0], settings.START_DELAY[1])
            logger.info(f"{self.session_name} | {delay} detik lagi login 🙇")
            await asyncio.sleep(delay=delay)

            token_live_time = randint(600, 800)
            while True:
                try:
                    if settings.NIGHT_MODE:
                        current_utc_time = datetime.datetime.now().time()

                        start_time = datetime.time(settings.NIGHT_TIME[0], 0)
                        end_time = datetime.time(settings.NIGHT_TIME[1], 0)

                        next_checking_time = randint(settings.NIGHT_CHECKING[0], settings.NIGHT_CHECKING[1])

                        if start_time <= current_utc_time <= end_time:
                            logger.info(f"{self.session_name} | Sekarang jam {current_utc_time.replace(microsecond=0)}, istirahat {round(next_checking_time / 3600, 1)} jam dulu gesss 😴")
                            await asyncio.sleep(next_checking_time)
                            continue

                    if time() - access_token_created_time >= token_live_time:
                        tg_web_data = await self.get_tg_web_data(proxy=proxy, bot_peer=self.main_bot_peer, ref=link, short_name="app")
                        if tg_web_data is None:
                            continue

                        http_client.headers["Authorization"] = f"initData {tg_web_data}"
                        logger.info(f"{self.session_name} | Memulai login ... 🤫")
                        user_info = await self.login(http_client=http_client)
                        logger.success(f"{self.session_name} | Login sukses 🎉")
                        access_token_created_time = time()
                        token_live_time = randint(600, 800)
                        sleep_time = randint(settings.SLEEP_TIME[0], settings.SLEEP_TIME[1])

                    await asyncio.sleep(delay=randint(1, 3))

                    balance = await self.get_balance(http_client)
                    logger.info(f"{self.session_name} | Saldo: <e>{balance}</e> PX 🔳")

                    await inform(self.user_id, balance)

                    if await self.join_template(http_client=http_client):
                        tmpl_req = await self.j_template(http_client=http_client, template_id=self.template_to_join)
                        if not tmpl_req:
                            self.joined = False
                            delay = randint(60, 120)
                            logger.info(f"{self.session_name} | Joining to template restart in {delay} seconds.")
                            await asyncio.sleep(delay=delay)
                            token_live_time = 0
                            continue

                    if settings.AUTO_DRAW:
                        await self.paint(http_client=http_client)

                    if settings.CLAIM_REWARD:
                        reward_status = await self.claim(http_client=http_client)
                        logger.info(f"{self.session_name} | Claim reward: <e>{reward_status}</e>")

                    if True:
                        if not await self.in_squad(http_client=http_client):
                            tg_web_data = await self.get_tg_web_data(proxy=proxy, bot_peer=self.squads_bot_peer,
                                                                     ref="cmVmPTQ2NDg2OTI0Ng==", short_name="squads")
                            await self.join_squad(http_client, tg_web_data, user_agent)
                        else:
                            logger.success(f"{self.session_name} | Udah gabung ke squad 🎳")

                    if settings.AUTO_TASK:
                        logger.info(f"{self.session_name} | Menjalankan task... 📝")
                        await self.tasks(http_client=http_client)
                        logger.info(f"{self.session_name} | Task komplit 🎉")

                    if settings.AUTO_UPGRADE:
                        reward_status = await self.upgrade(http_client=http_client)

                    logger.info(f"{self.session_name} | Turu <y>{round(sleep_time / 60, 1)}</y> menit 😴")
                    await asyncio.sleep(delay=sleep_time)

                except InvalidSession as error:
                    raise error

                except Exception as error:
                    logger.error(f"{self.session_name} | Unknown error: {error} ⚠️")
                    await asyncio.sleep(delay=randint(60, 120))


def get_link(code):
    link = ''
    return link


async def run_tapper(tg_client: Client, user_agent: str, proxy: str | None, first_run: bool):
    try:
        await Tapper(tg_client=tg_client, first_run=first_run).run(user_agent=user_agent, proxy=proxy)
    except InvalidSession:
        logger.error(f"{tg_client.name} | Invalid Session")
