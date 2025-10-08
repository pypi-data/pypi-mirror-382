---
description: Execute a Blueprint with optimized parallel execution using MCP tools
---

你現在要執行一個 Blueprint，使用 MCP tools 進行優化執行。

## ⚠️ 重要提醒
**所有 RBT 文件操作必須使用 rbt-document-editor MCP！**
- ✅ 使用 MCP tools：`get_outline`, `read_content`, `update_info`, `update_block` 等
- ❌ 禁止使用：Read, Write, Edit 工具直接操作 .md 文件

## 輸入參數
- feature_id: {{feature_id}}
- project_id: 從 CLAUDE.md 或 RAG 取得（預設 knowledge-smith）

## 執行流程

### 1. RAG 查詢（使用 graphiti-memory MCP）
使用 `search_memory_nodes` 和 `search_memory_facts` 查詢：
- 偏好 (Preference)：專案開發偏好、命名規範、工具使用習慣
- 程序 (Procedure)：TDD 流程、文件更新規範、Blueprint 執行標準
- 相關事實：與此 feature 相關的先前決策、技術選型

查詢範圍：`group_ids = [project_id, "Public"]`

### 2. 驗證階段（使用 rbt-document-editor MCP）
使用 `get_outline` 檢查：
- `BP-{feature_id}.md` 的 status 是否為 "Finalized" 或 "In Progress"
- `REQ-{feature_id}.md` 的 status 是否為 "Finalized"
- 列出所有 `TASK-{feature_id}-*.md` 檔案（可能在 tasks/ 子目錄）

如果 status 不符合，詢問是否要更新後繼續。

### 3. 讀取共享 Context（關鍵優化！）
使用 `read_section` 讀取完整內容：
- 讀取 BP 所有 sections（遞迴讀取，包含 blocks）
- 讀取 REQ 所有 sections（遞迴讀取，包含 blocks）

**這兩份內容會傳給每個 task-coding-agent，避免重複 cache write**

### 4. 執行規劃
詢問用戶執行策略：
- **平行**（預設）：所有 TASK 同時執行（快但較貴，~$9.5）
- **批次**：每批 3-4 個（平衡，~$5-6）
- **串行**：一個一個來（慢但最省，~$3）

### 5. 平行執行 Tasks
使用 `task-coding-agent`，每個 agent 的 prompt 包含：

```markdown
# Blueprint Context (已讀取)
{BP 完整內容}

# Requirement Context (已讀取)
{REQ 完整內容}

# RAG Context（偏好與程序）
{從 graphiti-memory 查詢的相關偏好與程序}

# Your Task
請實作 TASK-{feature_id}-{task_name}：

## ⚠️ 強制工具使用規範（必讀！）

### ❌ 絕對禁止
- **禁止使用 Read tool** 讀取 RBT 文件（.md 檔案）
- **禁止使用 Write tool** 寫入 RBT 文件
- **禁止使用 Edit tool** 編輯 RBT 文件
- **禁止使用 Glob/Grep** 搜尋 TASK 文件內容

❌ 錯誤示範：
```python
Read(file_path="tasks/TASK-xxx.md")  # 禁止！會讀取 4000+ tokens
Write(file_path="tasks/TASK-xxx.md", content="...")  # 禁止！會覆蓋整份文件
```

### ✅ 必須使用（rbt-document-editor MCP）

**Step 1: 讀取文件結構**
```python
# 正確：先用 get_outline 看結構（只消耗 800 tokens，節省 80%）
mcp__rbt-document-editor__get_outline(
    project_id="{project_id}",
    feature_id="{feature_id}",
    file_path="tasks/TASK-{feature_id}-{task_name}.md"
)
# 你會得到：metadata, info, sections 的樹狀結構（不含 blocks）
```

**Step 2: 讀取需要的區段**
```python
# 正確：只讀需要的 section（例如實作指引）
mcp__rbt-document-editor__read_section(
    project_id="{project_id}",
    feature_id="{feature_id}",
    file_path="tasks/TASK-{feature_id}-{task_name}.md",
    section_id="sec-implementation"  # 只讀這個 section，節省 90% tokens
)
```

**Step 3: 局部更新**
```python
# 正確：更新 info-section 的 status（使用專用工具）
mcp__rbt-document-editor__update_info(
    project_id="{project_id}",
    feature_id="{feature_id}",
    file_path="tasks/TASK-{feature_id}-{task_name}.md",
    status="In Progress",
    update_date="2025-10-08"
)

