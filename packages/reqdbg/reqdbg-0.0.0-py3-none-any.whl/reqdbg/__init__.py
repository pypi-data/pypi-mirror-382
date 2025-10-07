import requests


class AttrToFstr:
    def __getattribute__(self, name):
        return f'{{r.{name}}}'


atf: requests.Response = AttrToFstr()
r_fmt_str = f'{atf.status_code} {atf.reason} {atf.elapsed}\n{atf.text}\n{atf.headers}\n{atf.cookies}'


def format_r_info(r: requests.Response) -> str:
    return eval(f'f{repr(r_fmt_str)}')


def print_r_info(r: requests.Response):
    print(format_r_info(r))


def request_print(*args, **kwargs):
    r = requests.request(*args, **kwargs)
    print_r_info(r)
    return r



