from ast import literal_eval
from datetime import date, datetime, timedelta
import json
import ssl
import os
import sys
from urllib.request import urlopen, Request
from urllib.parse import urlencode


def parse_date(date):
    date = str(date)
    formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"]
    for fmt in formats:
        try:
            correct_date = datetime.strptime(date, fmt)
            return correct_date.strftime(fmt)
        except ValueError:
            pass
    raise ValueError(f"Unsupported date format: {date}")


def handle_parameters(parameters):
    overrides = {}
    processed_keys = []
    if parameters is None:
        return {}
    for parameter in parameters:
        if len(parameter.split('=')) < 2:
            error(f"Wrong parameter {parameter}. Should be key=value")
            sys.exit(1)
        else:
            if len(parameter.split('=')) == 2:
                key, value = parameter.split('=')
            else:
                split = parameter.split('=')
                key = split[0]
                value = parameter.replace(f"{key}=", '')
            if key in processed_keys:
                error(f"Repeated parameter {key}")
                sys.exit(1)
            else:
                processed_keys.append(key)
            if value.isdigit():
                value = int(value)
            elif value.lower() == 'true':
                value = True
            elif value.lower() == 'false':
                value = False
            elif value == 'None':
                value = None
            elif value == '[]':
                value = []
            elif value.startswith('[') and value.endswith(']'):
                if '{' in value:
                    value = literal_eval(value)
                else:
                    value = value[1:-1].split(',')
                    for index, v in enumerate(value):
                        v = v.strip()
                        value[index] = v
            overrides[key] = value
    return overrides


def _delete(url, headers):
    request = Request(url, headers=headers, method='DELETE')
    try:
        return urlopen(request)
    except Exception as e:
        error(e.read().decode())


def _get(url, headers):
    if not os.path.basename(url).split('?')[0].isnumeric():
        encoded_params = urlencode({"range": '0-99999'})
        delimiter = '&' if '?' in url else '?'
        url += f'{delimiter}{encoded_params}'
    try:
        return json.loads(urlopen(Request(url, headers=headers)).read())
    except Exception as e:
        error(e.read().decode())


def _patch(url, headers, data):
    data = json.dumps(data).encode('utf-8')
    try:
        return urlopen(Request(url, data=data, headers=headers, method='PATCH'))
    except Exception as e:
        error(e.read().decode())


def _post(url, headers, data):
    data = json.dumps(data).encode('utf-8')
    try:
        return urlopen(Request(url, data=data, headers=headers, method='POST'))
    except Exception as e:
        error(e.read().decode())


def _put(url, headers, data):
    data = json.dumps(data).encode('utf-8')
    try:
        return urlopen(Request(url, data=data, headers=headers, method='PUT'))
    except Exception as e:
        error(e.read().decode())


def error(text):
    color = "31"
    print(f'\033[0;{color}m{text}\033[0;0m')


def warning(text):
    color = "33"
    print(f'\033[0;{color}m{text}\033[0;0m')


def info(text):
    color = "36"
    print(f'\033[0;{color}m{text}\033[0;0m')


