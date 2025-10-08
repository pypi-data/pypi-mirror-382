import os
import time
from uuid import uuid4

from anthropic import Anthropic, NotGiven

from customer_utils import get_freeplay_thin_client, record_results_messages
from freeplay import ResponseInfo, CallInfo, RecordPayload

fp_client = get_freeplay_thin_client()
anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

project_id = os.environ["FREEPLAY_PROJECT_ID"]
template_prompt = fp_client.prompts.get(
    project_id=project_id, template_name="toolio", environment="latest"
)

test_run = fp_client.test_runs.create(
    project_id,
    "Tools",
    include_outputs=True,
    name=f"Test run: {uuid4()}",
    description="Run from Python examples",
    flavor_name=template_prompt.prompt_info.flavor_name,
)
for test_case in test_run.test_cases:
    formatted_prompt = template_prompt.bind(
        test_case.variables, history=test_case.history
    ).format()
    print(f"Ready for LLM: {formatted_prompt.llm_prompt}")

    start = time.time()
    completion = anthropic_client.messages.create(
        system=formatted_prompt.system_content or NotGiven(),
        messages=formatted_prompt.llm_prompt,
        model=formatted_prompt.prompt_info.model,
        tools=formatted_prompt.tool_schema,
        **formatted_prompt.prompt_info.model_parameters,
    )
    end = time.time()
    print("Completion: %s" % completion.content)

    session = fp_client.sessions.create()
    test_run_info = test_run.get_test_run_info(test_case.id)

    all_messages = formatted_prompt.all_messages(
        {"content": completion.content, "role": completion.role}
    )

    record_results_messages(
        fp_client,
        project_id,
        all_messages,
        test_case.variables,
        session,
        start,
        end,
        test_run_info=test_run_info,
        eval_results={"f1-score": 0.48, "is_non_empty": True},
        formatted_prompt=formatted_prompt,
    )

    print(all_messages)
    # Add tool result
    all_messages.append(
        {
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": all_messages[-1]["content"][1]["id"],
                    "content": "15 degrees",
                }
            ],
        }
    )

    new_prompt = template_prompt.bind(
        test_case.variables, history=all_messages
    ).format()
    print("NEW PROMPT", new_prompt.messages)

    start = time.time()
    second_completion = anthropic_client.messages.create(
        system=new_prompt.system_content or NotGiven(),
        messages=new_prompt.llm_prompt,
        model=new_prompt.prompt_info.model,
        tools=new_prompt.tool_schema,
        **new_prompt.prompt_info.model_parameters,
    )
    end = time.time()
    print("Completion: %s" % second_completion.content)

    final_messages = formatted_prompt.all_messages(
        {"content": second_completion.content, "role": second_completion.role}
    )

    call_info = CallInfo(
        formatted_prompt.prompt_info.provider,
        model=formatted_prompt.prompt_info.model,
        start_time=start,
        end_time=end,
        model_parameters=formatted_prompt.prompt_info.model_parameters,
    )

    response_info = ResponseInfo(is_complete=True)

    fp_client.recordings.create(
        RecordPayload(
            project_id=project_id,
            all_messages=final_messages,
            session_info=session.session_info,
            inputs=test_case.variables,
            prompt_version_info=formatted_prompt.prompt_info,
            call_info=call_info,
            response_info=response_info,
            test_run_info=test_run_info,
            eval_results={"f1-score": 0.48, "is_non_empty": True},
        )
    )

# wait 5 sec and get the results
time.sleep(5)
results = fp_client.test_runs.get(project_id, test_run.test_run_id)
print("Test run results")
print(results.test_run_id)
print(results.name)
print(results.description)
print(results.summary_statistics)
