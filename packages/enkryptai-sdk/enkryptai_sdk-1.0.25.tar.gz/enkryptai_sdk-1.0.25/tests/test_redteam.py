import time
from fixtures import *

redteam_test_name = None
redteam_model_test_name = None
custom_redteam_test_name = None
custom_redteam_model_test_name = None
redteam_picked_test_name = None
test_model_saved_name = "Test Model"
test_model_version = "v1"


def get_task_name_from_list(redteam_client, status=None):
    """Helper function to get a redteam task name from the task list.
    
    Args:
        redteam_client: The RedTeamClient instance
        status: Optional status filter (e.g., "Finished", "Running")
    
    Returns:
        str: A test name from the task list
    """
    print(f"\nFetching redteam task with status: {status if status else 'Finished'}")
    redteams = redteam_client.get_task_list(status=status)
    redteams_dict = redteams.to_dict()
    print(f"\nRedteam task list retrieved with {len(redteams_dict.get('tasks', []))} tasks")
    
    if not redteams_dict.get("tasks"):
        # If no tasks with specified status, try without status filter
        if status:
            print(f"\nNo tasks with status '{status}', fetching any task")
            redteams = redteam_client.get_task_list()
            redteams_dict = redteams.to_dict()
    
    if not redteams_dict.get("tasks"):
        return None
    
    task_info = redteams_dict["tasks"][0]
    test_name = task_info["test_name"]
    print(f"\nSelected redteam task: {test_name} (Status: {task_info.get('status', 'unknown')})")
    return test_name


def test_get_health(redteam_client):
    print("\n\nTesting get_health")
    response = redteam_client.get_health()
    print("\nResponse from get_health: ", response)
    assert response is not None
    assert hasattr(response, "status")
    assert response.status == "healthy"


# def test_model_health(redteam_client, sample_redteam_model_health_config):
#     print("\n\nTesting check_model_health")
#     response = redteam_client.check_model_health(config=sample_redteam_model_health_config)
#     print("\nResponse from check_model_health: ", response)
#     assert response is not None
#     assert hasattr(response, "status")
#     assert response.status == "healthy"


# def test_saved_model_health(redteam_client):
#     print("\n\nTesting check_saved_model_health")
#     response = redteam_client.check_saved_model_health(model_saved_name=test_model_saved_name, model_version=test_model_version)
#     print("\nResponse from check_saved_model_health: ", response)
#     assert response is not None
#     assert hasattr(response, "status")
#     assert response.status == "healthy"


def test_model_health_v3(redteam_client, sample_redteam_model_health_config_v3):
    print("\n\nTesting check_model_health_v3")
    response = redteam_client.check_model_health_v3(config=sample_redteam_model_health_config_v3)
    print("\nResponse from check_model_health_v3: ", response)
    assert response is not None
    assert hasattr(response, "status")
    assert response.status == "healthy"


# # Testing only via saved model as it should be sufficient
# ---------------------------------------------------------
# def test_add_task_with_target_model(redteam_client, sample_redteam_target_config):
#     print("\n\nTesting adding a new redteam task with target model")
#     # Debug sample_redteam_target_config
#     # print("\nSample redteam target config: ", sample_redteam_target_config)
#     response = redteam_client.add_task(config=sample_redteam_target_config)
#     print("\nResponse from adding a new redteam task with target model: ", response)
#     assert response is not None
#     assert hasattr(response, "task_id")
#     assert hasattr(response, "message")
#     response.message == "Redteam task has been added successfully"
#     # Sleep for a while to let the task complete
#     # This is also useful to avoid rate limiting issues
#     print("\nSleeping for 60 seconds to let the task complete if possible ...")
#     time.sleep(60)


