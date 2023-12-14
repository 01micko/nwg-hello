import json
import os
import pwd
import sys


def eprint(*args, log=False):
    print(*args, file=sys.stderr)
    if log:
        log_file = os.path.join(os.environ['HOME'], '.nwg_hello.log')
        with open(log_file, 'a') as f:
            print(*args, file=f)


def list_users():
    users = []
    for user in pwd.getpwall():
        if user.pw_dir.startswith('/home/'):
            users.append(user.pw_name)
    return users


def load_json(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        eprint(f"* error loading json: {e}")
        return {}


def save_json(src_dict, path, en_ascii=True):
    with open(path, 'w') as f:
        json.dump(src_dict, f, indent=2, ensure_ascii=en_ascii)


def load_text_file(path):
    try:
        with open(path, 'r') as file:
            data = file.read()
            return data
    except Exception as e:
        eprint(e)
        return None


def list_sessions(session_dirs):
    _sessions = []
    for session_dir in session_dirs:
        if os.path.isdir(session_dir):
            for file_name in sorted(os.listdir(session_dir)):
                p = os.path.join(session_dir, file_name)
                if p.endswith('.desktop'):
                    session = parse_desktop_entry(p)
                    if session:
                        _sessions.append(session)
    return _sessions


def parse_desktop_entry(path):
    paths = os.getenv('PATH').split(":")
    session = {}
    lines = load_text_file(path).splitlines()
    if lines:
        for line in lines:
            if line.startswith('Name'):
                session['name'] = line.split("=")[1]
                continue
            if line.startswith('Exec'):
                session['exec'] = line.split("=")[1]
                continue
            if line.startswith('TryExec'):
                session['try-exec'] = line.split("=")[1]
                continue
        if 'try-exec' in session:
            if os.path.isfile(session['try-exec']):
                return session
            else:
                for p in paths:
                    if os.path.isfile(os.path.join(p, session['try-exec'])):
                        return session
        else:
            return session
    else:
        return None
