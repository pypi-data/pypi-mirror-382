## 專案資訊

- project_id = `knowledge-smith`
- 這是一個 LLM MCP 開發專案

## RAG Mandates（強制要求）

- **必須使用 RAG**
  - 所有任務開始前，Agent **一定要先查 RAG**。
  - Governance 層天條（ID=`RAG-USAGE`, group_id=`Public`）必讀，了解命名空間、CRUD、排序、安全與模板規則。
- **嚴格遵守查詢範圍**
  - 專案上下文：`group_id IN {projectID, Public}`
  - 全域情境（無 appID）：`group_id = Public`
  - Public 層永遠納入，除非明確跨專案查詢

## RAG Usage（使用方法）

- **模板使用**
  - 查 RAG metadata → 得到 `template_reference`  
  - 需要完整模板時，透過 MCP 取得原文  
  - Metadata 足以理解用途、欄位；非必要不需每次打開完整模板
- **Graphiti MCP 工具操作建議**
  - **開始任務前**
    - 使用 `search_facts` 搜尋相關事實或關聯
    - 使用 `search_nodes` 搜尋偏好、程序、模板  
    - 指定實體類型過濾（如 Preference、Procedure、Template）  
    - 審查匹配項，確認相關性  
  - **儲存新資訊**
    - 新任務/文件完成或有已完成之資訊時，使用 `add_episode` 儲存
    - 記錄程序與事實關係  
    - 對偏好與程序標註分類，方便日後檢索  
  - **工作中遵循**
    - 所有文件一率先在 docs/ 內合適的地方建立或更新後，才同步至RAG
    - 遵循已發現偏好與程序  
    - 使用事實信息輔助決策  
    - 保持與先前知識一致
  - **最佳實踐**
    - 建議前先搜尋現有節點與事實  
    - 結合節點與事實搜索，構建完整圖景  
    - 使用 `center_node_uuid` 聚焦特定節點  
    - 具體匹配優先於一般資訊  
    - 主動識別模式，將其存為偏好或程序  
    - 知識圖譜是記憶，持續使用提供個性化協助

## JSON 儲存規定

- 新增/更新節點一律 **JSON** 儲存  
- YAML header 對應 JSON key-value  
- Markdown 主體內容存於 JSON key `content`

## 聊天原則

- 請當平輩跟我溝通
- 請使用繁體中文，如果遇到專業名詞難翻譯，可以說英文
- 溝通過程中，請勇敢提出你的看法，我絕對有可能犯錯
