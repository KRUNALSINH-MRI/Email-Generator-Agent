import json

import pytest
import requests
from azure.identity import DefaultAzureCredential


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

AGENT_ENDPOINT = (
    "https://email-generator-krunal-resource.services.ai.azure.com/"
    "api/projects/email-generator-foundry/"
    "agents/email-generator/"
    "endpoint/protocols/invocations?api-version=v1"
)

TOKEN_SCOPE = "https://ai.azure.com/.default"


# ---------------------------------------------------------------------------
# Authentication
# ---------------------------------------------------------------------------

def get_auth_headers():
    """
    Get an Azure access token using the current Azure login/environment.
    """

    credential = DefaultAzureCredential()

    token = credential.get_token(TOKEN_SCOPE)

    return {
        "Authorization": f"Bearer {token.token}",
        "Content-Type": "application/json",
    }


# ---------------------------------------------------------------------------
# Agent invocation
# ---------------------------------------------------------------------------

def invoke_agent(payload):
    """
    Call the deployed Azure Foundry Hosted Agent.
    """

    headers = get_auth_headers()

    response = requests.post(
        AGENT_ENDPOINT,
        headers=headers,
        json=payload,
        timeout=120,
    )

    return response


def parse_agent_response(response):
    """
    Parse the response returned by the Hosted Agent.

    The deployed agent currently returns a structure like:

    {
        "response": "{\"subject\": \"...\", \"email\": \"...\"}"
    }
    """

    response.raise_for_status()

    body = response.json()

    # The Hosted Agent wraps the actual result inside "response".
    if "response" in body:
        result = body["response"]

        if isinstance(result, str):
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                return {"response": result}

        return result

    return body


# ---------------------------------------------------------------------------
# Test data
# ---------------------------------------------------------------------------

FORMAL_PAYLOAD = {
    "tone": "formal",
    "context": (
        "Requesting an update from the development team "
        "about a delayed project."
    ),
    "data_points": [
        "Project delivery is delayed by two days.",
        "Updated timeline is required.",
        "Please provide the revised completion date.",
    ],
}


FRIENDLY_PAYLOAD = {
    "tone": "friendly",
    "context": (
        "Following up with a colleague about the progress "
        "of an important task."
    ),
    "data_points": [
        "The task was expected to be completed yesterday.",
        "Please share the current status.",
        "Let us know if any help is required.",
    ],
}


EMPATHETIC_PAYLOAD = {
    "tone": "empathetic",
    "context": (
        "Communicating with a customer who has been affected "
        "by a service delay."
    ),
    "data_points": [
        "The service was delayed by 24 hours.",
        "The issue has now been resolved.",
        "We appreciate the customer's patience.",
    ],
}


ASSERTIVE_PAYLOAD = {
    "tone": "assertive",
    "context": (
        "Requesting an overdue deliverable from the development team."
    ),
    "data_points": [
        "The deliverable was due on Friday.",
        "It is required for Monday's release.",
        "Please provide the deliverable and current status immediately.",
    ],
}


# ---------------------------------------------------------------------------
# Helper assertions
# ---------------------------------------------------------------------------

def assert_valid_email_response(response):
    """
    Verify that a successful agent invocation produced
    both a subject and an email body.
    """

    assert response.status_code == 200, (
        f"Expected HTTP 200 but received {response.status_code}.\n"
        f"Response: {response.text}"
    )

    result = parse_agent_response(response)

    assert isinstance(result, dict), (
        f"Expected a dictionary response but received: {result}"
    )

    assert "subject" in result, (
        f"Response does not contain 'subject': {result}"
    )

    assert "email" in result, (
        f"Response does not contain 'email': {result}"
    )

    assert isinstance(result["subject"], str), (
        "Subject should be a string."
    )

    assert isinstance(result["email"], str), (
        "Email should be a string."
    )

    assert result["subject"].strip(), (
        "Generated subject should not be empty."
    )

    assert result["email"].strip(), (
        "Generated email should not be empty."
    )

    return result