# 正確：更新特定 block
mcp__rbt-document-editor__update_block(
    project_id="{project_id}",
    feature_id="{feature_id}",
    file_path="tasks/TASK-{feature_id}-{task_name}.md",
    block_id="blk-execution-summary",
    content="- **實際耗時**: 2小時\n- **執行狀態**: ✅ 完成\n..."
)

# 正確：新增 list item（例如問題記錄）
mcp__rbt-document-editor__append_list_item(
    project_id="{project_id}",
    feature_id="{feature_id}",
    file_path="tasks/TASK-{feature_id}-{task_name}.md",
    block_id="blk-problems-table",
    item="| 相對路徑 import 失敗 | 改用 sys.path.insert | 15min | ❌ |"
)
```

### ✅ 正確流程範例

```python
# 1. 先看結構
outline = get_outline(project_id, feature_id, file_path)

# 2. 更新 status 為 In Progress
update_info(
    project_id=project_id,
    feature_id=feature_id,
    file_path=file_path,
    status="In Progress",
    update_date="2025-10-08"
)

# 3. 讀取實作指引
impl_guide = read_section(section_id="sec-implementation")

# 4. 進行開發（寫代碼、測試）

# 5. 填寫完成記錄
update_block(block_id="blk-execution-summary", content="...")
append_list_item(block_id="blk-problems-table", item="...")
update_block(block_id="blk-technical-debt", content="...")

# 6. 更新 status 為 Done
update_info(
    project_id=project_id,
    feature_id=feature_id,
    file_path=file_path,
    status="Done",
    update_date="2025-10-08"
)
```

## 執行步驟（嚴格遵守）

1. ✅ 使用 `get_outline` 讀取 TASK 結構
2. ✅ 使用 `update_info` 更新 status → "In Progress"
3. ✅ 使用 `read_section` 讀取實作指引 (sec-implementation)
4. 參考上述 BP 和 REQ context 進行實作
5. 實作並通過測試（TDD 紅綠重構）
   - ✅ 可以用 Read/Write/Edit 操作「代碼檔案」（.py, .json 等）
   - ❌ 但不能用來操作「RBT 文件」（.md 檔案）
6. ✅ 使用 `update_block` 填寫完成記錄：
   - blk-execution-summary（執行摘要）
   - blk-problems-table（問題記錄，用 `append_list_item`）
   - blk-technical-debt（技術債務）
7. ✅ 使用 `update_info` 更新 status → "Done"
8. ✅ 使用 `add_memory` 將重要決策儲存到 RAG

## Token 優化目標
- 讀取 TASK 結構：800 tokens（vs 傳統 4000 tokens）✅
- 更新單一區段：300-500 tokens（vs 傳統 8000 tokens）✅
- 目標：**總消耗 < 傳統方式的 20%**

## 注意事項
- 嚴格遵循 RAG 中的偏好與程序
- **所有 RBT 文件操作必須使用 MCP**，否則會嚴重浪費 token！
- 測試先行：Red → Green → Refactor
- 完成後記得儲存經驗到 RAG
```

### 6. 完成報告
所有 tasks 完成後：
1. 統計執行結果（成功/失敗/部分完成）
2. 彙總 token 消耗和成本
3. 使用 `add_memory` 將執行經驗儲存到 RAG：
   - 執行策略效果（平行/批次/串行）
   - 遇到的問題與解決方案
   - 優化建議
4. 詢問是否要更新 BP status 為 "Done"

## 成本預估
- 平行執行：~$9.5（40 分鐘）
- 批次執行：~$5-6（1.5 小時）
- 串行執行：~$3（3.5 小時）
