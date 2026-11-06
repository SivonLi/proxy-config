# Stash 配置

## 导入与选择节点

使用 [stash.yaml](stash.yaml) 作为主配置，导入 [Subscribe.stoverride](Subscribe.stoverride) 读取 Sub-Store 的 `Subscribe` 集合。在 Stash 的覆写页面，通过“Sub-Store 订阅”开关启用或停用该集合。适用于 iOS Stash 3.7.0，包括在 Apple silicon Mac 上运行的 iOS 版。原生 Stash for Mac 需要 4.4 及以上版本。Windows 已在 0.1.47 验证公司内网访问，需要同时完成 [Windows 公司 VPN 配置指南](windows-vpn.md)中的设置。规则预匹配功能在当前官方文档中仍标注为 Beta。

1. 下载下方的 `stash.yaml`，在 Stash 的配置页面通过本地文件导入，设为当前主配置。
2. 下载 `Subscribe.stoverride`。显示名称固定为“Sub-Store 订阅”，代理集名称为 `Sub-Store-Subscribe`，订阅地址为 `http://sub.store/download/collection/Subscribe?target=Stash`。使用该地址的设备需要能够访问 Sub-Store 的 `Subscribe` 集合。
3. 在 Stash 的覆写页面通过本地文件导入 `Subscribe.stoverride`，启用“Sub-Store 订阅”。该开关控制集合内的全部节点。
4. 停用与主配置冲突的 DNS、策略组或分流覆写。公司内网按下方说明启用 `aTrust.stoverride`。至少启用一个机场，启动 Stash，等待机场节点与规则下载成功。
5. 在“默认代理”手动选择香港、日本、美国、新加坡、台湾、韩国、欧洲或“其他地区”，初始地区为香港。所选地区需要包含可用节点。

```text
https://raw.githubusercontent.com/SivonLi/proxy-config/configs/stash/stash.yaml
https://raw.githubusercontent.com/SivonLi/proxy-config/configs/stash/Subscribe.stoverride
```

AI 初始选择新加坡，选项排除香港。Lark 仅提供日本和“默认代理”，初始选择日本。Apple 提供 `DIRECT`、“默认代理”和美国，初始选择 `DIRECT`。Microsoft 仅提供 `DIRECT` 与“默认代理”，初始选择 `DIRECT`。下载仅提供“默认代理”与 `DIRECT`，初始选择“默认代理”。测速初始选择 `DIRECT`，可以手动选择地区。

香港、日本、美国、新加坡、台湾、韩国和欧洲根据测速结果自动选择节点。欧洲包含英国、德国、荷兰等节点。“其他地区”使用 `select`，由你手动指定节点，通过 `interval: -1` 关闭该组自身的定时测速。它收纳上述地区以外的节点，过滤流量余额、套餐到期和重置时间等订阅提示项，并排除独立的 `aTrust` 内网节点。首次使用“其他地区”时，需要手动选择机场节点；初始的 `REJECT` 用于空组保护。