def assert_validation_error(response, expected_field):
    """
    Verify that the deployed agent detects a missing required field.

    Depending on the Hosted Agent / Invocation Protocol configuration,
    validation can be represented either by an HTTP error status or
    by an error message returned in a successful HTTP response.
    """

    # HTTP-level validation failure
    if response.status_code >= 400:
        response_text = response.text.lower()

        assert expected_field.lower() in response_text, (
            f"Expected validation error for '{expected_field}', "
            f"but received:\n{response.text}"
        )

        return

    # Some Hosted Agent implementations return validation errors
    # inside a successful HTTP response.
    try:
        body = response.json()
    except ValueError:
        body = response.text

    response_text = json.dumps(body).lower()

    assert expected_field.lower() in response_text, (
        f"Expected validation error mentioning '{expected_field}', "
        f"but received:\n{response.text}"
    )


# ---------------------------------------------------------------------------
# 1. Formal email
# ---------------------------------------------------------------------------

def test_formal_email():
    """
    Verify that the deployed agent generates a valid email
    when the requested tone is formal.
    """

    response = invoke_agent(FORMAL_PAYLOAD)

    result = assert_valid_email_response(response)

    print("\n--- Formal Email ---")
    print("Subject:", result["subject"])
    print("Email:")
    print(result["email"])


# ---------------------------------------------------------------------------
# 2. Friendly email
# ---------------------------------------------------------------------------

def test_friendly_email():
    """
    Verify that the deployed agent generates a valid email
    when the requested tone is friendly.
    """

    response = invoke_agent(FRIENDLY_PAYLOAD)

    result = assert_valid_email_response(response)

    print("\n--- Friendly Email ---")
    print("Subject:", result["subject"])
    print("Email:")
    print(result["email"])


# ---------------------------------------------------------------------------
# 3. Empathetic email
# ---------------------------------------------------------------------------

def test_empathetic_email():
    """
    Verify that the deployed agent generates a valid email
    when the requested tone is empathetic.
    """

    response = invoke_agent(EMPATHETIC_PAYLOAD)

    result = assert_valid_email_response(response)

    print("\n--- Empathetic Email ---")
    print("Subject:", result["subject"])
    print("Email:")
    print(result["email"])


# ---------------------------------------------------------------------------
# 4. Assertive email
# ---------------------------------------------------------------------------

def test_assertive_email():
    """
    Verify that the deployed agent generates a valid email
    when the requested tone is assertive.
    """

    response = invoke_agent(ASSERTIVE_PAYLOAD)

    result = assert_valid_email_response(response)

    print("\n--- Assertive Email ---")
    print("Subject:", result["subject"])
    print("Email:")
    print(result["email"])


# ---------------------------------------------------------------------------
# 5. Missing tone
# ---------------------------------------------------------------------------

def test_missing_tone():
    """
    Verify that the deployed agent validates a missing tone.
    """

    payload = {
        "tone": "",
        "context": (
            "Requesting an update from the development team "
            "about a delayed project."
        ),
        "data_points": [
            "Project delivery is delayed by two days.",
            "Updated timeline is required.",
        ],
    }

    response = invoke_agent(payload)

    assert_validation_error(response, "tone")


# ---------------------------------------------------------------------------
# 6. Missing context
# ---------------------------------------------------------------------------

def test_missing_context():
    """
    Verify that the deployed agent validates a missing context.
    """

    payload = {
        "tone": "formal",
        "context": "",
        "data_points": [
            "Project delivery is delayed by two days.",
            "Updated timeline is required.",
        ],
    }

    response = invoke_agent(payload)

    assert_validation_error(response, "context")


# ---------------------------------------------------------------------------
# 7. Missing data points
# ---------------------------------------------------------------------------

def test_missing_data_points():
    """
    Verify that the deployed agent validates missing data points.
    """

    payload = {
        "tone": "formal",
        "context": (
            "Requesting an update from the development team "
            "about a delayed project."
        ),
        "data_points": [],
    }

    response = invoke_agent(payload)

    assert_validation_error(response, "data_points")