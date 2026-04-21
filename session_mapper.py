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

    dir_map = {}
    if projects_file.exists():
        try:
            with open(projects_file, 'r', encoding='utf-8') as f:
                projects = json.load(f)
                
                if isinstance(projects, dict) and "projects" in projects:
                    projects_dict = projects["projects"]
                else:
                    projects_dict = projects
                
                if isinstance(projects_dict, dict):
                    for k, v in projects_dict.items():
                        if os.path.isabs(k) and not os.path.isabs(str(v)):
                            dir_map[v] = k
                        else:
                            dir_map[k] = v
        except Exception as e:
            pass

    # Now search for actual sessions inside tmp/{project_id}/chats/session-*.json
    tmp_dir = gemini_dir / "tmp"
    if tmp_dir.exists():
        for proj_folder in tmp_dir.iterdir():
            if not proj_folder.is_dir(): continue
            chats_dir = proj_folder / "chats"
            if not chats_dir.exists(): continue
            
            project_id = proj_folder.name
            proj_path = dir_map.get(project_id, f"Unknown ({project_id})")
            
            for json_file in chats_dir.glob("session-*.json"):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        
                    sid = data.get("sessionId", "")
                    if not sid:
                        continue
                        
                    # Get title from summary or first message
                    session_name = data.get("summary")
                    if not session_name:
                        messages = data.get("messages", [])
                        if messages:
                            content = messages[0].get("content", [])
                            if isinstance(content, list) and len(content) > 0:
                                text = str(content[0].get("text", ""))
                                session_name = text[:40] + ("..." if len(text) > 40 else "")
                        
                    if not session_name:
                        session_name = "Untitled Session"
                        
                    # Time
                    last_active = "Unknown"
                    timestamp = 0
                    last_updated_str = data.get("lastUpdated")
                    if last_updated_str:
                        try:
                            last_updated_str = last_updated_str.replace("Z", "+00:00")
                            dt = datetime.datetime.fromisoformat(last_updated_str)
                            # Convert to naive local time for get_time_ago
                            dt_local = dt.astimezone()
                            dt_naive = dt_local.replace(tzinfo=None)
                            timestamp = dt_local.timestamp()
                            last_active = get_time_ago(dt_naive)
                        except Exception:
                            pass
                            
                    if timestamp == 0:
                        mtime = os.path.getmtime(json_file)
                        timestamp = mtime
                        last_active = get_time_ago(datetime.datetime.fromtimestamp(mtime))
                        
                    results.append({
                        "Agent": "Gemini",
                        "Session Name": session_name,
                        "Project Directory": proj_path,
                        "Last Active": last_active,
                        "timestamp": timestamp,
                        "session_id": sid
                    })
                except Exception:
                    pass

    return results

def get_opencode_sessions():
    results = []
    
    # 1. Try SQLite Database (Linux/macOS/Windows)
    db_candidates = [
        Path.home() / ".local" / "share" / "opencode" / "opencode.db",
        Path.home() / ".config" / "opencode" / "opencode.db",
        Path(os.environ.get('APPDATA', '')) / "ai.opencode.desktop" / "opencode.db" if os.environ.get('APPDATA') else None,
    ]
    
    for db_path in filter(None, db_candidates):
        if db_path.exists():
            try:
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT id, title, directory, time_updated FROM session")
                rows = cursor.fetchall()
                conn.close()
                
                for sid, title, directory, updated_ms in rows:
                    if not directory or directory == "/":
                        directory = "Unknown"
                    
                    last_active = "Unknown"
                    timestamp = 0
                    if updated_ms:
                        timestamp = updated_ms / 1000.0
                        dt = datetime.datetime.fromtimestamp(timestamp)
                        last_active = get_time_ago(dt)
                    
                    session_name = title if title else sid
                    if not session_name:
                        session_name = directory
                        
                    results.append({
                        "Agent": "Opencode",
                        "Session Name": session_name,
                        "Project Directory": directory,
                        "Last Active": last_active,
                        "timestamp": timestamp,
                        "session_id": sid
                    })
                if results:
                    return results
            except Exception as e:
                pass

    # 2. Fallback to opencode.global.dat (Legacy/Windows)
    candidates = []
    appdata = os.environ.get('APPDATA')
    if appdata:
        candidates.append(Path(appdata) / "ai.opencode.desktop")
    candidates.append(Path.home() / "AppData" / "Roaming" / "ai.opencode.desktop")
    candidates.append(Path.home() / ".config" / "ai.opencode.desktop")
    candidates.append(Path.home() / ".local" / "share" / "ai.opencode.desktop")
    candidates.append(Path.home() / "Library" / "Application Support" / "ai.opencode.desktop")
    
    opencode_dir = None
    for cand in candidates:
        if cand.exists() and cand.is_dir():
            opencode_dir = cand
            break
            
    if opencode_dir:
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
                            
                            updated_ms = p.get("time", {}).get("updated", 0)
                            last_active = "Unknown"
                            timestamp = 0
                            if updated_ms:
                                timestamp = updated_ms / 1000.0
                                dt = datetime.datetime.fromtimestamp(timestamp)
                                last_active = get_time_ago(dt)
                                
                            session_name = os.path.basename(worktree)
                            if not session_name:
                                session_name = worktree
                                
                            results.append({
                                "Agent": "Opencode",
                                "Session Name": session_name,
                                "Project Directory": worktree,
                                "Last Active": last_active,
                                "timestamp": timestamp,
                                "session_id": p.get("id", worktree)
                            })
            except Exception as e:
                pass
    
    return results



