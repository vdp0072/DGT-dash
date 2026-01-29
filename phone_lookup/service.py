import io
import re
import sys
import threading
import time
from typing import Dict, Tuple
try:
    from .lookup import Sync_Me, CallerID, CallApp, Eyecon, Truecaller
except (ImportError, ValueError):
    from lookup import Sync_Me, CallerID, CallApp, Eyecon, Truecaller

def strip_ansi(text: str) -> str:
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def run_with_timeout(func, args, timeout):
    """Runs a function with a timeout using threading."""
    output_buffer = io.StringIO()
    exception = None

    def target():
        nonlocal exception
        old_stdout = sys.stdout
        sys.stdout = output_buffer
        try:
            func(*args)
        except Exception as e:
            exception = e
        finally:
            sys.stdout = old_stdout

    thread = threading.Thread(target=target)
    thread.setDaemon(True)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        return "TIMEOUT", f"Provider timed out after {timeout}s"
    
    if exception:
        return "ERROR", str(exception)
    
    return "SUCCESS", strip_ansi(output_buffer.getvalue()).strip()

def lookup_single(phone: str) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Performs a single phone lookup across multiple providers.
    Returns (findings, errors) dictionaries.
    """
    findings = {}
    errors = {}
    
    providers = [
        ("CallerID", CallerID().start_callerid_check, [phone, False]),
        ("SyncMe", Sync_Me().start_styncme, [phone, False]),
        ("CallApp", CallApp().send_request, [phone, False]),
        ("Eyecon_Pic", Eyecon().send_request_pic, [phone, False]),
        ("Eyecon_Name", Eyecon().send_request_getname, [phone, False]),
        ("Truecaller", Truecaller().send_request, [phone, False]),
    ]
    
    # Global budget 10s (8-10s as per user suggestion)
    # Give each provider a 2s cap to stay within budget
    prov_timeout = 2.0 
    
    for name, func, args in providers:
        status, result = run_with_timeout(func, args, prov_timeout)
        if status == "SUCCESS":
            if result:
                findings[name] = result
        else:
            errors[name] = result
            
    return findings, errors

if __name__ == "__main__":
    if len(sys.argv) > 1:
        num = sys.argv[1]
        print(f"Testing lookup for: {num}")
        f, e = lookup_single(num)
        print("Findings:", f)
        print("Errors:", e)
    else:
        print("Usage: python service.py <phone>")