各机场的远程代理集从 Clash 订阅中读取 `proxies` 节点列表。8 个节点分类通过 `include-all: true` 汇集节点，再按名称过滤。增加机场或修改机场名称时，只需编辑对应的机场覆写。字段用法见 [Stash 远程代理集文档](https://stash.wiki/proxy-protocols/proxy-providers)和 [策略组文档](https://stash.wiki/proxy-protocols/proxy-groups)。

DNS、策略组、规则集合、分流规则和图标由主配置管理。每份机场覆写只添加一个远程代理集，以及供覆写页面显示的名称、说明和分类。机场订阅中的其他顶层配置不会参与分流，节点内部的协议和连接参数仍由机场提供。可选的 [aTrust.stoverride](aTrust.stoverride) 单独管理公司内网节点、公司规则和对应 DNS 调整。

更新主配置时，下载新的 `stash.yaml` 并重新通过本地文件导入，保留设备上的机场覆写。机场订阅地址保存在各自的本地覆写中，节点和规则集合按配置中的周期独立更新。

机场订阅地址包含凭证，请保存在自己的设备中。工作区的 `.gitignore` 已排除 `stash/*.local.yaml` 和 `stash/*.local.stoverride`。

### 订阅名称与开关

机场覆写统一设置 `category: '机场订阅'`，在覆写页面按“机场订阅”分类管理。已导入的本地覆写可以直接在文件顶层添加这一行。

`Subscribe.stoverride` 的显示名称固定为“Sub-Store 订阅”，代理集名称为 `Sub-Store-Subscribe`。显示名称用于覆写页面，代理集名称用于合并节点订阅。Sub-Store 的 `Subscribe` 集合可以包含多个机场的节点，该覆写统一控制整个集合。

每个机场必须使用不同名称。Stash 会递归合并不同覆写中的 `proxy-providers`；同名代理集会合并或覆盖，无法作为两个独立机场管理。机场覆写采用普通字典合并，具体语义见 [覆写文档](https://stash.wiki/configuration/override)。

在覆写页面启用机场后，它的节点参与各地区组的筛选。7 个自动地区组按需测速，“其他地区”保留手动选择。关闭该机场的覆写并应用配置后，它的代理集从当前配置中移除。开关控制整份机场订阅，可以同时启用多个机场。

8 个节点分类均显式包含 `REJECT`，地区过滤保留 `REJECT` 并排除 `DIRECT`。全部机场关闭或某个地区没有匹配节点时，该地区仍有拒绝出口，无法通过空组转换为直连。地区流媒体使用隐藏的 `fallback`，在优先地区不可用时尝试指定备用地区，具体设置见“地区流媒体”。其他直接引用地区的服务需要保持所选地区有可用节点。每份模板均未指定固定缓存路径，复制模板时无需另行维护缓存文件名。

机场节点协议必须得到 Stash 支持。机场需要专用 DNS 时，该服务器必须支持加密 DNS；必要的 DNS 和 `hosts` 设置可以填写在自己的本地配置中。

地区分组通过节点名称识别中文地区名、英文名称、常见代码和旗帜。请在地区分组中确认机场节点已正确归类。节点命名不符合规则时，需要调整相应 `filter`，同时保留 `REJECT` 并排除 `DIRECT`。

### 首页订阅信息

首页流量和到期时间来自机场响应头中的 `Subscription-Userinfo`。根据 [Stash 服务提供商订阅文档](https://stash.wiki/features/service-provider-subscription)，Stash 优先读取主配置的定时更新地址；没有更新地址时，读取主配置中的 `proxy-providers.url`。Stash 优先使用 `HEAD` 请求获取这些信息。

机场接口需要返回有效的 `Subscription-Userinfo`，仅返回节点内容无法提供流量和到期时间。官方文档没有明确说明首页如何展示多个覆写中新增的代理集，因此这里不保证每个机场都有独立首页卡片。节点列表加载成功与首页订阅卡显示需要分别检查。

主配置采用本地文件导入，保持没有定时更新地址。通过 GitHub URL 导入会使 GitHub 更新来源参与订阅信息的优先判断，该地址没有机场的订阅响应头。

## 图标集

全部 15 个展示组使用仓库内的圆角方形 PNG，6 个隐藏的流媒体辅助组不设置图标。图标为 256 × 256 像素，统一白色底板、透明外边缘和标志区域，保留应用标志原色。配置通过 `icon` 字段引用图片，符合 [Stash 策略组图标文档](https://stash.wiki/configuration/proxy-group-icon)。

[一键导入 Stash 图标集](https://link.stash.ws/install-icon-set/raw.githubusercontent.com/SivonLi/proxy-config/configs/stash/icons/stash.json)。也可以在图标集导入页面填写此地址：

```text
https://raw.githubusercontent.com/SivonLi/proxy-config/configs/stash/icons/stash.json
```

[stash.json](icons/stash.json) 包含全部 15 个展示组的图标名称和 HTTPS 地址，图片保存在 [icons/rounded](icons/rounded)。`stash.yaml` 已引用这些图片；更新主配置即可使用，导入图标集后也可以在其他配置中手动选择。导入链接依据 [Stash URL Schema 文档](https://stash.wiki/faq/url-schema)。

AI 使用 Apple 开发者网站的 Apple Intelligence 图标，Lark 使用官方 App Store 图标。Apple 和 Microsoft 使用官方 GitHub 组织标志。默认代理、下载和地区旗帜来自 [Koolson/Qure](https://github.com/Koolson/Qure)，遵循来源署名与个人非商业使用要求。各品牌图标的权利归原权利人所有，完整下载地址见 [sources.json](icons/sources.json)。

测速、韩国、欧洲和“其他地区”图标来自 Qure 彩色图标集。

使用 ImageMagick 7 重新生成图标：

```powershell
pwsh -File stash/icons/build.ps1 -Magick magick
```

脚本使用 PowerShell 7 下载来源图片，等比例缩放到 176 × 176 像素区域，在 sRGB 色彩空间中合成到 232 × 232 像素的白色圆角底板上。全部图片共用 52 像素圆角和 12 像素透明外边距。源文件缓存在 `.work/icon-sources/`，生成结果保存在 `icons/rounded/`。图片地址的 `v` 参数用于更新客户端缓存。

在 PowerShell 中调用脚本时，可通过 `-Id korea,europe` 指定需要生成的图片；添加 `-UseCachedSources` 后只读取已有来源缓存，缓存缺失时立即报告错误。

## 分流行为

通用规则使用 [SukkaW/Surge](https://github.com/SukkaW/Surge) 发布的 Clash 格式文件。

| 流量 | 默认出口 |
| --- | --- |
| `guorenpcic.com` 及其子域名 | 主配置为 DIRECT；启用公司内网覆写后，业务请求使用 aTrust 节点，VPN 网关直连 |
| Sukka 与秋风拦截域名，公司域名除外 | REJECT / REJECT-DROP，提前拦截 |
| 搜狗输入法上报域名与进程 | REJECT，普通匹配 |
| Sukka 恶意 IP 与 DNS 劫持地址，私有地址除外 | REJECT-DROP，在 IP 阶段匹配 |
| 局域网域名与私有地址 | DIRECT |
| 1Password 专用服务、更新与附件 | DIRECT |
| AI 与 Apple Intelligence | AI，初始选择新加坡 |
| Lark 专用服务域名 | Lark，初始选择日本 |
| Spotify | 通用流媒体规则，使用默认代理 |
| 美国、欧洲、日本、韩国、香港、台湾流媒体及 Bilibili 国际版 | 优先对应地区，不可用时使用指定备用地区，见下表 |
| 其他流媒体 | 默认代理 |
| Telegram | 默认代理 |
| Apple 中国服务与 Apple CDN | DIRECT |
| 其他 Apple 服务 | Apple，初始为 DIRECT |
| Microsoft CDN | DIRECT |
| 其他 Microsoft 服务 | Microsoft，初始为 DIRECT |
| 规则中的下载站点与 IP | 下载，初始选择默认代理，可选择 DIRECT |
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

Spotify 的域名、关键词和 IP 由 Sukka 的通用 `stream` 与 `stream-ip` 集合覆盖，使用默认代理并随远程集合更新。Apple 和 Microsoft 规则优先于通用流媒体集合，Apple Intelligence 使用 AI 分组。

Apple 的 `icloud.com`、`icloud-content.com` 和推送服务使用 Apple 分组，初始选择 `DIRECT`。更新配置后，需要在策略页面确认 Apple 的当前选择；已保存的选择可能继续生效。

Sukka 的 `direct` 集合包含 macOS 下载工具等程序的 `PROCESS-NAME` 条目。连接匹配到这些条目时会直连，iOS 忽略进程条目。

### 地区流媒体

地区流媒体通过 6 个隐藏的 `fallback` 组选择出口，每组按 `[优先地区, 备用地区]` 的顺序选择可用成员。日本、美国、欧洲、韩国和台湾使用香港备用，香港使用新加坡备用。台湾流媒体和 Bilibili 国际版共用台湾的故障切换组。

地区流媒体的备用出口按下表设置，独立于“默认代理”的手动选择。通用流媒体规则引用“默认代理”，策略页面展示 15 个组。地区规则优先于通用流媒体集合，Apple 和 Microsoft 的专用策略继续优先生效。

| 流量分类 | Sukka 集合 | 优先地区 | 备用地区 | 上游收录示例 |
| --- | --- | --- | --- | --- |
| 美国流媒体 | `stream_us` | 美国 | 香港 | Hulu、Paramount+、Peacock、Tubi |
| 欧洲流媒体 | `stream_eu` | 欧洲 | 香港 | BBC、ITV |
| 日本流媒体 | `stream_jp` | 日本 | 香港 | Abema、Hulu Japan、TVer、niconico |
| 韩国流媒体 | `stream_kr` | 韩国 | 香港 | Naver TV |
| 香港流媒体 | `stream_hk` | 香港 | 新加坡 | myTV SUPER、ViuTV、Now E |
| 台湾流媒体 | `stream_tw` | 台湾 | 香港 | 巴哈姆特、KKTV、LiTV |
| Bilibili 国际版 | `stream_biliintl` | 台湾 | 香港 | Bilibili 国际版 |

各地区组包含不可用的 `REJECT` 出口；没有机场节点时，组内仍有成员，流量不会通过空组转换为直连。有可用节点时，地区的 `url-test` 选择低延迟节点；所有节点被判定不可用后，外层 `fallback` 尝试指定备用地区。`fallback` 每 600 秒检查一次，并启用 `lazy: true`；检测到优先地区恢复后，新连接重新优先使用该地区。断线检测与切换存在等待时间，已有连接仍可能需要应用重新建立。

优先地区和备用地区都需要包含可用节点，才能分别承担首选和备用出口。两个地区全部不可用时，连接失败或被拒绝。`REJECT` 用于地区组的非空保护。分组嵌套、故障切换与定时检查依据 [Stash 策略组文档](https://stash.wiki/proxy-protocols/proxy-groups)。

欧洲组按延迟自动选择英国、德国、荷兰等国家的节点。BBC、ITV 等服务可能要求英国出口，欧洲组选择其他国家时不保证播放权限。故障切换只依据节点连通性；切换至备用地区后，播放权限仍取决于账号和节点的解锁能力。

“其他地区”的节点选择由所有引用它的策略组共用。修改该组的节点，会影响当前选择“其他地区”的全部策略组。节点名称决定归类；没有地区标记的节点也会进入该组，需要核实其真实出口。

Hulu Japan 同时出现在日本与美国集合，日本集合优先。Bilibili 国际版的专用集合优先于香港集合。香港与台湾集合共同收录的 HBO Asia 域名优先使用香港节点组，不可用时使用新加坡。

Netflix、Disney+、YouTube 等通用服务继续使用默认代理。测速集合优先于 Apple 服务集合，以便指定 `networkQuality` 的测速出口；它不包含与 Netflix 共用基础设施的 `fast.com`。地区分流只指定出口，播放权限仍由账号、内容地区和节点的解锁能力决定。

### Sukka 规则覆盖

配置直接引用 46 个 Sukka 集合。公共分流覆盖通用服务、CDN、下载、测速、六个地区的流媒体、Bilibili 国际版、网易云 IP、Telegram CIDR 与 ASN，以及 Fake-IP 真实地址例外。拦截包含基础域名、扩展域名、钓鱼网站、关键词与通配符、高频重试、PCDN、搜狗输入法和恶意 IP。大型域名列表使用 `domain`，中国地址使用 `ipcidr`；包含关键词、通配符、进程名或 ASN 的集合保留上游 `classical` 格式。

以下公共子集通过已有集合覆盖，并沿用对应出口：

| 公共子集 | 当前覆盖方式 |
| --- | --- |
| `game-download` | `download-domain`，使用下载策略 |
| `domestic_cdn` | `domestic`，DIRECT |
| `neteasemusic` 域名 | `domestic`，DIRECT；专用 IP 单独订阅 |
| `icloud_private_relay` 域名 | Apple 规则，初始为 DIRECT |
| `teleproto` | 与 `telegram` IP 集合相同，使用默认代理 |

地区流媒体使用各自的域名集合，通用流媒体 IP 集合提供实际 IP 分流。去广告与隐私保护同时使用 Sukka 公共拦截集合和秋风完整规则。规则来自持续更新的上游，覆盖范围需要随集合内容变化检查。

## 去广告

主配置订阅 [Sukka 公共拦截规则](https://github.com/SukkaW/Surge#readme)和 [AWAvenue 秋风完整规则](https://github.com/TG-Twilight/AWAvenue-Ads-Rule)。全部集合每 86400 秒更新一次，并保存本地缓存。

| 配置中的集合 | 拦截内容 | 处理方式 |
| --- | --- | --- |
| `reject-domain` | 基础广告、跟踪与恶意域名 | domain，REJECT 提前拒绝 |
| `reject-extra` | 基础集合的扩展域名 | domain，REJECT 提前拒绝 |
| `reject-phishing` | 钓鱼网站域名 | domain，REJECT 提前拒绝 |
| `reject` | 域名、关键词、通配符及无需解析的 IP | classical，REJECT 提前拒绝 |
| `reject-drop` | 高频重试的统计与推送域名 | classical，REJECT-DROP，优先提前拦截 |
| `reject-no-drop` | PCDN 等需要立即拒绝的目标 | classical，使用 Stash 的 REJECT 提前拒绝 |
| `sogouinput` | 搜狗输入法上报域名与进程 | classical，普通 REJECT |
| `reject-ip` | 恶意 IP 与 DNS 劫持地址 | classical，IP 阶段 REJECT-DROP |
| `awavenue` | 秋风完整规则 | 官方 classical YAML，REJECT 提前拒绝 |

三份 Sukka `domain` 集合当前合计约 36.9 万条，首次下载的文本约 8.3 MB。大型集合会增加下载量与内存占用，iOS、macOS 和 Windows 的实际资源占用尚未测量。每日更新、本地缓存和提前拒绝用于控制重复下载与连接处理。

秋风完整规则包含广告、隐私跟踪和“不受欢迎”三类，后者涉及部分推送、强制更新、云控与 PCDN 服务。Sukka 的搜狗输入法集合也会影响账号同步、词库更新与问题反馈。命中的请求会被拒绝，因此相关应用的通知、更新或其他功能可能受到影响。拦截范围随上游更新；该配置无需为去广告启用 HTTPS 解密或脚本。

域名拦截使用 `pre-matching`。在能够匹配域名的 DNS 阶段返回空应答；其他符合条件的连接在入口阶段提前拒绝，减少连接处理。`reject-drop` 优先于其他拦截集合，使用 `REJECT-DROP` 静默丢弃连接。使用条件与匹配阶段见 [Stash 规则类型文档](https://stash.wiki/rules/rule-types)。

搜狗输入法集合含 `PROCESS-NAME`，采用普通匹配；iOS 忽略进程条目。`reject-ip` 在全部域名规则和局域网 IP 直连规则之后执行，通过 `no-resolve` 复用已经获取的地址。主配置优先直连公司域名和私有地址；启用公司内网覆写后，公司业务由覆写优先处理。

广告条件明确排除 `corporate-domains`，公司业务域名沿用对应的公司分流与 DNS 设置。提前拦截独立于普通规则顺序：其他 `DIRECT` 规则不能放行已被提前拦截的目标。DNS 的 53 端口限制仍按原有范围生效。

在“远程资源”查看上述集合的更新时间，确认规则已加载。提前拒绝的请求不进入连接列表，可通过核心日志中的 `pre-matched` 记录，或 [HTTP API](https://stash.wiki/features/http-api) 的 `/rules/match` 查询目标、命中规则和 `stage`。排查功能异常时需要记录实际请求域名和命中结果。

## 公司 VPN（Windows）

公司域名沿用 [mihomo 覆写](../mihomo/AIsouler.js)中的 `guorenpcic.com`，由 `corporate-domains` 集合管理。主配置默认使用系统 DNS、真实 IP 和 `DIRECT`。启用 [aTrust.stoverride](aTrust.stoverride) 后，公司业务域名和 5 个公司地址范围优先使用本机 `aTrust` SOCKS5 节点，地址为 `127.0.0.1:11080`。zju-connect 独立完成公司登录与 VPN 转发。

覆写将公司域名恢复为 Fake-IP，TCP 请求携带域名进入 zju-connect。zju-connect 进程与 VPN 网关直连；内网节点关闭测速与 UDP，并从机场地区组中排除。

按 [Windows 公司内网配置指南](windows-vpn.md)启动 zju-connect、启用覆写，并删除 Windows 中的公司域名绕过和 5 条公司网段排除。开启增强模式和系统代理，让请求先进入 Stash。这些 Windows 设置独立保存在本机，不随覆写开关恢复。当前监听地址仅供 Windows 本机使用。

## DNS 与接管范围

配置使用 Stash 默认的 Fake-IP、加密 Bootstrap 和独立节点 DNS。内置 DNS 的 `nameserver`、`default-nameserver` 和 `proxy-server-nameserver` 均使用 `https://223.5.5.5/dns-query`。`follow-rule: false` 让这些查询直接出站，减少 DNS 请求进入分流引擎的处理。具体语义见 [Stash DNS 文档](https://stash.wiki/features/dns-server)。

| 查询用途 | 解析方式 | 出口 |
| --- | --- | --- |
| 公司域名，未启用公司内网覆写 | system，返回真实地址 | 系统解析通道 |
| 公司业务域名，启用公司内网覆写 | Fake-IP，TCP 域名交给 zju-connect 处理 | aTrust 节点 |
| 机场节点域名、DNS Bootstrap | 阿里 DoH | 独立直连通道 |
| 需要直连的服务、局域网真实解析 | 阿里 DoH | DIRECT |
| 未命中域名规则、需要判断 IP 的连接 | 阿里 DoH | DIRECT |
| 命中代理域名规则的 TCP 连接 | 将目标域名交给代理节点解析 | 对应策略组最终选中的节点 |
| UDP 代理连接的目标域名 | Stash 经代理查询，默认使用 `1.0.0.1` | 对应代理节点 |

Fake-IP 把应用得到的地址与目标域名关联起来。对于支持域名转发的代理 TCP 连接，节点使用自己的 DNS 解析目标，让 CDN 按代理出口调度。Lark 选择日本、AI 选择新加坡时，各自通过对应节点解析和访问。Apple、Microsoft 或下载选择 `DIRECT` 时，使用国内 DoH 获取适合本地出口的地址。原理参考 [Sukka 关于 DNS、CDN 与 Fake-IP 的文章](https://blog.skk.moe/post/lets-talk-about-dns-cdn-fake-ip/)，Stash 官方也在[性能建议](https://stash.wiki/faq/effective-stash)中推荐中国用户使用国内 DNS。

IP 规则阶段得到的地址用于判断出口。使用支持域名转发的 TCP 代理时，最终仍交给节点解析目标。DNS 服务器使用 IP 地址，机场节点域名通过独立通道解析，启动代理不依赖已经建立的代理连接。

公共 DNS 上游查询使用 DoH，保持 TLS 证书校验。主配置中的公司域名使用 `system` 例外，可能使用 UDP / TCP 53，其解析路径与传输保护由系统决定。启用公司内网覆写后，公司 TCP 请求携带域名进入 zju-connect。国内解析服务可以看到其他直连域名、节点域名和需要判断 IP 的未知域名查询。未知境外域名也可能进入 IP 判断阶段。机场节点端的 DNS 由机场控制。

**UDP 代理解析有独立限制。** 根据 [Stash 协议文档](https://stash.wiki/proxy-protocols/proxy-types)，Stash 转发 UDP 时需要目标 IP，会通过代理发起 DNS 查询；`udp-nameserver` 仅支持 UDP。使用加密代理时，本机到节点这一段由代理保护，节点到 DNS 服务器这一段仍可能使用明文 UDP 53。`dns.nameserver` 中的 DoH 无法保证这一段也加密。WireGuard、MASQUE 等隧道协议还有各自的 DNS 配置，使用此类机场节点时需要单独核查。

主配置规则首条为 `DST-PORT,53,REJECT,pre-matching`，阻止进入 Stash 分流引擎的 TCP、UDP 53 端口连接，覆盖 IPv4 和 IPv6。`pre-matching` 是 3.7 新增的提前拒绝选项：iOS 在读取连接数据前拒绝，UDP 在首个数据包阶段拒绝，从而减少连接处理。Stash 内置 DNS 服务按当前应用的 DNS 配置处理查询。这条规则的控制范围是进入分流引擎的连接，不包括系统绕过流量、公司 VPN 内的独立 DNS 通信和机场服务器自己的 DNS 请求。选项语义与支持的规则类型见 [规则类型文档](https://stash.wiki/rules/rule-types)。

提前拒绝的请求不会出现在连接列表中。核心日志按目标限制记录频率；需要确认匹配阶段时，可使用 [HTTP API](https://stash.wiki/features/http-api) 的 `/rules/match` 查看 `stage` 字段。

仅由路由器或公司 DNS 解析的内网域名，公共 DoH 通常无法解析。主配置中的公司域名通过专用 policy 使用系统解析；公司内网覆写启用后，TCP 请求通过 Fake-IP 和 SOCKS5 将域名交给 zju-connect。其他内网域名可以通过 `hosts` 指定地址，或为其单独配置可用的内网 DNS；内网 DNS 支持 DoH、DoT 或 DoQ 时可使用对应的加密协议。发给公共 DoH 的内网域名会对该解析服务可见。

顶层 `ipv6: false` 让 Stash 自身只解析 IPv4，`dns.ipv6: false` 让应用 DNS 查询不返回 AAAA 记录。这两个设置控制 DNS 解析，直接访问 IPv6 地址的流量仍需要 Tunnel IPv6 路由接管。

主配置的 Fake-IP 真实地址例外包含公司域名、局域网集合和 Sukka 的 `clash_fake_ip_filter`，覆盖 `.m2m`、`.bogon` 与 AdGuard 本地辅助域名。公司内网覆写启用后，真实地址例外仅保留局域网与 Sukka 集合，公司业务域名返回 Fake-IP。公共 DNS 的每种查询用途配置一个 DoH 上游。Stash 自带乐观 DNS 缓存，缓存过期时继续使用已有结果，并在后台更新。

DNS 出口检测网站展示的是递归 DNS 访问权威 DNS 时的出口。出现国内解析器与本配置的国内直连、未知域名 IP 判断可以一致，单凭这个结果无法判定设备发生了明文 DNS 泄漏。检查时需要结合目标域名、命中规则、实际代理节点，以及设备是否向外发送了明文 53 端口请求。

**还需要完成 Stash 界面设置：**

- macOS 开启“增强模式”，让 Stash 接管应用流量。仅使用系统代理时，部分应用和 UDP 流量可能直接访问网络。
- 设备使用 IPv6 网络时，按照 [IPv6 文档](https://stash.wiki/faq/ipv6-compatible)在“网络设置”启用 Tunnel IPv6 路由，让直接访问 IPv6 DNS 地址的连接也进入 53 端口拦截规则。
- 在按需连接中开启“保持 Stash 开启”，保持各个网络下的接管。规则中保留局域网直连，无需为整个 Wi-Fi 停止 Stash。
- 导入后确认其他覆写没有替换本文件的 DNS 配置。

独立 DoH 应用、浏览器安全 DNS、iCloud Private Relay、其他 VPN 和应用自己的网络机制，会影响实际 DNS 出口。需要采用本配置 DNS 策略的应用，应关闭自行指定的 DNS。mDNS、Bonjour 和系统绕过隧道的通信超出这里的上游 DNS 与 53 端口规则范围。Stash 停止或系统绕过隧道时，配置无法提供完整的断网保护。地区组的 `REJECT` 保护只控制通过这些组的连接，导入和更新后仍需要确认机场节点加载正常。

## 省电设置

“默认代理”、服务分组和“其他地区”使用手动选择，通过 `interval: -1` 关闭这些分组自身的定时测速。香港、日本、美国、新加坡、台湾、韩国和欧洲使用 `url-test`，每 600 秒测速，并设置 `lazy: true`，一段时间未使用的地区跳过自身的自动测速。

隐藏的流媒体 `fallback` 组使用 600 秒周期和 `lazy: true`。每个辅助组的递归测速范围仅包含优先地区和指定备用地区，用于故障切换和恢复检测。例如，日本流媒体辅助组检查日本和香港，香港流媒体辅助组检查香港和新加坡。其他地区仍可能因 AI、Lark 或其他流量独立触发测速。多个组引用同一节点时共享其测速结果；相关行为见 [延迟测试文档](https://stash.wiki/proxy-protocols/proxy-benchmark)。

地区分组自动选择可用的低延迟节点。`tolerance: 50` 表示新节点比当前节点快超过 50 ms 才会切换；当前节点测速失败时立即切换。机场远程代理集使用 `http://www.gstatic.com/generate_204`，超时为 5 秒。HTTP 测速减少目标服务器一段的 TLS 处理开销，节点协议自身的加密继续生效。测速结果表示 HTTP 连通性和延迟，不能验证目标 HTTPS 的 TLS 连通性、下载带宽或服务解锁能力。具体语义见 [策略组文档](https://stash.wiki/proxy-protocols/proxy-groups)、[延迟测试文档](https://stash.wiki/proxy-protocols/proxy-benchmark)和 [远程代理集文档](https://stash.wiki/proxy-protocols/proxy-providers)。

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

公开规则联网检查最近验证于 2026-11-05，本地配置与公司内网覆写验证于 2026-11-06：

- 17 项本地检查通过，涵盖主配置与覆写的 YAML 解析、重复键、分组引用、地区过滤表达式、内网节点隔离、空组保护、流媒体故障切换结构及递归测速范围、内置 DNS 加密、Fake-IP 例外、公司规则范围、域名与 IP 规则顺序、流媒体优先级、Sukka 拦截覆盖与公司域名豁免、机场覆写范围和图标集。
- 8 个节点分类通过 `include-all: true` 汇集节点，7 个地区自动测速，“其他地区”手动选择。主配置的 `proxy-providers` 为空字典。`Subscribe.stoverride` 只定义一个代理集及展示字段，显示名称固定为“Sub-Store 订阅”，订阅地址指向 Sub-Store 的 `Subscribe` 集合，测速使用 HTTP 204 地址。
- 公共 DNS 上游均为 HTTPS DNS，只有公司域名 policy 使用 `system`。`follow-rule` 关闭，两个 IPv6 解析开关关闭，53 端口提前拦截位于全部分流规则之前。
- 配置包含 47 个远程集合与 3 个 inline 集合，引用检查通过。远程集合已通过规则类型和 CIDR 格式检查；Sukka `non_ip` 集合中附带的 IP 条目均包含 `no-resolve`，不会自行触发域名解析。
- 7 条地区流媒体规则引用 6 个隐藏的故障切换组，通用流媒体引用默认代理；主配置包含 15 个展示组，图标集对应这 15 个组。引用检查确认全部目标有效且不存在循环依赖。递归检查确认每个辅助组只引用指定的两个基础地区组，两个地区均保留 `REJECT` 保护。
- 8 个节点分类显式包含 `REJECT`，全部地区过滤均保留 `REJECT` 并排除 `DIRECT`。Windows 0.1.47 的只读 `/proxies` 查询确认内置 `REJECT` 返回 `alive: false`、`state: unhealthy`；地区断线与恢复演练尚未执行。
- “其他地区”的节点过滤与各自动地区组互不重复，订阅提示项从该分类排除。韩国和欧洲流媒体分别引用对应地区组，英国、德国、荷兰等节点统一归入欧洲。
- 秋风完整规则下载与 YAML 解析通过，Windows 已加载全部 976 条，包含 960 条精确域名、12 条域名后缀和 4 条关键词规则。`ad-api.4pyun.com` 与 `unityads.unity3d.com` 在规则诊断中命中提前拒绝，广告条件明确排除公司域名集合。
- 公司内网覆写已在 Windows 0.1.47 与 zju-connect v1.3.1 验证。公司域名返回 Fake-IP，实际请求命中 `corporate-domains` 并经 `aTrust` 节点收到 HTTP 200。公司域名绕过与 5 条公司网段排除已移除，5 个公司地址范围均命中内网节点。官方 aTrust 服务停止、进程全部退出、虚拟网卡断开后，6 项真实访问检查通过：公司域名和真实 IP 经 Stash 访问均返回 HTTP 200，Apple HTTPS 直连返回 HTTP 200，Google HTTPS 经原有香港节点返回 HTTP 204。其余公司业务服务尚未逐项验证。
- 1Password 的 11 个域名条目使用 `domain` 集合，直连规则优先于下载和通用境外服务规则。
- 山姆的 `api-sams.walmartmobile.cn`、`decoration-sams.walmartmobile.cn` 通过国内 DoH 返回 `157.148.16.212`，属于 Sukka 中国 IP 集合。
- 万达的 `cinema-api-prd-mx.wandafilm.com`、`misc-api-prd-mx.wandafilm.com` 通过国内 DoH 返回 `120.53.82.119`，属于 Sukka 中国 IP 集合。
- `223.5.5.5` 在不指定 HTTP 代理时，为 8 个业务域名返回有效的 DoH 答案，验证过程保持 TLS 证书校验。

上游联网检查验证了规则服务与 DoH 的可用性；公司内网检查还验证了 Fake-IP、Stash 请求出口、Windows 系统代理绕过移除和隧道接管。HTTP 检查未执行公司业务系统的账号登录或业务操作。

检查脚本只读取仓库文件和公开规则、查询 DoH，不修改已安装 Stash 的配置、订阅或策略选择。更新主配置由使用者在应用中操作。流媒体的实际播放权限与 iOS、macOS 的设备耗电尚未实测。

iMessage 图片上传速度需要结合发送时的连接记录判断，记录应包含上传域名、命中规则和实际出口。当前没有 iMessage 的连接记录，无法确认其速度问题的原因。

配置参考了 [LumexOverwrite](https://github.com/int-del/LumexOverwrite)和 [Clash Configuration Template](https://github.com/Accademia/Clash_Configuration_Template)。Stash 字段以官方文档为依据。
