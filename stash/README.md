# Stash 配置

## 导入与选择节点

使用 [stash.yaml](stash.yaml) 作为主配置，每个机场单独导入一份 [airport.stoverride](airport.stoverride)。在 Stash 的覆写页面，通过各自的开关启用或停用机场。适用于 iOS Stash 3.7.0，包括在 Apple silicon Mac 上运行的 iOS 版。原生 Stash for Mac 需要 4.4 及以上版本。Windows 已在 0.1.47 验证公司内网访问，需要同时完成 [Windows 公司 VPN 配置指南](windows-vpn.md)中的设置。规则预匹配功能在当前官方文档中仍标注为 Beta。

1. 下载下方的 `stash.yaml`，在 Stash 的配置页面通过本地文件导入，设为当前主配置。
2. 下载 `airport.stoverride`。将 `&airport_name` 后面的 `'我的机场'` 改为机场名称，将 `url` 改为完整 HTTPS Clash 订阅地址。保留缩进、两侧单引号，以及 `&airport_name` 和 `*airport_name`。
3. 将填写后的文件保存为 `airport-a.local.stoverride`，在 Stash 的覆写页面通过本地文件导入并启用。第二个机场使用另一份模板，填写不同名称和地址，保存为 `airport-b.local.stoverride` 后导入。继续添加机场时使用同样的方法。
4. 停用会修改 DNS、策略组或分流规则的其他覆写。至少启用一个机场，启动 Stash，等待机场节点与规则下载成功。
5. 在“默认代理”手动选择香港、日本、美国、新加坡、台湾、韩国、欧洲或“其他地区”，初始地区为香港。所选地区需要包含可用节点。

```text
https://raw.githubusercontent.com/SivonLi/proxy-config/configs/stash/stash.yaml
https://raw.githubusercontent.com/SivonLi/proxy-config/configs/stash/airport.stoverride
```

AI 初始选择美国，GitLab 和 Lark 初始选择日本。AI 与 GitLab 的选项排除香港。Spotify 初始选择“默认代理”，也可以独立选择地区。Apple、Microsoft 和测速初始选择 `DIRECT`。下载初始选择香港，可手动选择 `DIRECT`。

香港、日本、美国、新加坡、台湾、韩国和欧洲根据测速结果自动选择节点。欧洲包含英国、德国、荷兰等节点。“其他地区”使用 `select`，由你手动指定节点，通过 `interval: -1` 关闭该组的定时测速。它收纳上述地区以外的节点，过滤流量余额、套餐到期和重置时间等订阅提示项。

