# 自动化执行记录：刷新 small-wafer 首页 V2EX 热帖

## 任务
定时运行 scripts/fetch_v2ex.py 抓取 V2EX 热帖写入 assets/v2ex.json，内容变化时提交并推送到 GitHub Pages。

## 执行历史

### 2026-10-02 00:47
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 10 条。
- 变更：assets/v2ex.json 有变化（23 增 23 删）。
- 提交：`3a228c3 刷新 V2EX 热帖`
- 推送：**直连成功**（本次未走代理）。关键：`GIT_TERMINAL_PROMPT=0` + `-c credential.helper= -c credential.helper=store` 避免 GCM 挂起。
- 结果：已上线，工作区干净。

### 2026-10-02 06:59
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 10 条。
- 变更：assets/v2ex.json 有变化（20 增 20 删）。
- 提交：`5268c35 刷新 V2EX 热帖`
- 推送：直连失败（`Recv failure: Connection was reset`），加 `https_proxy=http://127.0.0.1:7890` 后成功。
- 结果：已上线，工作区干净（仅 .workbuddy-ai/ 未跟踪，勿动）。

### 2026-10-02 10:08
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 9 条（V2EX 本次仅返回 9 条热帖，非脚本异常）。
- 变更：assets/v2ex.json 有变化（30 增 37 删）。
- 提交：`683c23b 刷新 V2EX 热帖`
- 推送：直连失败（`Recv failure: Connection was reset`），加 `https_proxy=http://127.0.0.1:7890` 后成功（5268c35..683c23b）。
- 结果：已上线，工作区干净（仅 .workbuddy-ai/ 未跟踪，勿动），HEAD == origin/main。

### 2026-10-02 13:10
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 10 条。
- 变更：assets/v2ex.json 有变化（33 增 26 删）。
- 提交：`9cf348b 刷新 V2EX 热帖`
- 推送：直连失败（`Recv failure: Connection was reset`），加 `https_proxy=http://127.0.0.1:7890` 后成功（683c23b..9cf348b）。
- 结果：已上线，工作区干净（仅 .workbuddy-ai/ 未跟踪，勿动），HEAD == origin/main。

### 2026-10-02 16:12
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 9 条。
- 变更：assets/v2ex.json 有变化（30 增 37 删）。
- 提交：`db90e0e 刷新 V2EX 热帖`
- 推送：**直连成功**（本次未走代理，9cf348b..db90e0e）。
- 结果：已上线，工作区干净（仅 .workbuddy-ai/ 未跟踪，勿动），HEAD == origin/main。

### 2026-10-02 19:14
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 10 条。
- 变更：assets/v2ex.json 有变化（33 增 26 删）。
- 提交：`76ee948 刷新 V2EX 热帖`
- 推送：**直连成功**（本次未走代理，db90e0e..76ee948）。
- 结果：已上线，工作区干净（仅 .workbuddy-ai/ 未跟踪，勿动），HEAD == origin/main。

### 2026-10-02 22:15
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 10 条。
- 变更：assets/v2ex.json 有变化（21 增 21 删）。
- 提交：`b644fff 刷新 V2EX 热帖`
- 推送：**直连成功**（本次未走代理，76ee948..b644fff）。
- 结果：已上线，工作区干净（仅 .workbuddy-ai/ 未跟踪，勿动），HEAD == origin/main。

### 2026-10-03 20:58
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 10 条。
- 变更：assets/v2ex.json 有变化（40 增 40 删）。
- 提交：`d63a24e 刷新 V2EX 热帖`
- 推送：**直连成功**（本次未走代理，b644fff..d63a24e）。
- 结果：已上线，工作区干净（仅 .workbuddy-ai/ 未跟踪，勿动），HEAD == origin/main。

### 2026-10-04 10:43
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 9 条。
- 变更：assets/v2ex.json 有变化（36 增 43 删）。
- 提交：`129d22a 刷新 V2EX 热帖`
- 推送：**直连成功**（本次未走代理，d63a24e..129d22a）。
- 结果：已上线，工作区干净（仅 .workbuddy-ai/ 未跟踪，勿动），HEAD == origin/main。

### 2026-10-04 10:44（重复触发）
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 9 条。
- 变更：assets/v2ex.json 有变化（2 增 2 删，仅 `updated` 时间戳 + 首条 replies 42→43）。
- 提交：`f1c972c 刷新 V2EX 热帖`
- 推送：**直连成功**（未走代理，129d22a..f1c972c）。
- 结果：已上线，工作区干净（仅 .workbuddy-ai/ 未跟踪，勿动），HEAD == origin/main。

### 2026-10-04 13:44
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 8 条（V2EX 本次返回 8 条，非脚本异常）。
- 变更：assets/v2ex.json 有变化（22 增 29 删）。
- 提交：`f378f78 刷新 V2EX 热帖`
- 推送：**直连成功**（未走代理，ab77d4d..f378f78）。注意本次 push 前基点为 ab77d4d（非上次记录的 f1c972c），说明期间有其它提交，属正常。
- 结果：已上线，工作区干净（仅 .workbuddy-ai/ 未跟踪，勿动），HEAD == origin/main。

### 2026-10-04 16:46
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 9 条。
- 变更：assets/v2ex.json 有变化（34 增 27 删）。
- 提交：`36225d9 刷新 V2EX 热帖`
- 推送：直连失败（`Recv failure: Connection was reset`），加 `https_proxy=http://127.0.0.1:7890` 后成功（f378f78..36225d9）。
- 结果：已上线，工作区干净（仅 .workbuddy-ai/ 未跟踪，勿动），HEAD == origin/main。

### 2026-10-04 19:48
- 抓取：直连失败（URLError），Clash 代理 127.0.0.1:7890 成功，写入 9 条。
- 变更：assets/v2ex.json 有变化（28 增 28 删）。
- 提交：`b86684b 刷新 V2EX 热帖`
- 推送：**直连成功**（未走代理，36225d9..b86684b）。
- 注意：工作区另有 `linux.html` 处于修改状态（非本任务所为，未触碰，保持原样）。
- 结果：已上线，HEAD == origin/main。

## 经验
- 抓取通道：直连基本不可用，7890 稳定可用。
- 每次抓取条数不固定（8~10 条），V2EX 返回多少就写多少，非异常。
- push 直连不稳定（上一轮成功、本轮被重置），策略仍为：先直连，失败立即加 https_proxy 重试，一次即通。
- 必须带 `-c credential.helper=` 覆盖，否则 credential-selector 会永久挂起。
- 只需 `git add assets/v2ex.json`，不要碰 `.workbuddy-ai/`。
- 脚本的「无变化跳过」判断包含 `replies` 回复数与 `updated` 时间戳，因此即使热帖列表相同，回复数微增也会触发写入+提交（属正常，照常推送即可）。
