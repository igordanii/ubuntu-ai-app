# capture_utils.py
import subprocess
import tempfile
import os
import time
from shutil import which # For is_tool_available
import uuid # For unique IDs

def get_session_type():
    """Detects the current session type (e.g., 'x11', 'wayland')."""
    # XDG_SESSION_TYPE is the most standard way.
    # Fallback to 'x11' if it's not set, though on modern systems it usually is.
    return os.environ.get('XDG_SESSION_TYPE', 'x11').lower()

def is_tool_available(name):
    """Check whether `name` is on PATH and marked as executable."""
    return which(name) is not None

def capture_screen(full_screen=True, temp_dir=None):
    capture_id = str(uuid.uuid4()) # Generate a unique ID for this capture attempt
    print(f"[{capture_id}] ENTERING capture_screen: full_screen={full_screen}")

    session_type = get_session_type()
    print(f"[{capture_id}] Detected session type: {session_type}")

    temp_image_path = None # Ensure it's defined for cleanup in case of early exit
    tool_used = ""
    command = []

    try:
        # Create a temporary file that gnome-screenshot (or other tools) will write to.
        # mkstemp creates the file, so tools need write permission.
        # It returns a file descriptor (fd) and path. We close fd as Popen uses the path.
        fd, temp_image_path = tempfile.mkstemp(suffix=".png", dir=temp_dir)
        os.close(fd)

        if session_type == "wayland":
            if is_tool_available("gnome-screenshot"):
                tool_used = "gnome-screenshot"
                if full_screen:
                    command = ["gnome-screenshot", "-f", temp_image_path]
                else:
                    command = ["gnome-screenshot", "-a", "-f", temp_image_path]
            elif is_tool_available("grim") and (full_screen or is_tool_available("slurp")):
                tool_used = "grim/slurp"
                if full_screen:
                    command = ["grim", temp_image_path]
                else: # Area selection with grim/slurp
                    if not is_tool_available("slurp"):
                        print(f"[{capture_id}] Error: 'slurp' is required for area selection with 'grim' but not found.")
                        if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
                        return None
                    try:
                        slurp_process = subprocess.run("slurp", capture_output=True, text=True, check=True, timeout=30)
                        geometry = slurp_process.stdout.strip()
                        if not geometry:
                            print(f"[{capture_id}] Wayland selection with slurp cancelled or failed (no geometry).")
                            if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
                            return None
                        command = ["grim", "-g", geometry, temp_image_path]
                    except subprocess.TimeoutExpired:
                        print(f"[{capture_id}] Error: 'slurp' command timed out.")
                        if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
                        return None
                    except subprocess.CalledProcessError as e:
                        print(f"[{capture_id}] Error during slurp execution: {e.stderr}")
                        if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
                        return None
            else:
                print(f"[{capture_id}] Error: No suitable Wayland screenshot tool found (tried gnome-screenshot, grim/slurp).")
                if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
                return None

        elif session_type == "x11":
            if not is_tool_available("scrot"):
                print(f"[{capture_id}] Error: 'scrot' command not found for X11 session.")
                if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
                return None
            tool_used = "scrot"
            if full_screen:
                command = ["scrot", "-z", temp_image_path]
            else: # Area selection with scrot
                time.sleep(0.3) # Small delay for user to react before selection starts
                command = ["scrot", "-s", "-z", "-f", temp_image_path]
        else:
            print(f"[{capture_id}] Unsupported session type: {session_type}")
            if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
            return None

        if not command:
            print(f"[{capture_id}] Error: Could not determine screenshot command (should not happen if logic above is complete).")
            if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
            return None

        # Debug prints for environment variables (can be commented out if not needed)
        # print(f"[{capture_id}] Current LD_LIBRARY_PATH: {os.environ.get('LD_LIBRARY_PATH')}")
        # print(f"[{capture_id}] Current PYTHONHOME: {os.environ.get('PYTHONHOME')}")
        # print(f"[{capture_id}] Current PYTHONPATH: {os.environ.get('PYTHONPATH')}")

        print(f"[{capture_id}] Using tool: {tool_used}. Executing Popen for command: {' '.join(command)}")
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            stdout, stderr = process.communicate(timeout=60) # stdout and stderr are bytes
            return_code = process.returncode
        except subprocess.TimeoutExpired:
            process.kill() # Ensure process is killed
            # Try to communicate again to get any final output after kill
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
            # For gnome-screenshot, a return code of 0 should mean success.
            # However, we still check file existence and size as a safeguard.
            if os.path.exists(temp_image_path) and os.path.getsize(temp_image_path) > 0:
                print(f"[{capture_id}] Screenshot saved to: {temp_image_path}")
                if stdout_str: print(f"[{capture_id}] STDOUT from {tool_used} (RC=0): {stdout_str}")
                if stderr_str: print(f"[{capture_id}] STDERR from {tool_used} (RC=0): {stderr_str}") # Often empty on success
                return temp_image_path
            else:
                print(f"[{capture_id}] Error: Screenshot command ({tool_used}) executed with code 0 but no valid file was created or file is empty.")
                print(f"[{capture_id}] File path checked: {temp_image_path}")
                print(f"[{capture_id}] Exists: {os.path.exists(temp_image_path)}")
                if os.path.exists(temp_image_path):
                    print(f"[{capture_id}] Size: {os.path.getsize(temp_image_path)}")
                if stdout_str: print(f"[{capture_id}] STDOUT from {tool_used} (RC=0, but file issue): {stdout_str}")
                if stderr_str: print(f"[{capture_id}] STDERR from {tool_used} (RC=0, but file issue): {stderr_str}")
                if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
                return None
        else: # Non-zero return code
            print(f"[{capture_id}] Error: Screenshot command ({tool_used}) failed with return code {return_code}.")
            if stdout_str: print(f"[{capture_id}] STDOUT from {tool_used} (RC={return_code}): {stdout_str}")
            if stderr_str: print(f"[{capture_id}] STDERR from {tool_used} (RC={return_code}): {stderr_str}")
            if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
            return None

    except FileNotFoundError as e: # If Popen fails to find the command (should be caught by is_tool_available earlier)
        print(f"[{capture_id}] Error: Command '{command[0] if command else 'unknown'}' not found during Popen. {e}")
        if temp_image_path and os.path.exists(temp_image_path): os.remove(temp_image_path)
        return None
    except Exception as e: # Catch any other unexpected errors during capture
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