import json
import subprocess
import run_tool


def handler(event, context):
    return run_tool.main(event)
    # # Convert the Lambda event to a JSON string
    # event_json = json.dumps(event)

    # # Run the run_tool.py script with the event as an argument

    # result = subprocess.run(
    #     ["python", "run_tool.py", event_json],
    #     capture_output=True,
    #     text=True,
    # )

    # # Check if the script ran successfully
    # if result.returncode == 0:
    #     return {"statusCode": 200, "body": json.dumps("Tool ran successfully")}
    # else:
    #     return {
    #         "statusCode": 500,
    #         "body": json.dumps(f"Error running tool: {result.stderr}"),
    #     }
