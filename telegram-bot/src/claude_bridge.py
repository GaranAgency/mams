import asyncio
import json
import logging
from typing import Optional, Tuple

log = logging.getLogger(__name__)


class ClaudeError(RuntimeError):
    pass


async def run_claude(
    prompt: str,
    cwd: str,
    claude_bin: str,
    session_id: Optional[str] = None,
    timeout_sec: int = 600,
) -> Tuple[Optional[str], str]:
    cmd = [claude_bin, "-p", "--output-format", "json", "--dangerously-skip-permissions"]
    if session_id:
        cmd.extend(["--resume", session_id])
    cmd.append(prompt)

    log.info("invoking claude: session=%s cwd=%s prompt_len=%d", session_id, cwd, len(prompt))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout_sec)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise ClaudeError(f"claude timed out after {timeout_sec}s")

    stdout = stdout_b.decode("utf-8", errors="replace")
    stderr = stderr_b.decode("utf-8", errors="replace")

    if proc.returncode != 0:
        log.error("claude exit=%d stderr=%s", proc.returncode, stderr[:500])
        raise ClaudeError(f"claude exit {proc.returncode}: {stderr[:500]}")

    try:
        data = json.loads(stdout)
    except json.JSONDecodeError:
        log.warning("claude output not JSON, using as plain text")
        return None, stdout.strip()

    if isinstance(data, dict):
        new_session = data.get("session_id") or data.get("sessionId")
        result = data.get("result") or data.get("response") or data.get("text") or ""
        if not result and "messages" in data:
            parts = []
            for m in data.get("messages", []):
                if m.get("role") == "assistant":
                    content = m.get("content", "")
                    if isinstance(content, list):
                        for c in content:
                            if c.get("type") == "text":
                                parts.append(c.get("text", ""))
                    else:
                        parts.append(str(content))
            result = "\n".join(parts).strip()
        return new_session, result.strip()

    return None, stdout.strip()
