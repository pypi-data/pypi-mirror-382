# AWS Step Functions Execution MCP Server

這是從 `mcp/stepfunction` 遷移過來的 MCP server，已轉換為 uvx 支援的格式。

## 功能
- 查詢 AWS Step Functions 下所有 execution (`list_executions`)
- 查詢指定 execution 的 output JSON (`get_execution_output`)

## 安裝與使用

### 本地開發安裝
```bash
cd mcp/sfn_exec
pip install -e .
```

### 使用 uvx 執行
```bash
# 從本地路徑執行
uvx --from ./mcp/sfn_exec sfn-exec-mcp

# 或直接執行（如果已安裝）
uvx sfn-exec-mcp
```

## MCP 設定檔

在 Claude MCP 設定中使用：

建議使用方式，請注意：你可能需要修改GitHub的key檔案路徑
```json
{
  "command": "uvx",
  "args": [
    "git+ssh://git@dsgithub.trendmicro.com/workload-security/BarbarAIns-ai-hackathon.git#subdirectory=mcp/sfn_exec"
  ],
  "env": {
    "AWS_REGION": "us-east-1",
    "GIT_SSH_COMMAND": "ssh -i ~/.ssh/id_ed25519"
  }
}
```

如果你有下載source code，記得修改到你的路徑
```json
{
  "command": "uvx",
  "args": ["--from", "/Users/xxxx/BarbarAIns-ai-hackathon/mcp/sfn_exec", "sfn-exec-mcp"],
  "env": {
    "AWS_REGION": "us-east-1"
  }
}
```

## MCP 工具說明

### 1. list_executions

**參數：**
- `state_machine_arn` (str): Step Function 的 ARN
- `execution_name_contains` (str, 可選): execution 名稱包含的字串
- `start_time` (str, 可選): 開始時間 (ISO format)
- `end_time` (str, 可選): 結束時間 (ISO format)

**回傳：**
- executions (list): 所有符合條件的 execution 資訊

### 2. get_execution_output

**參數：**
- `execution_arn` (str): execution 的 ARN

**回傳：**
- output (dict): 該 execution 的 output JSON

## 環境變數

- `AWS_REGION`: AWS 區域設定（預設: us-east-1）

## 注意事項

- 需有 AWS IAM 權限可讀取 Step Functions
- 若有多個 region，可用環境變數切換
- 支援時間範圍和名稱過濾來查詢 execution

---

## 遷移說明

此版本已從 `mcp/stepfunction` 遷移至 `mcp/sfn_exec`，主要變更：
- 轉換為 uvx 支援的 Python package 格式
- 加入 `pyproject.toml` 設定檔
- 重新組織檔案結構
- 保留原有功能和 API