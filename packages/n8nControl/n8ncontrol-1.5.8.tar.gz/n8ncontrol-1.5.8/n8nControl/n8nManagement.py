import os
import subprocess
import time
import shutil
import tempfile
import urllib.request
from n8nControl.response import appResponse
from fastapi import HTTPException
import sqlite3, json, time, os
import uuid

class N8nManagement:
    container_name = "n8n"
    db_path = "/root/n8n/database.sqlite"
    def __init__(self,):
        print("N8nManagement initialized")

    
    def import_workflow(self, file_remote):
        try:
            filename = os.path.basename(file_remote)
            container_upload_dir = "/home/node/.n8n/uploads"
            container_file_path = f"{container_upload_dir}/{filename}"
            # use a temporary path inside the container (not the uploads bind mount)
            container_tmp_path = f"/tmp/{filename}"

            check_dir_cmd = [
                "docker", "exec", self.container_name,
                "sh", "-c",
                f"if [ ! -d '{container_upload_dir}' ]; then mkdir -p '{container_upload_dir}' && chmod -R 777 '{container_upload_dir}'; fi"
            ]
            subprocess.run(check_dir_cmd, check=True)
        
            # Copy file into container /tmp to avoid permission problems on bind mounts
            copy_cmd = ["docker", "cp", file_remote, f"{self.container_name}:{container_tmp_path}"]
            subprocess.run(copy_cmd, check=True)

            subprocess.run([
                "docker", "exec", self.container_name,
                "sh", "-c",
                f"chmod 644 '{container_tmp_path}'"
            ], check=False)

            subprocess.run([
                "docker", "exec", "--user", "root", self.container_name,
                "sh", "-c",
                f"chown node:node '{container_tmp_path}'"
            ], check=False)
            

            cmd = [
                "docker", "exec", self.container_name,
                "n8n", "import:workflow",
                f"--input={container_tmp_path}",
                "--overwrite"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print("import_workflow stdout:", result.stdout)
                print("import_workflow stderr:", result.stderr)
                raise HTTPException(status_code=500, detail=f"n8n import failed: {result.stderr.strip()}")

            return appResponse.AppResponse("success", "Import workflow success", None)
        except Exception as e:
            print(f"❌ import_workflow failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))


    def export_workflow(self):
        try:
            conn =sqlite3.connect(self.db_path)
            cursor =conn.cursor()
            cursor.execute("SELECT id, name, nodes, connections FROM workflow_entity")
            rows = cursor.fetchall()
            conn.close()
            workFlows =[]
            for row in rows:
                workFlows.append({
                    "id": row[0],
                    "name": row[1],
                    "nodes": json.loads(row[2]),
                    "connections": json.loads(row[3]),
                })
            export_dir = "/root/n8n_exports"
            os.makedirs(export_dir, exist_ok=True)
            file_name = f"workflows-db-{int(time.time())}.json"
            file_path = os.path.join(export_dir, file_name)

            with open(file_path, "w") as f:
                json.dump(workFlows, f, indent=2)

            return {"filePath": file_path, "filename": file_name}
        except Exception as e:
            print(f"❌ n8n export failed: {e}")
            raise HTTPException(status_code=500, detail="n8n export failed")

    # def import_workflows_to_db(self, file_remote):
    #     """Import workflows from a JSON file (or URL or directory) into the workflow_entity table.

    #     file_remote may be:
    #     - a local file path
    #     - a directory path (the newest regular file inside will be used)
    #     - an http/https URL
    #     """
    #     temp_dir = None
    #     try:
    #         # Resolve source path (support URL and directory)
    #         source_path = file_remote
    #         if isinstance(file_remote, str) and (file_remote.startswith("http://") or file_remote.startswith("https://")):
    #             temp_dir = tempfile.mkdtemp()
    #             filename = os.path.basename(file_remote)
    #             temp_file_path = os.path.join(temp_dir, filename)
    #             urllib.request.urlretrieve(file_remote, temp_file_path)
    #             source_path = temp_file_path
    #         elif os.path.isdir(file_remote):
    #             entries = [os.path.join(file_remote, p) for p in os.listdir(file_remote)]
    #             files = [p for p in entries if os.path.isfile(p)]
    #             if not files:
    #                 raise HTTPException(status_code=400, detail=f"No files found in directory: {file_remote}")
    #             files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    #             source_path = files[0]

    #         # Read JSON
    #         with open(source_path, "r", encoding="utf-8") as f:
    #             data = json.load(f)

    #         # Normalize different JSON shapes into a list of workflow dicts:
    #         # - list of workflows
    #         # - single workflow object -> wrap into list
    #         # - object with key "workflows" or "data" containing a list -> use that list
    #         # - mapping id -> workflow (values are dicts) -> take values()
    #         workflows = None
    #         if isinstance(data, list):
    #             workflows = data
    #         elif isinstance(data, dict):
    #             # common envelope
    #             if "workflows" in data and isinstance(data["workflows"], list):
    #                 workflows = data["workflows"]
    #             elif "data" in data and isinstance(data["data"], list):
    #                 workflows = data["data"]
    #             # single workflow object
    #             elif any(k in data for k in ("id", "nodes", "connections", "name")):
    #                 workflows = [data]
    #             # mapping of id->workflow objects
    #             elif all(isinstance(v, dict) for v in data.values()):
    #                 workflows = list(data.values())
    #             else:
    #                 raise HTTPException(status_code=400, detail="Unrecognized JSON structure for workflows")
    #         else:
    #             raise HTTPException(status_code=400, detail="Unrecognized JSON structure for workflows")

    #         conn = sqlite3.connect(self.db_path)
    #         cursor = conn.cursor()

    #         cursor.execute("PRAGMA table_info(workflow_entity)")
    #         table_info = cursor.fetchall()
    #         table_cols = [row[1] for row in table_info]

    #         for wf in workflows:
    #             wf_id = wf.get("id") or str(uuid.uuid4())

    #             # Build record dict based on available table columns
    #             record = {"id": wf_id}
    #             if "name" in table_cols:
    #                 record["name"] = wf.get("name") or ""
    #             if "nodes" in table_cols:
    #                 record["nodes"] = json.dumps(wf.get("nodes") or [])
    #             if "connections" in table_cols:
    #                 record["connections"] = json.dumps(wf.get("connections") or {})
    #             # Provide sensible defaults for common additional fields
    #             if "active" in table_cols:
    #                 record["active"] = wf.get("active", 1)
    #             # timestamps: prefer integer unix time
    #             now_ts = int(time.time())
    #             if "createdAt" in table_cols and "createdAt" not in record:
    #                 record["createdAt"] = wf.get("createdAt", now_ts)
    #             if "created_at" in table_cols and "created_at" not in record:
    #                 record["created_at"] = wf.get("created_at", now_ts)
    #             if "updatedAt" in table_cols:
    #                 record["updatedAt"] = wf.get("updatedAt", now_ts)
    #             if "updated_at" in table_cols:
    #                 record["updated_at"] = wf.get("updated_at", now_ts)

    #             # Upsert dynamically using available columns
    #             cursor.execute("SELECT COUNT(1) FROM workflow_entity WHERE id = ?", (wf_id,))
    #             exists = cursor.fetchone()[0]
    #             if exists:
    #                 set_cols = [c for c in record.keys() if c != "id"]
    #                 if set_cols:
    #                     set_clause = ", ".join([f"{c} = ?" for c in set_cols])
    #                     values = [record[c] for c in set_cols] + [wf_id]
    #                     sql = f"UPDATE workflow_entity SET {set_clause} WHERE id = ?"
    #                     cursor.execute(sql, values)
    #             else:
    #                 cols = list(record.keys())
    #                 placeholders = ", ".join(["?" for _ in cols])
    #                 sql = f"INSERT INTO workflow_entity ({', '.join(cols)}) VALUES ({placeholders})"
    #                 values = [record[c] for c in cols]
    #                 cursor.execute(sql, values)

    #         conn.commit()
    #         conn.close()

    #         return appResponse.AppResponse("success", "Imported workflows into database", None)

    #     except HTTPException:
    #         raise
    #     except Exception as e:
    #         print(f"❌ import_workflows_to_db failed: {e}")
    #         raise HTTPException(status_code=500, detail=str(e))
    #     finally:
    #         if temp_dir:
    #             try:
    #                 shutil.rmtree(temp_dir)
    #             except Exception:
    #                 pass

    # def import_workflows_via_cli(self, file_remote):
    #     """Import workflows using the n8n CLI inside the container.

    #     - Supports local file path, directory (newest file), or http/https URL.
    #     - If the JSON is a list, each element will be imported individually.
    #     - Returns a summary dict with per-file import stdout/stderr.
    #     """
    #     temp_dir = None
    #     results = []
    #     try:
    #         # Resolve source_path (support URL and directory)
    #         source_path = file_remote
    #         if isinstance(file_remote, str) and (file_remote.startswith("http://") or file_remote.startswith("https://")):
    #             temp_dir = tempfile.mkdtemp()
    #             filename = os.path.basename(file_remote) or "download.json"
    #             temp_file_path = os.path.join(temp_dir, filename)
    #             urllib.request.urlretrieve(file_remote, temp_file_path)
    #             source_path = temp_file_path
    #         elif os.path.isdir(file_remote):
    #             entries = [os.path.join(file_remote, p) for p in os.listdir(file_remote)]
    #             files = [p for p in entries if os.path.isfile(p)]
    #             if not files:
    #                 raise HTTPException(status_code=400, detail=f"No files found in directory: {file_remote}")
    #             files.sort(key=lambda p: os.path.getmtime(p), reverse=True)
    #             source_path = files[0]

    #         # Try to load JSON to decide behavior (list -> split, object -> import as-is)
    #         try:
    #             with open(source_path, "r", encoding="utf-8") as f:
    #                 data = json.load(f)
    #         except Exception:
    #             # If cannot parse as JSON, attempt to import the file as-is
    #             data = None

    #         files_to_import = []
    #         if isinstance(data, list):
    #             # create one temp file per workflow
    #             if temp_dir is None:
    #                 temp_dir = tempfile.mkdtemp()
    #             for idx, item in enumerate(data):
    #                 tmp_name = f"workflow_{idx}_{int(time.time())}.json"
    #                 tmp_path = os.path.join(temp_dir, tmp_name)
    #                 with open(tmp_path, "w", encoding="utf-8") as tf:
    #                     json.dump(item, tf)
    #                 files_to_import.append(tmp_path)
    #         elif isinstance(data, dict):
    #             # single object -> import the source file as-is
    #             files_to_import.append(source_path)
    #         else:
    #             # unknown or non-json -> import the source file as-is
    #             files_to_import.append(source_path)

    #         for local_path in files_to_import:
    #             filename = os.path.basename(local_path)
    #             container_tmp = f"/tmp/{filename}"
    #             # copy into container
    #             subprocess.run(["docker", "cp", local_path, f"{self.container_name}:{container_tmp}"], check=True)

    #             # attempt to chmod/chown inside tmp (non-fatal)
    #             subprocess.run(["docker", "exec", self.container_name, "sh", "-c", f"chmod 644 '{container_tmp}'"], check=False)
    #             subprocess.run(["docker", "exec", "--user", "root", self.container_name, "sh", "-c", f"chown node:node '{container_tmp}'"], check=False)

    #             # run n8n import CLI
    #             cmd = ["docker", "exec", self.container_name, "n8n", "import:workflow", f"--input={container_tmp}", "--overwrite"]
    #             proc = subprocess.run(cmd, capture_output=True, text=True)
    #             results.append({
    #                 "file": filename,
    #                 "returncode": proc.returncode,
    #                 "stdout": proc.stdout,
    #                 "stderr": proc.stderr,
    #             })

    #         # if any failed, return details with 500
    #         failed = [r for r in results if r["returncode"] != 0]
    #         if failed:
    #             msg = "; ".join([f"{f['file']}: {f['stderr'].strip()}" for f in failed])
    #             print("import_workflows_via_cli results:", results)
    #             raise HTTPException(status_code=500, detail=msg)

    #         return appResponse.AppResponse("success", "Imported workflows via n8n CLI", {"results": results})

    #     except HTTPException:
    #         raise
    #     except Exception as e:
    #         print(f"❌ import_workflows_via_cli failed: {e}")
    #         raise HTTPException(status_code=500, detail=str(e))
    #     finally:
    #         if temp_dir:
    #             try:
    #                 shutil.rmtree(temp_dir)
    #             except Exception:
    #                 pass

    def change_domain(self,new_domain):
        nginx_conf = f"""
server {{
    listen 80 default_server;
    server_name _;

    return 444;
}}

server {{
    listen 80;
    server_name {new_domain};

    location / {{
        proxy_pass http://127.0.0.1:5678;
        proxy_http_version 1.1;

        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }}
}}
""".strip()

        remote_path = "/etc/nginx/conf.d/n8n.conf"

        try:
            with open(remote_path, "w") as f:
                f.write(nginx_conf)

            subprocess.run(["nginx", "-t"], check=True)
            subprocess.run(["systemctl", "reload", "nginx"], check=True)

            return appResponse.AppResponse("success", "Domain changed successfully", None)

        except Exception as e:
            print(f"❌ changeDomain failed: {e}")

    def reset_user_info(self):
        try:
            result = subprocess.run(
                ["docker", "exec", "-i", self.container_name, "n8n", "user-management:reset"],
                capture_output=True,
                text=True,
                check=True
            )

            print("stdout:", result.stdout)
            print("stderr:", result.stderr)
            subprocess.run(["docker", "restart", self.container_name], check=True)

            return appResponse.AppResponse("success", "Reset user info successfully", None)
        except Exception as e:
            print(f"❌ n8n export failed: {e}")
            raise HTTPException(status_code=500, detail="reset failed")

    def update_version(self,version):
        try:
            print(f"🆙 Updating n8n to version {version}")
            subprocess.run(["docker", "pull", f"n8nio/n8n:{version}"], check=True)

            subprocess.run(["docker", "stop", self.container_name], check=True)

            subprocess.run([
            "docker", "run", "-d",
            "--name", f"{self.container_name}_new",
            "--restart=always",
            "-p", "5678:5678",
            "-v", "/root/n8n:/home/node/.n8n",
            f"n8nio/n8n:{version}"
            ], check=True)
            subprocess.run(["docker", "rm", self.container_name], check=False)

            subprocess.run(["docker", "rename", f"{self.container_name}_new", self.container_name], check=True)

            return appResponse.AppResponse("success", f"Updated n8n to version {version}", None)
        except Exception as e:
            print(f"❌ update_version failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
