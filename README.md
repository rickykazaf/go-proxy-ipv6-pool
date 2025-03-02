
## 启动参数
```
nohup go run . --port 1552 --cidr 2605:a141:2240:6470::/64 --user kocaptcha --password wuyao666 --name ipv6proxy > ipv6proxy.log 2>&1 &
```

## 查看后台进程
```
ps -ef | grep ipv6proxy
```

## 停止后台进程
```
kill -9 $(ps -ef | grep ipv6proxy | grep -v grep | awk '{print $2}')

```

##  CURL查看ip
```
curl -v -x http://ip:1552 http://ipv6.ip.mir6.com/
```

