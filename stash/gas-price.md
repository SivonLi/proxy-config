# 哈尔滨油价面板

[一键导入 Stash](https://link.stash.ws/install-override/raw.githubusercontent.com/SivonLi/proxy-config/configs/stash/gas-price.stoverride)。导入后在覆写页面启用“哈尔滨油价”，应用配置，在首页查看面板。

也可以在 Stash 的覆写页面通过 URL 导入：

```text
https://raw.githubusercontent.com/SivonLi/proxy-config/configs/stash/gas-price.stoverride
```

面板每小时读取一次中石化油价。正文固定为三行，分别显示 92 号、95 号和 98 号汽油的价格，以及各型号较上次调整的金额。价格和涨跌金额的单位均为元/升。上涨使用 `↑`，下跌使用 `↓`，没有变化时显示“持平”。标题显示哈尔滨及北京时间的获取日期和时间，格式为 `哈尔滨 MM/DD HH:mm`。点击面板可以打开中石化油价网页。

默认城市为哈尔滨，使用中石化黑龙江南区，区域 ID 为 `23002`。接口的区域说明包含哈尔滨、牡丹江、大庆、鸡西和七台河。数据代表接口公布的区域价格，各油站的实际售价和优惠以油站为准。

覆写内置脚本，只添加 `tiles` 和 `script-providers`。脚本通过 HTTPS 主动请求公开接口，使用 Stash 的自动 Cookie 功能完成初始化与省份切换。无需登录账号或安装 MitM 证书。

显示样式采用 Stash 原生 Tile 的标题、图标和三行正文，适用于 iOS 小组件的三行展示空间。具体字号、换行和刷新时机由 Stash 与 iOS 控制。请求失败或接口字段异常时，本次脚本立即终止，错误记录在脚本日志中。面板可能保留上次成功的内容，请结合标题中的日期和时间判断数据是否及时。

数据请求流程参考 [jnlaoshu/MySelf 的 GasPrice.js](https://raw.githubusercontent.com/jnlaoshu/MySelf/master/Egern/Widget/GasPrice.js)。配置字段依据 [Stash 面板文档](https://stash.wiki/script/tile)、[脚本管理文档](https://stash.wiki/script/manage-script)和 [脚本接口文档](https://stash.wiki/script/syntax-and-interface)。
