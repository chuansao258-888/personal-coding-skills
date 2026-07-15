# 模块文档完整性复核契约

在以下任一场景中，完成初稿后必须执行本契约：模块跨越三个以上组件、包含异步/并发/重试/派生超时、包含评测或 benchmark、需要 ImageGen，或属于多文档知识库的一部分。

本契约用于发现“文字看起来完整、但关键语义没有追到最终结果”的遗漏。它不替代 `SKILL.md` 的覆盖台账和证据要求。

## 1. 下游可见性台账

对每个关键输入、状态转换、失败信号和恢复动作，沿当前可达代码追到所有最终消费者。至少回答：

| 字段 | 必须核对的内容 |
|---|---|
| 触发源 | HTTP/事件/provider chunk/定时器/锁过期/数据库结果/配置变化是什么？ |
| 内部状态 | 哪个对象、字段、枚举、原子状态或记录持有它？谁拥有写权限？ |
| 控制流结果 | 它改变哪个分支、重试、fallback、取消、提交或清理动作？ |
| 持久化结果 | 是否写入数据库、缓存、队列、outbox、文件或完全不持久化？ |
| 用户可见结果 | HTTP/SSE/UI/错误码/最终文本是否能观察到？若被缓冲、吞掉或降级，要明确写出。 |
| 运维可见结果 | 哪条日志、指标、健康状态、manifest 或管理接口能观察到？ |
| 失败与恢复 | 异常、取消、超时、重复、陈旧结果或进程退出时最终状态是什么？ |
| 证据 | 生产调用者、最终消费者和对应测试/产物在哪里？ |

禁止把“内部已产生事件”“回调已被调用”“消息已进入队列”直接写成用户已收到、数据已提交或运行成功。分别验证 transport success、business success、persistence success 和 user-visible success。

## 2. 数字、计数与派生时间审计

每个会影响行为的数字都要从声明点追到算式与停止条件，尤其是超时、重试、repair、批量、窗口、阈值、容量、并发和 TTL。

逐项核对：

- 名称、单位、声明默认值、部署覆盖值、运行时有效值和派生值；
- timer 在哪一行开始、暂停、重置和结束；超时是单次 attempt、单阶段还是全局 deadline；
- `maxAttempts` 是否包含首次尝试，`maxRetries` 是否只计算重试，循环边界是 `<` 还是 `<=`；
- retry/attempt 计数在哪一行递增，进入终局前的比较发生在递增前还是递增后；把总执行次数写成 `initial attempts + explicit retries + repair/fallback attempts` 的可复算公式；
- 常量 N 表示“额外 retry/repair 数”还是“包含首次的总 attempt 数”；初始 attempt 的编号、最后一次是否仍运行 guard、终止比较符和总 provider/callback 次数必须分别写清；
- repair/fallback 是否与 retry 共用预算，成功或部分结果是否会消耗下一阶段预算；
- 名称包含 `actual/real/success/complete` 的 counter 在查重、CAS、callback start、callback complete、事务提交和最终消费的哪一侧递增；名称与增量点不一致时按代码语义降级表述；
- clamp、`min/max`、单位换算、向上/向下取整、默认回退和特殊值（0、负数、空值）；
- 并发数、队列容量和限流配额是进程内、节点级、租户级、用户级还是集群级；
- 配置注释、计划文档、实现代码和测试断言是否一致。

推荐表：

| 参数/常量 | 声明值 | 覆盖值 | 派生公式 | 计数/边界语义 | timer 范围 | 最终消费者 | 证据 |
|---|---:|---:|---|---|---|---|---|

文档中的“最多 N 次”“等待 N 秒”“默认 N”“总预算 N”必须能从代码和算式复算。无法证明时写“依据未记录”或“未读取运行环境”，不能用经验补齐。

## 3. 事件顺序与竞态矩阵

只要两个信号可能来自不同线程、回调、future、消息、事务或定时器，就至少检查两种到达顺序：`A → B` 与 `B → A`。不要只描述理想时序。

| 事件 A | 事件 B | A→B 的最终状态 | B→A 的最终状态 | 状态所有者/同步原语 | 用户/持久化/指标影响 | 测试证据 |
|---|---|---|---|---|---|---|

### 3.1 Gate、持久状态变更与结果消费

对每条含预算、权限、deadline、CAS、重试或恢复的控制流，按源码求值顺序列出：

```text
pure validation/gate -> budget reservation -> durable mutation/CAS
                     -> external callback -> terminal commit
                     -> result propagation -> final consumer
```

