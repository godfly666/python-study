# Git 速查表(自己的踩坑版)

> 一句话:**`cd` 进房间 → `status` 看变化 → `add` 装箱 → `commit` 封箱贴标签 → `push` 发快递**
>
> 代码只活在"你的文件夹"里。git 不会自动备份,它等你按顺序走完下面这条流水线。

```
你的文件夹         ──git add──▶   暂存区        ──git commit──▶   本地仓库(.git)   ──git push──▶   GitHub
(工作区)                        (待提交清单)                      (有历史、能回去)                  (云端备份)
```

---

## 1. `cd` —— 站到正确的地方

```powershell
cd C:\Users\l1809\PycharmProjects\WelcomeScreen\study
```

- `cd` = change directory,**是 PowerShell 的命令,不是 git 的**,所以前面没有 `git`。
- **git 只认当前目录**:仓库信息在 `study\.git`,站在外面敲 `git status` 会报 `not a git repository`。
- **相对路径也从当前目录算**:脚本里的 `"./chroma_db_v2"`、`"./notes.txt"` 都相对"我现在站的地方"。所以 `python rag_step4.py` 必须在脚本所在的目录里跑。
- 提示符 `(.venv) PS C:\Users\l1809\PycharmProjects\WelcomeScreen\study>`:`(.venv)` = 在虚拟环境里、`PS` = PowerShell、后面 = **你此刻站的位置**。每次敲命令前瞄一眼。

配套:`cd ..` 退一级 · `cd \` 退到盘根 · `pwd` 或 `Get-Location` 我在哪。

## 2. `git status --short` —— 看一眼(只读,永远安全)

两列,左边=暂存区,右边=工作区:

```
 M  04_rag_project/rag_step1.py    改过,还没 add
M   .gitignore                     改过,而且已经 add
A   04_rag_project/rag_step4.py    新文件,已经 add
??  04_rag_project/chroma_db_v2/   新东西,git 还没管它
 D  notes.txt                      被删了,还没 add
```

符号只有四个:`M` 改过 · `A` 新增 · `D` 删除 · `??` 没跟踪。

**`??` 不是错误**,只是"git 不知道你想不想管它"。该管的 `add`,不该管的写进 `.gitignore`。

## 3. `git add -A` —— 装箱

```powershell
git add -A
```

- `-A` = all:新增 + 修改 + 删除,全部登记到暂存区。
- **为什么要有暂存区**:让你挑着提交,一次提交只讲一件事。
- **风险点**:`-A` 只看"变没变",不看内容好坏 → **`.gitignore` 是唯一的守门员**(密钥、`.db`、`chroma_db*/`、`__pycache__/`、`notes.txt`)。
- 装错了怎么办:`git restore --staged 文件名`(拿出来,**文件本身不动**)。

## 4. `git commit -m "说明"` —— 封箱、贴标签

```powershell
git commit -m "关R4:真实文档切分入库 + 检索带来源(metadata 溯源)"
```

- 给暂存区**拍快照**,记录在本地 `.git` 里。**此时 GitHub 上还是没有东西。**
- `-m` 后面引号里的字是**写给人看的说明,不是文件名**(踩过坑:写成 `git commit -m .\study-day04.py`,历史里就留了一条叫文件名的话)。
- **永远带 `-m`**:不带会打开编辑器(Nano/Vim),新手容易卡在里面出不来。
- 说明怎么写:一句话说清"做了什么",**前 20 字最重要**(`git log --oneline` 只显示一行)。
  - `关R4:真实文档切分入库 + 检索带来源`
  - `修复:BMI 接口边界值 18.5 漏判`
  - `清理:删除 PyCharm 自动导入的垃圾 import`
- **一个 commit = 一个可以回去的时间点。** git 的真正价值不是备份,是时间机器。

## 5. `git push` —— 发快递

```powershell
git push
```

- 把本地还没发出去的提交推到 GitHub(`origin` = 远端名字)。
- 第一次用过 `git push -u origin main`,`-u` 已经把 main 和 origin/main 绑好,以后直接 `git push`。
- 成功:`To https://github.com/godfly666/python-study.git   1a97b09..3f2c1ab  main -> main`
- 失败两次典型:**网络**(`Could not connect to server`)→ 等会儿重试,东西还在本地;**权限**(没登录/token 过期)。

---

## 三条安全规则

1. **提交前扫密钥**:`git grep -n "sk-"` —— 有结果就停下来看清楚。
2. **不该进仓库的**(能重新生成/含隐私/很大):写进 `.gitignore`,永远不要 `add`。
3. **已经推上去的密钥 = 已泄露**:删文件没用,历史永久保留 → 立刻去平台**作废重发**。

## 常见报错对照(都是我真遇到过的)

| 报错 | 意思 | 怎么办 |
|---|---|---|
| `not a git repository` | 站错目录 | `cd` 到仓库根(有 `.git` 的那个) |
| `Please tell me who you are` | 没配用户名 | `git config --global user.name "名字"` + `user.email` |
| `src refspec main does not match any` | 本地还没有提交 | 先 `git add` + `git commit`,才有分支可推 |
| `nothing to commit, working tree clean` | 没有新变化 | 正常,不用管 |
| `remote origin already exists` | 远程已经加过了 | 正常,不用管(重复配置而已) |
| `LF will be replaced by CRLF` | Windows 换行符提示 | **无害**,忽略 |
| `Failed to connect ... 443` | 网络到不了 GitHub | 等会儿重试;有代理软件就打开它 |
| `error: failed to push, fetch first` | 远端有你本地没有的提交 | `git pull --rebase` 再 `git push` |

## 另外五个够用的

```powershell
git log --oneline -5              # 最近 5 次提交:我在做什么
git diff                          # 还没 add 的改动,具体改了什么
git diff --cached                 # 已 add、等着 commit 的改动
git restore --staged 文件名        # 从暂存区拿出来(文件不动)
git checkout -- 文件名             # 撤销没提交的修改(⚠️ 会丢改动,慎用)
```

## 一次完整的收工流程(照抄)

```powershell
cd C:\Users\l1809\PycharmProjects\WelcomeScreen\study
git status --short                 # ① 看清有哪些变化
git grep -n "sk-"                  # ② 扫一眼有没有密钥
git add -A                         # ③ 装箱
git commit -m "一句话说明"          # ④ 封箱
git push                           # ⑤ 发出去
```
