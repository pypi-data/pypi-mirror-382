#!/usr/bin/env python3
"""
henosis-tools CLI
-----------------
Standalone CLI to run local machine interactions with sandboxing:
- Filesystem: read, write, append, list, apply_patch
- Commands: run whitelisted commands without a shell

Examples:
  henosis-tools fs ls .
  henosis-tools fs read README.md
  henosis-tools fs write notes/todo.txt --content "hello" --scope workspace
  henosis-tools cmd run "git status" --allow "git,python" --cwd .
  henosis-tools patch apply --patch-file changes.patch --scope workspace

Environment variables (optional):
  HENOSIS_WORKSPACE_DIR, HENOSIS_ALLOW_EXTENSIONS, HENOSIS_MAX_FILE_BYTES,
  HENOSIS_MAX_EDIT_BYTES, HENOSIS_EDIT_SAFEGUARD_MAX_LINES,
  HENOSIS_ALLOW_COMMANDS, HENOSIS_COMMAND_TIMEOUT_SEC
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional

from henosis_cli_tools import (
    FileToolPolicy,
    resolve_path,
    read_file as tool_read_file,
    write_file as tool_write_file,
    append_file as tool_append_file,
    list_dir as tool_list_dir,
    run_command as tool_run_command,
    apply_patch as tool_apply_patch,
)


def _policy_from_args(args: argparse.Namespace) -> FileToolPolicy:
    scope = args.scope
    workspace = Path(args.workspace).expanduser().resolve() if args.workspace else Path(os.getenv("HENOSIS_WORKSPACE_DIR", "./workspace")).expanduser().resolve()
    host_base = Path(args.host_base).expanduser().resolve() if args.host_base else None
    allowed_roots = None
    if args.allowed_roots:
        allowed_roots = [Path(p).expanduser().resolve() for p in args.allowed_roots.split(",") if p.strip()]
    allowed_exts = set()
    if args.allowed_exts:
        allowed_exts = {e.strip().lower() for e in args.allowed_exts.split(",") if e.strip()}
    else:
        # Empty -> use default set inside policy
        allowed_exts = frozenset()
    max_bytes = int(args.max_bytes) if args.max_bytes else None
    pol = FileToolPolicy(
        scope=scope,
        workspace_base=workspace,
        host_base=host_base,
        allowed_roots=allowed_roots,
        allowed_exts=allowed_exts or FileToolPolicy().allowed_exts,
        max_bytes=max_bytes or FileToolPolicy().max_bytes,
    )
    return pol


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="henosis-tools", description="Local sandboxed tools for filesystem and commands")
    sub = p.add_subparsers(dest="cmd")

    # Common policy args helper
    def add_policy_args(sp: argparse.ArgumentParser) -> None:
        sp.add_argument("--scope", choices=["workspace", "host"], default="workspace", help="Scope for path resolution (default: workspace)")
        sp.add_argument("--workspace", default=None, help="Workspace base directory (default: ./workspace)")
        sp.add_argument("--host-base", default=None, help="Absolute base directory for host scope (optional)")
        sp.add_argument("--allowed-roots", default=None, help="CSV of absolute allowed roots for host scope")
        sp.add_argument("--allowed-exts", default=None, help="CSV of allowed file extensions (lower-case). Omit to use defaults.")
        sp.add_argument("--max-bytes", type=int, default=None, help="Max bytes per read/write (default: env or 1GB)")

    # fs group
    fs = sub.add_parser("fs", help="Filesystem operations")
    fs_sub = fs.add_subparsers(dest="fs_cmd")

    p_ls = fs_sub.add_parser("ls", help="List directory")
    p_ls.add_argument("path", nargs="?", default=".")
    add_policy_args(p_ls)

    p_read = fs_sub.add_parser("read", help="Read a text file with BOM/UTF auto-detect")
    p_read.add_argument("path")
    add_policy_args(p_read)

    p_write = fs_sub.add_parser("write", help="Write a text file (overwrite)")
    p_write.add_argument("path")
    p_write.add_argument("--content", default=None, help="Inline text content (use '-' to read from stdin)")
    add_policy_args(p_write)

    p_append = fs_sub.add_parser("append", help="Append to a text file")
    p_append.add_argument("path")
    p_append.add_argument("--content", default=None, help="Inline text content (use '-' to read from stdin)")
    add_policy_args(p_append)

    # cmd group
    pcmd = sub.add_parser("cmd", help="Run whitelisted commands without a shell")
    pcmd_sub = pcmd.add_subparsers(dest="cmd_cmd")

    p_run = pcmd_sub.add_parser("run", help="Run a command")
    p_run.add_argument("command", help="Command string (parsed without a shell)")
    p_run.add_argument("--cwd", default=".")
    p_run.add_argument("--timeout", type=float, default=None)
    p_run.add_argument("--allow", default=None, help="CSV allowlist of base commands (default: env HENOSIS_ALLOW_COMMANDS)")
    add_policy_args(p_run)

    # patch group
    ppatch = sub.add_parser("patch", help="Apply simplified multi-file patch")
    ppatch_sub = ppatch.add_subparsers(dest="patch_cmd")

    p_apply = ppatch_sub.add_parser("apply", help="Apply a patch from stdin or file")
    p_apply.add_argument("--patch-file", default=None, help="Path to patch file (omit to read from stdin)")
    p_apply.add_argument("--cwd", default=".")
    p_apply.add_argument("--lenient", action="store_true", default=True)
    p_apply.add_argument("--no-lenient", dest="lenient", action="store_false")
    p_apply.add_argument("--dry-run", action="store_true", default=False)
    p_apply.add_argument("--backup", action="store_true", default=True)
    p_apply.add_argument("--no-backup", dest="backup", action="store_false")
    p_apply.add_argument("--safeguard-max-lines", type=int, default=None)
    p_apply.add_argument("--confirm", dest="safeguard_confirm", action="store_true", default=False)
    add_policy_args(p_apply)

    return p


def _read_content_arg(val: Optional[str]) -> str:
    if val == "-":
        return sys.stdin.read()
    return val or ""


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_help()
        return 1

    pol = _policy_from_args(args)

    try:
        if args.cmd == "fs":
            if args.fs_cmd == "ls":
                res = tool_list_dir(args.path, pol)
            elif args.fs_cmd == "read":
                res = tool_read_file(args.path, pol)
            elif args.fs_cmd == "write":
                content = _read_content_arg(args.content)
                res = tool_write_file(args.path, content, pol)
            elif args.fs_cmd == "append":
                content = _read_content_arg(args.content)
                res = tool_append_file(args.path, content, pol)
            else:
                parser.print_help()
                return 1
        elif args.cmd == "cmd":
            if args.cmd_cmd == "run":
                res = tool_run_command(args.command, pol, cwd=args.cwd, timeout=args.timeout, allow_commands_csv=args.allow)
            else:
                parser.print_help()
                return 1
        elif args.cmd == "patch":
            if args.patch_cmd == "apply":
                if args.patch_file:
                    patch_text = Path(args.patch_file).read_text(encoding="utf-8")
                else:
                    patch_text = sys.stdin.read()
                smax = args.safeguard_max_lines if args.safeguard_max_lines is not None else int(os.getenv("HENOSIS_EDIT_SAFEGUARD_MAX_LINES", "30000"))
                res = tool_apply_patch(
                    patch=patch_text,
                    policy=pol,
                    cwd=args.cwd,
                    lenient=args.lenient,
                    dry_run=args.dry_run,
                    backup=args.backup,
                    safeguard_max_lines=smax,
                    safeguard_confirm=args.safeguard_confirm,
                )
            else:
                parser.print_help()
                return 1
        else:
            parser.print_help()
            return 1
    except Exception as e:
        print(json.dumps({"ok": False, "error": str(e)}))
        return 2

    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0 if res.get("ok") else 3


if __name__ == "__main__":
    raise SystemExit(main())
