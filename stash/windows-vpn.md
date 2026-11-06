# Windows 公司内网配置指南

## 连接方式

适用于本仓库的 [stash.yaml](stash.yaml)、[aTrust.stoverride](aTrust.stoverride) 和 Windows 版 zju-connect。Stash 接管应用请求，公司域名和指定网段通过本机 SOCKS5 节点进入 zju-connect，再访问公司网关允许的资源。公网请求继续使用主配置的分流规则。

2026-11-06 已在 Stash for Windows 0.1.47 和 zju-connect v1.3.1 验证公司 CODING 站点。公司网关使用 `auth/psw` 账号密码认证，登录域为 `local`。覆写文件不保存 VPN 账号、密码或会话数据。

## 启动 zju-connect

下载 [zju-connect v1.3.1 Windows amd64](https://github.com/Mythologyli/zju-connect/releases/tag/v1.3.1)，解压后在程序目录打开 PowerShell。以下命令通过系统凭据窗口读取账号密码，密码仅传入本次进程。

```powershell
$credential = Get-Credential -Message '输入公司 VPN 账号和密码'
$env:ZJU_CONNECT_USERNAME = $credential.UserName
$env:ZJU_CONNECT_PASSWORD = $credential.GetNetworkCredential().Password
try {
    .\zju-connect.exe -protocol atrust -server vpn.guorenpcic.com -port 443 `
        -auth-type auth/psw -login-domain local `
        -socks-bind 127.0.0.1:11080 -http-bind 127.0.0.1:11081 `
        -tun-mode=false -add-route=false -dns-hijack=false -fake-ip=false `
        -bind-interface WLAN -local-dns-server 223.5.5.5 `
        -update-best-nodes-interval 0 `
        -keep-alive-url http://codingcorp.devops.guorenpcic.com/
} finally {
    Remove-Item Env:ZJU_CONNECT_USERNAME, Env:ZJU_CONNECT_PASSWORD
    $credential = $null
}
```

`WLAN` 是本机的物理网络接口名称。使用有线网络或其他电脑时，通过 `Get-NetAdapter` 查询实际接口名称并替换。绑定物理网络接口，让 zju-connect 的网关连接直接出站。`local-dns-server` 用于解析 VPN 网关，业务域名由 zju-connect 按网关下发的资源配置处理。

公司网关没有下发 DNS，zju-connect 的默认 DNS 保活不会启用。启动命令使用公司 HTTP 站点保活。保持程序运行并保持账号会话有效；此命令没有设置开机自启。

代理只监听 `127.0.0.1`。当前覆写使用 SOCKS5 的 TCP 转发，并关闭节点测速与 UDP。公司网关仍决定每项资源可访问的地址、端口和账号权限。

## 导入并启用覆写

1. 导入本仓库的 `stash.yaml`，设为当前配置。
2. 在“覆写”页面导入 `aTrust.stoverride`，启用“aTrust 公司内网”。
3. 保留机场订阅覆写，将公司内网覆写放在会修改 DNS 或分流规则的其他覆写之后。
4. 开启 Stash 的增强模式和“设为系统代理”。

覆写添加名为 `aTrust` 的 SOCKS5 节点，地址为 `127.0.0.1:11080`。规则默认插入主配置之前，zju-connect 进程和 `vpn.guorenpcic.com` 网关直连，公司业务使用该节点。主配置中的地区过滤排除 `aTrust`，该节点不参与机场选择。

DNS 覆写清空主配置的 `nameserver-policy`，并用 `#!replace` 将真实地址例外设为 `rule-set:lan` 和 `rule-set:fake-ip-exclude`。公司业务域名由 Stash 返回 Fake-IP，TCP 请求携带原始域名进入 SOCKS5。其他 DNS 上游保持主配置的设置。自行添加其他 DNS policy 时，需要一并维护这份覆写的替换列表。

停用覆写会移除它添加的节点、规则和 DNS 修改。Windows 的系统代理绕过与隧道排除单独保存，不随覆写开关恢复。

## 设置 Windows 接管范围

打开“设置 → 网络 → 绕过列表”，删除以下两项，保留其他内容：

```text
guorenpcic.com
*.guorenpcic.com
```

在 Windows“环境变量”的用户变量中检查 `NO_PROXY`，移除 `guorenpcic.com`、`.guorenpcic.com` 或 `*.guorenpcic.com` 公司域名条目，保留其他内容。该修改对新启动的应用生效，已经运行的应用可能继续使用启动时读取的值；增强模式仍需接管这些应用的连接。

打开“设置 → 隧道 → 排除的网段”，移除以下 5 条公司地址范围，保留其他用途的排除项：

```text
10.75.0.0/16
10.100.11.24/32
10.78.137.33/32
172.18.20.200/32
172.31.200.5/32
```

这 5 条范围已加入覆写的 `IP-CIDR` 规则。它们用于选择内网节点，资源访问权限仍由公司网关控制。其他私有地址继续按主配置直连。

修改隧道排除会重载隧道，已有连接可能短暂中断。修改后重新打开公司网页。系统代理的通用私有地址绕过可以保留，直接访问公司 IP 的流量仍需增强模式接管。

## 验证访问

在 PowerShell 运行：

```powershell
Resolve-DnsName codingcorp.devops.guorenpcic.com -Type A
curl.exe --noproxy "" --proxy socks5h://127.0.0.1:11080 --max-time 15 `
    --output NUL --write-out "SOCKS5 HTTP=%{http_code}\n" `
    http://codingcorp.devops.guorenpcic.com/
curl.exe --noproxy "" --proxy http://127.0.0.1:7890 --max-time 15 `
    --output NUL --write-out "Stash HTTP=%{http_code}\n" `
    http://codingcorp.devops.guorenpcic.com/
```

代理端口按实际设置填写。检查结果应满足：

- 公司域名返回 Stash 的 Fake-IP，通常位于 `198.18.0.0/15`。
- SOCKS5 和 Stash 两条路径均返回 HTTP 200。
- Stash 请求列表显示公司站点命中 `corporate-domains`，出口为 `aTrust`。
- 公司 IP 命中覆写的对应 `IP-CIDR`，VPN 网关命中 `DIRECT`。
- “其他地区”和各地区组均不包含 `aTrust`。

2026-11-06 本机验证时，公司 CODING 域名返回 `198.18.16.50`；通过 Stash 收到 37,767 字节页面。请求列表确认出口为 `aTrust`，zju-connect 确认真实业务目标为 `10.75.11.237:80`。通过系统 DNS 和增强模式访问同样返回 HTTP 200。其他公司网段已验证规则匹配，尚未逐项验证业务服务。

官方 aTrust 服务已停止，安装目录下的进程全部退出，虚拟网卡状态为断开。该状态下 6 项真实访问检查通过：公司站点经 Stash HTTP 代理、系统增强模式和 zju-connect HTTP 代理均返回 HTTP 200；公司真实 IP 经增强模式返回 HTTP 200；Apple HTTPS 直连返回 HTTP 200；Google HTTPS 经原有香港节点返回 HTTP 204。公司连接记录确认出口为 `aTrust`，验证的公司站点访问不依赖官方客户端运行。

## 无法访问时检查

| 现象 | 检查内容 |
| --- | --- |
| `127.0.0.1:11080` 无法连接 | 检查 zju-connect 进程、登录结果和监听地址 |
| SOCKS5 访问失败 | 检查公司会话、资源权限、业务服务端口和 zju-connect 日志 |
| SOCKS5 成功，Stash 失败 | 检查覆写是否启用、节点端口与实际连接出口 |
| 公司域名没有返回 Fake-IP | 检查覆写 DNS 是否应用，以及应用是否使用自定义 DNS |
| 公司请求未进入 Stash | 检查增强模式、公司域名绕过和公司网段排除 |
| zju-connect 日志出现循环连接 | 检查物理接口绑定，以及进程和网关直连规则 |
| 一段时间后无法访问 | 检查账号会话、HTTP 保活与网关返回的错误 |
| 新增公司服务无法访问 | 核对域名、实际地址及网关权限，按需补充公司规则 |

## 其他设备

`127.0.0.1` 指向运行 Stash 的那台设备。macOS 需要在本机运行 zju-connect，或填写可访问的服务地址。iOS 使用此覆写时，也需要可访问的 zju-connect 服务地址。当前服务仅监听 Windows 本机，其他设备无法直接使用。

覆写合并、SOCKS5 与 DNS 字段见 [Stash 覆写文档](https://stash.wiki/configuration/override)、[协议文档](https://stash.wiki/proxy-protocols/proxy-types)和 [DNS 文档](https://stash.wiki/features/dns-server)。