必须反向检查以下失败点：

- `&&`/`||` 短路、early return 或异常发生在第二、第三个条件时，前一个条件是否已经修改数据库、Redis、文件或外部状态；
- durable mutation 后的 gate 失败是否有同事务回滚、显式补偿或 recovery owner；没有时登记半推进状态；
- 外部 callback/publish/business effect 已经成功、超时未知或仅缺本地 terminal commit 时，catch 是否仍统一进入自动 retry；必须分别记录 `definite failure / definite success / ambiguous success`，ambiguous 分支需要 reconciliation owner，不能默认重放副作用；
- typed result 是否包含 `status/blocked/partial/error/stopReason`，调用者是否只取 payload 而吞掉控制语义；
- callback、publish 或 persist 成功后，response 是否进入 memory/notebook/prompt/数据库/用户输出等下一权威消费者；
- rollback/cleanup 是否同时维护引用它的 journal、outbox、索引、FK 与幂等键，还是制造“终态仍在但证据已删”的不可恢复组合。

重点检查：

- content/success、error、cancel、timeout、complete、commit、rollback 的竞争；
- claim/renew/reclaim/release 与锁或 lease 过期；
- outbox 写入、业务提交、消息发布、消费确认和重试；
- first packet、metadata-only packet、empty completion、fallback 与 circuit 更新；
- watchdog、worker、shutdown hook 和进程崩溃；
- CAS/锁只保护了状态赋值，还是同时保护了副作用。

如果两种顺序产生不同的用户可见结果、指标或健康状态，正文必须解释该窗口；若测试缺失，将其列为限制或测试缺口。

## 4. 评测与 benchmark 专项契约

评测文档必须把生产运行链与评测链分开，不得把评测脚本、stub、fixture 或 judge 当成生产能力。

至少覆盖：

| 维度 | 必须回答的问题 |
|---|---|
| 评测对象 | 具体评估哪个生产入口、版本、配置或离线产物？ |
| 数据集 | 来源、版本、样本数、字段、切分、过滤、去重、隐私和许可是什么？ |
| 执行器 | 谁调用被测系统；是本地、CI、容器、脚本还是线上 shadow？ |
| evaluator/judge | 规则、库、模型和 prompt 是什么；版本与随机性怎样固定？ |
| 指标 | 公式、范围、方向、聚合方式、空值/失败样本处理是什么？ |
| 阈值 | 在哪里声明，依据是什么；是发布门禁、告警还是仅供观察？ |
| 真实性 | real provider、fixture、stub、synthetic 数据分别覆盖什么、不证明什么？ |
| 产物血缘 | manifest、原始输出、汇总、hash、时间戳、代码版本、dirty 状态、diff/patch 绑定和保留策略如何关联？ |
| 摘要可复算性 | 正文嵌入的 hash/checksum 能否由当前 checkout 重算；序列化、编码和 LF/CRLF 是否规范化或明确记录？ |
| 输入绑定与影子产物 | report 记录的 dataset/baseline/candidate/config hash 是否逐个匹配当前精确输入；是否存在同 suite、runId、文件名或不同 schema 的旧/shadow artifact，哪一个是唯一权威？ |
| promotion | 谁读取结果，何时允许晋级，失败如何阻断或回滚？ |
| 可复现性 | 命令、依赖、种子、环境、秘密要求和已知不稳定因素是什么？ |
| 字段证明强度 | manifest/report 中每个 status、counter、boolean、provenance、`inserted/matched/pass/complete` 字段由谁产生，公式是什么，是外部回执、行为 probe、派生代理还是标签？ |
| 门禁消费者 | 哪个断言/promotion 逻辑真正读取该字段；false、missing、failure 有多少，为什么仍能 pass/accept？ |

对吞吐和容量报告，还要区分 submitted、accepted、started、completed、failed、timed out、rejected；队列 `ready` 与 `unacknowledged/in-flight` 必须分开。CPU、内存、工作集、线程、连接、队列和依赖延迟的采样范围要可追溯。区分配置的采样周期、循环中的 sleep 与产物时间戳显示的实际采样间隔；外部命令和采样开销不能被忽略。合成模型或绕过生产路由的结果必须显式标注。

manifest 标记 `dirty=true` 时，产物只能绑定到“该 commit 基础上的已修改工作树”，除非同时保留并校验 diff/patch digest，不能声称它可由该干净 commit 单独复现。正文引用校验和时，既要按仓库当前规范化字节重算，也要检查生成工具是否在 Git 换行转换前计算了平台相关字节；不能用“内容看起来相同”掩盖不可复算摘要。

