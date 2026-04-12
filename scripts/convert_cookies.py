import json
from pathlib import Path
from typing import Any


INPUT_FILE = Path("youtube-cookies.json")
OUTPUT_FILE = Path("cookies.txt")


def _normalize_cookie_items(raw: Any) -> list[dict]:
    if isinstance(raw, list):
        return [item for item in raw if isinstance(item, dict)]
    if isinstance(raw, dict):
        maybe_list = raw.get("cookies")
        if isinstance(maybe_list, list):
            return [item for item in maybe_list if isinstance(item, dict)]
    return []


def _to_netscape_line(cookie: dict) -> str | None:
    domain = str(cookie.get("domain") or "").strip()
    if not domain:
        return None

    original_domain = domain
    if cookie.get("httpOnly"):
        domain = f"#HttpOnly_{domain}"

    include_subdomains = "TRUE" if original_domain.startswith(".") else "FALSE"
    path = str(cookie.get("path") or "/")
    secure = "TRUE" if cookie.get("secure") else "FALSE"
    expires = str(int(cookie.get("expirationDate") or 0))
    name = str(cookie.get("name") or "")
    value = str(cookie.get("value") or "")

    return "\t".join([domain, include_subdomains, path, secure, expires, name, value])


def main() -> None:
    raw = json.loads(INPUT_FILE.read_text(encoding="utf-8"))
    cookies = _normalize_cookie_items(raw)

    exported = 0
    with OUTPUT_FILE.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write("# Netscape HTTP Cookie File\n")
        for cookie in cookies:
            line = _to_netscape_line(cookie)
            if not line:
                continue
            fh.write(line + "\n")
            exported += 1

    print(f"Wrote {exported} cookies to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
