import json
from pathlib import Path

import ibm_watsonx_data_integration.services.datastage.models.flow_json_model as models
from ibm_watsonx_data_integration.services.datastage.codegen.code_generator import (
    # BuildStageCodeGenerator,
    ConnectionCodeGenerator,
    # CustomStageCodeGenerator,
    # DataDefinitionCodeGenerator,
    FlowCodeGenerator,
    # JobSettingsCodeGenerator,
    MasterCodeGenerator,
    # ParamSetCodeGenerator,
    # SubflowCodeGenerator,
    # WrappedStageCodeGenerator,
)
from ibm_watsonx_data_integration.services.datastage.codegen.dag_generator import (
    ConnectionGenerator,
    DAGGenerator,
)
from ibm_watsonx_data_integration.services.datastage.codegen.exporters.util import (
    _check_create_dir,
    _create_init_file,
    _format_code,
    _generate_flow_name,
)
from ibm_watsonx_data_integration.services.datastage.codegen.importers import ZipImporter


def _get_json_type(path: str):
    if path.startswith("data_intg_subflow"):
        return "subflow"
    elif path.startswith("data_intg_flow"):
        return "flow"
    elif path.startswith("parameter_set"):
        return "parameter_set"
    elif path.startswith("connection"):
        return "connection"
    elif path.startswith("job"):
        return "job"
    elif path.startswith("px_executables"):
        return "executables"
    elif path.startswith("ENCRYPTED"):
        return "encrypted"
    else:
        return ""


def _get_use_paramsets(paramsets: list):
    use_ps = ""
    for paramset in paramsets:
        use_ps += f"flow.use_paramset({paramset})\n"
    return use_ps