对报告里的 dataset、baseline、candidate observations、config、split 或 manifest digest，必须找到它声称绑定的**精确文件**并重新计算。继续搜索 artifact root、tracked resources 和被忽略目录中同 suite/runId/文件名的替代文件，比较 schema、类别、样本数与 hash。若用当前输入重跑可得到相同指标，但报告保存的输入 hash 不匹配，只能写“核心数值可由当前输入复算；原报告输入血缘已漂移”，不能写“报告证据链完全可复现”。

不要按字段名判断证据强度。对正文引用的每个 artifact 字段，继续追到写入代码：`inserted=true` 可能只是 `chunkCount > 0` 的派生代理，`pass` 可能只表示没有结构化异常，`completed` 可能允许空结果，`matched=false` 可能未被 promotion gate 读取。至少统计 total/true/false/missing/failure，列出非成功项的分类，并明确该字段是硬门禁、告警、诊断还是无人消费。外部系统成功只能由实际 response/ack/query/持久化回读等对应证据证明。

对于 benchmark 相关代码，不能以注释、测试名或变量名代替控制流证据。逐项核对实际 guard、循环、callback 条件、sleep、时间戳和断言上下界。若测试只证明 `elapsed > TTFT`，它不能单独证明代码还等待了完整 stream duration；若循环每次执行外部命令后再 sleep 100 ms，`100 ms` 只能称为循环 sleep，不是严格采样周期，实际间隔应从产物时间戳计算。

## 5. ImageGen 事实与文字 QA

Mermaid 是可维护的事实权威，位图是帮助理解的展示层。生成后必须实际查看最终文件，并执行：

1. 对照 Mermaid 逐一核对组件、分区、箭头方向、分支和边界。
2. 对图片中的每个可读标签做逐字检查，特别是类名、接口名、端口、数字、方向词和成功/失败语义。
3. 不把精确参数值、复杂类名或容易拼错的路径强塞进位图；放进 Mermaid 或正文更可靠。
4. 使用版本化临时文件迭代，只把接受版本复制到文档资源目录；删除仓库内被拒绝的变体。
5. 检查 Markdown 引用为仓库内相对路径，文件真实存在，不引用会话 URL、临时目录或 `$CODEX_HOME/generated_images`。
6. 图注明确“架构事实以当前代码与 Mermaid 为准”。

任何标签错误、箭头幻觉或遗漏关键失败路线都必须重生成或从位图中移除，不能仅靠图注免责。

## 6. 多文档套件的权威边界

当一个系统由多份模块文档共同介绍时，先建立覆盖矩阵：

| 行为/边界 | 主权威文档 | 详细附录/相邻文档 | 代码所有者 | 重叠处理 | 状态 |
|---|---|---|---|---|---|

规则：

- 每个当前行为只有一个主解释文档；其他文档只摘要并链接，不复制整段参数或流程。
- 总览文档负责系统边界和导航，不成为所有细节的第二权威。
- 跨模块链路可以有 master walkthrough，但参数、schema 和局部机制仍链接到拥有它的模块文档。
- 重命名或拆分后更新所有反向链接、编号、图片和总览矩阵。
- 只有在替代文档已存在、覆盖关系已核验、链接已更新后，才删除旧 summary；删除前用搜索确认没有唯一事实被一起删除。
- 发现旧文档与代码冲突时，不要复制漂移内容；在新文档记录当前行为，并按需要保留简短历史说明。

## 7. 初稿后的文字反证

完成文档后不要只检查格式。重新阅读全文，搜索以下高风险词并逐句反证：

```text
当前 默认 总是 一定 仅 直接 自动 实时 流式 异步 事务 原子
成功 完成 已验证 已移除 最多 至少 重试 超时 降级 一致
```

对每个命中，问：

- 它描述的是代码路径、某次运行，还是历史文档声明？
- 是否忽略合法空结果、部分成功、取消、并发反序或最终消费者？
- 数字是否包含首次尝试、派生等待、单位转换或全局 deadline？
- “流式/异步/事务/原子”覆盖到哪个边界，边界之外是什么语义？
- “已验证”是否有本次实际命令和产物，而不是旧文档中的命令文本？

所有修正都要回写到正文、参数表、限制、面试答案和 Mermaid 中相关位置，不能只在覆盖台账补一句。

## 8. 符号、绑定、指标与传输语义核对

