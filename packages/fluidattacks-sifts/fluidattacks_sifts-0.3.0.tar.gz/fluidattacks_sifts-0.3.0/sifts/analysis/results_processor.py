import json

import aioboto3

from sifts.io.db.types import AnalysisFacet


async def submit_vulnerability_to_sqs(result: AnalysisFacet) -> None:
    session = aioboto3.Session()
    async with session.client("sqs", region_name="us-east-1") as sqs_client:
        await sqs_client.send_message(
            QueueUrl="https://sqs.us-east-1.amazonaws.com/205810638802/integrates_llm_report",
            MessageBody=json.dumps(
                {
                    "id": f"{result.snippet_hash_id}_{result.commit}",
                    "task": "report_llm",
                    "args": [result.root_nickname, result.path, result.snippet_hash_id, "None"],
                },
            ),
        )
