"""Code execution proxy -> WandBox public API (https://wandbox.org).

Free, no API key required. Pinned compiler versions are used because
WandBox's "-head" rolling compilers occasionally break.

Maps friendly language names to WandBox compilers. Java code is
normalized so the public class is named `prog` (a WandBox requirement).
"""

import re

import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from http_client import make_client

router = APIRouter(prefix="/api", tags=["execute"])

WANDBOX_URL = "https://wandbox.org/api/compile.json"

# language -> WandBox compiler name (pinned, verified working)
COMPILERS = {
    "python": "cpython-3.12.7",
    "javascript": "nodejs-20.17.0",
    "java": "openjdk-jdk-21+35",
    "c": "gcc-13.2.0-c",
}


class ExecuteIn(BaseModel):
    language: str = "python"
    code: str = ""
    stdin: str = ""


def _normalize_java(code: str) -> str:
    """WandBox requires the public class to be named `prog`."""
    renamed, n = re.subn(r"(public\s+)?class\s+\w+", "public class prog", code, count=1)
    return renamed if n else f"public class prog {{\n{code}\n}}"


@router.post("/execute")
def execute(payload: ExecuteIn):
    lang = payload.language.lower()
    compiler = COMPILERS.get(lang)
    if not compiler:
        raise HTTPException(400, f"unsupported language; choose from {sorted(COMPILERS)}")
    code = payload.code
    if not code.strip():
        raise HTTPException(400, "code is empty")
    if lang == "java":
        code = _normalize_java(code)
    try:
        with make_client() as client:
            r = client.post(
                WANDBOX_URL,
                json={"compiler": compiler, "code": code, "stdin": payload.stdin or ""},
                timeout=45,
            )
        r.raise_for_status()
        data = r.json()
        if isinstance(data, dict) and data.get("status") == "0":
            return {
                "stdout": data.get("program_output", "") or data.get("program_message", ""),
                "stderr": data.get("program_error", ""),
                "output": data.get("program_message", ""),
                "exit_code": 0,
                "language": lang,
            }
        # compilation or runtime failure — surface compiler messages
        detail = (data.get("compiler_error") or data.get("program_error") or "execution failed").strip()
        return {
            "stdout": data.get("program_output", ""),
            "stderr": detail,
            "output": data.get("program_message", ""),
            "exit_code": 1,
            "language": lang,
        }
    except httpx.HTTPError as e:
        raise HTTPException(502, f"code execution service unavailable: {e}")
