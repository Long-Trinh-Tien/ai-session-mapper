import os
import json
import re
import datetime
from pathlib import Path

def get_time_ago(dt):
    now = datetime.datetime.now()
    diff = now - dt
    
    if diff.days > 0:
        return f"{diff.days}d ago"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours}h ago"
    minutes = (diff.seconds % 3600) // 60
    if minutes > 0:
        return f"{minutes}m ago"
    return "just now"

def get_gemini_sessions():
    results = []
    gemini_dir = Path.home() / ".gemini"
    projects_file = gemini_dir / "projects.json"
    sessions_dir = gemini_dir / "sessions"

    if projects_file.exists():
        try:
            with open(projects_file, 'r', encoding='utf-8') as f:
                projects = json.load(f)
                
                # Handle nested "projects" key if it exists
                if isinstance(projects, dict) and "projects" in projects:
                    projects_dict = projects["projects"]
                else:
                    projects_dict = projects
                
                # Check dict structure mapping session_id <-> path
                if isinstance(projects_dict, dict):
                    for k, v in projects_dict.items():
                        session_id = k
                        proj_path = v
                        # In case mapping is path -> session_id
                        if os.path.isabs(k) and not os.path.isabs(str(v)):
                            session_id = v
                            proj_path = k
                        
                        last_active = "Unknown"
                        
                        session_path_folder = sessions_dir / session_id
                        session_path_json = sessions_dir / f"{session_id}.json"
                        
                        if session_path_folder.exists() and session_path_folder.is_dir():
                            mtime = os.path.getmtime(session_path_folder)
                            dt = datetime.datetime.fromtimestamp(mtime)
                            last_active = get_time_ago(dt)
                        elif session_path_json.exists():
                            mtime = os.path.getmtime(session_path_json)
                            dt = datetime.datetime.fromtimestamp(mtime)
                            last_active = get_time_ago(dt)
                            
                        # Extract Session Name from the path
                        session_name = os.path.basename(proj_path)
                        if not session_name:
                            session_name = session_id
                            
                        results.append({
                            "Agent": "Gemini",
                            "Session Name": session_name,
                            "Project Directory": proj_path,
                            "Last Active": last_active
                        })
        except Exception as e:
            results.append({
                "Agent": "Gemini",
                "Session Name": "Error",
                "Project Directory": f"Could not parse projects.json: {e}",
                "Last Active": "-"
            })
    return results

def get_opencode_sessions():
    results = []
    
    appdata_dir = os.environ.get('APPDATA')
    if appdata_dir:
        opencode_dir = Path(appdata_dir) / "ai.opencode.desktop"
    else:
        opencode_dir = Path.home() / "AppData" / "Roaming" / "ai.opencode.desktop"
    
    global_dat = opencode_dir / "opencode.global.dat"
    if global_dat.exists():
        try:
            with open(global_dat, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            projects_str = data.get("globalSync.project")
            if projects_str:
                projects = json.loads(projects_str)
                if isinstance(projects, dict) and "value" in projects:
                    for p in projects["value"]:
                        worktree = p.get("worktree", "")
                        if not worktree or worktree == "/":
                            continue
                        
                        # Time comes as milliseconds
                        updated_ms = p.get("time", {}).get("updated", 0)
                        last_active = "Unknown"
                        if updated_ms:
                            dt = datetime.datetime.fromtimestamp(updated_ms / 1000.0)
                            last_active = get_time_ago(dt)
                            
                        session_name = os.path.basename(worktree)
                        if not session_name:
                            session_name = worktree
                            
                        results.append({
                            "Agent": "Opencode",
                            "Session Name": session_name,
                            "Project Directory": worktree,
                            "Last Active": last_active
                        })
        except Exception as e:
            pass

    return results

def main():
    print("[i] Scanning for AI Agent Logging Sessions (Gemini & Opencode)...")
    gemini_data = get_gemini_sessions()
    opencode_data = get_opencode_sessions()
    
    all_sessions = gemini_data + opencode_data
    
    if not all_sessions:
        print("[!] No sessions found on this machine.")
        return
        
    col_widths = {
        "Agent": 10,
        "Session Name": 18,
        "Project Directory": 20,
        "Last Active": 12
    }
    
    for row in all_sessions:
        col_widths["Agent"] = max(col_widths["Agent"], len(str(row["Agent"])))
        col_widths["Session Name"] = max(col_widths["Session Name"], len(str(row["Session Name"])))
        col_widths["Project Directory"] = max(col_widths["Project Directory"], len(str(row["Project Directory"])))
        col_widths["Last Active"] = max(col_widths["Last Active"], len(str(row["Last Active"])))
        
    def print_row(agent, sname, proj, active, sep=" | "):
        print(f"| {agent.ljust(col_widths['Agent'])}{sep}"
              f"{sname.ljust(col_widths['Session Name'])}{sep}"
              f"{proj.ljust(col_widths['Project Directory'])}{sep}"
              f"{active.ljust(col_widths['Last Active'])} |")
              
    separator_len = sum(col_widths.values()) + 13
    print("-" * separator_len)
    print_row("Agent", "Session Name", "Project Directory", "Last Active")
    print("-" * separator_len)
    
    for row in all_sessions:
        print_row(str(row["Agent"]), str(row["Session Name"]), str(row["Project Directory"]), str(row["Last Active"]))

    print("-" * separator_len)

if __name__ == "__main__":
    main()
