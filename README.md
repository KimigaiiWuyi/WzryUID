# WzryUID

<p align="center">
  <a href="https://github.com/KimigaiiWuyi/WzryUID"><img src="https://s2.loli.net/2024/01/07/axQ4wLcNHyO9RUr.png" width="256" height="256" alt="WzryUID"></a>
</p>
<h1 align = "center">WzryUID 0.4.0</h1>
<h4 align = "center">🚧支持OneBot(QQ)、QQ频道、微信、开黑啦、Telegram的全功能某MOBA游戏Bot插件🚧</h4>
<div align = "center">
        <a href="http://docs.gsuid.gbots.work/#/" target="_blank">安装文档</a>
</div>


## 丨安装提醒

> **注意：该插件为[早柚核心(gsuid_core)](https://github.com/Genshin-bots/gsuid_core)的扩展，具体安装方式可参考[GenshinUID](https://github.com/KimigaiiWuyi/GenshinUID)**
>
> 支持NoneBot2 & HoshinoBot & ZeroBot & YunzaiBot & Koishi的某Moba游戏的Bot插件

## 丨安装方式
1. 发送`core安装插件wzryuid`
2. 发送`gs重启`应用插件

## 丨用前注意（登录态）

新版查询接口已改用**营地新版协议**（`encodeParam` 签名 + 响应体 XXTEA 加解密），
旧的 43 字符 CK 已失效。查询所用的登录态（`token` / `userKey` / `encodeRes`）需要由扫码获取：

1. **先绑定 UID**：`王者绑定UID<营地ID>`（绑定关系存放在 gsuid_core 数据库 `wzrybind` 表）。
2. **再扫码登录**：安装配套插件 **WzryScanLogin** 后发送 `王者扫码登录`（微信/QQ 均可），
   扫码成功后登录态会自动写入本插件的账号池，之后即可正常查询。
3. 查询时若提示「账号池中没有可用的登录态」「登录态已失效」，重新发送 `王者扫码登录` 即可。

> `王者添加CK` 作为**备用登录方式**保留：它只写入数据库，新版查询优先使用扫码登录态。
> 推荐优先用扫码登录；该命令供兼容/备用场景使用。

- 扫码登录会使王者营地 APP 被顶号，扫码后请勿在营地 APP 登录该账号，否则登录态会失效。
- 强烈建议使用小号扫码。

## 丨新版协议与账号池（本次更新）

- **新协议客户端** `WzryUID/utils/camp_auth.py`：实现新版请求头、`encodeParam` 签名、
  `campencrypt` 响应解密；战绩、段位、英雄榜、皮肤墙等全部查询接口均已迁移到新协议。
- **自包含加解密助手** `WzryUID/utils/xxtea_helper.js`：XXTEA 加解密通过 Node 调用，
  需在机器人运行环境中安装 **Node.js**（`node` 需在 PATH 中）。
- **独立账号池** `data/WzryUID/AuthPool.json`：存放新版登录态密钥，路径由 `get_res_path('WzryUID')`
  动态解析，不含任何写死的绝对路径，换电脑/换部署目录都能正常使用。该文件位于 `data/` 目录，
  已被 `.gitignore` 排除，不会泄露凭据。
- **解耦说明**：本插件与参考插件 GloryOfKings-Plugin 只共用协议实现思路，不共享任何运行时文件。
  UID 绑定关系由 gsuid_core 数据库维护，账号池仅补充新版签名密钥。
- **失效提示**：缺少/失效登录态时，错误提示会引导使用 `王者扫码登录`；`王者帮助` 也新增了扫码入口说明。

## 丨功能
<details><summary>绑定切换删除UID - 命令: 王者绑定UID、王者删除UID、王者切换UID</summary><p>
还没有图
</p></details>

<details><summary>扫码登录（需 WzryScanLogin）- 命令: 王者扫码登录</summary><p>
扫码获取新版查询所需登录态，详情见上方「用前注意」。
</p></details>

<details><summary>皮肤墙 - 命令: 皮肤墙</summary><p>
<a><img src="https://s2.loli.net/2023/09/07/BPLFpys4fdR15u8.jpg"></a>
</p></details>

<details><summary>当前段位 - 命令: 当前段位</summary><p>
<a><img src="https://s2.loli.net/2023/08/14/yXWFmw2Cca3jgEd.jpg"></a>
</p></details>

<details><summary>查战绩 - 命令: 查荣耀</summary><p>
<a><img src="https://s2.loli.net/2023/08/14/gFYKnW1Ma56jcPT.jpg"></a>
</p></details>

<details><summary>英雄榜 - 命令: 见 王者帮助</summary><p>
英雄榜为全局接口，使用账号池中的全局默认账号查询。
</p></details>

## 丨其他

+ 本项目仅供学习使用，请勿用于商业用途
+ [GPL-3.0 License](https://github.com/qwerdvd/StarRailUID/blob/master/LICENSE)
