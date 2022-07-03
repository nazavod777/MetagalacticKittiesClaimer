import asyncio
import aiohttp
from os import system
from urllib3 import disable_warnings
from loguru import logger
from platform import system as platform_system
from sys import stderr, platform
from web3.auto import w3
from os.path import exists
from aiohttp_proxy import ProxyConnector
from random import choice, randint
from pyuseragents import random as random_useragent
from multiprocessing.dummy import Pool


headers = {
    'Acept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru,en;q=0.9,vi;q=0.8,es;q=0.7',
    'Content-Type': 'application/json',
    'Origin': 'https://freenft.anmol.network',
    'Referer': 'https://freenft.anmol.network/'
}


class Wrong_Response(Exception):
    pass


disable_warnings()
def clear(): return system('cls' if platform_system() == "Windows" else 'clear')


logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white>"
                          " | <level>{level: <8}</level>"
                          " | <cyan>{line}</cyan>"
                          " - <white>{message}</white>")


def random_file_proxy():
    with open(proxy_folder, 'r', encoding='utf-8') as file:
        lines = file.readlines()

    proxy_str = f'{proxy_type}://' + choice(lines)

    return(proxy_str)


def random_tor_proxy():
    proxy_auth = str(randint(1, 0x7fffffff)) + ':' + str(randint(1, 0x7fffffff))
    proxies = f'socks5://{proxy_auth}@localhost:' + str(choice(tor_ports))
    return(proxies)


def create_wallet():
    account = w3.eth.account.create()
    privatekey = str(account.privateKey.hex())
    address = str(account.address)
    return(address, privatekey)


async def get_connector():
    if use_proxy:
        if proxy_source == 1:
            connector = ProxyConnector.from_url(random_tor_proxy())

        else:
            connector = ProxyConnector.from_url(random_file_proxy())

    else:
        connector = None

    return(connector)


async def main():
    global progress
    try:
        wallet_data = create_wallet()

        async with aiohttp.ClientSession(headers={
                                                    **headers,
                                                    'user-agent': random_useragent()
                                                },
                                         connector=await get_connector()) as session:
            async with session.post('https://kitty-backend.herokuapp.com/api/nft/mint',
                                    json={"address": wallet_data[0]}) as r:
                if 'Create transaction hash: ' not in str(await r.text()):
                    raise Wrong_Response(str(await r.text()))

    except Wrong_Response as error:
        logger.error(f'{wallet_data[0]} | Wrong Response, '
                     f'response text: {error}')

    except Exception as error:
        logger.error(f'{wallet_data[0]} | Unexpected error: {error}')

    else:
        with open('registered.txt', 'a', encoding='utf-8') as file:
            file.write(f'{wallet_data[0]}:{wallet_data[1]}\n')

        logger.success(f'{wallet_data[0]} | NFT successfully sent')

        progress += 1
        system('title ' + str(progress))


def wrapper(data):
    while True:
        asyncio.run(main())


if __name__ == '__main__':
    if platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    progress = 0
    system('title ' + str(progress))
    clear()

    if exists('tor_ports.txt'):
        with open('tor_ports.txt', 'r', encoding='utf-8') as file:
            tor_ports = [row.strip() for row in file]

    else:
        tor_ports = [9150]

    threads = int(input('Threads: '))
    use_proxy = input('Use proxies? (y/N): ').lower()

    if use_proxy == 'y':
        use_proxy = True

        proxy_source = int(input('Proxy Source (1 - tor proxies; '
                                 '2 - from .txt): '))

        if proxy_source == 2:
            proxy_type = input('Enter proxy type (http; https; socks4; socks5): ')
            proxy_folder = input('Drop .txt with proxies: ')

    else:
        use_proxy = False

    clear()

    with Pool() as executor:
        executor.map(wrapper, [None for _ in range(threads)])
