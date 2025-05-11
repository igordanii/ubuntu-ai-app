# capture_utils.py
import subprocess
import tempfile
import os
import time
from shutil import which
import uuid

def get_session_type():
    return os.environ.get('XDG_SESSION_TYPE', 'x11').lower()

def is_tool_available(name):
    return which(name) is not None

def capture_screen(full_screen=True, temp_dir=None):
    capture_id = str(uuid.uuid4())
    print(f"[{capture_id}] ENTERING capture_screen: full_screen={full_screen}")

    session_type = get_session_type()
    print(f"[{capture_id}] Detected session type: {session_type}")

    temp_image_path = None
    tool_used = ""
    command = []

    try:
        fd, temp_image_path = tempfile.mkstemp(suffix=".png", dir=temp_dir)
        os.close(fd)

        # --- Determine command (same logic as before) ---
        if session_type == "wayland":
            if is_tool_available("gnome-screenshot"):
                tool_used = "gnome-screenshot"
                if full_screen:
                    command = ["gnome-screenshot", "-f", temp_image_path]
                else:
                    command = ["gnome-screenshot", "-a", "-f", temp_image_path]
            # ... (elif for grim/slurp - truncated for brevity, keep your existing logic) ...
            else:
                print(f"[{capture_id}] Error: No suitable Wayland screenshot tool found.")
                if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
                return None
        elif session_type == "x11":
            if is_tool_available("scrot"):
                tool_used = "scrot"
                if full_screen:
                    command = ["scrot", "-z", temp_image_path]
                else:
                    time.sleep(0.3)
                    command = ["scrot", "-s", "-z", "-f", temp_image_path]
            # ... (else for no X11 tool - truncated, keep your existing logic) ...
            else:
                print(f"[{capture_id}] Error: No suitable X11 screenshot tool found.")
                if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
                return None
        else:
            print(f"[{capture_id}] Unsupported session type: {session_type}")
            if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
            return None

        if not command:
            print(f"[{capture_id}] Error: Could not determine screenshot command.")
            if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
            return None

        # --- Create a Sanitized Environment for Popen ---
        clean_env = {}
        # Essential for finding system commands and for GUI apps to connect to display server
        essential_vars = ['PATH', 'HOME', 'DISPLAY', 'XAUTHORITY', 'XDG_RUNTIME_DIR', 'WAYLAND_DISPLAY', 'DBUS_SESSION_BUS_ADDRESS']
        
        # Ensure a minimal, standard PATH. Crucially, do NOT include Snap paths if they were in os.environ['PATH']
        # You might want to be even more restrictive, e.g., PATH="/usr/bin:/bin"
        system_paths = [p for p in os.environ.get('PATH', '').split(os.pathsep) if not p.startswith('/snap/')]
        clean_env['PATH'] = os.pathsep.join(system_paths) if system_paths else "/usr/local/bin:/usr/bin:/bin"
        if '/usr/bin' not in clean_env['PATH'].split(os.pathsep): # Ensure /usr/bin is present
             clean_env['PATH'] = f"/usr/bin:{clean_env['PATH']}"


        for var_name in essential_vars:
            if var_name == 'PATH': continue # Already handled
            if var_name in os.environ:
                clean_env[var_name] = os.environ[var_name]
        
        # Explicitly unset/remove variables known to be set by Snap environments
        # that might cause issues if they somehow still linger.
        # This is more of a precaution.
        vars_to_remove_if_present = ['SNAP', 'SNAP_ARCH', 'SNAP_COMMON', 'SNAP_CONTEXT', 
                                     'SNAP_DATA', 'SNAP_INSTANCE_KEY', 'SNAP_INSTANCE_NAME',
                                     'SNAP_LIBRARY_PATH', 'SNAP_NAME', 'SNAP_REEXEC', 
                                     'SNAP_REVISION', 'SNAP_USER_COMMON', 'SNAP_USER_DATA', 
                                     'SNAP_VERSION', 'LD_PRELOAD'] # LD_PRELOAD can also cause issues
        
        # The clean_env starts empty, so we don't need to remove from it,
        # but this illustrates variables you'd want to avoid copying from os.environ.

        print(f"[{capture_id}] Using tool: {tool_used}. Executing Popen with command: {' '.join(command)}")
        print(f"[{capture_id}] Using sanitized PATH: {clean_env.get('PATH')}")
        # print(f"[{capture_id}] Full sanitized env: {clean_env}") # For deep debugging

        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=clean_env) # Pass the sanitized env
        try:
            stdout, stderr = process.communicate(timeout=60)
            return_code = process.returncode
        except subprocess.TimeoutExpired:
            process.kill()
            stdout_t, stderr_t = process.communicate()
            print(f"[{capture_id}] Error: Screenshot command ({tool_used}) timed out.")
            if stdout_t: print(f"[{capture_id}] STDOUT on timeout: {stdout_t.decode(errors='ignore')}")
            if stderr_t: print(f"[{capture_id}] STDERR on timeout: {stderr_t.decode(errors='ignore')}")
            if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
            return None

        print(f"[{capture_id}] Command finished. Tool: {tool_used}, Return Code: {return_code}")
        
        stdout_str = stdout.decode(errors='ignore').strip()
        stderr_str = stderr.decode(errors='ignore').strip()

        if return_code == 0:
            if os.path.exists(temp_image_path) and os.path.getsize(temp_image_path) > 0:
                print(f"[{capture_id}] Screenshot saved to: {temp_image_path}")
                if stdout_str: print(f"[{capture_id}] STDOUT from {tool_used} (RC=0): {stdout_str}")
                if stderr_str: print(f"[{capture_id}] STDERR from {tool_used} (RC=0): {stderr_str}")
                return temp_image_path
            else:
                # ... (error handling for RC=0 but bad file, same as before, include stdout_str/stderr_str) ...
                print(f"[{capture_id}] Error: Screenshot command ({tool_used}) executed with code 0 but no valid file was created or file is empty.")
                # ... (print file path, exists, size)
                if stdout_str: print(f"[{capture_id}] STDOUT from {tool_used} (RC=0, but file issue): {stdout_str}")
                if stderr_str: print(f"[{capture_id}] STDERR from {tool_used} (RC=0, but file issue): {stderr_str}")
                if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
                return None
        else:
            # ... (error handling for non-zero RC, same as before, include stdout_str/stderr_str) ...
            print(f"[{capture_id}] Error: Screenshot command ({tool_used}) failed with return code {return_code}.")
            if stdout_str: print(f"[{capture_id}] STDOUT from {tool_used} (RC={return_code}): {stdout_str}")
            if stderr_str: print(f"[{capture_id}] STDERR from {tool_used} (RC={return_code}): {stderr_str}")
            if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
            return None

    except Exception as e:
        print(f"[{capture_id}] An unexpected error occurred in capture_screen: {e}")
        import traceback
        traceback.print_exc()
        if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
        return None

if __name__ == '__main__':
    print("Testing capture_utils.py directly...")

    print("\n--- Test 1: Full Screen Capture ---")
    # You might want to create a dedicated temporary directory for testing artifacts
    test_temp_dir = "capture_test_temp_files"
    os.makedirs(test_temp_dir, exist_ok=True)
    print(f"Test temporary files will be in ./{test_temp_dir}/")

    full_screen_path = capture_screen(full_screen=True, temp_dir=test_temp_dir)
    if full_screen_path:
        print(f"SUCCESS: Full screen capture test. Image at: {full_screen_path}")
        # os.remove(full_screen_path) # Clean up test file
    else:
        print("FAILED: Full screen capture test.")

    print("\n--- Test 2: Selected Area Capture ---")
    selected_area_path = capture_screen(full_screen=False, temp_dir=test_temp_dir)
    if selected_area_path:
        print(f"SUCCESS: Selected area capture test. Image at: {selected_area_path}")
        # os.remove(selected_area_path) # Clean up test file
    else:
        print("FAILED: Selected area capture test (or cancelled by user).")
    
    print(f"\nTest finished. Check ./{test_temp_dir}/ for any created image files if not auto-deleted.")