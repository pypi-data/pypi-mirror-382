# This file is generated from https://raw.githubusercontent.com/zed-industries/agent-client-protocol/refs/heads/main/schema/meta.json.
# Do not edit by hand.
AGENT_METHODS = {
    "authenticate": "authenticate",
    "initialize": "initialize",
    "model_select": "session/set_model",
    "session_cancel": "session/cancel",
    "session_load": "session/load",
    "session_new": "session/new",
    "session_prompt": "session/prompt",
    "session_set_mode": "session/set_mode",
}
CLIENT_METHODS = {
    "fs_read_text_file": "fs/read_text_file",
    "fs_write_text_file": "fs/write_text_file",
    "session_request_permission": "session/request_permission",
    "session_update": "session/update",
    "terminal_create": "terminal/create",
    "terminal_kill": "terminal/kill",
    "terminal_output": "terminal/output",
    "terminal_release": "terminal/release",
    "terminal_wait_for_exit": "terminal/wait_for_exit",
}
PROTOCOL_VERSION = 1
