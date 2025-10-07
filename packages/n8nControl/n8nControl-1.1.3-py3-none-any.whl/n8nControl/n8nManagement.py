import os
import subprocess
import time
import shutil
from n8nControl.response import appResponse
from fastapi import HTTPException
class N8nManagement:
    def __init__(self):
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
                "n8n", "import:workflow", f"--input={remote_path}", "--overwrite"
            ], check=True,env={**os.environ, "N8N_USER_FOLDER": "/root/.n8n"})
            return appResponse.AppResponse("success", "Import data success", None)
        except Exception as e:
            print(f"❌ n8n export failed: {e}")
            raise HTTPException(status_code=500, detail="n8n export failed")


    def export_workflow(self):
        try:
            export_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../modularlogics/download'))
            os.makedirs(export_dir, exist_ok=True)

            file_name = f"workflows-{int(time.time())}.json"
            export_path = f"/root/workflows.json"
            local_path = os.path.join(export_dir, file_name)

            subprocess.run(
            ["/usr/bin/n8n", "export:workflow", "--all", f"--output={export_path}"],
            check=True,
            env={**os.environ, "N8N_USER_FOLDER": "/root/.n8n"}
            )

            shutil.copy(export_path, local_path)
            os.remove(export_path)

            return {"filePath": local_path, "filename": file_name}

        except subprocess.CalledProcessError as e:
            print(f"❌ n8n export failed: {e}")
            raise HTTPException(status_code=500, detail="n8n export failed")
        except Exception as e:
            print(f"❌ export_workflow failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

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
            db_path = "/root/.n8n/database.sqlite"
            
            subprocess.run(
                ["sqlite3", db_path, "DELETE FROM user;"],
                check=True
            )
           
            subprocess.run(
                ["sqlite3", db_path, "DELETE FROM settings WHERE key='userManagement.isInstanceOwnerSet';"],
                check=True
            )
            
            subprocess.run(["pm2", "stop", "n8n"], check=True)
            
            subprocess.run(["rm", "-rf", "/root/.n8n"], check=True)
            
            subprocess.run(["pm2", "start", "n8n"], check=True)
            subprocess.run(["pm2", "restart", "n8n"], check=True)
            return appResponse.AppResponse("success", "Delete database success", None)
        except Exception as e:
            print(f"❌ n8n export failed: {e}")
            raise HTTPException(status_code=500, detail="n8n export failed")

    def update_version(self,new_version):
        print(f"Updating version to {new_version}")
