from pathlib import Path
from config import ACCOUNTS, MESSAGES
from color_logger import logger
from collections import defaultdict

script_location = Path(__file__).absolute().parent


with open(script_location / ACCOUNTS, 'r') as f:
    parse_accounts, message_accounts = [], []
    for account in [[i for i in line.strip().split(':') if i] for line in f.readlines() if line]:
        if account:
            (parse_accounts if int(account[0]) else message_accounts).append(account[1:])
    result = defaultdict(list)
    for i in parse_accounts:
        if len(i) > 2:
            result[i[0]].append(i[2:])
    parse_accounts = {i[0]: [i[0], i[1], result[i[0]]] for i in parse_accounts}.values()

with open(script_location / MESSAGES, 'r') as f:
    messages = {}
    for line in f.readlines():
        data = line.strip().split(':', 1)
        messages[data[0]] = data[1]


def del_token(token):
    global parse_accounts
    global message_accounts
    parse_accounts = list(filter(lambda x: x[0] != token, parse_accounts))
    message_accounts = list(filter(lambda x: x[0] != token, message_accounts))
    with open(script_location / ACCOUNTS, 'w') as file:
        for account_data in parse_accounts:
            if account_data[2]:
                for additional_data in account_data[2]:
                    file.write(f'1:{":".join(account_data[:2]+additional_data)}\n')
            else:
                file.write(f'1:{":".join(account_data[:2])}\n')
        [file.write(f'0:{":".join(i)}\n') for i in message_accounts]
    with open(script_location / 'bad_tokens.txt', 'a+') as file:
        file.write(f'{token}\n')
    if not parse_accounts or not message_accounts:
        logger.critical(f'No {"parser" if not parse_accounts else "message"} accounts')
        return True
