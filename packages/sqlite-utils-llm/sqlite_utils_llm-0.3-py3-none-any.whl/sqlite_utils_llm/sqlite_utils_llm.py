import sqlite_utils
import subprocess

def fn_llm(model, prompt):
    # we can't use llm python api because llm depends on sqlite-utils
    result = subprocess.run(["llm", "-m", model, prompt], capture_output=True, text=True)
    return result.stdout.rstrip()

@sqlite_utils.hookimpl
def prepare_connection(conn):
    conn.create_function("llm", 2, fn_llm)