# def test_add_task_with_saved_model(redteam_client, sample_redteam_model_config):
#     print("\n\nTesting adding a new redteam task with saved model")
#     response = redteam_client.add_task_with_saved_model(config=sample_redteam_model_config,model_saved_name=test_model_saved_name, model_version=test_model_version)
#     print("\nResponse from adding a new redteam task with saved model: ", response)
#     assert response is not None
#     assert hasattr(response, "task_id")
#     assert hasattr(response, "message")
#     response.message == "Redteam task has been added successfully"
#     # Sleep for a while to let the task complete
#     # This is also useful to avoid rate limiting issues
#     print("\nSleeping for 60 seconds to let the task complete if possible ...")
#     time.sleep(60)


# # Testing only via saved model as it should be sufficient
# ---------------------------------------------------------
# def test_add_custom_task_with_target_model(redteam_client, sample_custom_redteam_target_config):
#     print("\n\nTesting adding a new custom redteam task with target model")
#     # Debug sample_custom_redteam_target_config
#     # print("\nSample custom redteam target config: ", sample_custom_redteam_target_config)
#     response = redteam_client.add_custom_task(config=sample_custom_redteam_target_config)
#     print("\nResponse from adding a new custom redteam task with target model: ", response)
#     assert response is not None
#     assert hasattr(response, "task_id")
#     assert hasattr(response, "message")
#     response.message == "Task submitted successfully"
#     # Sleep for a while to let the task complete
#     # This is also useful to avoid rate limiting issues
#     print("\nSleeping for 60 seconds to let the task complete if possible ...")
#     time.sleep(60)


# def test_add_custom_task_with_saved_model(redteam_client, sample_custom_redteam_model_config):
#     print("\n\nTesting adding a new custom redteam task with saved model")
#     response = redteam_client.add_custom_task_with_saved_model(config=sample_custom_redteam_model_config, model_saved_name=test_model_saved_name, model_version=test_model_version)
#     print("\nResponse from adding a new custom redteam task with saved model: ", response)
#     assert response is not None
#     assert hasattr(response, "task_id")
#     assert hasattr(response, "message")
#     response.message == "Task submitted successfully"
#     # Sleep for a while to let the task complete
#     # This is also useful to avoid rate limiting issues
#     print("\nSleeping for 60 seconds to let the task complete if possible ...")
#     time.sleep(60)


# ------------------- V3 TESTS -------------------

# def test_add_custom_task_v3(redteam_client, sample_custom_redteam_target_config_v3):
#     print("\n\nTesting adding a new custom redteam v3 task with target model")
#     response = redteam_client.add_custom_task_v3(config=sample_custom_redteam_target_config_v3)
#     print("\nResponse from adding a new custom redteam v3 task with target model: ", response)
#     assert response is not None
#     assert hasattr(response, "task_id")
#     assert hasattr(response, "message")
#     response.message == "Task submitted successfully"
#     # Sleep for a while to let the task complete
#     # This is also useful to avoid rate limiting issues
#     print("\nSleeping for 60 seconds to let the task complete if possible ...")
#     time.sleep(60)


def test_add_custom_task_with_saved_model_v3(redteam_client, sample_custom_redteam_model_config_v3):
    print("\n\nTesting adding a new custom redteam v3 task with saved model")
    response = redteam_client.add_custom_task_with_saved_model_v3(config=sample_custom_redteam_model_config_v3, model_saved_name=test_model_saved_name, model_version=test_model_version)
    print("\nResponse from adding a new custom redteam v3 task with saved model: ", response)
    assert response is not None
    assert hasattr(response, "task_id")
    assert hasattr(response, "message")
    response.message == "Task submitted successfully"
    # Sleep for a while to let the task complete
    # This is also useful to avoid rate limiting issues
    print("\nSleeping for 60 seconds to let the task complete if possible ...")
    time.sleep(60)


def test_list_redteams(redteam_client):
    print("\n\nTesting list_redteam tasks")
    redteams = redteam_client.get_task_list(status="Finished")
    redteams_dict = redteams.to_dict()
    print("\nRedteam task list: ", redteams_dict)
    assert redteams_dict is not None
    assert isinstance(redteams_dict, dict)
    assert "tasks" in redteams_dict
    
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None
        print("\nPicked redteam finished task in list_redteams: ", redteam_picked_test_name)