各机场的远程代理集从 Clash 订阅中读取 `proxies` 节点列表。8 个节点分类通过 `include-all: true` 汇集节点，再按名称过滤。增加机场或修改机场名称时，只需编辑对应的机场覆写。字段用法见 [Stash 远程代理集文档](https://stash.wiki/proxy-protocols/proxy-providers)和 [策略组文档](https://stash.wiki/proxy-protocols/proxy-groups)。

DNS、策略组、规则集合、分流规则和图标由主配置管理。每份机场覆写只添加一个远程代理集，以及供覆写页面显示的名称、说明和分类。机场订阅中的其他顶层配置不会参与分流，节点内部的协议和连接参数仍由机场提供。

更新主配置时，下载新的 `stash.yaml` 并重新通过本地文件导入，保留设备上的机场覆写。机场订阅地址保存在各自的本地覆写中，节点和规则集合按配置中的周期独立更新。

机场订阅地址包含凭证，请保存在自己的设备中。工作区的 `.gitignore` 已排除 `stash/*.local.yaml` 和 `stash/*.local.stoverride`。

### 机场名称与开关

机场覆写统一设置 `category: '机场订阅'`，在覆写页面按“机场订阅”分类管理。已导入的本地覆写可以直接在文件顶层添加这一行。

机场名称只填写一次。模板通过 YAML 锚点 `&airport_name` 和别名 `*airport_name`，让代理集名称与覆写页面的显示名称使用同一个值。每份文件中的锚点相互独立，各机场可以使用同一份模板。

每个机场必须使用不同名称。Stash 会递归合并不同覆写中的 `proxy-providers`；同名代理集会合并或覆盖，无法作为两个独立机场管理。机场覆写采用普通字典合并，具体语义见 [覆写文档](https://stash.wiki/configuration/override)。

在覆写页面启用机场后，它的节点参与各地区组的筛选。7 个自动地区组按需测速，“其他地区”保留手动选择。关闭该机场的覆写并应用配置后，它的代理集从当前配置中移除。开关控制整份机场订阅，可以同时启用多个机场。

**全部机场关闭，或所选地区没有节点时，Stash 会将空组视为 `DIRECT`。** 使用代理前需要保持相应地区至少有一个可用节点。每份模板均未指定固定缓存路径，复制模板时无需另行维护缓存文件名。

机场节点协议必须得到 Stash 支持。机场需要专用 DNS 时，该服务器必须支持加密 DNS；必要的 DNS 和 `hosts` 设置可以填写在自己的本地配置中。

地区分组通过节点名称识别中文地区名、英文名称、常见代码和旗帜。请在地区分组中确认机场节点已正确归类。Stash 会将没有匹配节点的空组视为 `DIRECT`，使用前需要确认所选地区包含机场节点；节点命名不符合规则时，需要调整相应 `filter`。

### 首页订阅信息

首页流量和到期时间来自机场响应头中的 `Subscription-Userinfo`。根据 [Stash 服务提供商订阅文档](https://stash.wiki/features/service-provider-subscription)，Stash 优先读取主配置的定时更新地址；没有更新地址时，读取主配置中的 `proxy-providers.url`。Stash 优先使用 `HEAD` 请求获取这些信息。

机场接口需要返回有效的 `Subscription-Userinfo`，仅返回节点内容无法提供流量和到期时间。官方文档没有明确说明首页如何展示多个覆写中新增的代理集，因此这里不保证每个机场都有独立首页卡片。节点列表加载成功与首页订阅卡显示需要分别检查。

主配置采用本地文件导入，保持没有定时更新地址。通过 GitHub URL 导入会使 GitHub 更新来源参与订阅信息的优先判断，该地址没有机场的订阅响应头。

## 图标集

全部 24 个策略组使用仓库内的圆角方形 PNG。图标为 256 × 256 像素，统一白色底板、透明外边缘和标志区域，保留应用标志原色。地区与对应流媒体组共用旗帜或地图图片。配置通过 `icon` 字段引用图片，符合 [Stash 策略组图标文档](https://stash.wiki/configuration/proxy-group-icon)。

[一键导入 Stash 图标集](https://link.stash.ws/install-icon-set/raw.githubusercontent.com/SivonLi/proxy-config/configs/stash/icons/stash.json)。也可以在图标集导入页面填写此地址：

```text
https://raw.githubusercontent.com/SivonLi/proxy-config/configs/stash/icons/stash.json
```

[stash.json](icons/stash.json) 包含全部 24 个策略组的图标名称和 HTTPS 地址，共用 18 张图片，保存在 [icons/rounded](icons/rounded)。`stash.yaml` 已引用这些图片；更新主配置即可使用，导入图标集后也可以在其他配置中手动选择。导入链接依据 [Stash URL Schema 文档](https://stash.wiki/faq/url-schema)。

AI 使用 Apple 开发者网站的 Apple Intelligence 图标，Lark 使用官方 App Store 图标。Spotify 使用[官方品牌资源](https://developer.spotify.com/documentation/design)中的标志，Apple 和 Microsoft 使用官方 GitHub 组织标志。默认代理、下载和地区旗帜来自 [Koolson/Qure](https://github.com/Koolson/Qure)，遵循来源署名与个人非商业使用要求。各品牌图标的权利归原权利人所有，完整下载地址见 [sources.json](icons/sources.json)。

GitLab 使用[官方品牌资源](https://about.gitlab.com/press/press-kit/)中的彩色标志。测速、欧洲、东南亚和“其他地区”图标来自 Qure 彩色图标集。`sources.json` 的 `groups` 字段记录多个策略组共用同一张图片的关系。

使用 ImageMagick 7 重新生成图标：

```powershell
pwsh -File stash/icons/build.ps1 -Magick magick
```

脚本使用 PowerShell 7 下载来源图片，等比例缩放到 176 × 176 像素区域，在 sRGB 色彩空间中合成到 232 × 232 像素的白色圆角底板上。全部图片共用 52 像素圆角和 12 像素透明外边距。Spotify 取自官方资源中完整的圆形标志区域，裁剪位置记录在 `sources.json`。源文件缓存在 `.work/icon-sources/`，生成结果保存在 `icons/rounded/`。图片地址的 `v` 参数用于更新客户端缓存。

在 PowerShell 中调用脚本时，可通过 `-Id gitlab,europe` 指定需要生成的图片；添加 `-UseCachedSources` 后只读取已有来源缓存，缓存缺失时立即报告错误。

## 分流行为

通用规则使用 [SukkaW/Surge](https://github.com/SukkaW/Surge) 发布的 Clash 格式文件。

| 流量 | 默认出口 |
| --- | --- |
| `guorenpcic.com` 及其子域名 | DIRECT；Windows 配合系统代理绕过与 aTrust 路由 |
| 秋风完整规则中的目标，公司域名除外 | REJECT，提前拦截 |
| 局域网域名与私有地址 | DIRECT |
| 1Password 专用服务、更新与附件 | DIRECT |
| AI 与 Apple Intelligence | AI，初始选择美国 |
| Lark 专用服务域名 | Lark，初始选择日本 |
| Spotify | Spotify，初始使用默认代理 |
| 美国、欧洲、日本、韩国、香港、台湾流媒体及 Bilibili 国际版 | 各自的策略组，初始出口见下表 |
| 其他流媒体 | 默认代理 |
| Telegram | 默认代理 |
| Apple 中国服务与 Apple CDN | DIRECT |
| 其他 Apple 服务 | Apple，初始为 DIRECT |
| Microsoft CDN | DIRECT |
| 其他 Microsoft 服务 | Microsoft，初始为 DIRECT |
| 规则中的下载站点 | 下载，初始选择香港，可选择 DIRECT |
| GitLab 公共服务 | GitLab，初始选择日本 |
| Speedtest 等测速服务 | 测速，初始为 DIRECT，可手动选择地区 |
| 网易云音乐域名与专用 IP | DIRECT |
| 通用 CDN 域名与 IP | 默认代理；服务专用规则和国内域名优先 |
| 国内域名、解析后属于中国 IP 的其余域名 | DIRECT |
| Sukka 境外服务域名与其余流量 | 默认代理 |

域名规则先于 IP 规则，国内域名集合优先于通用境外服务集合。规则范围和加载顺序依据 [Sukka 的使用说明](https://github.com/SukkaW/Surge#readme)。`domestic` 是人工维护的常见国内服务集合，中国 IP 集合用于判断域名集合尚未收录的国内服务。

未命中域名规则的连接进入 IP 规则阶段。首个局域网 IP 集合允许触发真实地址解析，后续服务 IP 集合复用解析结果。中国 IPv4、IPv6 集合允许解析，命中中国地址时直连，其余连接使用默认代理。通用 CDN 同时使用 `domainset/cdn`、`non_ip/cdn` 和 `ip/cdn`，按 Sukka 的建议分配给默认代理。

已命中代理域名规则的 TCP 连接直接交给所选节点，不进入后面的中国 IP 判断。域名集合尚未收录的国内服务通过国内 DoH 获取地址，再由中国 IP 集合判断是否直连。真实解析对这部分连接仍然必要，不能给全部 IP 规则统一添加 `no-resolve`。

明确指定代理的 Lark、AI、流媒体、Telegram、下载和境外服务域名，按各自规则访问。域名集合、地址归属数据和服务部署都可能变化，这套规则无法保证所有中国应用的每个请求都直连。

1Password 使用 `onepassword` 内嵌域名集合，固定选择 `DIRECT`，优先于下载和通用境外服务规则。专用域名取自 Sukka 的 `global`、`download` 和 `cdn`，并按 [1Password 官方网络清单](https://support.1password.com/ports-domains/)补充 `1infra.net`。集合包含 9 个域名后缀和 2 个精确域名，覆盖美国、欧洲、加拿大账号服务，以及附件、更新、图标和社区，随本配置维护。共享第三方服务继续使用通用分流。

Lark 集合使用[官方防火墙域名清单](https://www.larksuite.com/hc/en-US/articles/360044784554-configure-organization-firewall-domain-and-ip-allowlist)中的 6 个专用域名，覆盖 `larksuite.com`、`larksuite-us.com`、`larksuitecdn.com`、`larksuitepkg.com`、`larkenterprise.com` 和 `baseopendevx.com` 及其子域名。集合优先于通用服务规则，随本配置维护。其他共享服务域名和直接访问 IP 的连接继续按通用规则处理。

Spotify 的 17 个域名、1 个关键词和 1 个 IP 条目来自 [Sukka 的 Spotify 定义](https://github.com/SukkaW/Surge/blob/master/Source/stream.ts#L630)。域名和 IP 使用 Stash inline 集合，关键词使用单独规则，均优先于通用流媒体集合。内嵌条目随本配置维护。Apple 和 Microsoft 规则优先于通用流媒体集合，Apple Intelligence 使用 AI 分组。

Apple 的 `icloud.com`、`icloud-content.com` 和推送服务使用 Apple 分组，初始选择 `DIRECT`。更新配置后，需要在策略页面确认 Apple 的当前选择；已保存的选择可能继续生效。

Sukka 的 `direct` 集合包含 macOS 下载工具等程序的 `PROCESS-NAME` 条目。连接匹配到这些条目时会直连，iOS 忽略进程条目。

### 地区流媒体

地区流媒体组均为手动选择，选项为地区分类。规则优先于通用流媒体集合，Apple、Microsoft 和 Spotify 的专用策略继续优先生效。

| 策略组 | Sukka 集合 | 初始出口 | 上游收录示例 |
| --- | --- | --- | --- |
| 美国流媒体 | `stream_us` | 美国 | Hulu、Paramount+、Peacock、Tubi |
| 欧洲流媒体 | `stream_eu` | 欧洲 | BBC、ITV |
| 日本流媒体 | `stream_jp` | 日本 | Abema、Hulu Japan、TVer、niconico |
| 韩国流媒体 | `stream_kr` | 韩国 | Naver TV |
| 香港流媒体 | `stream_hk` | 香港 | myTV SUPER、ViuTV、Now E |
| 台湾流媒体 | `stream_tw` | 台湾 | 巴哈姆特、KKTV、LiTV |
| 东南亚流媒体 | `stream_biliintl` | 新加坡 | Bilibili 国际版 |

欧洲流媒体默认使用欧洲节点分类，韩国流媒体默认使用韩国节点分类。欧洲组按延迟自动选择英国、德国、荷兰等国家的节点。BBC、ITV 等服务可能要求英国出口，欧洲组选择其他国家时不保证播放权限。

“其他地区”的节点选择由所有引用它的策略组共用。修改该组的节点，会影响当前选择“其他地区”的全部策略组。节点名称决定归类；没有地区标记的节点也会进入该组，需要核实其真实出口。

Hulu Japan 同时出现在日本与美国集合，日本集合优先。Bilibili 国际版的专用集合优先于香港集合。香港与台湾集合共同收录的 HBO Asia 域名使用香港流媒体策略，可在该策略中手动选择台湾出口。

Netflix、Disney+、YouTube 等通用服务继续使用默认代理。测速集合优先于 Apple 服务集合，以便指定 `networkQuality` 的测速出口；它不包含与 Netflix 共用基础设施的 `fast.com`。地区分流只指定出口，播放权限仍由账号、内容地区和节点的解锁能力决定。

### Sukka 规则覆盖

配置直接引用 39 个 Sukka 集合。公共分流覆盖通用服务、CDN、下载、测速、GitLab、六个地区的流媒体、Bilibili 国际版、网易云 IP、Telegram CIDR 与 ASN，以及 Fake-IP 真实地址例外。大型域名列表使用 `domain`，中国地址使用 `ipcidr`；包含关键词、通配符、进程名或 ASN 的集合保留上游 `classical` 格式。

以下公共子集通过已有集合覆盖，并沿用对应出口：

| 公共子集 | 当前覆盖方式 |
| --- | --- |
| `game-download` | `download-domain`，使用下载策略 |
| `domestic_cdn` | `domestic`，DIRECT |
| `neteasemusic` 域名 | `domestic`，DIRECT；专用 IP 单独订阅 |
| `icloud_private_relay` 域名 | Apple 规则，初始为 DIRECT |
| `teleproto` | 与 `telegram` IP 集合相同，使用默认代理 |

七个地区流媒体 IP 文件当前只有作者标识条目。通用流媒体 IP 集合提供实际 IP 分流。去广告使用秋风完整规则，Sukka 的个人 `my_*`、额外拦截和 Surge 模块不在这份公共分流配置的覆盖范围内。规则来自持续更新的上游，覆盖范围需要随集合内容变化检查。

## 去广告

主配置通过 `awavenue` 规则集合订阅 [AWAvenue 秋风完整规则](https://github.com/TG-Twilight/AWAvenue-Ads-Rule)。使用官方的 `AWAvenue-Ads-Rule-Clash-Classical.yaml`，保留精确域名、域名后缀和关键词条目。规则每 86400 秒更新一次，并保存本地缓存。

完整规则包含广告、隐私跟踪和“不受欢迎”三类，后者涉及部分推送、强制更新、云控与 PCDN 服务。命中的请求会被拒绝，因此相关应用的通知、更新或其他功能可能受到影响。拦截范围随上游更新；该配置无需为去广告启用 HTTPS 解密或脚本。

拦截规则使用 `REJECT,pre-matching`。在能够匹配域名的 DNS 阶段返回空应答；其他符合条件的连接在入口阶段提前拒绝，减少连接处理。使用条件与匹配阶段见 [Stash 规则类型文档](https://stash.wiki/rules/rule-types)。

广告条件明确排除 `corporate-domains`，公司域名继续使用系统 DNS 和 `DIRECT`。提前拦截独立于普通规则顺序：其他 `DIRECT` 规则不能放行已被提前拦截的目标。DNS 的 53 端口限制仍按原有范围生效。

在“远程资源”查看 `awavenue` 的更新时间，确认规则已加载。提前拒绝的请求不进入连接列表，可通过核心日志中的 `pre-matched` 记录，或 [HTTP API](https://stash.wiki/features/http-api) 的 `/rules/match` 查询目标、命中规则和 `stage`。排查功能异常时需要记录实际请求域名和命中结果。

## 公司 VPN（Windows）

公司域名沿用 [mihomo 覆写](../mihomo/AIsouler.js)中的 `guorenpcic.com`。主配置通过 `corporate-domains` 集合统一管理分流、`nameserver-policy` 和 `fake-ip-filter`：公司域名交给系统 DNS 解析，返回真实 IP，并优先匹配 `DIRECT`。字段用法见 [Stash DNS 文档](https://stash.wiki/features/dns-server)。aTrust 负责建立公司 VPN、提供内网解析能力和业务路由。

安装新设备或重新安装 Stash 时，按 [Windows 公司 VPN 配置指南](windows-vpn.md)完成系统代理绕过、5 条网段排除和开关设置。指南提供可复制的完整绕过列表、操作位置、验证命令和故障检查方法。这些 Windows 设置保存在本机，需要与 YAML 主配置一起配置。

## DNS 与接管范围

配置使用 Stash 默认的 Fake-IP、加密 Bootstrap 和独立节点 DNS。内置 DNS 的 `nameserver`、`default-nameserver` 和 `proxy-server-nameserver` 均使用 `https://223.5.5.5/dns-query`。`follow-rule: false` 让这些查询直接出站，减少 DNS 请求进入分流引擎的处理。具体语义见 [Stash DNS 文档](https://stash.wiki/features/dns-server)。

| 查询用途 | 解析方式 | 出口 |
| --- | --- | --- |
| 公司域名 `guorenpcic.com` 及其子域名 | system，由系统和 aTrust 提供解析 | 系统解析通道 |
| 机场节点域名、DNS Bootstrap | 阿里 DoH | 独立直连通道 |
| 需要直连的服务、局域网真实解析 | 阿里 DoH | DIRECT |
| 未命中域名规则、需要判断 IP 的连接 | 阿里 DoH | DIRECT |
| 命中代理域名规则的 TCP 连接 | 将目标域名交给代理节点解析 | 对应策略组最终选中的节点 |
| UDP 代理连接的目标域名 | Stash 经代理查询，默认使用 `1.0.0.1` | 对应代理节点 |

Fake-IP 把应用得到的地址与目标域名关联起来。对于支持域名转发的代理 TCP 连接，节点使用自己的 DNS 解析目标，让 CDN 按代理出口调度。Lark 选择日本、AI 选择美国时，各自通过对应节点解析和访问。Apple、Microsoft 或下载选择 `DIRECT` 时，使用国内 DoH 获取适合本地出口的地址。原理参考 [Sukka 关于 DNS、CDN 与 Fake-IP 的文章](https://blog.skk.moe/post/lets-talk-about-dns-cdn-fake-ip/)，Stash 官方也在[性能建议](https://stash.wiki/faq/effective-stash)中推荐中国用户使用国内 DNS。

IP 规则阶段得到的地址用于判断出口。使用支持域名转发的 TCP 代理时，最终仍交给节点解析目标。DNS 服务器使用 IP 地址，机场节点域名通过独立通道解析，启动代理不依赖已经建立的代理连接。

公共 DNS 上游查询使用 DoH，保持 TLS 证书校验。公司域名使用 `system` 例外，可能使用 UDP / TCP 53，其解析路径与传输保护由系统和 aTrust 决定。国内解析服务可以看到其他直连域名、节点域名和需要判断 IP 的未知域名查询。未知境外域名也可能进入 IP 判断阶段。机场节点端的 DNS 由机场控制。

**UDP 代理解析有独立限制。** 根据 [Stash 协议文档](https://stash.wiki/proxy-protocols/proxy-types)，Stash 转发 UDP 时需要目标 IP，会通过代理发起 DNS 查询；`udp-nameserver` 仅支持 UDP。使用加密代理时，本机到节点这一段由代理保护，节点到 DNS 服务器这一段仍可能使用明文 UDP 53。`dns.nameserver` 中的 DoH 无法保证这一段也加密。WireGuard、MASQUE 等隧道协议还有各自的 DNS 配置，使用此类机场节点时需要单独核查。

规则首条为 `DST-PORT,53,REJECT,pre-matching`，阻止进入 Stash 分流引擎的 TCP、UDP 53 端口连接，覆盖 IPv4 和 IPv6。`pre-matching` 是 3.7 新增的提前拒绝选项：iOS 在读取连接数据前拒绝，UDP 在首个数据包阶段拒绝，从而减少连接处理。Stash 内置 DNS 服务按上述公共 DoH 和公司域名 policy 处理查询。这条规则的控制范围是进入分流引擎的连接，不包括系统绕过流量、公司 VPN 内的独立 DNS 通信和机场服务器自己的 DNS 请求。选项语义与支持的规则类型见 [规则类型文档](https://stash.wiki/rules/rule-types)。

提前拒绝的请求不会出现在连接列表中。核心日志按目标限制记录频率；需要确认匹配阶段时，可使用 [HTTP API](https://stash.wiki/features/http-api) 的 `/rules/match` 查看 `stage` 字段。

仅由路由器或公司 DNS 解析的内网域名，公共 DoH 通常无法解析。当前公司域名通过专用 policy 使用系统解析。其他内网域名可以通过 `hosts` 指定地址，或为其单独配置可用的内网 DNS；内网 DNS 支持 DoH、DoT 或 DoQ 时可使用对应的加密协议。发给公共 DoH 的内网域名会对该解析服务可见。

顶层 `ipv6: false` 让 Stash 自身只解析 IPv4，`dns.ipv6: false` 让应用 DNS 查询不返回 AAAA 记录。这两个设置控制 DNS 解析，直接访问 IPv6 地址的流量仍需要 Tunnel IPv6 路由接管。

Fake-IP 的真实地址例外包含公司域名、局域网集合和 Sukka 的 `clash_fake_ip_filter`，覆盖 `.m2m`、`.bogon` 与 AdGuard 本地辅助域名。该集合只影响 DNS 返回真实地址的范围。公共 DNS 的每种查询用途配置一个 DoH 上游，公司域名由系统解析。Stash 自带乐观 DNS 缓存，缓存过期时继续使用已有结果，并在后台更新。

DNS 出口检测网站展示的是递归 DNS 访问权威 DNS 时的出口。出现国内解析器与本配置的国内直连、未知域名 IP 判断可以一致，单凭这个结果无法判定设备发生了明文 DNS 泄漏。检查时需要结合目标域名、命中规则、实际代理节点，以及设备是否向外发送了明文 53 端口请求。

**还需要完成 Stash 界面设置：**

- macOS 开启“增强模式”，让 Stash 接管应用流量。仅使用系统代理时，部分应用和 UDP 流量可能直接访问网络。
- 设备使用 IPv6 网络时，按照 [IPv6 文档](https://stash.wiki/faq/ipv6-compatible)在“网络设置”启用 Tunnel IPv6 路由，让直接访问 IPv6 DNS 地址的连接也进入 53 端口拦截规则。
- 在按需连接中开启“保持 Stash 开启”，保持各个网络下的接管。规则中保留局域网直连，无需为整个 Wi-Fi 停止 Stash。
- 导入后确认其他覆写没有替换本文件的 DNS 配置。

独立 DoH 应用、浏览器安全 DNS、iCloud Private Relay、其他 VPN 和应用自己的网络机制，会影响实际 DNS 出口。需要采用本配置 DNS 策略的应用，应关闭自行指定的 DNS。mDNS、Bonjour 和系统绕过隧道的通信超出这里的上游 DNS 与 53 端口规则范围。Stash 停止、系统绕过隧道、订阅为空时，配置无法提供完整的断网保护。Stash 会把空的远程节点集合视为 `DIRECT`，因此导入和更新后需要确认节点集合正常。

## 省电设置

“默认代理”、服务分组、地区流媒体和“其他地区”使用手动选择，通过 `interval: -1` 关闭这些分组的定时测速。香港、日本、美国、新加坡、台湾、韩国和欧洲使用 `url-test`，每 600 秒测速，并设置 `lazy: true`，一段时间未使用的地区跳过自动测速。

地区分组自动选择可用的低延迟节点。`tolerance: 50` 表示新节点比当前节点快超过 50 ms 才会切换；当前节点测速失败时立即切换。机场远程代理集使用 `https://www.gstatic.com/generate_204`，超时为 5 秒。测速结果表示连通性和延迟，不能表示下载带宽或服务解锁能力。具体语义见 [策略组文档](https://stash.wiki/proxy-protocols/proxy-groups)、[延迟测试文档](https://stash.wiki/proxy-protocols/proxy-benchmark)和 [远程代理集文档](https://stash.wiki/proxy-protocols/proxy-providers)。

已启用机场的远程代理集和规则集合每 86400 秒更新一次。规则集合指定本地缓存路径。每种 DNS 用途只配置一个上游，减少重复查询。较大的域名和中国 IP 集合使用 `domain` / `ipcidr` 格式，其余集合保留官方的 `classical` 格式。

在 Stash 界面关闭“混合使用多个网络”和“并发连接”。保持正常日志等级，日常配置使用 `warning`。这些措施减少额外连接与网络请求，实际耗电仍取决于节点协议、信号质量、应用流量和系统状态。

规则结构与资源使用依据 [规则集合文档](https://stash.wiki/rules/rule-set)、[性能建议](https://stash.wiki/faq/effective-stash)和 [网络优化说明](https://stash.wiki/features/network-performance-enhance)。

## 验证范围

检查脚本为 [check_config.py](check_config.py)，依赖清单为 [requirements-check.txt](requirements-check.txt)。在工作区根目录运行：

```powershell
python -m pip install -r stash/requirements-check.txt
python stash/check_config.py
python stash/check_config.py --online --proxy http://127.0.0.1:7890
```

`--proxy` 仅用于下载公开规则，DoH 检查不指定 HTTP 代理。代理端口按本机配置填写。联网检查会访问真实公开服务；解析结果变化时，脚本直接报告失败。

本地配置与上游联网检查最近验证于 2026-11-05：

- 12 项本地检查通过，涵盖主配置与机场模板的 YAML 解析、重复键、分组引用、地区过滤表达式、内置 DNS 加密、Fake-IP 例外、域名与 IP 规则顺序、流媒体优先级、机场覆写范围和图标集。
- 8 个节点分类通过 `include-all: true` 汇集节点，7 个地区自动测速，“其他地区”手动选择。主配置的 `proxy-providers` 为空字典。机场模板只定义一个代理集及展示字段，名称通过 YAML 锚点复用，订阅地址为占位值。
- 公共 DNS 上游均为 HTTPS DNS，只有公司域名 policy 使用 `system`。`follow-rule` 关闭，两个 IPv6 解析开关关闭，53 端口提前拦截位于全部分流规则之前。
- 配置包含 40 个远程集合与 5 个 inline 集合，引用检查通过。远程集合已通过规则类型和 CIDR 格式检查；Sukka `non_ip` 集合中附带的 IP 条目均包含 `no-resolve`，不会自行触发域名解析。
- Windows 已加载 24 个策略组与全部 45 个规则集合。22 个目标的核心规则诊断通过，覆盖地区流媒体、CDN、GitLab、测速、下载 IP、网易云 IP、Telegram 和原有国内服务。检查验证了规则与出口选择，未执行流媒体账号登录或视频播放。
- “其他地区”的实际节点与各自动地区组互不重复，订阅提示项未进入节点分类。韩国和欧洲流媒体分别选择对应地区组，英国、德国、荷兰等节点统一归入欧洲。
- 秋风完整规则下载与 YAML 解析通过，Windows 已加载全部 976 条，包含 960 条精确域名、12 条域名后缀和 4 条关键词规则。`ad-api.4pyun.com` 与 `unityads.unity3d.com` 在规则诊断中命中提前拒绝，广告条件明确排除公司域名集合。
- Windows 0.1.47 已加载主配置。公司域名命中 `corporate-domains`，Stash DNS API 确认解析来源为 `system`。本机使用系统代理绕过和 5 条隧道网段排除，内网 HTTP 请求返回 `200`。
- 1Password 的 11 个域名条目使用 `domain` 集合，直连规则优先于下载和通用境外服务规则。
- 山姆的 `api-sams.walmartmobile.cn`、`decoration-sams.walmartmobile.cn` 通过国内 DoH 返回 `157.148.16.212`，属于 Sukka 中国 IP 集合。
- 万达的 `cinema-api-prd-mx.wandafilm.com`、`misc-api-prd-mx.wandafilm.com` 通过国内 DoH 返回 `120.53.82.119`，属于 Sukka 中国 IP 集合。
- `223.5.5.5` 在不指定 HTTP 代理时，为 8 个业务域名返回有效的 DoH 答案，验证过程保持 TLS 证书校验。

上游联网检查验证了规则服务与 DoH 的可用性；公司内网检查还验证了 Stash 的实际 DNS policy、Windows 系统代理绕过和 aTrust 路由。HTTP 检查未执行公司系统的账号登录或业务操作。

当前工作区位于 Windows，没有 Apple 平台的 Stash 运行环境。Windows 的验证范围见上文；iOS、macOS 的 VPN 共存和设备耗电尚未实测。

iMessage 图片上传速度需要结合发送时的连接记录判断，记录应包含上传域名、命中规则和实际出口。当前没有 iMessage 的连接记录，无法确认其速度问题的原因。

配置参考了 [LumexOverwrite](https://github.com/int-del/LumexOverwrite)和 [Clash Configuration Template](https://github.com/Accademia/Clash_Configuration_Template)。Stash 字段以官方文档为依据。
