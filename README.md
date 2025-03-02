
## 安装golang
```
sudo apt install golang
```

## 查看golang版本
```
go version
```

## 查看ipv6地址
```
ip a
然后找到eth0 的ipv6地址
ip -6 addr
```

## 启动参数
```
nohup go run . --port 1552 --cidr 2605:a141:2240:6470::/64 --user kocaptcha --password wuyao666 > ipv6proxy.log 2>&1 &

go run . --port 1552 --cidr 2a02:c207:2248:9266::1/64 --user kocaptcha --password wuyao666



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
curl -v -x http://kocaptcha:wuyao666@144.126.146.97:1552 http://ipv6.ip.mir6.com/
```

## 查看日志
```
tail -f ipv6proxy.log
```