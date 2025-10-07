from ibm_watsonx_data_integration.services.datastage.api.datastage_flow_api import PipelineJson
from typing import Literal


class FlowRunner:
    # def __init__(self, config: Config):
    #     self.project_id = config._get_project_id()
    #     self.catalog_id = None
    #     self.flow_id = None
    #     self.flow_service = config._get_environment()._get_flow_service()
    #     self.job_service = config._get_environment()._get_job_service()
    #     self.env = (
    #         "cpd"
    #         if isinstance(config._get_environment(), CloudPakForDataEnvironment)
    #         else "cloud"
    #     )

    def get_flows(
        self,
        project_id: str | None = None,
        # add in other types of ids?
        entity_name: str | None = None,
    ):
        project_id = project_id or self.project_id
        if not project_id:
            raise ValueError("Project id must be provided")
        response = self.flow_service.list_datastage_flows(project_id=project_id, entity_name=entity_name)
        return response

    def get_flow(self, flow_id: str, project_id: str | None = None):
        project_id = project_id or self.project_id
        if not project_id:
            raise ValueError("Project id must be provided")

        if not flow_id:
            raise ValueError("Flow id must be provided")

        response = self.flow_service.get_datastage_flows(project_id=project_id, data_intg_flow_id=flow_id)
        return response

    def create_flow(
        self,
        flow_name: str,
        flow_json: dict,
        project_id: str | None = None,
        catalog_id: str | None = None,
    ):
        if not flow_name:
            raise ValueError("Flow name must be provided")
        project_id = project_id or self.project_id
        catalog_id = catalog_id or self.catalog_id
        if project_id:
            response = self.flow_service.create_datastage_flows(
                data_intg_flow_name=flow_name,
                pipeline_flows=flow_json,
                project_id=project_id,
            )
            return response
        elif catalog_id:
            response = self.flow_service.create_datastage_flows(
                data_intg_flow_name=flow_name,
                pipeline_flows=flow_json,
                catalog_id=catalog_id,
            )
            return response
        else:
            raise ValueError("Project id or catalog id must be provided")

    def update_flow(
        self,
        flow_name: str,
        flow_json: dict,
        flow_id: str | None = None,
        project_id: str | None = None,
        catalog_id: str | None = None,
    ):
        if not flow_name:
            raise ValueError("Flow name must be provided")
        flow_id = flow_id
        project_id = project_id or self.project_id
        catalog_id = catalog_id or self.catalog_id
        if not flow_id:
            raise ValueError("Create a new flow or provide a flow id")
        if project_id:
            response = self.flow_service.update_datastage_flows(
                data_intg_flow_id=flow_id,
                data_intg_flow_name=flow_name,
                pipeline_flows=flow_json,
                project_id=project_id,
            )
            return response
        elif catalog_id:
            response = self.flow_service.update_datastage_flows(
                data_intg_flow_id=flow_id,
                data_intg_flow_name=flow_name,
                pipeline_flows=flow_json,
                catalog_id=catalog_id,
            )
            return response
        else:
            raise ValueError("Project id or catalog id must be provided")

    def compile_flow(
        self,
        flow_id: str,
        project_id: str | None = None,
        catalog_id: str | None = None,
    ):
        project_id = project_id or self.project_id
        catalog_id = catalog_id or self.catalog_id
        if not flow_id:
            raise ValueError("Create a new flow or provide a flow id")
        if project_id:
            response = self.flow_service.compile_datastage_flows(data_intg_flow_id=flow_id, project_id=project_id)
            return response
        elif catalog_id:
            response = self.flow_service.compile_datastage_flows(data_intg_flow_id=flow_id, catalog_id=catalog_id)
            return response
        else:
            raise ValueError("Project id or catalog id must be provided")

    def get_compile_status(
        self,
        flow_id: str | None = None,
        project_id: str | None = None,
        catalog_id: str | None = None,
    ):
        flow_id = flow_id or self.flow_id
        project_id = project_id or self.project_id
        catalog_id = catalog_id or self.catalog_id
        if not flow_id:
            raise ValueError("Create a new flow or provide a flow id")
        if project_id:
            response = self.flow_service.get_flow_compile_status(data_intg_flow_id=flow_id, project_id=project_id)
            return response
        elif catalog_id:
            response = self.flow_service.get_flow_compile_status(data_intg_flow_id=flow_id, catalog_id=catalog_id)
            return response
        else:
            raise ValueError("Project id or catalog id must be provided")

    def get_compile_info(
        self,
        flow_id: str,
        project_id: str | None = None,
        catalog_id: str | None = None,
    ):
        project_id = project_id or self.project_id
        catalog_id = catalog_id or self.catalog_id
        if not flow_id:
            raise ValueError("Create a new flow or provide a flow id")
        if project_id:
            response = self.flow_service.datastage_flows_compile_info(data_intg_flow_id=flow_id, project_id=project_id)
            return response
        elif catalog_id:
            response = self.flow_service.datastage_flows_compile_info(data_intg_flow_id=flow_id, catalog_id=catalog_id)
            return response
        else:
            raise ValueError("Project id or catalog id must be provided")

    # def get_jobs(self, project_id: str | None = None, asset_ref: str | None = None):
    #     project_id = project_id or self.project_id
    #     # include space_id?

    #     if not project_id:
    #         raise ValueError("Project id must be provided")

    #     response = self.job_service.jobs_list(
    #         project_id=project_id, asset_ref=asset_ref
    #     )
    #     return response

    # def get_job(self, project_id: str | None = None, job_id: str | None = None):
    #     project_id = project_id or self.project_id
    #     if not project_id:
    #         raise ValueError("Project id must be provided")

    #     if not job_id:
    #         raise ValueError("Please create a job or provide a job id")

    #     response = self.job_service.jobs_get(job_id=job_id, project_id=project_id)
    #     return response

    # def create_job(
    #     self,
    #     job_name: str,
    #     flow_id: str,
    #     project_id: str | None = None,
    #     paramsets: list = None,
    #     runtime: Runtime = None,
    #     schedule: Schedule = None,
    #     job_body: JobPostBodyJob = None,
    # ):
    #     project_id = project_id or self.project_id
    #     if not project_id:
    #         raise ValueError("Project id must be provided")

    #     if not flow_id:
    #         raise ValueError("Flow id must be provided")

    #     retention_policy = JobPostBodyJobRetentionPolicy()
    #     configuration = JobPostBodyConfiguration()
    #     schedule_info = JobPostBodyJobScheduleInfo()
    #     schedule_cron = None
    #     if runtime:
    #         if runtime.runtime_settings:
    #             retention_policy = runtime.runtime_settings._get_retention_policy()
    #             configuration = runtime.runtime_settings._get_configuration(
    #                 project_id, self.env
    #             )
    #     if schedule:
    #         schedule_info = JobPostBodyJobScheduleInfo(
    #             repeat=schedule.repeat, start_on=schedule.start, end_on=schedule.end
    #         )
    #         schedule_cron = schedule.schedule

    #     if not job_body:
    #         job = JobPostBodyJob(
    #             name=job_name,
    #             configuration=configuration,
    #             asset_ref=flow_id,
    #             parameter_sets=paramsets,
    #             retention_policy=retention_policy,
    #             schedule_info=schedule_info,
    #             schedule=schedule_cron,
    #         )
    #     else:
    #         job = job_body

    #     response = self.job_service.jobs_create(job=job, project_id=project_id)
    #     return response

    # def update_job(
    #     self,
    #     job_json: dict,
    #     job_id: str,
    #     project_id: str | None = None,
    #     runtime: Runtime = None,
    #     paramsets: list = None,
    #     schedule: Schedule = None,
    # ):
    #     project_id = project_id or self.project_id
    #     if not project_id:
    #         raise ValueError("Project id must be provided")

    #     if not job_id:
    #         raise ValueError("Please create a job or provide a job id")

    #     configuration = job_json["entity"]["job"]["configuration"]
    #     job = job_json["entity"]["job"]

    #     patches = []

    #     if paramsets:
    #         job["parameter_sets"] = paramsets

    #     if runtime:
    #         if runtime.runtime_settings:
    #             if runtime.runtime_settings.env:
    #                 configuration["env_id"] = (
    #                     runtime.runtime_settings.env.value + "-" + project_id
    #                 )
    #             if runtime.runtime_settings.warn_limit:
    #                 configuration["flow_limits"] = {
    #                     "warn_limit": runtime.runtime_settings.warn_limit
    #                 }
    #             job["configuration"] = configuration
    #             if runtime.runtime_settings.days:
    #                 job["retention_policy"] = {"days": runtime.runtime_settings.days}
    #             if runtime.runtime_settings.amount:
    #                 job["retention_policy"] = {
    #                     "amount": runtime.runtime_settings.amount
    #                 }
    #     if schedule:
    #         if schedule.schedule:
    #             job["schedule"] = schedule.schedule
    #         schedule_info = {}
    #         if schedule.start:
    #             schedule_info["startOn"] = schedule.start
    #         if schedule.end:
    #             schedule_info["endOn"] = schedule.end
    #         if schedule.repeat:
    #             schedule_info["repeat"] = schedule.repeat
    #         job["schedule_info"] = schedule_info

    #     patches.append(
    #         JSONJobPatchModelItem(op="replace", path="/entity/job", value=job)
    #     )

    #     response = self.job_service.jobs_update(
    #         job_id=job_id, body=patches, project_id=project_id
    #     )
    #     return response

    # def run_job(self, job_id: str, project_id: str | None = None):
    #     if not job_id:
    #         raise ValueError("Please create a job or provide a job id")
    #     project_id = project_id or self.project_id
    #     if not project_id:
    #         raise ValueError("Project id must be provided")

    #     response = self.job_service.job_runs_create(
    #         project_id=project_id,
    #         job_id=job_id,
    #         job_run=JobRunPostBodyJobRunConfiguration(),
    #     )
    #     return response

    # def get_job_run(
    #     self,
    #     job_id: str,
    #     run_id: str,
    #     project_id: str | None = None,
    # ):
    #     if not run_id:
    #         raise ValueError("Please create a job run or provide a run id")
    #     if not job_id:
    #         raise ValueError("Please create a job or provide a job id")
    #     project_id = project_id or self.project_id
    #     if not project_id:
    #         raise ValueError("Project id must be provided")

    #     response = self.job_service.job_runs_get(
    #         job_id=job_id, run_id=run_id, project_id=project_id
    #     )
    #     return response

    # def get_job_log(
    #     self,
    #     job_id: str,
    #     run_id: str,
    #     project_id: str | None = None,
    # ):
    #     if not run_id:
    #         raise ValueError("Please create a job run or provide a run id")
    #     if not job_id:
    #         raise ValueError("Please create a job or provide a job id")
    #     project_id = project_id or self.project_id
    #     if not project_id:
    #         raise ValueError("Project id must be provided")

    #     response = self.job_service.job_runs_logs(
    #         job_id=job_id, run_id=run_id, project_id=project_id
    #     )
    #     return response

    def create_or_replace_flow(
        self,
        flow_name: str,
        flow_json: dict,
        duplicate_assets: Literal["Skip", "Rename", "Overwrite"],
    ):
        flow_exist_response = self.get_flows(entity_name=flow_name)
        flow_exists = False
        flow_id = None
        for flow in flow_exist_response.result["data_flows"]:
            if flow["metadata"]["name"] == flow_name:
                flow_exists = True
                flow_id = flow["metadata"]["asset_id"]

        pipeline_json = PipelineJson.from_dict(flow_json)
        if flow_exists:
            if duplicate_assets == "Overwrite":
                response = self.update_flow(flow_name=flow_name, flow_json=pipeline_json, flow_id=flow_id)
            if duplicate_assets == "Rename":
                new_name_exists = True
                new_name = None
                i = 0
                while new_name_exists:
                    i += 1
                    new_name = flow_name + "_" + str(i)
                    new_name_exist_response = self.get_flows(entity_name=new_name)
                    found_new_name = False
                    for flow in new_name_exist_response.result["data_flows"]:
                        if flow["metadata"]["name"] == new_name:
                            found_new_name = True
                    new_name_exists = found_new_name
                response = self.create_flow(flow_name=new_name, flow_json=pipeline_json)
            if duplicate_assets == "Skip":
                response = self.get_flow(flow_id=flow_id)
        else:
            response = self.create_flow(flow_name=flow_name, flow_json=pipeline_json)

        return response

    def delete_flow(self, flow_name: str):
        flows_res = self.flow_service.list_datastage_flows(project_id=self.project_id)

        def get_flow_id():
            for flow in flows_res.result["data_flows"]:
                if flow["metadata"]["name"] == flow_name:
                    return flow["metadata"]["asset_id"]

        flow_id = get_flow_id()
        if flow_id is None:
            raise ValueError(f"Error in deleting flow: Flow with name {flow_name} not found")

        self.flow_service.delete_datastage_flows(
            id=[flow_id],
            project_id=self.project_id,
        )