def test_get_task_status(redteam_client):
    print("\n\nTesting get_task_status")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.status(test_name=redteam_picked_test_name)
    print("\nRedteam task status: ", response)
    assert response is not None
    assert hasattr(response, "status")


def test_get_task(redteam_client):
    print("\n\nTesting get_task")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.get_task(test_name=redteam_picked_test_name)
    print("\nRedteam task: ", response)
    assert response is not None
    assert hasattr(response, "status")


def test_get_download_link(redteam_client):
    print("\n\nTesting get_download_link")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.get_download_link(test_name=redteam_picked_test_name)
    print("\nRedteam task download link: ", response)
    assert response is not None
    assert hasattr(response, "link")
    assert hasattr(response, "expiry")
    assert hasattr(response, "expires_at")


def test_get_result_summary(redteam_client):
    print("\n\nTesting get_result_summary")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.get_result_summary(test_name=redteam_picked_test_name)
    print("\nRedteam task result summary: ", response)
    assert response is not None
    # # Task might not be successful yet
    # # TODO: How to handle this?
    # assert hasattr(response, "summary")


def test_get_result_summary_test_type(redteam_client):
    print("\n\nTesting get_result_summary_test_type")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.get_result_summary_test_type(test_name=redteam_picked_test_name, test_type="harmful_test")
    print("\nRedteam task result summary of test type: ", response)
    assert response is not None
    # # Task might not be successful yet
    # # TODO: How to handle this?
    # assert hasattr(response, "summary")


def test_get_result_details(redteam_client):
    print("\n\nTesting get_result_details")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.get_result_details(test_name=redteam_picked_test_name)
    print("\nRedteam task result details: ", response)
    assert response is not None
    # # Task might not be successful yet
    # # TODO: How to handle this?
    # assert hasattr(response, "details")


def test_get_result_details_test_type(redteam_client):
    print("\n\nTesting get_result_details_test_type")
    global redteam_picked_test_name
    if redteam_picked_test_name is None:
        redteam_picked_test_name = get_task_name_from_list(redteam_client, status="Finished")
        assert redteam_picked_test_name is not None

    response = redteam_client.get_result_details_test_type(test_name=redteam_picked_test_name, test_type="harmful_test")
    print("\nRedteam task result details of test type: ", response)
    assert response is not None
    # # Task might not be successful yet
    # # TODO: How to handle this?
    # assert hasattr(response, "details")


def test_get_findings(redteam_client, sample_redteam_summary):
    print("\n\nTesting get_findings")
    response = redteam_client.get_findings(redteam_summary=sample_redteam_summary)
    print("\nRedteam task findings: ", response)
    assert response is not None
    assert hasattr(response, "key_findings")
    assert len(response.key_findings) > 0
    assert response.message == "Key Findings have been generated successfully"


def test_risk_mitigation_guardrails_policy(redteam_client, sample_redteam_risk_mitigation_guardrails_policy_config):
    print("\n\nTesting risk_mitigation_guardrails_policy")
    response = redteam_client.risk_mitigation_guardrails_policy(config=sample_redteam_risk_mitigation_guardrails_policy_config)
    print("\nResponse from risk_mitigation_guardrails_policy: ", response)
    print("\nGuardrails policy: ", response.guardrails_policy.to_dict())
    assert response is not None
    assert hasattr(response, "analysis")
    assert hasattr(response, "guardrails_policy")
    assert hasattr(response, "message")
    assert response.message == "Guardrails configuration has been generated successfully"


def test_risk_mitigation_system_prompt(redteam_client, sample_redteam_risk_mitigation_system_prompt_config):
    print("\n\nTesting risk_mitigation_system_prompt")
    response = redteam_client.risk_mitigation_system_prompt(config=sample_redteam_risk_mitigation_system_prompt_config)
    print("\nResponse from risk_mitigation_system_prompt: ", response)
    assert response is not None
    assert hasattr(response, "analysis")
    assert hasattr(response, "system_prompt")
    assert hasattr(response, "message")
    assert response.message == "System prompt has been generated successfully"

