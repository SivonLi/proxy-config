# Windows 公司 VPN 配置指南

## 适用范围

适用于本仓库的 [stash.yaml](stash.yaml)、Stash for Windows 和公司 aTrust VPN。文档按 Stash 0.1.47 编写，设置核对日期为 2026-11-05。

主配置已为 `guorenpcic.com` 及其子域名设置系统 DNS、真实 IP 和优先直连。Windows 的系统代理绕过、隧道网段排除和断网保护另行保存在设备中。**重新安装 Stash 或更换电脑后，需要重新完成下列设置。**

## 连接公司 VPN

1. 安装并登录 aTrust，连接公司 VPN。
2. 确认仅连接 aTrust 时，浏览器可以打开平时使用的公司内网网站。
3. 按 [主配置导入说明](README.md#导入与选择节点)导入 `stash.yaml` 和机场覆写，启动 Stash。

aTrust 负责公司登录、内网解析和业务路由。以下设置沿用 aTrust 已提供的访问权限。

## 设置系统代理绕过

打开“设置 → 网络”，开启“设为系统代理”。在“绕过列表”中保留现有内容，用英文分号追加以下两项：

```text
guorenpcic.com;*.guorenpcic.com
```

第一项匹配公司根域名，第二项匹配其子域名。已有条目末尾没有分号时，追加前补充一个分号。

输入框为空时，Stash 使用界面提示的默认列表。填写自定义内容后，需要把默认条目一起保留。本机当前的完整列表如下，可整行复制；其他自定义绕过条目也应继续保留：

```text
localhost;127.*;10.*;172.16.*;172.17.*;172.18.*;172.19.*;172.20.*;172.21.*;172.22.*;172.23.*;172.24.*;172.25.*;172.26.*;172.27.*;172.28.*;172.29.*;172.30.*;172.31.*;192.168.*;<local>;guorenpcic.com;*.guorenpcic.com
```

遵循 Windows 系统代理设置的应用会直接连接这些地址。应用单独指定了 HTTP / SOCKS 代理时，还需在该应用中为公司域名设置直连。

## 设置隧道排除网段

打开“设置 → 隧道 → 排除的网段”，每次输入一条并点击“添加”，共添加以下 5 条：

```text
10.75.0.0/16
10.100.11.24/32
10.78.137.33/32
172.18.20.200/32
172.31.200.5/32
```

修改列表会重载隧道，连接可能短暂中断。完成后确认列表中包含全部 5 条，保留设备原有的其他排除项。

这些地址通过 Windows 路由访问，由 aTrust 接管对应的公司业务流量。`DIRECT` 分流规则本身无法代替这项设置。

`10.75.0.0/16` 排除整个 `10.75.*.*` 范围，其余 4 条各排除一个地址。2026-11-05 本机验证时，这些范围覆盖了 aTrust 的 157 条业务路由。该版本最多接受 128 条排除项，因此采用上述 5 条范围。

这里排除的是指定地址范围，实际可访问的资源由 aTrust 路由和权限决定。公司新增其他网段时，应按新的业务路由补充排除项。

## 保持运行开关

| 位置 | 设置 |
| --- | --- |
| aTrust | 保持公司 VPN 已连接 |
| Stash 仪表盘 | 保持 Stash 运行，开启增强模式 |
| 设置 → 网络 | “设为系统代理”开启 |
| 设置 → 隧道 | “断网保护”关闭，允许排除的流量通过公司 VPN |

完成设置后，重新打开公司网页。仍在复用旧连接的应用需要退出后重新打开。

## 验证访问

保持 aTrust 和 Stash 同时运行，用平时使用的浏览器打开公司内网网站。应能显示网站页面或公司登录页面。通过系统代理绕过、隧道排除的连接可能不会出现在 Stash 请求列表中。

需要检查解析和路由时，在 PowerShell 执行以下命令，输入实际公司内网域名：

```powershell
$corpHost = Read-Host '输入公司内网域名，不含协议和路径'
$corpAddress = [System.Net.Dns]::GetHostAddresses($corpHost) |
    Where-Object AddressFamily -eq InterNetwork |
    Select-Object -First 1 -ExpandProperty IPAddressToString
$corpAddress
Find-NetRoute -RemoteIPAddress $corpAddress |
    Format-List InterfaceAlias, IPAddress, DestinationPrefix, NextHop
Test-NetConnection -ComputerName $corpAddress -Port 80 -InformationLevel Detailed |
    Format-List RemoteAddress, RemotePort, InterfaceAlias, SourceAddress, TcpTestSucceeded
```

HTTP 网站通常使用 80 端口，HTTPS 网站通常使用 443 端口，其他服务填写实际端口。检查结果应满足以下条件：

- DNS 返回公司业务的真实地址。当前已验证的业务地址位于 `10.75.*.*`。
- 路由出口属于 aTrust 网卡。本机名称为“本地连接”，描述为 `Sangfor aTrust VNIC`；其他电脑以实际名称为准。
- `TcpTestSucceeded` 为 `True`，说明目标地址的指定端口可连接。浏览器还需能打开页面，端口连通不代表账号已获得业务权限。

PowerShell 的端口检查使用系统路由；浏览器访问同时检查应用是否正确采用系统代理绕过。

## 无法访问时检查

| 现象 | 检查内容 |
| --- | --- |
| 仅连接 aTrust 也无法访问 | 检查 aTrust 登录、公司权限和业务服务状态 |
| 无法解析公司域名 | 检查 aTrust 连接，以及主配置的 `nameserver-policy` 是否仍使用 `system` |
| 公司域名返回 Fake-IP | 检查主配置的 `fake-ip-filter` 是否包含 `rule-set:corporate-domains`，其他覆写是否改动 DNS |
| 路由出口没有使用 aTrust | 检查目标 IP 是否包含在排除网段中，以及 aTrust 是否提供对应路由 |
| 浏览器成功，某个应用失败 | 检查应用自己的代理和 DNS 设置，将公司域名设置为直连并使用系统解析 |
| 公司新增服务无法访问 | 获取目标真实 IP，核对 aTrust 业务路由与 Stash 排除范围 |

## 设置保存位置

以下路径用于核对本机设置，日常通过 Stash 界面修改：

| 文件 | 对应内容 |
| --- | --- |
| `%APPDATA%\ws.stash.windows\preferences.json` | `systemProxyBypass`：系统代理绕过列表 |
| `C:\ProgramData\Stash\split-tunnel.json` | `subnets`：排除的网段 |
| `C:\ProgramData\Stash\settings.json` | `killSwitch`：断网保护开关，本方案为 `false` |

上述 Windows 设置需要在每台电脑分别配置。`stash.yaml` 可以继续与 iOS、原生 Stash for Mac 共用。DNS 字段见 [Stash DNS 文档](https://stash.wiki/features/dns-server)，其他平台的公司 VPN 共存方式见 [官方说明](https://stash.wiki/faq/conflict-with-vpn)。