class MultiFileExporter:
    def __init__(
        self,
        zip_importer: ZipImporter,
        output_path: str | None,
        *,
        offline: bool = False,
        include_run: bool = True,
        print_logs: bool = True,
        include_create: bool = False,
        use_flow_name: bool = True,
    ):
        self.zip_importer = zip_importer
        if output_path is not None and output_path.strip() != "":
            self.output_path = str(Path(output_path).absolute())
            self.write_to_output = True
        else:
            self.output_path = ""
            self.write_to_output = False
        self.offline = offline
        self.include_run = include_run
        self.print_logs = print_logs
        self.include_create = include_create
        self.use_flow_name = use_flow_name

    def run(self):
        generated_code = {}

        master_gen = MasterCodeGenerator()
        imports: list[str] = []
        paramsets: list[str] = []
        job_vars: list[str] = []

        if self.write_to_output:
            _check_create_dir(self.output_path)
        else:
            self.output_path = ""  # Use relative path in returned code

        # paramset_path = Path(self.output_path) / "parameter_set"
        connection_path = Path(self.output_path) / "connection"
        # data_definition_path = Path(self.output_path) / "data_definition"
        job_path = Path(self.output_path) / "job"
        # build_stage_path = Path(self.output_path) / "data_intg_build_stage"
        # wrapped_stage_path = Path(self.output_path) / "data_intg_wrapped_stage"
        # custom_stage_path = Path(self.output_path) / "data_intg_custom_stage"
        # custom_stage_attachments_path = Path(self.output_path) / "custom_stage_library"
        # subflow_path = Path(self.output_path) / "data_intg_subflow"
        flow_path = Path(self.output_path) / "data_intg_flow"

        if self.write_to_output:  # Create and initialize output paths
            # if self.zip_importer.paramsets:
            #     _check_create_dir(str(paramset_path))
            #     _create_init_file(str(paramset_path))
            if self.zip_importer.connections:
                _check_create_dir(str(connection_path))
                _create_init_file(str(connection_path))
            # if self.zip_importer.data_definitions:
            #     _check_create_dir(str(data_definition_path))
            #     _create_init_file(str(data_definition_path))
            if self.zip_importer.jobs:
                _check_create_dir(str(job_path))
                _create_init_file(str(job_path))
            # if self.zip_importer.subflows:
            #     _check_create_dir(str(subflow_path))
            #     _create_init_file(str(subflow_path))
            # if self.zip_importer.build_stages:
            #     _check_create_dir(str(build_stage_path))
            #     _create_init_file(str(build_stage_path))
            # if self.zip_importer.wrapped_stages:
            #     _check_create_dir(str(wrapped_stage_path))
            #     _create_init_file(str(wrapped_stage_path))
            # if self.zip_importer.custom_stage_attachments:
            #     _check_create_dir(str(custom_stage_attachments_path))
            # if self.zip_importer.custom_stages:
            #     _check_create_dir(str(custom_stage_path))
            #     _create_init_file(str(custom_stage_path))
            if self.zip_importer.flows:
                _check_create_dir(str(flow_path))

        # for f_info, f_content in self.zip_importer.paramsets:
        #     mod_name = f_info.filename.split("/")[-1].replace(".json", "")
        #     imports.append(f"from parameter_set.{mod_name} import *")
        #     json_data = json.loads(f_content)["parameter_set"]
        #     param_set = ParameterSet.from_dict(json_data)
        #     ps_code_gen = ParamSetCodeGenerator(param_set, master_gen)
        #     ps_code = ps_code_gen.generate_code()
        #     formatted = _format_code(ps_code)
        #     var_name = master_gen.get_object_var(param_set)
        #     paramsets.append(var_name)
        #     # Save parameter set code
        #     file_name = paramset_path / (f_info.filename.split("/")[-1].replace("json", "py"))
        #     file_contents = ps_code_gen.get_imports() + f"\n\n{formatted}"
        #     generated_code[str(file_name)] = file_contents
        #     if self.write_to_output:
        #         with open(file_name, "w") as f:
        #             f.write(file_contents)

        for f_info, f_content in self.zip_importer.connections:
            json_data = json.loads(f_content)
            conn_gen = ConnectionGenerator(json_data)
            conn_model = conn_gen.create_connection_model()
            conn_code_gen = ConnectionCodeGenerator(conn_model, master_gen)
            conn_code = conn_code_gen.generate_code()
            formatted = _format_code(conn_code)
            mod_name = master_gen.get_object_var(conn_model)
            imports.append(f"from connection.{mod_name} import *")
            # Save connections code
            file_name = connection_path / (mod_name + ".py")
            file_contents = conn_code_gen.get_imports() + f"\n\n{formatted}"
            generated_code[str(file_name)] = file_contents
            if self.write_to_output:
                with open(file_name, "w") as f:
                    f.write(file_contents)

        # for f_info, f_content in self.zip_importer.data_definitions:
        #     json_data = json.loads(f_content)
        #     data_def = DataDefinition.from_dict(json_data)
        #     data_def_code_gen = DataDefinitionCodeGenerator(data_def, master_gen)
        #     data_def_code = data_def_code_gen.generate_code()
        #     formatted = _format_code(data_def_code)
        #     # Save data definition code
        #     file_name = data_definition_path / (f_info.filename.split("/")[-1].replace("json", "py"))
        #     file_contents = data_def_code_gen.get_imports() + f"\n\n{formatted}"
        #     generated_code[str(file_name)] = file_contents
        #     if self.write_to_output:
        #         with open(file_name, "w") as f:
        #             f.write(file_contents)

        # for f_info, f_content in self.zip_importer.jobs:
        #     mod_name = f_info.filename.split("/")[-1].replace(".json", "").replace(" ", "_").replace(".", "_")
        #     imports.append(f"from job.{mod_name} import *")
        #     job_json = json.loads(f_content)["entity"]["job"]
        #     job_gen = JobGenerator(job_json)
        #     job_settings = job_gen.create_job_model()
        #     job_code_gen = JobSettingsCodeGenerator(job_settings, master_gen)
        #     job_code = job_code_gen.generate_code()
        #     formatted = _format_code(job_code)
        #     job_var = master_gen.get_object_var(job_settings)
        #     job_vars.append(job_var)
        #     # Save job code
        #     file_name = job_path / (mod_name + ".py")
        #     file_contents = job_code_gen.get_imports() + f"\n\n{formatted}"
        #     generated_code[str(file_name)] = file_contents
        #     if self.write_to_output:
        #         with open(file_name, "w") as f:
        #             f.write(file_contents)

        # for f_info, f_content in self.zip_importer.subflows:
        #     subflow_json = json.loads(f_content)
        #     subflow_name = subflow_json["name"] if "name" in subflow_json else f_info.filename.split("/")[-1].replace(".json", "")
        #     subflow_model = models.Flow(**subflow_json)
        #     subflow_dag_gen = DAGGenerator(subflow_model)
        #     dag = subflow_dag_gen.generate()._dag
        #     subflow = Subflow(dag=dag, name=subflow_name, is_local=False)
        #     master_gen.subflows[subflow_name] = subflow
        #     subflow_code_gen = SubflowCodeGenerator(
        #         subflow=subflow,
        #         master_gen=master_gen,
        #         offline=self.offline,
        #         zip_structure=True,
        #     )
        #     subflow_code = subflow_code_gen.generate_all()
        #     formatted = _format_code(subflow_code)
        #     mod_name = master_gen.get_object_var(subflow)
        #     imports.append(f"from data_intg_subflow.{mod_name} import *")
        #     # Save subflow code
        #     file_name = subflow_path / (mod_name + ".py")
        #     file_contents = subflow_code_gen.get_imports() + f"\n\n{formatted}"
        #     generated_code[str(file_name)] = file_contents
        #     if self.write_to_output:
        #         with open(file_name, "w") as f:
        #             f.write(file_contents)

        # for f_info, f_content in self.zip_importer.build_stages:
        #     build_stage_json = json.loads(f_content)
        #     build_stage_name = (
        #         build_stage_json["name"] if "name" in build_stage_json else f_info.filename.split("/")[-1].replace(".json", "")
        #     )
        #     build_stage_model = BuildStage.from_dict(build_stage_json)
        #     build_stage_code_gen = BuildStageCodeGenerator(asset=build_stage_model, master_gen=master_gen)
        #     build_stage_code = build_stage_code_gen.generate_code()
        #     formatted = _format_code(build_stage_code)
        #     mod_name = master_gen.get_object_var(build_stage_model)
        #     build_stages[build_stage_name] = mod_name
        #     imports.append(f"from data_intg_build_stage.{mod_name} import *")
        #     # Save build stage code
        #     file_name = build_stage_path / (mod_name + ".py")
        #     file_contents = build_stage_code_gen.get_imports() + f"\n\n{formatted}"
        #     generated_code[str(file_name)] = file_contents
        #     if self.write_to_output:
        #         with open(file_name, "w") as f:
        #             f.write(file_contents)

        # for f_info, f_content in self.zip_importer.wrapped_stages:
        #     wrapped_stage_json = json.loads(f_content)
        #     wrapped_stage_name = (
        #         wrapped_stage_json["name"] if "name" in wrapped_stage_json else f_info.filename.split("/")[-1].replace(".json", "")
        #     )
        #     wrapped_stage_model = WrappedStage.from_dict(wrapped_stage_json)
        #     wrapped_stage_code_gen = WrappedStageCodeGenerator(asset=wrapped_stage_model, master_gen=master_gen)
        #     wrapped_stage_code = wrapped_stage_code_gen.generate_code()
        #     formatted = _format_code(wrapped_stage_code)
        #     mod_name = master_gen.get_object_var(wrapped_stage_model)
        #     wrapped_stages[wrapped_stage_name] = mod_name
        #     imports.append(f"from data_intg_wrapped_stage.{mod_name} import *")
        #     # Save wrapped stage code
        #     file_name = wrapped_stage_path / (mod_name + ".py")
        #     file_contents = wrapped_stage_code_gen.get_imports() + f"\n\n{formatted}"
        #     generated_code[str(file_name)] = file_contents
        #     if self.write_to_output:
        #         with open(file_name, "w") as f:
        #             f.write(file_contents)

        # for f_info, f_content in self.zip_importer.custom_stage_attachments:
        #     attachment_path = custom_stage_attachments_path / (Path(f_info.filename).stem + ".so")
        #     # Save custom stage attachments
        #     file_contents = str(base64.b64encode(f_content))[2:-1]
        #     generated_code[str(attachment_path)] = file_contents
        #     if self.write_to_output:
        #         with open(attachment_path, "w") as f:
        #             f.write(file_contents)

        #     custom_stage_paths[Path(f_info.filename).stem] = attachment_path

        # for f_info, f_content in self.zip_importer.custom_stages:
        #     # NEED TO ADD SOMETHING ABOUT FILE PATH
        #     custom_stage_json = json.loads(f_content)
        #     custom_stage_name = (
        #         custom_stage_json["name"] if "name" in custom_stage_json else f_info.filename.split("/")[-1].replace(".json", "")
        #     )
        #     for attachment in custom_stage_paths:
        #         if f"lib_{custom_stage_name}" == attachment:
        #             if "entity" in custom_stage_json:
        #                 custom_stage_json["entity"]["library_path"] = str(custom_stage_paths[attachment])
        #             else:
        #                 custom_stage_json["library_path"] = str(custom_stage_paths[attachment])
        #     custom_stage_model = CustomStage.from_dict(custom_stage_json)
        #     custom_stage_code_gen = CustomStageCodeGenerator(asset=custom_stage_model, master_gen=master_gen)
        #     custom_stage_code = custom_stage_code_gen.generate_code()
        #     formatted = _format_code(custom_stage_code)
        #     mod_name = master_gen.get_object_var(custom_stage_model)
        #     custom_stages[custom_stage_name] = mod_name
        #     imports.append(f"from data_intg_custom_stage.{mod_name} import *")
        #     # Save custom stage code
        #     file_name = custom_stage_path / (mod_name + ".py")
        #     file_contents = custom_stage_code_gen.get_imports() + f"\n\n{formatted}"
        #     generated_code[str(file_name)] = file_contents
        #     if self.write_to_output:
        #         with open(file_name, "w") as f:
        #             f.write(file_contents)

        for f_info, f_content in self.zip_importer.flows:
            flow_json = json.loads(f_content)
            try:
                flow_model = models.Flow(**flow_json)
            except Exception:
                try:
                    flow_json = flow_json["attachments"]
                    flow_model = models.Flow(**flow_json)
                except Exception:
                    try:
                        flow_json = flow_json[0]
                        flow_model = models.Flow(**flow_json)
                    except Exception as e:
                        raise ValueError(f"Bad flow json: {e}")

            dag_gen = DAGGenerator(flow_model)
            fc = dag_gen.generate()

            # for node in fc._dag.nodes():
            #     if isinstance(node, BuildStageStage):
            #         bs_name = node.configuration.op_name
            #         for build_stage in build_stages:
            #             if build_stage == bs_name:
            #                 node.build_stage = build_stages[build_stage]
            #     if isinstance(node, WrappedStageStage):
            #         ws_name = node.configuration.op_name
            #         for wrapped_stage in wrapped_stages:
            #             if wrapped_stage == ws_name:
            #                 node.wrapped_stage = wrapped_stages[wrapped_stage]
            #     if isinstance(node, CustomStageStage):
            #         cs_name = node.configuration.op_name
            #         for custom_stage in custom_stages:
            #             if custom_stage == cs_name:
            #                 node.custom_stage = custom_stages[custom_stage]

            code_gen = FlowCodeGenerator(fc, master_gen, self.offline, skip_subflows=True)
            code = code_gen.generate_all_zip()

            file_name = f_info.filename.split("/")[-1].replace("json", "py")
            if self.use_flow_name:
                flow_name = file_name.strip(".py")
            else:
                flow_name = _generate_flow_name()

            # Assemble flow code
            full_flow_path = flow_path / file_name
            file_contents = "\n".join(imports) + "\n" + code + f"\n{_get_use_paramsets(paramsets)}"
            if self.include_run:
                if len(job_vars) == 1:
                    file_contents += (
                        f'\n\nsdk.run_flow(flow=flow, flow_name="{flow_name}", job_settings={job_vars[0]}, print_logs={self.print_logs})'
                    )
                else:
                    file_contents += f'\n\njob_logs = sdk.run_flow(flow=flow, flow_name="{flow_name}", print_logs={self.print_logs})'
            if self.include_create:
                file_contents += f'\n\nsdk.create_flow(flow=flow, flow_name="{flow_name}")'

            # Save flow code
            generated_code[str(file_name)] = file_contents
            if self.write_to_output:
                with open(full_flow_path, "w") as f:
                    f.write(file_contents)

        return generated_code
