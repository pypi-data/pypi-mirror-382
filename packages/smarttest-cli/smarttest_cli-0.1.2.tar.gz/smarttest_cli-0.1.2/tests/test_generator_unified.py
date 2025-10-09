import json
from types import SimpleNamespace
from unittest.mock import patch


def test_generator_returns_dict_on_list_response():
    from gpt import generate_validations_for_scenario

    fake_llm_list = [
        {"validation_text": "status == 200", "confidence": 0.9},
        {"validation_text": "body.id exists"},
    ]

    with patch("gpt.get_openai_client"), \
         patch("gpt.__call_and_process_gpt_answer", return_value=fake_llm_list):
        out = generate_validations_for_scenario(
            scenario={"scenario_id": 1, "scenario_name": "S1"},
            scenario_response={"status_code": 200, "headers": {}, "body": {"id": 1}},
        )

    assert set(out.keys()) == {"generated_validations", "confidence", "explanation"}
    assert isinstance(out["generated_validations"], list) and len(out["generated_validations"]) == 2
    assert out["generated_validations"][0]["validation_text"] == "status == 200"


def test_generator_handles_dict_validations_key():
    from gpt import generate_validations_for_scenario

    fake_llm_dict = {
        "validations": [
            {"validation_text": "Status is 201", "confidence": 0.8}
        ]
    }

    with patch("gpt.get_openai_client"), \
         patch("gpt.__call_and_process_gpt_answer", return_value=fake_llm_dict):
        out = generate_validations_for_scenario(
            scenario={"scenario_id": 2, "scenario_name": "S2"},
            scenario_response={"status_code": 201, "headers": {}, "body": {}},
        )

    assert out["generated_validations"][0]["validation_text"] == "Status is 201"


def test_generator_handles_json_parse_error_returns_empty():
    from gpt import generate_validations_for_scenario

    with patch("gpt.get_openai_client"), \
         patch("gpt.__call_and_process_gpt_answer", return_value={"error": "json_parse_failed"}):
        out = generate_validations_for_scenario(
            scenario={"scenario_id": 3, "scenario_name": "S3"},
            scenario_response={"status_code": 200, "headers": {}, "body": {}},
        )

    assert out["generated_validations"] == []
    assert out["confidence"] == 0.0
    assert "parse" in out["explanation"].lower()


def test_generator_prompt_includes_basic_swagger_when_available():
    from gpt import generate_validations_for_scenario

    # Minimal endpoint object with success responses but no definitions
    endpoint_db = SimpleNamespace(
        method="GET",
        endpoint="/x",
        raw_definition={"responses": {"200": {"description": "ok"}}},
        definitions_for_responses=[],
    )

    fake_llm_list = [
        {"validation_text": "status == 200"}
    ]

    with patch("gpt.get_openai_client"), \
         patch("gpt.__call_and_process_gpt_answer", return_value=fake_llm_list) as mocked:
        _ = generate_validations_for_scenario(
            scenario={"scenario_id": 4, "scenario_name": "S4"},
            scenario_response={"status_code": 200, "headers": {}, "body": {}},
            endpoint_db=endpoint_db,
        )

    # Assert the prompt contained BASIC RESPONSE STRUCTURE text
    prompt_arg = mocked.call_args[0][0]
    assert "BASIC RESPONSE STRUCTURE" in prompt_arg
    assert json.dumps(endpoint_db.raw_definition["responses"], indent=2) in prompt_arg


def test_generator_skips_swagger_block_for_error_scenario():
    from gpt import generate_validations_for_scenario

    endpoint_db = SimpleNamespace(
        method="GET",
        endpoint="/x",
        raw_definition={"responses": {"200": {}}},
        definitions_for_responses=[],
    )
    scenario_db = SimpleNamespace(error_in="body")

    fake_llm_list = [
        {"validation_text": "status == 400"}
    ]

    with patch("gpt.get_openai_client"), \
         patch("gpt.__call_and_process_gpt_answer", return_value=fake_llm_list) as mocked:
        _ = generate_validations_for_scenario(
            scenario={"scenario_id": 5, "scenario_name": "S5"},
            scenario_response={"status_code": 400, "headers": {}, "body": {}},
            endpoint_db=endpoint_db,
            scenario_db=scenario_db,
        )

    prompt_arg = mocked.call_args[0][0]
    assert "EXPECTED RESPONSE STRUCTURE" not in prompt_arg
    assert "BASIC RESPONSE STRUCTURE" not in prompt_arg



