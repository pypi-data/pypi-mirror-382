from __future__ import annotations

import os
from typing import Any

from ..rich_formatter import print_formatted_response, print_info, print_error, get_formatter, print_user_input
from ..rich_ui.io_helpers import print_stage_badge
from .session import cleanup_and_save_session
from ..runtime.telemetry import get_usage as _telemetry_usage, get_metrics as _telemetry_metrics
from .repl_helpers import (
    create_session_stack,
    safe_detect_stage,
    handle_system_command,
    process_manual_turn,
    build_react_enhanced_input,
    run_agent_turn,
)
"""REPL with optional context enrichment from attachments and tools."""


## get_langchain_tools is defined in runtime/tools_wrappers.py; no duplication here.


def online_repl(agent: Any, loaded_variant: str) -> None:
    agent_mode = os.environ.get("LC_AGENT_MODE", "react").strip().lower()
    use_manual_routing = agent_mode == "chat"

    session_logger, chat_logger = create_session_stack(
        {"loaded_prompt_variant": loaded_variant, "agent_mode": agent_mode}
    )

    if hasattr(agent, 'set_chat_logger'):
        agent.set_chat_logger(chat_logger)
    if hasattr(agent, 'set_session_logger'):
        try:
            agent.set_session_logger(session_logger)
        except Exception:
            pass

    formatter = get_formatter()
    formatter.print_rule("Academic Research Mentor")
    print_info(f"Loaded prompt variant: {loaded_variant}")
    print_info(f"Agent mode: {agent_mode}")
    print_info("Type 'exit' to quit")
    formatter.console.print("")

    try:
        while True:
            try:
                formatter.console.print("[bold cyan]You:[/bold cyan] ", end="")
                user = input().strip()
                session_logger.log_event("raw_input", {"text": user})
            except EOFError:
                print_info("\n📝 EOF received. Saving chat session...")
                cleanup_and_save_session(chat_logger, "EOF (Ctrl+D)", session_logger)
                break

            outcome = handle_system_command(user, agent, session_logger, allow_resume=True)
            if outcome.exit_command:
                cleanup_and_save_session(chat_logger, outcome.exit_command, session_logger)
                break
            if outcome.handled:
                formatter.console.print("")
                continue

            turn_number = chat_logger.next_turn_number()
            session_logger.start_turn(turn_number, user)

            stage = safe_detect_stage(user, chat_logger, session_logger)
            if stage:
                print_stage_badge(
                    str(stage.get("code", "")).upper() or "A",
                    str(stage.get("name", "")).strip() or "Pre idea",
                    float(stage.get("confidence", 0.0)),
                )
            print_user_input(user)

            if use_manual_routing:
                manual = process_manual_turn(user, session_logger, enable_research_context=True)
                if manual.consumed:
                    chat_logger.add_turn(user, manual.tool_calls)
                    formatter.console.print("")
                    continue
                enhanced_user_input = manual.enhanced_input
            else:
                enhanced_user_input = build_react_enhanced_input(user, session_logger)

            run_agent_turn(
                agent,
                user,
                enhanced_user_input,
                use_manual_routing=use_manual_routing,
                chat_logger=chat_logger,
                session_logger=session_logger,
                turn_number=turn_number,
            )

            formatter.console.print("")
    finally:
        try:
            from .args import build_parser as _bp
            p = _bp()
            # crude parse to check flag presence in argv
            import sys as _sys
            if "--telemetry" in (_sys.argv or []):
                u = _telemetry_usage()
                m = _telemetry_metrics()
                if u or m:
                    print_info(f"Telemetry: tools={u}, metrics={m}")
        except Exception:
            pass
        if not any(turn.get("user_prompt", "").lower() in {"exit", "quit", "eof (ctrl+d)"} for turn in chat_logger.current_session):
            cleanup_and_save_session(chat_logger, "unexpected_exit", session_logger)


def offline_repl(reason: str) -> None:
    formatter = get_formatter()
    formatter.print_rule("Academic Research Mentor (Offline Mode)")
    print_info("Type 'exit' to quit")
    if reason:
        print_error(f"Offline reason: {reason}")
    print_info("Falling back to a simple echo mentor")
    formatter.console.print("")

    metadata = {"mode": "offline"}
    if reason:
        metadata["offline_reason"] = reason
    session_logger, chat_logger = create_session_stack(metadata)

    try:
        while True:
            try:
                formatter.console.print("[bold cyan]You:[/bold cyan] ", end="")
                user = input().strip()
                session_logger.log_event("raw_input", {"text": user})
            except EOFError:
                print_info("\n📝 EOF received. Saving chat session...")
                cleanup_and_save_session(chat_logger, "EOF (Ctrl+D)", session_logger)
                break
            outcome = handle_system_command(user, agent=None, session_logger=session_logger, allow_resume=False)
            if outcome.exit_command:
                cleanup_and_save_session(chat_logger, outcome.exit_command, session_logger)
                break
            if outcome.handled:
                formatter.console.print("")
                continue

            turn_number = chat_logger.next_turn_number()
            session_logger.start_turn(turn_number, user)

            stage = safe_detect_stage(user, chat_logger, session_logger)
            if stage:
                print_stage_badge(
                    str(stage.get("code", "")).upper() or "A",
                    str(stage.get("name", "")).strip() or "Pre idea",
                    float(stage.get("confidence", 0.0)),
                )
            print_user_input(user)

            manual = process_manual_turn(user, session_logger, enable_research_context=False)
            if manual.consumed:
                chat_logger.add_turn(user, manual.tool_calls)
                continue

            chat_logger.add_turn(
                user,
                [],
                "A few quick questions to calibrate: What is your goal, compute budget, and target venue? Then I can suggest next steps.",
            )

            print_formatted_response(
                "A few quick questions to calibrate: What is your goal, compute budget, and target venue? Then I can suggest next steps.",
                "Mentor",
            )

            formatter.console.print("")
    finally:
        if not any(turn.get("user_prompt", "").lower() in {"exit", "quit", "eof (ctrl+d)"} for turn in chat_logger.current_session):
            cleanup_and_save_session(chat_logger, "unexpected_exit", session_logger)