#!/usr/bin/env python3
"""NoyAcg API 最小客户端。

仅供学习与技术研究。默认不执行任何写操作：
`send` 必须显式加 `--yes` 才会真的发帖。

用法::

    export NOY_SESSION=xxxx          # 二选一：直接给会话 Cookie
    export NOY_EMAIL=you@example.com NOY_PASS=...   # 或者给账号密码现登

    python noy_client.py whoami
    python noy_client.py ads
    python noy_client.py signin
    python noy_client.py home --adult false
    python noy_client.py badges
    python noy_client.py toggle-badge 8 --yes
    python noy_client.py upload ./pic.jpg
    python noy_client.py send --title 测试 --content 你好 --image <file> --yes

字段含义与失败分支见仓库 docs/ 目录。
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

import requests

BASE_URL = "https://noymanga.com"
BUCKET_URL = "https://bucket.noymanga.com"


class NoyError(RuntimeError):
    """接口返回了 status != ok。"""


class AuthRequired(NoyError):
    """status == login：会话缺失或过期。"""


class NoyClient:
    def __init__(
        self,
        session_cookie: str | None = None,
        *,
        base_url: str = BASE_URL,
        allow_adult: str = "false",
        timeout: float = 20.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {
                "accept": "application/json",
                "user-agent": "NoyAcg-API-Collect/example (+https://github.com/kwkare/NoyAcg-API-Collect)",
                "origin": self.base_url,
                "referer": f"{self.base_url}/",
                "allow-adult": allow_adult,
            }
        )
        if session_cookie:
            self.session.cookies.set("NOY_SESSION", session_cookie, domain="noymanga.com", path="/")

    # ---------------------------------------------------------------- 内部

    def _post(
        self,
        path: str,
        *,
        data: dict[str, Any] | None = None,
        ok_statuses: tuple[Any, ...] = ("ok",),
    ) -> dict[str, Any]:
        resp = self.session.post(f"{self.base_url}{path}", data=data, timeout=self.timeout)
        resp.raise_for_status()
        payload = resp.json()
        self._raise_for_status(payload, ok_statuses)
        return payload

    @staticmethod
    def _raise_for_status(payload: dict[str, Any], ok_statuses: tuple[Any, ...] = ("ok",)) -> None:
        status = payload.get("status")
        if status in ok_statuses:
            return
        if status == "login":
            raise AuthRequired("会话失效（status=login），请重新登录")
        raise NoyError(f"接口返回 status={status!r}：{json.dumps(payload, ensure_ascii=False)[:200]}")

    # ---------------------------------------------------------------- 鉴权

    def login(self, email: str, password: str) -> None:
        """成功后 Cookie 自动落在 self.session 里。"""
        resp = self.session.post(
            f"{self.base_url}/api/login",
            data={"user": email, "pass": password},
            timeout=self.timeout,
        )
        resp.raise_for_status()
        self._raise_for_status(resp.json())
        if "NOY_SESSION" not in self.session.cookies:
            # status=ok 但没拿到 Cookie，说明服务端行为变了
            raise NoyError("登录返回 ok，但没有下发 NOY_SESSION")

    @property
    def session_cookie(self) -> str | None:
        return self.session.cookies.get("NOY_SESSION", domain="noymanga.com")

    # ---------------------------------------------------------------- 读

    def home(self) -> dict[str, Any]:
        return self._post("/api/home")

    def userinfo(self) -> dict[str, Any]:
        return self._post("/api/v3/userinfo").get("userinfo", {})

    def ads(self) -> list[dict[str, Any]]:
        """首页广告位。注意：不传 allow-adult 时等同于 false，不会返回成人向素材。"""
        return self._post("/api/v3/ads").get("data", [])

    def signin_record(self) -> dict[str, Any]:
        """签到记录。这个接口的 status 是数字 200，所以单独放行。"""
        return self._post("/api/v4/signin/record", ok_statuses=("ok", 200))

    def badges(self) -> dict[str, Any]:
        payload = self._post("/api/badge")
        return {"data": payload.get("data", []), "show": payload.get("show", [])}

    # ---------------------------------------------------------------- 写

    def set_badge_show(self, badge_id: int) -> bool:
        """开关式：调用一次翻转一次，不幂等。"""
        self._post("/api/v3/set_badge_show", data={"id": badge_id})
        return True

    def upload_image(self, path: str) -> str:
        """上传到图床并返回 file 名。注意这里不共享 session，避免把 Cookie 发给图床。"""
        token = self._post("/api/get_image_bucket_token").get("token")
        if not token:
            raise NoyError("没有拿到上传 token")

        filename = os.path.basename(path)
        with open(path, "rb") as fh:
            resp = requests.post(
                f"{BUCKET_URL}/api/upload_image",
                headers={"origin": self.base_url, "referer": f"{self.base_url}/"},
                data={"token": token},
                files={"file": (filename, fh)},
                timeout=60,
            )
        resp.raise_for_status()
        payload = resp.json()
        if payload.get("status") != "ok":
            raise NoyError(f"上传失败：{payload}")
        return payload["file"]

    def send_community(
        self,
        title: str,
        content: str,
        images: list[str] | None = None,
        platform: str = "web",
    ) -> bool:
        data: dict[str, Any] = {"title": title, "content": content, "platform": platform}
        if images:
            # 关键：JSON 数组的「字符串」，元素带 image/ 前缀
            data["image"] = json.dumps([f"image/{name}" for name in images])
        self._post("/api/v3/send_community", data=data)
        return True


# -------------------------------------------------------------------- CLI


def _client_from_env(args: argparse.Namespace) -> NoyClient:
    client = NoyClient(
        os.environ.get("NOY_SESSION"),
        allow_adult=str(args.adult) if hasattr(args, "adult") else "false",
    )
    if client.session_cookie is None:
        email, password = os.environ.get("NOY_EMAIL"), os.environ.get("NOY_PASS")
        if not (email and password):
            sys.exit("缺少凭证：设置 NOY_SESSION，或同时设置 NOY_EMAIL / NOY_PASS")
        client.login(email, password)
    return client


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="NoyAcg API 最小客户端（学习用途）")
    parser.add_argument("--adult", default="false", choices=["true", "false", "both"], help="allow-adult 取值")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("whoami", help="打印用户信息摘要")
    sub.add_parser("ads", help="首页广告位")
    sub.add_parser("signin", help="签到记录（只读）")

    p_home = sub.add_parser("home", help="首页聚合数据")
    p_home.add_argument("--out", help="把原始 JSON 写到这里")

    p_badges = sub.add_parser("badges", help="打印徽章与佩戴状态")
    p_badges.add_argument("--toggle", type=int, metavar="ID", help="同时切换某个徽章的佩戴状态（写操作）")
    p_badges.add_argument("--yes", action="store_true", help="确认执行写操作")

    p_upload = sub.add_parser("upload", help="上传图片到图床，返回 file 名")
    p_upload.add_argument("path")

    p_send = sub.add_parser("send", help="发帖（默认 dry-run）")
    p_send.add_argument("--title", required=True)
    p_send.add_argument("--content", required=True)
    p_send.add_argument("--image", action="append", default=[], help="图床返回的 file 名，可重复")
    p_send.add_argument("--platform", default="web", choices=["web", "android"])
    p_send.add_argument("--yes", action="store_true", help="真的发出去")

    args = parser.parse_args(argv)
    client = _client_from_env(args)

    try:
        if args.cmd == "whoami":
            info = client.userinfo()
            print(
                json.dumps(
                    {
                        "uid": info.get("Uid"),
                        "username": info.get("Username"),
                        "integral": info.get("Integral"),
                        "badges": [b.get("Name") for b in info.get("Badge", [])],
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )

        elif args.cmd == "ads":
            for ad in client.ads():
                host = ad["url"].split("/")[2] if "//" in ad["url"] else ad["url"]
                print(f"{host:24} {ad['img']}")

        elif args.cmd == "signin":
            rec = client.signin_record()
            print(f"连续签到 {rec.get('continuous')} 天，今天已签到：{rec.get('today')}")

        elif args.cmd == "home":
            data = client.home()
            print({k: (len(v) if isinstance(v, list) else v) for k, v in data.items()})
            if args.out:
                with open(args.out, "w", encoding="utf-8") as fh:
                    json.dump(data, fh, ensure_ascii=False, indent=2)
                print(f"已写入 {args.out}")

        elif args.cmd == "badges":
            result = client.badges()
            shown = {int(i) for i in result["show"]}
            for badge in result["data"]:
                mark = "佩戴中" if badge["Id"] in shown else "未佩戴"
                print(f"{mark}  {badge['Id']:>4}  {badge['Name']}")
            if args.toggle is not None:
                if not args.yes:
                    print(f"[dry-run] 会切换徽章 {args.toggle} 的佩戴状态（加 --yes 执行）")
                else:
                    client.set_badge_show(args.toggle)
                    print(f"已切换徽章 {args.toggle}")

        elif args.cmd == "upload":
            print(client.upload_image(args.path))

        elif args.cmd == "send":
            if not args.yes:
                print(f"[dry-run] 将要发布：{args.title!r}，图片 {args.image or '无'}（加 --yes 真的发）")
            else:
                client.send_community(args.title, args.content, args.image, args.platform)
                print("已提交")

    except AuthRequired as exc:
        sys.exit(str(exc))
    except NoyError as exc:
        sys.exit(str(exc))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
