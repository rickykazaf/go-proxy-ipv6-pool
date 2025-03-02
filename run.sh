#!/bin/bash

# 获取 IPv6 地址
IPV6=$(ip -6 addr show eth0 | grep "scope global" | awk '{print $2}' | cut -d'/' -f1)
echo "获取到的 IPv6 地址: $IPV6"

# 添加路由
echo "添加 IPv6 路由..."
sudo ip route add local ${IPV6}/64 dev eth0

# 设置 ip_nonlocal_bind
echo "设置 ip_nonlocal_bind..."
sudo sysctl net.ipv6.ip_nonlocal_bind=1

# 安装 ndppd
echo "安装 ndppd..."
sudo apt update
sudo apt install -y ndppd

# 创建 ndppd 配置文件
echo "创建 ndppd 配置..."
sudo cat > /etc/ndppd.conf << EOF
route-ttl 30000
proxy eth0 {
    router no
    timeout 500
    ttl 30000
    rule ${IPV6}/64 {
        static
    }
}
EOF

# 重启 ndppd 服务
echo "重启 ndppd 服务..."
sudo service ndppd restart

# 验证配置
echo "配置完成，当前状态："
echo "1. IPv6 路由："
ip -6 route show | grep local
echo "2. ip_nonlocal_bind 设置："
sysctl net.ipv6.ip_nonlocal_bind
echo "3. ndppd 服务状态："
service ndppd status | grep Active

# 启动代理服务
echo "启动代理服务..."
# git clone https://github.com/rickykazaf/go-proxy-ipv6-pool.git ipv6proxy
# cd ipv6proxy
nohup go run . --port 1552 --cidr ${IPV6}/64 --user kocaptcha --password wuyao666 > ipv6proxy.log 2>&1 &

# 显示代理服务状态
echo "代理服务已启动，日志保存在 ipv6proxy.log"
echo "可以使用以下命令查看日志："
echo "tail -f ipv6proxy.log"

echo "配置完成！"