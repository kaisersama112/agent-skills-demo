#!/usr/bin/env python3
"""从命令行直接执行用户输入 -> Planner -> Executor -> Renderer 的完整流程。"""

import argparse
import asyncio
import json
import uuid

from core.chat_orchestrator import chat_orchestrator


async def _run_once(session_id: str, message: str) -> dict:
    return await chat_orchestrator.handle_message(session_id=session_id, user_input=message)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full user-input orchestration flow")
    parser.add_argument("message", help="用户输入内容")
    parser.add_argument(
        "--session-id",
        default=f"cli-{uuid.uuid4().hex[:8]}",
        help="会话ID，默认自动生成",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="是否格式化输出 JSON",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="本地演示模式：不调用外部LLM，直接返回示例成功结果",
    )
    args = parser.parse_args()

    if args.dry_run:
        result = {
            "type": "json",
            "content": {
                "status": "success",
                "user_input": args.message,
                "plan": {
                    "skill": "demo",
                    "action": "demo_action",
                    "input": {"user_input": args.message},
                    "reason": "dry-run",
                },
                "execution": {
                    "status": "success",
                    "skill": "demo",
                    "action": "demo_action",
                    "script": "scripts/demo_action.py",
                    "returncode": 0,
                },
            },
        }
    else:
        result = asyncio.run(_run_once(session_id=args.session_id, message=args.message))

    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
