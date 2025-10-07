from tron.core.app.workflow.ci_pipeline.ci_pipeline_models import *


class CiPipelineHandlers:
    def __init__(self, base_url: str, headers: dict):
        pass

    @staticmethod
    def get_ci_id_using_name(base_url, headers, ci_pipeline_name: str, app_id):
        import requests

        url = f"{base_url}/orchestrator/app/ci-pipeline/{app_id}"
        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": "Failed to get CI Pipelines"
                }
            pipelines = response.json().get("result", {}).get("ciPipelines", [])
            for pipeline in pipelines:

                if pipeline.get("name", "") == ci_pipeline_name:
                    return {
                        "success": True,
                        "ci_pipeline_id": pipeline.get("id", 0)
                    }
            return {
                "success": False,
                "error": "CI Pipeline not found"
            }

        except Exception as e:
            print("Could not fetch the CI pipeline ID")
            return {
                "success": False,
                "error": str(e)
            }

    @staticmethod
    def get_pre_post_step_variable(input_vars: list) -> list[InputVariable]:
        try:
            input_variables = []
            if input_vars:
                for variable in input_vars:

                    value_constraint = InputVariableValueConstraint(
                        _id=variable.get("valueConstraint", {}).get("id", 0),
                        choices=variable.get("valueConstraint", {}).get("choices", []),
                        block_custom_value=variable.get("valueConstraint", {}).get("blockCustomValue", False),
                        constraint=variable.get("valueConstraint", {}).get("constraint", {})
                    )

                    input_variables.append(InputVariable(
                        allow_empty_value=variable.get("allowEmptyValue", False),
                        description=variable.get("description", ""),
                        _format=variable.get("format", "STRING"),
                        _id=variable.get("id", 0),
                        name=variable.get("name", ""),
                        value=variable.get("value", ""),
                        value_constraint=value_constraint,
                        variable_type=variable.get("variableType", "NEW")
                    ))
                return input_variables

        except Exception as e:
            print("get_pre_post_step_variable", "Exception occurred:", e)
            return []


    @staticmethod
    def get_pre_post_ci_cd_step_detail(plugin_ref_detail: dict) -> PluginRefStepDetail:
        try:
            input_vars = plugin_ref_detail.get("inputVariables", [])
            input_variables = CiPipelineHandlers.get_pre_post_step_variable(input_vars)

            return PluginRefStepDetail(
                plugin_id=plugin_ref_detail.get("pluginId", 0),
                plugin_name=plugin_ref_detail.get("pluginName", ""),
                plugin_version=plugin_ref_detail.get("pluginVersion", ""),
                input_var_data=input_variables,
                out_put_variables=plugin_ref_detail.get("outputVariables", []),
                condition_details=plugin_ref_detail.get("conditionDetails", [])
            )

        except Exception as e:
            print("get_pre_post_ci_cd_step_detail","Exception occurred:", e)
            return {}


    @staticmethod
    def get_pre_post_ci_step(step: dict) -> PrePostBuildConfigStep:

        try:
            plugin_ref_step_detail = CiPipelineHandlers.get_pre_post_ci_cd_step_detail(step.get("pluginRefStepDetail", {}))

            return PrePostBuildConfigStep(
                _id=step.get("id", 0),
                name=step.get("name", ""),
                description=step.get("description", ""),
                index=step.get("index", 0),
                step_type=step.get("stepType", ""),
                output_directory_path=step.get("outputDirectoryPath", None),
                inline_step_detail=step.get("inlineStepDetail", {}),
                trigger_if_parent_stage_fail=step.get("triggerIfParentStageFail", False),
                plugin_ref_step_detail=plugin_ref_step_detail
            )

        except Exception as e:
            print("get_pre_post_ci_step",f"Exception occurred:", e)
            return {}


    @staticmethod
    def get_pre_post_build_config(pre_post_ci_cd_stage: dict) -> PrePostBuildConfig:
        try:
            if not pre_post_ci_cd_stage:
                return {}
            pre_post_ci_steps = []

            for step in pre_post_ci_cd_stage.get("steps", []):
                pre_post_ci_steps.append(CiPipelineHandlers.get_pre_post_ci_step(step))

            return PrePostBuildConfig(
                _type=pre_post_ci_cd_stage.get("type", ""),
                _id=pre_post_ci_cd_stage.get("id", 0),
                trigger_blocked_info=pre_post_ci_cd_stage.get("triggerBlockedInfo", {}),
                steps=pre_post_ci_steps
            )

        except Exception as e:
            print("get_pre_post_build_config","Exception occurred:", e)
            return {}


    @staticmethod
    def check_if_plugin_updated(plugin_name: str = "", plugin_id: int = 0, plugin_version: str = "1.0.0", plugin_metadata: dict = None) -> dict:

        for plugin in plugin_metadata.get("parentPlugins", []):
            for minimal_plugin_version_data in plugin.get("pluginVersions", {}).get("minimalPluginVersionData", []):
                if plugin_name == minimal_plugin_version_data["name"]:

                    if plugin_version == minimal_plugin_version_data["pluginVersion"] and plugin_id == minimal_plugin_version_data["id"]:

                        return {
                            "is_modified": False,
                            "field": {}
                        }
                    elif plugin_version == minimal_plugin_version_data["pluginVersion"]:

                        return {
                            "is_modified": True,
                            "field": {
                                "pluginId" : minimal_plugin_version_data["id"],
                                "pluginVersion": minimal_plugin_version_data["pluginVersion"]
                            }
                        }

        return {
            "is_modified": True,
            "field": {"pluginName": plugin_name }
        }

    @staticmethod
    def update_pre_post_ci_steps(current_steps: list, new_steps: list, plugin_metadata: dict, applied_plugin_metadata: list) -> list:
        try:
            current_steps_indices = {}
            plugin_minimal_data = {}

            for plugin in plugin_metadata.get("parentPlugins", []):
                for version in plugin.get("pluginVersions", {}).get("detailedPluginVersionData", []):
                    (plugin_name, plugin_version) = (version.get("name", ""), version.get("pluginVersion", ""))

                    if (plugin_name, plugin_version) != ("", ""):
                        plugin_minimal_data[(plugin_name, plugin_version)] = version

            plugin_name = ""
            for i in range(len(current_steps)):
                for parentPlugin in plugin_metadata.get("parentPlugins", []):
                    for minimal_plugin_version_data in parentPlugin.get("pluginVersions", {}).get("minimalPluginVersionData", []):

                        if minimal_plugin_version_data.get("id", 0) == current_steps[i].plugin_ref_step_detail.plugin_id:
                            plugin_name = minimal_plugin_version_data.get("name", "")

                current_steps_indices[(current_steps[i].name, plugin_name)] = current_steps[i]
            indices = [(step["task_name"], step["name"]) for step in new_steps]

            index = 1

            updated_steps = []
            for step in new_steps:
                if current_steps_indices.get((step["task_name"], step["name"])):
                    patch_pre_post_ci_step_result = CiPipelineHandlers.patch_pre_post_ci_step(current_steps_indices.get((step["task_name"], step["name"])), step, index, plugin_minimal_data[(step["name"], step["version"])])
                    if not patch_pre_post_ci_step_result["success"]:
                        return current_steps
                    updated_steps.append(patch_pre_post_ci_step_result.get("desired_step"))
                    index += 1

                else:
                    detailed_plugin_version_data = []
                    for plugin_data in applied_plugin_metadata:
                        if step.get("name", "") == plugin_data.get("name"):
                            detailed_plugin_version_data = plugin_data.get("pluginVersions", {}).get("detailedPluginVersionData", [])
                            break
                    if not detailed_plugin_version_data:
                        return current_steps

                    add_plugin_result = CiPipelineHandlers.add_new_plugin(step, index, applied_plugin_metadata, detailed_plugin_version_data)
                    if not add_plugin_result["success"]:
                        return current_steps
                    updated_steps.append(add_plugin_result.get("desired_step"))
                    index += 1

            return updated_steps

        except Exception as e:
            print("Error coocurred:", str(e))
            return current_steps

    @staticmethod
    def add_new_plugin(step: dict, index: int, applied_plugin_metadata: list, detailed_plugin_version_data: list):


        try:
            plugin_version = step.get("version", "1.0.0")
            plugin = {}
            for data in detailed_plugin_version_data:
                if data.get("pluginVersion", "") == plugin_version:
                    plugin = data
                    break

            input_variables = []
            if plugin.get("inputVariables", []):

                for input_variable in plugin.get("inputVariables", []):

                    input_variables.append(InputVariable(
                        allow_empty_value=input_variable.get("allowEmptyValue", False),
                        description=input_variable.get("description", ""),
                        _format=input_variable.get("format", "STRING"),
                        _id=input_variable.get("id", 0),
                        name=input_variable.get("name", ""),
                        value=step.get("input_variables", {}).get(input_variable.get("name", ""), ""),
                        value_constraint=None,
                        variable_type="NEW"
                    ))

            plugin_ref_step_detail = PluginRefStepDetail(
                    plugin_id=plugin.get("id", 0),
                    plugin_name="",
                    plugin_version=plugin.get("pluginVersion", ""),
                    input_var_data=input_variables,
                    out_put_variables=None,
                    condition_details=None
                )

            desired_step = PrePostBuildConfigStep(
                _id=index,
                name=step.get("task_name", ""),
                description=step.get("description", ""),
                index=index,
                step_type="REF_PLUGIN",
                plugin_ref_step_detail=plugin_ref_step_detail,
                output_directory_path=None,
                inline_step_detail={},
                trigger_if_parent_stage_fail=False
            )

            return {
                "success": True,
                "desired_step": desired_step,
                "Message": "Plugin object returned successfully"
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


    @staticmethod
    def patch_pre_post_ci_step(current_step: PrePostBuildConfigStep, desired_step: dict, index: int, plugin: dict)-> dict:
        try:

            input_variables = []

            for variable in current_step.plugin_ref_step_detail.input_variables:


                tmp = InputVariable(
                    allow_empty_value=variable.allow_empty_value,
                    description=variable.description,
                    _format=variable._format,
                    _id=variable.id,
                    name=variable.name,
                    value=desired_step.get("input_variables", {}).get(variable.name),
                    value_constraint=variable.value_constraint,
                    variable_type=variable.variable_type
                )
                input_variables.append(tmp)

            current_step.index = index
            current_step.plugin_ref_step_detail.plugin_id = plugin.get("id", 0)
            current_step.plugin_ref_step_detail.plugin_version = desired_step.get("version", "")
            current_step.plugin_ref_step_detail.input_variables = input_variables


            return {
                "success": True,
                'desired_step': current_step,
                "message": "Configstep patched"
            }

        except Exception as e:
            print("patch_pre_post_ci_step","Exception occurred:", e)
            return {
                "success": False,
                "error": str(e)
            }


    @staticmethod
    def update_pre_post_ci_steps_old(current_steps: list, new_steps: list, plugin_metadata: dict) -> list:
        index = 1
        for i in range(len(new_steps)):
            for j in range(len(current_steps)):
                if new_steps[i].get("task_name", "") == current_steps[j].name:
                    is_plugin_updated = CiPipelineHandlers.check_if_plugin_updated(new_steps[i].get("name", ""), current_steps[j].pluginRefStepDetail.pluginId, new_steps[i].get("version", ""), plugin_metadata)
                    if not is_plugin_updated["is_modified"]:
                        for variable in current_steps[j].pluginRefStepDetail.inputVariables:
                            variable.value = new_steps[i].get("input_variables", {}).get(variable.name, "")
                        current_steps[j].index = index
                        index += 1
                    else:
                        if is_plugin_updated.get("field", {}).get("pluginVersion", ""):
                            print("Version of the plugin is updated")
                        else:
                            print("Another plugin is getting used")
        return current_steps



    @staticmethod
    def update_pre_post_build_config(current_pre_post_build: PrePostBuildConfig, pre_post_build_config: list, plugin_metadata: dict, applied_plugin_metadata: list, is_cd: bool = False, step_type: str = "", trigger_type: str = "MANUAL") -> PrePostBuildConfig:


        try:

            if not current_pre_post_build:
                current_pre_post_build =  PrePostBuildConfig(
                    steps=[],
                    _type=step_type,
                    trigger_type=trigger_type
                )

            if is_cd:
                current_pre_post_build.trigger_type  = trigger_type

            current_pre_post_build.steps = CiPipelineHandlers.update_pre_post_ci_steps(
                current_pre_post_build.steps,
                pre_post_build_config,
                plugin_metadata,
                applied_plugin_metadata
            )


            return current_pre_post_build

        except Exception as e:
            print("update_pre_post_build_config","Exception occurred:", e)
            return {}


    @staticmethod
    def get_ci_material(ci_material: list[dict]) -> list[CiMaterial]:
        try:
            materials = []
            for material in ci_material:
                source = material.get("source", {})
                ci_material_source = CiMaterialSource(
                    _type=source.get("type", ""),
                    value=source.get("value", ""),
                    regex=source.get("regex", "")
                )
                materials.append(CiMaterial(
                    git_material_id=material.get("gitMaterialId", 0),
                    _id=material.get("id", 0),
                    git_material_name=material.get("gitMaterialName", ""),
                    is_regex=material.get("isRegex", False),
                    source=ci_material_source
                ))
            return materials

        except Exception as e:
            print("get_ci_material","Exception occurred:", e)
            return []


    @staticmethod
    def update_ci_material(ci_material: list[CiMaterial], branches: list[dict]) -> list[CiMaterial]:
        try:

            for i in range(len(branches)):
                ci_material[i].source.type = branches[i].get("type", ci_material[i].source.type)
                ci_material[i].source.value = branches[i].get("branch", ci_material[i].source.value)
                ci_material[i].source.regex = branches[i].get("regex", ci_material[i].source.regex)

            return ci_material

        except Exception as e:
            print("update_ci_material","Exception occurred:", e)
            return []


    @staticmethod
    def get_ci_pipeline(base_url: str, headers: dict, app_id: int, ci_pipeline_id: int) -> dict:
        import requests

        url = f"{base_url}/orchestrator/app/ci-pipeline/{app_id}/{ci_pipeline_id}"

        try:
            response = requests.get(url, headers=headers)
            if response.status_code != 200:
                return {
                    "success": False,
                    "error": f"Failed to fetch CI pipeline details: {response.text}"
                }

            details = response.json().get("result", {})

            if details.get("workflowCacheConfig"):
                workflow_cache_config = WorkflowCacheConfig(
                    _type=details.get("workflowCacheConfig", {}).get("type", ""),
                    value=details.get("workflowCacheConfig", {}).get("value", False),
                    global_value=details.get("workflowCacheConfig", {}).get("global_value", False)
                )
            else:
                workflow_cache_config = None

            ci_pipeline = CiPipeline(
                is_manual=details.get("isManual", False),
                app_id=details.get("appId", 0),
                pipeline_type=details.get("pipelineType", ""),
                name=details.get("name", ""),
                workflow_cache_config=workflow_cache_config,
                external_ci_config=ExternalCiConfig(),
                ci_material=CiPipelineHandlers.get_ci_material(details.get("ciMaterial", [])),
                _id=details.get("id", 0),
                active=details.get("active", False),
                linked_count=details.get("linkedCount", 0),
                scan_enabled=details.get("scanEnabled", False),
                app_workflow_id=details.get("appWorkflowId", 0),
                pre_build_stage=CiPipelineHandlers.get_pre_post_build_config(details.get("preBuildStage", {})),
                post_build_stage=CiPipelineHandlers.get_pre_post_build_config(details.get("postBuildStage", {})),
                is_docker_config_overridden=details.get("isDockerConfigOverridden", False),
                last_triggered_env_id=details.get("lastTriggeredEnvId", 0),
                default_tag=[],
                enable_custom_tag=False,
                docker_args=DockerArgs(),
                custom_tag=CustomTag()
            )
            return {"success": True, "ci_pipeline": ci_pipeline}

        except Exception as e:
            return {"success": False, "error": str(e)}

    @staticmethod
    def update_current_ci_pipeline(base_url: str, headers: dict, current_ci_pipeline: CiPipeline, ci_config: dict, plugin_metadata: dict, applied_plugin_metadata: list):

        try:
            if current_ci_pipeline.pipeline_type == "LINKED":
                return {
                    "success": True,
                    "message": "Linked CI pipeline cannot be updated"
                }
            current_ci_pipeline.is_manual       = ci_config.get("is_manual", current_ci_pipeline.is_manual)
            current_ci_pipeline.pipeline_type   = ci_config.get("type", current_ci_pipeline.pipeline_type)
            current_ci_pipeline.ci_material     = CiPipelineHandlers.update_ci_material(current_ci_pipeline.ci_material, ci_config.get("branches", []))
            current_ci_pipeline.pre_build_stage = CiPipelineHandlers.update_pre_post_build_config(current_ci_pipeline.pre_build_stage, ci_config.get("pre_build_configs", {}).get("tasks", []), plugin_metadata, step_type="PRE_CI", applied_plugin_metadata=applied_plugin_metadata)

            patch_result = CiPipelineHandlers.patch_ci_pipeline(base_url, headers, current_ci_pipeline)
            if patch_result["success"]:

                return {"success": True, "message": "CI Pipeline has been updated successfully"}

            return {"success": False, "message": "Failed to update CI Pipeline"}

        except Exception as e:
            print("update_current_ci_pipeline", f"Exception occurred: {str(e)}")
            return {"success": False, "message": str(e)}


    @staticmethod
    def patch_ci_pipeline(base_url, headers, ci: CiPipeline):

        import requests

        payload = {
            "appId": ci.app_id,
            "appWorkflowId": ci.app_workflow_id,
            "action": 1,
            "ciPipeline": {
                "isManual": ci.is_manual,
                "workflowCacheConfig": ci.workflow_cache_config.to_dict(),
                "dockerArgs": ci.docker_args.to_dict(),
                "isExternal": ci.is_external,
                "parentCiPipeline": ci.parent_ci_pipeline,
                "parentAppId": ci.parent_app_id,
                "appId": ci.app_id,
                "externalCiConfig": {
                    "id": 0,
                    "webhookUrl": "",
                    "payload": "",
                    "accessKey": "",
                    "payloadOption": None,
                    "schema": None,
                    "responses": None,
                    "projectId": 0,
                    "projectName": "",
                    "environmentId": "",
                    "environmentName": "",
                    "environmentIdentifier": "",
                    "appId": 0,
                    "appName": "",
                    "role": ""
                },
                "ciMaterial": [material.to_dict() for material in ci.ci_material],
                "name": ci.name,
                "id": ci._id,
                "active": True,
                "linkedCount": ci.linked_count,
                "scanEnabled": ci.scan_enabled,
                "pipelineType": ci.pipeline_type,
                "preBuildStage": ci.pre_build_stage.to_dict(),
                "postBuildStage": {},
                "appWorkflowId": ci.app_workflow_id,
                "isDockerConfigOverridden": False,
                "dockerConfigOverride": ci.docker_config_override,
                "lastTriggeredEnvId": 0,
                "defaultTag": ci.default_tag,
                "enableCustomTag": ci.enable_custom_tag,
                "customTag": ci.custom_tag.to_dict(),
            }
        }

        response = requests.post(f"{base_url}/orchestrator/app/ci-pipeline/patch", headers=headers, json=payload)

        if response.status_code != 200:

            return {'success': False, 'error': f"Failed to patch CI pipeline: {response.text}"}
        return {
            "success": True,
            "message": "The Pipeline has been updated"
        }


    @staticmethod
    def get_pre_post_build_plugin_ids(ci_pipeline: CiPipeline) -> list:
        plugin_ids = []
        if ci_pipeline.pre_build_stage:
            for step in ci_pipeline.pre_build_stage.steps:

                plugin_ids.append(step.plugin_ref_step_detail.plugin_id)

        return plugin_ids