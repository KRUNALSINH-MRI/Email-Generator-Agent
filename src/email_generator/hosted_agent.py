import json

from langchain_azure_ai.agents.hosting import InvocationsHostServer

from .graph import graph


class EmailGeneratorHostServer(InvocationsHostServer):
    @staticmethod
    def _validate_graph_schema(graph):
        return None

    async def parse_request(self, request):
        data = await request.json()

        if isinstance(data, dict):
            if "tone" in data or "data_points" in data or "context" in data:
                message = json.dumps(data)
            elif "message" in data:
                msg = data["message"]
                message = json.dumps(msg) if isinstance(msg, dict) else str(msg) if msg else ""
            elif "input" in data:
                inp = data["input"]
                message = json.dumps(inp) if isinstance(inp, dict) else str(inp) if inp else ""
            else:
                message = json.dumps(data)
        elif isinstance(data, str):
            message = data
        else:
            message = json.dumps(data) if data else ""

        if not message:
            message = json.dumps({"tone": "", "context": "", "data_points": []})

        stream = bool(data.get("stream", False)) if isinstance(data, dict) else False
        return message, stream

    def build_input(self, message: str):
        try:
            payload = json.loads(message)
            if not isinstance(payload, dict):
                payload = {}
        except (json.JSONDecodeError, TypeError):
            payload = {}

        return {
            "tone": payload.get("tone", ""),
            "context": payload.get("context", ""),
            "data_points": payload.get("data_points", []),
            "mcp_guidelines": "",
            "prompt": "",
            "subject": "",
            "email": "",
            "error": "",
        }

    def parse_output(self, output) -> str:
        error = output.get("error", "")
        if error:
            missing = []
            if "tone" in error.lower():
                missing.append("tone")
            if "context" in error.lower():
                missing.append("context")
            if "data_points" in error.lower() or "data point" in error.lower():
                missing.append("data_points")
            return json.dumps({
                "subject": "",
                "email": "",
                "error": error,
                "missing_fields": missing,
            })

        return json.dumps({
            "subject": output.get("subject", ""),
            "email": output.get("email", ""),
        })


def main():
    server = EmailGeneratorHostServer(
        graph=graph,
    )

    server.run()


if __name__ == "__main__":
    main()