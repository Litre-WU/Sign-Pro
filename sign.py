import asyncio
import httpx
from fastapi import FastAPI, BackgroundTasks, Body, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
from typing import Dict, Union
from pathlib import Path
from diskcache import Cache
from http import cookies
from json import dumps, loads
from time import time
import hashlib
import hmac
from base64 import b64encode
import re

db_path = str(Path(__file__).parent / "tmp")

cache = Cache(db_path)


app = FastAPI(title="API", version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 程序开始
@app.on_event("startup")
async def startup_event():
    print("\033[92m服务启动")


# 程序停止
@app.on_event("shutdown")
async def shutdown_event():
    print("\033[91m服务结束")


@app.post("/{path}", tags=["api"])
async def api(request: Request, path: str, background_tasks: BackgroundTasks,
              cookie: Union[str, None] = Body(default="XXX"),
              token: Union[str, None] = Body(default="XXX"),
              secret: Union[str, None] = Body(default="XXX"),
              time: Union[str, None] = Body(default="09:00:00")):
    cid = hmac.new("sign".encode(), f'{cookie}'.encode(), digestmod="MD5").hexdigest()
    print(cid)
    # if cookie:
    #     cache["account-x"][path].update({"cookies": {cid: {"cookie": cookie, "time": time}}})


# 请求函数
async def fetch(*args, **kwargs):
    if not kwargs.get("url"): return None
    if not kwargs.get("method"): kwargs.update({"method": "GET"})
    http2 = kwargs.pop("http2") if kwargs.get("http2") else False
    try:
        async with asyncio.Semaphore(100):
            async with httpx.AsyncClient(http2=http2, follow_redirects=True, timeout=5) as client:
                rs = await client.request(**kwargs)
                return rs
    except Exception as e:
        print(f'\033[94mfetch {kwargs["url"]} {e}')
        retry = args[0] if args else 0
        retry += 1
        if retry > 2:
            return None
        kwargs.update({"http2": http2})
        return await fetch(retry, **kwargs)


async def test():
    path = "ding"
    token = ""
    secret = ""

    args = cache["fun"][path]["args"]

    for i, arg in enumerate(args):
        if "token" in arg:
            args[i] = token
        if "secret" in arg:
            args[i] = secret
        if arg.startswith(":"):
            args[i] = eval(arg[1:].format(*args[:i]))
    for meta in cache["fun"]["ding"]["fetch"]:
        for k, v in meta["params"].items():
            if v.startswith("{") and v.endswith("}"):
                meta["params"][k] = v.format(*args)
        for i in re.findall(r'!(\d+)~', dumps(meta["json"])):
            meta["json"] = loads(re.sub(f'!{int(i)}~', args[int(i)], dumps(meta["json"])))
        print(meta)
        res = await fetch(**meta)
        if res and res.status_code == 200:
            print(res.text)
            if path == "ding":
                cache["account-x"]["ding"].update({hmac.new("sign".encode(), f'{token}{secret}'.encode(),
                                                            digestmod="MD5").hexdigest(): {'access_token': token,
                                                                                           'secret': secret}})


if __name__ == "__main__":
    asyncio.run(test())

    # cache.set("fun", {
    #     "jd": {
    #         "fetch": [
    #             {
    #                 "method": "POST",
    #                 "url": "https://api.m.jd.com/client.action",
    #                 "params": {"functionId": "signBeanAct", "appid": "ld", "client": "apple"},
    #                 "cookies": {
    #                     "pt_key": "~",
    #                     "pt_pin": "~"
    #                 }
    #             },
    #             {
    #                 "method": "POST",
    #                 "url": "https://lop-proxy.jd.com/jiFenApi/signInAndGetReward",
    #                 "json": [{"userNo": "$cooMrdGatewayUid$"}],
    #                 "headers": {
    #                     "AppParams": '{"appid":158,"ticket_type":"m"}',
    #                     "uuid": "~",
    #                     "LOP-DN": "jingcai.jd.com"
    #                 }}],
    #         "args": ["pt_key", "pt_pin", ":'{:.0f}'.format(time() * 10 ** 13)"]},
    #     # "csai": {"fetch": [], "args": []},
    #     "ding": {
    #         "fetch": [{
    #             "method": "POST",
    #             "url": "https://oapi.dingtalk.com/robot/send",
    #             "params": {
    #                 "access_token": "{0}",
    #                 "timestamp": "{1}",
    #                 "sign": "{3}",
    #             },
    #             "json": {
    #                 "msgtype": "text",
    #                 "text": {"content": "!4~"}
    #             },
    #             "headers": {"Content-Type": "application/json"}
    #         }],
    #         "args": ["access_token", ":round(time() * 1000)", "secret",
    #                  ":b64encode(hmac.new('{2}'.encode(), '{1}\\n{2}'.encode(), digestmod=hashlib.sha256).digest()).decode()",
    #                  "测试"]},
    # })

    # cache.set("account-x", {
    #     "jd": {
    #         "cookies":
    #             {
    #                 "c021c6668b8cff8bd64456c91b79e69e": {
    #                     "cookie": "pt_key=AA; pt_pin=jd_;",
    #                     "time": "01:00"}
    #             }},
    #     "ding": {
    #         "a233f7076862a52a2a0b2c7b8658a8ae": {
    #             "access_token": "",
    #             "secret": ""
    #         }}
    # })