class Glpi(object):
    def __init__(self, url, user, token):
        self.url = url or os.environ.get('GLPI_URL')
        if self.url is None:
            error('GLPI_URL is not set')
            sys.exit(1)
        user = user or os.environ.get('GLPI_USER')
        if user is None:
            error('GLPI_USER is not set')
            sys.exit(1)
        self.user = user.split('@')[0]
        token = token or os.environ.get('GLPI_TOKEN')
        if token is None:
            error('GLPI_TOKEN is not set')
            sys.exit(1)
        ssl._create_default_https_context = ssl._create_unverified_context
        headers = {'Content-Type': 'application/json', 'Authorization': f"user_token {token}"}
        response = _get(f'{self.url}/initSession?get_full_session=true', headers)
        self.headers = {'Content-Type': 'application/json', "Session-Token": response['session_token']}

    def get_user(self, user=None):
        user = user or self.user
        users = _get(f'{self.url}/User', headers=self.headers)
        for u in users:
            if user in u['name']:
                return u

    def list_users(self, overrides={}):
        users = []
        for u in _get(f'{self.url}/User', headers=self.headers):
            if overrides:
                for key in overrides:
                    if u[key] != overrides[key]:
                        continue
            users.append(u)
        return users

    def get_options(self, item_type):
        search_options = {}
        all_options = _get(f'{self.url}/listSearchOptions/{item_type}', headers=self.headers)
        for key in all_options:
            if key.isnumeric():
                search_options[all_options[key]['uid']] = key
        return search_options

    def info_computer(self, overrides={}):
        computer = overrides.get('computer')
        if computer is not None:
            field = 2 if isinstance(computer, int) or computer.isnumeric() else 1
            search_data = "criteria[0][link]=AND&criteria[0][itemtype]=Computer"
            search_data = f"&criteria[0][field]={field}&criteria[0][searchtype]=contains"
            search_data += f"&criteria[0][value]={computer}"
        else:
            search_options = self.get_options('Computer')
            search_data = ''
            for index, key in enumerate(overrides):
                value = overrides[key]
                if not key.startswith('Computer'):
                    key = f'Computer.{key}'
                if key not in search_options:
                    warning("Invalid key {key}")
                    continue
                key_id = search_options[key]
                search_data += "criteria[{index}][link]=AND&criteria[{index}][itemtype]=Computer"
                search_data = f"&criteria[{index}][field]={key_id}&criteria[{index}][searchtype]=contains"
                search_data += f"&criteria[{index}][value]={value}"
        url = f'{self.url}/search/Computer?{search_data}&uid_cols'
        if overrides.get('uid', False):
            url += '&forcedisplay[0]=2'
        computers = _get(url, headers=self.headers)
        return computers['data'] if 'data' in computers else []

    def info_reservation(self, reservation):
        return _get(f'{self.url}/ReservationItem/{reservation}', headers=self.headers)

    def list_reservations(self, overrides={}):
        now = datetime.now()
        user = overrides.get('user') or self.user
        response = _get(f'{self.url}/Reservation', headers=self.headers)
        user_id = self.get_user(user)['id']
        l = [r for r in response if r['users_id'] == user_id and parse_date(r['end']) > now]
        return l

    def list_computers(self, user=None, overrides={}):
        computers = _get(f'{self.url}/search/Computer?uid_cols', headers=self.headers)['data']
        if not overrides:
            return computers
        results = []
        memory = overrides.get('memory')
        cpu_model = overrides.get('cpumodel')
        number = overrides.get('number')
        for computer in computers:
            current_cpu_model = computer['Computer.Item_DeviceProcessor.DeviceProcessor.designation'] or 'XXX'
            if isinstance(current_cpu_model, list):
                current_cpu_model = current_cpu_model[0]
            if cpu_model is not None and cpu_model.lower() not in current_cpu_model.lower():
                continue
            current_memory = computer['Computer.Item_DeviceMemory.size'] or '0'
            if memory is not None and int(float(current_memory)) < int(memory):
                continue
            results.append(computer)
            if number is not None and len(results) >= int(number):
                break
        return results

    def update_computer(self, computer, overrides):
        computer_info = self.info_computer({'computer': computer, 'uid': True})
        if not computer_info:
            error(f"Computer {computer} not found")
            return
        computer_id = computer_info[0]['Computer.id']
        valid_keys = list(_get(f'{self.url}/Computer/', self.headers)[0].keys())
        wrong_keys = [key for key in overrides if key not in valid_keys]
        if wrong_keys:
            error(f"Ignoring keys {','.join(wrong_keys)}")
            for key in wrong_keys:
                del overrides[key]
        if not overrides:
            info("Nothing to update")
        data = {'input': overrides}
        return _put(f'{self.url}/Computer/{computer_id}', self.headers, data)

    def create_reservation(self, computer, overrides):
        overrides['begin'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        if 'end' not in overrides:
            overrides['end'] = date.today() + timedelta(days=30)
        user = overrides.get('user', self.user)
        if 'users_id' not in overrides:
            user_id = self.get_user(user)['id']
            overrides['users_id'] = user_id
        overrides['end'] = parse_date(str(overrides['end']))
        if 'comment' not in overrides:
            overrides['comment'] = f'reservation for {user}'
        computer_id = self.info_computer({'computer': computer, 'uid': True})[0]['Computer.id']
        reservationitem_id = self.get_reservation_item_id(computer_id)
        overrides['reservationitems_id'] = reservationitem_id
        valid_keys = list(_get(f'{self.url}/Reservation/', self.headers)[0].keys())
        wrong_keys = [key for key in overrides if key not in valid_keys]
        if wrong_keys:
            error(f"Ignoring keys {','.join(wrong_keys)}")
            for key in wrong_keys:
                del overrides[key]
        if not overrides:
            info("Nothing to create")
            return
        data = {'input': overrides}
        return _post(f'{self.url}/Reservation', self.headers, data)

    def delete_reservation(self, reservation):
        return _delete(f'{self.url}/Reservation/{reservation}', headers=self.headers)

    def update_reservation(self, reservation, overrides):
        valid_keys = list(_get(f'{self.url}/Reservation/', self.headers)[0].keys()) + ['user']
        wrong_keys = [key for key in overrides if key not in valid_keys]
        if wrong_keys:
            error(f"Ignoring keys {','.join(wrong_keys)}")
            for key in wrong_keys:
                del overrides[key]
        if not overrides:
            date_after_month = datetime.today() + timedelta(days=30)
            new_date = date_after_month.strftime('%Y-%m-%d 00:00:00')
            warning(f"Setting end date to {new_date}")
            overrides['end'] = new_date
        if 'end' in overrides:
            overrides['end'] = parse_date(str(overrides['end']))
        new_user = overrides.get('user') or overrides.get('users_id')
        if new_user is not None and not str(new_user).isnumeric():
            overrides['users_id'] = self.get_user(new_user)['id']
        if 'user' in overrides:
            del overrides['user']
        data = {'input': overrides}
        return _put(f'{self.url}/Reservation/{reservation}', self.headers, data)

    def get_reservation_item_id(self, computer_id):
        url = f'{self.url}/ReservationItem?uid_cols'
        reservation_items = _get(url, headers=self.headers)
        for entry in reservation_items:
            if entry['itemtype'] == 'Computer' and entry['items_id'] == computer_id:
                return entry['id']