import math
import subprocess

def resume_session(session):
    agent = session["Agent"]
    proj_dir = session["Project Directory"]
    
    print(f"\n🚀 Resuming {agent} session in: {proj_dir}\n")
    
    try:
        if agent == "Gemini":
            # Resume Gemini with session ID if available, otherwise fallback to latest
            sid = session.get("session_id")
            cmd = "gemini.cmd" if os.name == 'nt' else "gemini"
            if sid:
                subprocess.run([cmd, "--resume", sid], cwd=proj_dir)
            else:
                subprocess.run([cmd, "--resume", "latest"], cwd=proj_dir)
        elif agent == "Opencode":
            # Resume Opencode with session ID
            sid = session.get("session_id")
            cmd = "opencode-cli.exe" if os.name == 'nt' else "opencode"
            if sid:
                subprocess.run([cmd, "-s", sid])
            else:
                subprocess.run([cmd, proj_dir])
    except FileNotFoundError:
        print(f"[!] '{agent.lower()}' executable not found in PATH. Make sure it is installed.")
    except Exception as e:
        print(f"[!] Error resuming session: {e}")

def main():
    print("[i] Scanning for AI Agent Logging Sessions (Gemini & Opencode)...")
    gemini_data = get_gemini_sessions()
    opencode_data = get_opencode_sessions()
    
    all_sessions = gemini_data + opencode_data
    
    if not all_sessions:
        print("[!] No sessions found on this machine.")
        return

    # Sort by recency (timestamp descending)
    all_sessions.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
    
    current_filter = "all"
    page = 0
    page_size = 10
    
    # Enable ANSI escape sequences on Windows
    if os.name == 'nt':
        os.system('')
        
    RESET = "\033[0m"
    BOLD = "\033[1m"
    CYAN = "\033[36m"
    MAGENTA = "\033[35m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    DIM = "\033[2m"
    
    while True:
        # Apply filter
        if current_filter == "gemini":
            filtered_sessions = [s for s in all_sessions if s["Agent"] == "Gemini"]
        elif current_filter == "opencode":
            filtered_sessions = [s for s in all_sessions if s["Agent"] == "Opencode"]
        else:
            filtered_sessions = all_sessions

        if not filtered_sessions:
            print("\n[!] No sessions match the current filter.")
            # Let user change filter or quit
            choice = input("\nFilter: [g] Gemini, [o] Opencode, [a] All, [q] Quit: ").strip().lower()
            if choice == 'q': break
            elif choice == 'g': current_filter = "gemini"; continue
            elif choice == 'o': current_filter = "opencode"; continue
            elif choice == 'a': current_filter = "all"; continue
            else: continue

        total_pages = math.ceil(len(filtered_sessions) / page_size)
        if page >= total_pages:
            page = 0
            
        print("\n" + "="*80)
        filter_text = f" Filter: {current_filter.capitalize()}" if current_filter != "all" else ""
        print(f"📄 Page {page + 1} of {total_pages} {filter_text}")
        print("="*80)
        
        start_idx = page * page_size
        end_idx = start_idx + page_size
        current_page_sessions = filtered_sessions[start_idx:end_idx]
        
        col_widths = {
            "Idx": 3,
            "Agent": 8,
            "Session ID": 12,
            "Session Name": 12,
            "Project Directory": 17,
            "Last Active": 11
        }
        
        max_sname_len = 50
        max_proj_len = 45
        
        def truncate(text, max_len):
            return text[:max_len-3] + "..." if len(text) > max_len else text
        
        for row in current_page_sessions:
            sname_trunc = truncate(str(row["Session Name"]), max_sname_len)
            proj_trunc = truncate(str(row["Project Directory"]), max_proj_len)
            row["_sname_trunc"] = sname_trunc
            row["_proj_trunc"] = proj_trunc
            
            col_widths["Agent"] = max(col_widths["Agent"], len(str(row["Agent"])))
            sid_str = str(row.get("session_id", ""))[:12] if row.get("session_id") else ""
            col_widths["Session ID"] = max(col_widths["Session ID"], len(sid_str))
            col_widths["Session Name"] = max(col_widths["Session Name"], len(sname_trunc))
            col_widths["Project Directory"] = max(col_widths["Project Directory"], len(proj_trunc))
            col_widths["Last Active"] = max(col_widths["Last Active"], len(str(row["Last Active"])))
            
        def print_row(idx, agent, sid, sname, proj, active, is_header=False):
            c_idx = idx.ljust(col_widths['Idx'])
            c_agent = agent.ljust(col_widths['Agent'])
            c_sid = sid.ljust(col_widths['Session ID'])
            c_sname = sname.ljust(col_widths['Session Name'])
            c_proj = proj.ljust(col_widths['Project Directory'])
            c_active = active.ljust(col_widths['Last Active'])
            
            if is_header:
                print(f" {BOLD}{c_idx}  {c_agent}  {c_sid}  {c_sname}  {c_proj}  {c_active}{RESET}")
            else:
                agent_c = CYAN if agent == "Gemini" else MAGENTA
                print(f" {YELLOW}{c_idx}{RESET}  {agent_c}{c_agent}{RESET}  {DIM}{c_sid}{RESET}  {c_sname}  {DIM}{c_proj}{RESET}  {GREEN}{c_active}{RESET}")
                   
        separator_len = sum(col_widths.values()) + 11
        print("─" * separator_len)
        print_row("Idx", "Agent", "Session ID", "Session Name", "Project Directory", "Last Active", is_header=True)
        print("─" * separator_len)
        
        for i, row in enumerate(current_page_sessions):
            global_idx = start_idx + i
            sid_str = str(row.get("session_id", ""))[:12] if row.get("session_id") else "None"
            print_row(str(global_idx), str(row["Agent"]), sid_str, row["_sname_trunc"], row["_proj_trunc"], str(row["Last Active"]))
        
        print("─" * separator_len)
        
        print("\nCommands:")
        print("  [0-9] Resume the session by index")
        print("  [g]   Filter Gemini sessions")
        print("  [o]   Filter Opencode sessions")
        print("  [a]   Show all sessions")
        if page < total_pages - 1:
            print("  [n]   Next page")
        if page > 0:
            print("  [p]   Previous page")
        print("  [q]   Quit")
        
        choice = input("\nSelect an option: ").strip().lower()
        if choice == 'q':
            print("Goodbye!")
            break
        elif choice == 'g':
            current_filter = "gemini"
            page = 0
        elif choice == 'o':
            current_filter = "opencode"
            page = 0
        elif choice == 'a':
            current_filter = "all"
            page = 0
        elif choice == 'n' and page < total_pages - 1:
            page += 1
        elif choice == 'p' and page > 0:
            page -= 1
        elif choice.isdigit():
            idx = int(choice)
            if 0 <= idx < len(filtered_sessions):
                session = filtered_sessions[idx]
                resume_session(session)
                break
            else:
                print(f"[!] Invalid index. Please select a number between 0 and {len(filtered_sessions)-1}.")
        else:
            print("[!] Invalid command.")

if __name__ == "__main__":
    main()
