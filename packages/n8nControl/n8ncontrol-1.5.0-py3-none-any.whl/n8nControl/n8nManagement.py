import os
import subprocess
import time
import shutil
import tempfile
import urllib.request
from n8nControl.response import appResponse
from fastapi import HTTPException
import sqlite3, json, time, os

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

            check_dir_cmd = [
                "docker", "exec", self.container_name,
                "sh", "-c",
                f"if [ ! -d '{container_upload_dir}' ]; then mkdir -p '{container_upload_dir}' && chmod -R 777 '{container_upload_dir}'; fi"
            ]
            subprocess.run(check_dir_cmd, check=True)
            source_path = file_remote
            temp_dir = None
            if isinstance(file_remote, str) and (file_remote.startswith("http://") or file_remote.startswith("https://")):
                temp_dir = tempfile.mkdtemp()
                temp_file_path = os.path.join(temp_dir, filename)
                urllib.request.urlretrieve(file_remote, temp_file_path)
                source_path = temp_file_path

            source_path = os.path.abspath(source_path)

            copy_cmd = ["docker", "cp", source_path, f"{self.container_name}:{container_file_path}"]
            subprocess.run(copy_cmd, check=True)

        
            cmd = [
                "docker", "exec", self.container_name,
                "n8n", "import:workflow",
                f"--input={container_file_path}",
                "--overwrite"
            ]
            subprocess.run(cmd, check=True)

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
