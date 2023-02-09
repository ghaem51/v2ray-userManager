if [[ "$1"  == ''  ]]; then
	echo "auto generate userId"
	userId=$(uuidgen)
else
	userId="$1"

fi
echo "enter username:"
read username
echo "set expireManual?(y/n)"
read setExpireManual
if [[ "$setExpireManual" == "y" ]]; then
	echo "set expire (format. yyyy-mm-dd, ex: 2021-10-10):"
	read expireTime
	expire="$expireTime"
else
	echo "expire after (default 1 month):"
	read expireafter
	expire=$(date -d "+$expireafter month" '+%Y-%m-%d')
fi
echo "userId: $userId"
jq ".inbounds[0].settings.clients += [{ 
    \"user\": \"$username\",
    \"id\": \"$userId\",
    \"alterId\": 64,
    \"exp\": \"$expire\"
}] " /etc/v2ray/config.json > /etc/v2ray/newconfig.json
mv /etc/v2ray/newconfig.json /etc/v2ray/config.json
systemctl restart v2ray.service
#systemctl status v2ray.service
echo "connection:"
string=$(echo "{                             
  \"v\": \"2\",
  \"ps\": \"v2ray_clinet_side_name\",
  \"add\": \"YourV2rayServerAddress\",
  \"port\": \"443\",
  \"id\": \"$userId\",
  \"aid\": \"0\",
  \"net\": \"ws\",
  \"type\": \"none\",
  \"host\": \"YourV2rayServerAddress\",
  \"path\": \"/YourV2rayServerPath/\",
  \"tls\": \"tls\"
}" | base64 -w 0)
echo "vmess://$string"
echo "vmess://$string" | qrencode -o - -t utf8
