from fastmcp import FastMCP
import boto3
import os

def main():
    AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
    client = boto3.client("stepfunctions", region_name=AWS_REGION)

    mcp = FastMCP("StepFunction MCP")

    @mcp.tool()
    def list_executions(
        state_machine_arn: str,
        execution_name_contains: str = None,
        start_time: str = None,
        end_time: str = None
    ) -> list:
        """
        Return all executions for a given state machine ARN, filtered by start_time, end_time (ISO format), and name_contains.
        """
        executions = []
        next_token = None
        while True:
            params = {
                "stateMachineArn": state_machine_arn,
                "maxResults": 1000
            }
            if next_token:
                params["nextToken"] = next_token
            resp = client.list_executions(**params)
            for exe in resp.get("executions", []):
                # Filter by time range
                if start_time or end_time:
                    start_dt = exe.get("startDate")
                    if start_dt:
                        exe_start_iso = start_dt.isoformat()
                        if start_time and exe_start_iso < start_time:
                            continue
                        if end_time and exe_start_iso > end_time:
                            continue
                # Filter by name_contains
                if execution_name_contains and execution_name_contains not in exe.get("name", ""):
                    continue
                executions.append(exe)
            next_token = resp.get("nextToken")
            if not next_token:
                break
        return executions

    @mcp.tool()
    def get_execution_output(execution_arn: str) -> dict:
        """
        Return output JSON for a given execution ARN.
        """
        try:
            resp = client.describe_execution(executionArn=execution_arn)
            return {
                "execution_arn": execution_arn,
                "output": resp.get("output", "{}")
            }
        except Exception as e:
            return {"error": str(e)}

    mcp.run()

if __name__ == "__main__":
    main()