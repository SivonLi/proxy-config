# Stash 配置

## 导入与选择节点

配置文件为 [stash.yaml](stash.yaml)。适用于 iOS Stash 3.7.0，包括在 Apple silicon Mac 上运行的 iOS 版。原生 Stash for Mac 需要 4.4 及以上版本。本文使用的覆写参数和规则预匹配功能，在当前官方文档中仍标注为 Beta。

1. 将 `stash.yaml` 导入 Stash，作为主配置。
2. 在覆写页面导入 [airport.stoverride](airport.stoverride)，打开“参数”，填写机场的完整 HTTPS Clash 订阅地址，保存并启用覆写。启动 Stash，机场订阅和规则首次下载成功后，进入策略页面。
3. 在“默认代理”手动选择香港、日本、美国、新加坡或台湾，初始地区为香港。
4. AI 初始选择美国，可选日本、新加坡和台湾。Lark 初始选择日本，可选香港、美国、新加坡和台湾。Spotify 初始选择“默认代理”，也可以独立选择地区。Apple 和 Microsoft 初始选择 `DIRECT`，也可以选择地区。下载初始选择香港，可手动选择 `DIRECT`。地区分组根据测速结果自动选择节点。

覆写只修改 `proxy-providers.airport.url`。订阅参数为必填项，每台设备分别填写；更新覆写会保留本设备的参数，分享或导出覆写只包含原始模板。参数用法见 [Stash 覆写文档](https://stash.wiki/configuration/override)。更新主配置时，继续启用此覆写即可使用已填写的订阅。

也可以复制主配置为 `stash.local.yaml`，直接填写 `proxy-providers.airport.url` 后导入，保留地址两侧的单引号。这种方式更新主配置时，需要保留自己的订阅地址。

机场订阅地址包含凭证，请保存在自己的设备中。工作区的 `.gitignore` 已排除 `stash/*.local.yaml`。

Stash 从完整 Clash 订阅中提取 `proxies`。机场提供的分组、规则、DNS 和 `hosts` 不会自动合并。机场需要专用 DNS 时，该服务器必须支持加密 DNS；机场需要的 `hosts` 可以补充到本地配置。节点协议必须得到 Stash 支持。

地区分组通过节点名称识别中文地区名、英文名称、常见代码和旗帜。请在地区分组中确认机场节点已正确归类。Stash 会将没有匹配节点的空组视为 `DIRECT`，使用前需要确认所选地区包含机场节点；节点命名不符合规则时，需要调整相应 `filter`。

## 分流行为

通用规则使用 [SukkaW/Surge](https://github.com/SukkaW/Surge) 发布的 Clash 格式文件。

| 流量 | 默认出口 |
| --- | --- |
| 局域网域名与私有地址 | DIRECT |
| AI 与 Apple Intelligence | AI，初始选择美国 |
| Lark 专用服务域名 | Lark，初始选择日本 |
| Spotify | Spotify，初始使用默认代理 |
| 其他流媒体 | 默认代理 |
| Telegram | 默认代理 |
| Apple 中国服务与 Apple CDN | DIRECT |
| 其他 Apple 服务 | Apple，初始为 DIRECT |
| Microsoft CDN | DIRECT |
| 其他 Microsoft 服务 | Microsoft，初始为 DIRECT |
| 规则中的下载站点 | 下载，初始选择香港，可选择 DIRECT |
| 国内域名、解析后属于中国 IP 的其余域名 | DIRECT |
| Sukka 境外服务域名与其余流量 | 默认代理 |

域名规则先于 IP 规则，国内域名集合优先于通用境外服务集合。规则范围和加载顺序依据 [Sukka 的使用说明](https://github.com/SukkaW/Surge#readme)。`domestic` 是人工维护的常见国内服务集合，中国 IP 集合用于判断域名集合尚未收录的国内服务。

未命中域名规则的连接进入 IP 规则阶段。首个局域网 IP 集合允许触发真实地址解析，后续服务 IP 集合复用解析结果。中国 IPv4、IPv6 集合允许解析，命中中国地址时直连，其余连接使用默认代理。公共 CDN 根据服务域名和地址采用相同的分流逻辑。

明确指定代理的 Lark、AI、流媒体、Telegram、下载和境外服务域名，按各自规则访问。域名集合、地址归属数据和服务部署都可能变化，这套规则无法保证所有中国应用的每个请求都直连。

Lark 集合使用[官方防火墙域名清单](https://www.larksuite.com/hc/en-US/articles/360044784554-configure-organization-firewall-domain-and-ip-allowlist)中的 6 个专用域名，覆盖 `larksuite.com`、`larksuite-us.com`、`larksuitecdn.com`、`larksuitepkg.com`、`larkenterprise.com` 和 `baseopendevx.com` 及其子域名。集合优先于通用服务规则，随本配置维护。其他共享服务域名和直接访问 IP 的连接继续按通用规则处理。

Spotify 的 17 个域名、1 个关键词和 1 个 IP 条目来自 [Sukka 的 Spotify 定义](https://github.com/SukkaW/Surge/blob/master/Source/stream.ts#L630)。域名和 IP 使用 Stash inline 集合，关键词使用单独规则，均优先于通用流媒体集合。内嵌条目随本配置维护。Apple 和 Microsoft 规则优先于通用流媒体集合，Apple Intelligence 使用 AI 分组。

Apple 的 `icloud.com`、`icloud-content.com` 和推送服务使用 Apple 分组，初始选择 `DIRECT`。更新配置后，需要在策略页面确认 Apple 的当前选择；已保存的选择可能继续生效。

Sukka 的 `direct` 集合包含 macOS 下载工具等程序的 `PROCESS-NAME` 条目。连接匹配到这些条目时会直连，iOS 忽略进程条目。公司 VPN 的接口和路由由实际设备决定，此文件仅提供局域网直连规则。

## DNS 与接管范围

配置利用 Stash 3.6 / macOS 4.3 新增的加密 Bootstrap、独立节点 DNS 和 DNS 引用规则集合功能。具体语义见 [Stash DNS 文档](https://stash.wiki/features/dns-server)。

| 查询用途 | 上游 | 出口 |
| --- | --- | --- |
| 机场节点域名、DNS Bootstrap | `https://223.5.5.5/dns-query` | 独立直连通道 |
| 国内域名、Apple 服务、Microsoft 服务、直连集合域名 | `https://223.5.5.5/dns-query` | DIRECT |
| Lark、AI、Apple Intelligence、Spotify、其他流媒体、Telegram、Sukka 境外服务集合 | `https://1.1.1.1/dns-query` | 默认代理 |
| 尚未收录的域名 | `https://223.5.5.5/dns-query` | DIRECT |
| 局域网集合中的域名 | `https://223.5.5.5/dns-query` | DIRECT |

Lark、AI、Apple Intelligence 和 Spotify 的 DNS 集合优先于 Apple、Microsoft 集合，Apple、Microsoft 集合优先于通用流媒体集合。国内域名集合优先于通用境外服务集合。未收录域名使用国内 DoH，以获取适合国内直连的 CDN 地址。该解析服务可以看到这些查询，未知境外域名也属于这个范围。

DNS 服务器使用 IP 地址，节点 DNS 使用独立通道，连接代理时不会依赖已经建立的代理连接。

Stash 管理的全部上游查询使用 DoH，包括节点域名、Bootstrap 和局域网域名。配置中没有系统 DNS、明文 DNS 或明文回退。国内解析服务可以看到分配给它的查询，机场节点端的域名解析由机场控制。

规则首条为 `DST-PORT,53,REJECT,pre-matching`，阻止进入 Stash 分流引擎的 TCP、UDP 53 端口连接，覆盖 IPv4 和 IPv6。`pre-matching` 是 3.7 新增的提前拒绝选项：iOS 在读取连接数据前拒绝，UDP 在首个数据包阶段拒绝，从而减少连接处理。已交给 Stash 内置 DNS 服务处理的查询，使用上述 DoH 上游。选项语义与支持的规则类型见 [规则类型文档](https://stash.wiki/rules/rule-types)。

提前拒绝的请求不会出现在连接列表中。核心日志按目标限制记录频率；需要确认匹配阶段时，可使用 [HTTP API](https://stash.wiki/features/http-api) 的 `/rules/match` 查看 `stage` 字段。

仅由路由器或公司 DNS 解析的内网域名，公共 DoH 通常无法解析。可以通过私有 IP 访问设备，或在 `hosts` 中填写内网域名与地址。需要动态解析内网域名时，必须配置能解析这些名称的内网 DoH、DoT 或 DoQ 服务。发给公共 DoH 的内网域名会对该解析服务可见。

顶层 `ipv6: false` 让 Stash 自身只解析 IPv4，`dns.ipv6: false` 让应用 DNS 查询不返回 AAAA 记录。这两个设置控制 DNS 解析，直接访问 IPv6 地址的流量仍需要 Tunnel IPv6 路由接管。

Stash 默认使用 Fake-IP，局域网集合返回真实地址。已命中代理域名规则的连接可以交给节点解析。未命中域名规则的连接需要一次真实地址查询，供 IP 规则判断。配置没有开启并发回退 DNS。

**还需要完成 Stash 界面设置：**

- macOS 开启“增强模式”，让 Stash 接管应用流量。仅使用系统代理时，部分应用和 UDP 流量可能直接访问网络。
- 设备使用 IPv6 网络时，按照 [IPv6 文档](https://stash.wiki/faq/ipv6-compatible)在“网络设置”启用 Tunnel IPv6 路由，让直接访问 IPv6 DNS 地址的连接也进入 53 端口拦截规则。
- 在按需连接中开启“保持 Stash 开启”，保持各个网络下的接管。规则中保留局域网直连，无需为整个 Wi-Fi 停止 Stash。
- 导入后确认其他覆写没有替换本文件的 DNS 配置。

独立 DoH 应用、浏览器安全 DNS、iCloud Private Relay、其他 VPN 和应用自己的网络机制，会影响实际 DNS 出口。需要采用本配置 DNS 策略的应用，应关闭自行指定的 DNS。mDNS、Bonjour 和系统绕过隧道的通信超出这里的上游 DNS 与 53 端口规则范围。Stash 停止、系统绕过隧道、订阅为空时，配置无法提供完整的断网保护。Stash 会把空的远程节点集合视为 `DIRECT`，因此导入和更新后需要确认节点集合正常。

## 省电设置

“默认代理”和服务分组使用手动选择，通过 `interval: -1` 关闭这些分组的定时测速。香港、日本、美国、新加坡和台湾使用 `url-test`，每 600 秒测速，并设置 `lazy: true`，一段时间未使用的地区跳过自动测速。

地区分组自动选择可用的低延迟节点。`tolerance: 50` 表示新节点比当前节点快超过 50 ms 才会切换；当前节点测速失败时立即切换。测速使用 `https://www.gstatic.com/generate_204`，超时为 5 秒。测速结果表示连通性和延迟，不能表示下载带宽或服务解锁能力。具体语义见 [策略组文档](https://stash.wiki/proxy-protocols/proxy-groups)和 [远程代理集文档](https://stash.wiki/proxy-protocols/proxy-providers)。

机场订阅与规则每 86400 秒更新一次，并设置本地缓存路径。每种 DNS 用途只配置一个上游，减少重复查询。较大的域名和中国 IP 集合使用 `domain` / `ipcidr` 格式，其余集合保留官方的 `classical` 格式。

在 Stash 界面关闭“混合使用多个网络”和“并发连接”。保持正常日志等级，日常配置使用 `warning`。这些措施减少额外连接与网络请求，实际耗电仍取决于节点协议、信号质量、应用流量和系统状态。

规则结构与资源使用依据 [规则集合文档](https://stash.wiki/rules/rule-set)、[性能建议](https://stash.wiki/faq/effective-stash)和 [网络优化说明](https://stash.wiki/features/network-performance-enhance)。

## 验证范围

检查脚本为 [check_config.py](check_config.py)，依赖清单为 [requirements-check.txt](requirements-check.txt)。在工作区根目录运行：

```powershell
python -m pip install -r stash/requirements-check.txt
python stash/check_config.py
python stash/check_config.py --online --proxy http://127.0.0.1:7890
```

`--proxy` 用于下载公开规则和访问境外 DoH。国内 DoH 检查不指定 HTTP 代理。代理端口按本机配置填写。联网检查会访问真实公开服务；解析结果变化时，脚本直接报告失败。

2026-11-04 完成以下检查：

- 7 项本地检查通过，涵盖主配置与覆写的 YAML 解析、重复键、分组引用、地区过滤表达式、DNS 加密、国内规则顺序和订阅参数声明。
- 全部上游均为 HTTPS DNS，两个 IPv6 解析开关关闭，53 端口提前拦截位于全部分流规则之前。
- 23 个远程集合与 3 个 inline 集合验证通过，合计 12,918 条记录；规则类型、引用和 CIDR 格式检查通过。
- 山姆的 `api-sams.walmartmobile.cn`、`decoration-sams.walmartmobile.cn` 通过国内 DoH 返回 `157.148.16.212`，属于 Sukka 中国 IP 集合。
- 万达的 `cinema-api-prd-mx.wandafilm.com`、`misc-api-prd-mx.wandafilm.com` 通过国内 DoH 返回 `120.53.82.119`，属于 Sukka 中国 IP 集合。
- `223.5.5.5` 在不指定 HTTP 代理时返回有效的 DoH 答案。
- `1.1.1.1` 经现有 Windows HTTP 代理返回有效的 DoH 答案，验证过程没有关闭 TLS 证书校验。

上述请求验证了上游服务的可用性。Windows 上的连接路径受当前系统网络设置影响，没有执行 Stash 的实际 DNS 规则。

当前工作区位于 Windows，没有 Apple 平台的 Stash 运行环境，也没有机场订阅凭证。Stash 原生配置加载、订阅节点协议、节点连通性、隧道接管和设备耗电需要结合实际设备验证。本地检查不能代替这些运行结果。

iMessage 图片上传速度需要结合发送时的连接记录判断。记录应包含上传域名、命中规则和实际出口。现有山姆、万达记录已经证明这些业务请求通过香港节点访问；当前没有 iMessage 的连接记录，无法确认其速度问题的原因。

配置参考了 [LumexOverwrite](https://github.com/int-del/LumexOverwrite)和 [Clash Configuration Template](https://github.com/Accademia/Clash_Configuration_Template)。Stash 字段以官方文档为依据。
