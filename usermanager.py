import json
from datetime import datetime, timedelta
import sys
import uuid
import subprocess

archived_users_location="/etc/v2ray/archived_users.json"
config_file_location="/etc/v2ray/config.json"

class UserManager:
    def __init__(self, config_file):
        self.config_file = config_file
        try:
            with open(self.config_file) as json_file:
                self.config = json.load(json_file)
        except FileNotFoundError:
            self.config = {"inbounds": []}

    def add_user(self, user, id, alterId, days_valid):
        expire_time = (datetime.now() + timedelta(days=days_valid)).strftime("%Y-%m-%d")
        self.config["inbounds"][0]["settings"]["clients"].append({
          "user": user,
          "id": id,
          "alterId": alterId,
          "exp": expire_time
        })
        self.save_config()

    def remove_user(self, user):
        for inbound in self.config["inbounds"]:
            if inbound["protocol"] == "vmess":
                for i, client in enumerate(inbound["settings"]["clients"]):
                    if client["user"] == user:
                        del inbound["settings"]["clients"][i]
                        self.save_config()
                        return
        print(f"User with user {user} not found.")

    def check_expire(self):
        change_file=false
        for inbound in self.config["inbounds"]:
            if inbound["protocol"] == "vmess":
                for i, client in enumerate(inbound["settings"]["clients"]):
                   if 'exp' in client:
                        expire_time = datetime.strptime(client['exp'], '%Y-%m-%d')
                        if datetime.now() > expire_time:
                            change_file=true
                            self.archived_user(client)
                            del inbound["settings"]["clients"][i]
                            print(f"User with user {client['user']} has been removed due to expire")
         if (change_file):
           self.save_config()

    def archived_user(self, client):
        with open(archived_users_location, "r+") as json_file:
            try:
                data = json.load(json_file)
                data["users"].append(client)
            except json.decoder.JSONDecodeError:
                data = {"users": [client]}
            json_file.seek(0)
            json_file.write(json.dumps(data))
            json_file.truncate()
            print(f"User with user {client['user']} has been archived.")

    def renew_user(self, user, days_valid):
        with open("archived_users.json", "r") as json_file:
            data = json.load(json_file)
            for i, client in enumerate(data["users"]):
                if client["user"] == user:
                    client["exp"] = (datetime.now() + timedelta(days=days_valid)).strftime("%Y-%m-%d")
                    self.config["inbounds"][0]["settings"]["clients"].append(client)
                    del data["users"][i]
                    with open(archived_users_location, "w") as json_file:
                        json.dump(data, json_file)
                    self.save_config()
                    print(f"User with user {user} has been renewed for {days_valid} days.")
                    return
            print(f"User with user {user} not found in archived users.")

    def save_config(self):
        with open(self.config_file, "w") as json_file:
            json.dump(self.config, json_file, indent=4)
        subprocess.run(["systemctl", "restart", "v2ray.service"])

    def run(self, action, *args):
        if action == "add":
            self.add_user(*args)
        elif action == "check_expire":
            self.check_expire()
        elif action == "renew":
            self.renew(*args)
        else:
            print("Invalid action.")
manager = UserManager(config_file_location)
action = sys.argv[1]
print(action)
if action == "check_expire":
  manager.check_expire()
elif action == "cli":
  while True:
    action = input("Enter an action (add, check_expire, list:to list expire users, exit): ")
    if action == "add":
        user = input("Enter user: ")
        id = str(uuid.uuid4())
        days_valid = int(input("Enter days valid: "))
        manager.run(action, user, id, 64, days_valid)
    elif action == "check_expire":
        manager.run(action)
    elif action == "list":
        with open(archived_users_location) as json_file:
            data = json.load(json_file)
            for i, client in enumerate(data["users"]):
                print(f"{i+1}. user: {client['user']}  Expired at: {client['exp']}")
            index = int(input("Enter the index of the user you want to renew: "))
            if index > 0 and index <= len(data["users"]):
                user = data["users"][index - 1]["user"]
                days_valid = int(input("Enter days valid: "))
                manager.run("renew", user, days_valid)
            else:
                print("Invalid index.")
    elif action == "exit":
        break
    else:
        print("Invalid action.")
else:
  print("Invalid action.")