格式校验不能证明语义忠实。完成全文后，对正文中出现的每个权威符号和外部效果做一次定向核对，尤其避免“名称像是这样”“框架通常如此”或“指标应该有这个标签”的推测。

| 核对对象 | 必须验证的事实 | 常见错误 |
|---|---|---|
| 类、方法、字段、文件和 key | 名称逐字存在；可见性、调用者和当前注册路径正确 | 把概念名写成不存在的方法；引用旧包或旧 member 格式 |
| 配置覆盖 | YAML 是字面值还是 `${...}`；环境变量靠 placeholder、relaxed binding、系统属性还是 CLI；最终优先级和 binder 是什么 | 看到 env 文档就声称 YAML 已接 placeholder；把声明默认值写成运行有效值 |
| 注释、测试名与分支 | 注释/名称声称的行为是否真的经过对应 guard、callback、循环和终局；断言边界能否区分强弱语义 | 用测试名证明未执行的 stream wait；用较弱时间下界声称完整时长已等待 |
| 采样与计时 | 配置周期、循环 sleep、外部命令开销、调度偏差和产物时间戳中的实际间隔分别是多少 | 把 sleep 100 ms 写成每 100 ms 严格采样；忽略命令执行时间 |
| 指标 | 注册处的 meter 名、类型和标签；所有记录调用点；何时采样、哪些分支不记录 | 给 timer 发明不存在的 type 标签；把只在 timeout 记录的 timer 写成所有请求延迟 |
| HTTP/SSE/事件 | 精确状态码、envelope、payload 字段、事件顺序、固定文案和缺失字段 | 只写理想 schema；忽略 helper 实际省略 turn ID 或前一步异常会截断后续事件 |
| Terminal correlation | 每个 success/direct/fallback/error/timeout/replay producer 是否填同一 correlation key；consumer 是否只对匹配 turn/job/request 解锁、回滚或重试 | 主 Agent 路径的 DONE 带 turn ID，却忽略 direct reply 的 DONE 缺字段，前端只能等轮询或错误地清另一轮 |
| 实时连接与广播 | stream key 到连接是 1:1 还是 1:N；重连替换是否关闭旧连接；同节点/跨节点投递、broker 失败、本地 fallback、heartbeat、event ID、replay、gap 和 backpressure | `Map<session,sender>.put` 被写成支持多 tab；Redis publish 失败时没有本地发送，却称节点内仍可靠 |
| 异步/after-commit durability | listener/callback 在 commit 前后何时触发；commit 后进程崩溃、callback 前崩溃、订阅断线和失败是否有持久 job/outbox、claim、retry、watchdog | 把 `afterCommit(() -> ingest())` 或普通 `@Async` listener 写成不会丢任务的队列 |
| MQ/流式 transport | publish、confirm、ACK、NACK、reject、requeue、DLQ、close/cancel 的调用顺序和终局 | 把 `basicReject(false)` 写成 ACK；把入队写成用户成功；混淆失败重试与容量等待 |
| 外部效果/本地终态边界 | 外部 publish/callback/business write 是否已发生；confirm/timeout 是明确还是未知；随后 DB/Redis/journal/ACK 提交失败时进入 retry、ambiguous 还是 reconciliation | `publish()` 已 confirm 后 `markSent()` 抛异常，外层 catch 仍按“发布失败”重发；业务已完成但幂等终态失败后盲重跑 |
| Redis/数据库生命周期 | 创建、更新、过期、删除、空结构、TTL、事务和崩溃回收的实际语义 | 推断 Redis 会保留空集合；把 TTL 当业务超时；把 helper 调用当已提交 |
| 正反索引与凭证轮换 | token/resource 正向 key 和 user/owner 反向集合的 save/delete/rotate/bulk revoke 是否原子；并发重放、孤儿、过期成员和 TTL 漂移 | 三条 Redis 命令被写成原子双索引；先 save 新 token 再 delete 旧 token 被写成严格单会话 |
| 缓存与安全新鲜度 | 本地/共享缓存 TTL、negative cache、容量、mutation invalidation、跨实例传播和最大陈旧授权窗口 | 当前 JVM invalidate 被写成所有节点立即降权；把 token claim 或 UI currentUser 当最新权限 |
| 软删除与唯一性 | 查询是否隐藏 deleted row；unique index 是否 partial；重建/重注册、错误映射和关联数据保留语义 | `find active` 返回空就声称名称可复用，但全局 unique 仍拒绝 insert |
| 跨系统删除/撤销 | FK/cascade、child→parent 顺序、DB transaction、cache/index/storage/remote effect、tombstone、幂等 cleanup 和 reconciliation | 先删 parent 再删 child 忽略 FK；用 `@Transactional` 声称数据库与 Milvus/文件系统原子 |
| 状态机 mutation 顺序 | 每个拒绝 gate、预算 reservation、CAS、外部副作用、terminal commit 的求值顺序；失败后是否回滚/补偿 | 在 `prepare() && budget() && dispatch()` 中忽略 prepare 已成功而 budget 失败留下的半推进状态 |
| Typed outcome 与结果传播 | 调用者是否读取 status/blocked/partial/error/stop reason；payload 是否进入下一 prompt、memory、notebook、持久化或用户输出 | 只取 `.response()` 就写“执行成功”；只断言 callback 被调用而不证明结果被消费 |
| Deadline/timeout 执行 | descriptor/注释声称的 deadline mode；剩余时间是否进入真实 connect/read/request timeout、reactive cancellation 或线程中断；阻塞期间能否有界退出 | 只在外部调用前后读取 remaining time，就声称固定 30 s 的阻塞 transport 严格执行 2 s 剩余 deadline |
| 大小与内存上限 | 限制发生在读取前、流式累计中还是完整缓冲后；单位是 wire bytes、UTF-16 chars、items 还是 tokens；超限前是否已分配 | body(String.class) 完整读入后检查 length，却写成 1 MiB transport/OOM 防护 |
| E2E/preflight/probe | 每个结果字段对应的真实动作、请求、回执和断言；fixture 是否存在且可启动；是否允许 unavailable/skip | 只 GET 工具目录后返回固定 resultCount=0、passed=true，却称 live provider transport smoke 已通过 |
| Artifact/manifest 字段 | 字段生产者、计算公式、数据类型、缺失/false 计数、真实回执或代理值、读取它的 gate/consumer；所有输入 digest 对精确文件重算并排除 shadow artifact | 因为字段名叫 `inserted/pass/completed` 就声称外部系统成功；指标可复算就忽略 report hash 已漂移 |
| 校验与安全声明 | 实际检查集合、拒绝条件、未检查类型、fallback 和最终失败位置 | 把扩展名/MIME/正则/非空/probe/prompt 约束扩大成严格格式验证、安全扫描或端到端保证 |

