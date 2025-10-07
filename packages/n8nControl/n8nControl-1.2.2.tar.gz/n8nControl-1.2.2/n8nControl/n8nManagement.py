import os
import subprocess
import time
import shutil
from n8nControl.response import appResponse
from fastapi import HTTPException
import sqlite3, json, time, os

class N8nManagement:
    db_path = "/root/.n8n/database.sqlite"
    def __init__(self,):
        print("N8nManagement initialized")

    
    def import_workflow(self,file_path,file_remote_name=None):
        try:
            if file_remote_name:
                remote_path = f"/root/{file_remote_name}"
                # Copy file lên đúng vị trí nếu cần
                if file_path != remote_path:
                    subprocess.run(["cp", file_path,  remote_path], check=True)
            else:
                remote_path = file_path

            # Import workflow vào n8n
            subprocess.run([
                "/usr/bin/node", "/usr/bin/n8n", "import:workflow", f"--input={remote_path}", "--overwrite"
            ], check=True,env={**os.environ, "N8N_USER_FOLDER": "/root/.n8n"})
            return appResponse.AppResponse("success", "Import data success", None)
        except Exception as e:
            print(f"❌ n8n export failed: {e}")
            raise HTTPException(status_code=500, detail="n8n export failed")


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
            conn =sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM user;")

            cursor.execute("DELETE FROM settings WHERE key='userManagement.isInstanceOwnerSet';")

            conn.commit()
            conn.close()
            cmd = "pm2 stop n8n || true && rm -rf /root/.n8n && pm2 start n8n && pm2 restart n8n"
            subprocess.run(['bash', '-lc', cmd], check=True)
            return appResponse.AppResponse("success", "Delete database success", None)
        except Exception as e:
            print(f"❌ n8n export failed: {e}")
            raise HTTPException(status_code=500, detail="reset failed")

    def update_version(self,new_version):
        print(f"Updating version to {new_version}")