执行方法：

1. 从文档提取反引号中的符号、配置键、meter 名和协议动作，使用代码搜索逐一定位。
2. 对指标、配置和 transport 不能只读声明；继续搜索所有写入/调用点及最终 handler。
3. 对 artifact/manifest 字段不能只读 JSON 值；搜索写入代码、派生公式、false/missing 行和实际读取它的断言/promotion gate。
4. 对 artifact 输入 digest 逐个重算并搜索同名/same-run shadow 文件；分别判断数值可复算性与原始血缘完整性。
5. 对“成功、完成、拒绝、降级、重试、超时”逐项写出精确终局：HTTP 状态、事件、持久化、ACK/NACK/reject/DLQ 和指标。
6. 对含多条件短路的状态机逐条件注入失败，核对 durable state；对 typed outcome 搜索所有 getter/consumer，确认控制状态和 payload 都被消费。
7. 对 deadline/timeout 从声明追到实际 transport；用 slow fixture 证明剩余 deadline 能取消或缩短外部等待。对 size cap 定位检查发生在 buffering 前后并核对单位。
8. 对 E2E/preflight/probe 的每个字段定位生产动作；固定值、只检查暴露状态、允许 unavailable 或缺失 fixture 时降低证据等级。
9. 对“校验、安全、隔离、验证通过”列出未覆盖输入和失败落点；没有扫描、沙箱、授权或真实回执时明确说没有。
10. 枚举每个 terminal/event producer，逐个对照 consumer 的 correlation、解锁、rollback 和 retry 条件；对实时连接检查 1:1/1:N、替换关闭、broker 故障、本地 fallback、heartbeat 和 replay。
11. 对 `afterCommit`、普通异步 listener 和内存/PubSub 派发做 commit/crash 矩阵；没有持久 job/outbox 时明确其 best-effort 边界。
12. 对 delete/detach/revoke 画出 DB parent/child、缓存、索引、存储和远端效果顺序，并从 migration/DDL 验证 FK/cascade；对正反索引、软删除唯一键和本地安全缓存做并发/多实例反证。
13. 找到一个语义错误后，搜索全文中的同义表述、表格、图和面试答案，避免只修正文某一处。
14. 无法从代码或运行证据确认时，标为推断或本轮未验证，不用框架惯例补齐。
