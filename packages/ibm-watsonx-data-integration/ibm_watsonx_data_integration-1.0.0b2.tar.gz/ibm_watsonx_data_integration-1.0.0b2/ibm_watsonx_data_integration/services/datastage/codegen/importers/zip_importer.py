from io import BytesIO
from pathlib import Path
from zipfile import ZipFile, ZipInfo


def _get_json_type(path: str):
    if path.startswith("data_intg_subflow"):
        return "subflow"
    elif path.startswith("data_intg_flow"):
        return "flow"
    elif path.startswith("parameter_set"):
        return "parameter_set"
    elif path.startswith("data_definition"):
        return "data_definition"
    elif path.startswith("data_intg_message_handler"):
        return "message_handler"
    elif path.startswith("data_intg_java_library"):
        return "java_library"
    elif path.startswith("connection"):
        return "connection"
    elif path.startswith("data_intg_parallel_function"):
        return "function_library"
    elif path.startswith("data_intg_build_stage"):
        return "build_stage"
    elif path.startswith("data_intg_wrapped_stage"):
        return "wrapped_stage"
    elif path.startswith("data_intg_custom_stage"):
        return "custom_stage"
    elif path.startswith("custom_stage_library"):
        return "custom_stage_attachment"
    elif path.startswith("ds_match_specification"):
        return "match_specification"
    elif path.startswith("job"):
        return "job"
    elif path.startswith("px_executables"):
        return "executables"
    elif path.startswith("ENCRYPTED"):
        return "encrypted"
    elif path.startswith("data_intg_test_case"):
        return "test_case"
    else:
        return ""


class ZipImporter:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.subflows: list[tuple[ZipInfo, bytes]] = []
        self.flows: list[tuple[ZipInfo, bytes]] = []
        self.paramsets: list[tuple[ZipInfo, bytes]] = []
        self.data_definitions: list[tuple[ZipInfo, bytes]] = []
        self.message_handlers: list[tuple[ZipInfo, bytes]] = []
        self.java_libraries: list[tuple[ZipInfo, bytes]] = []
        self.connections: list[tuple[ZipInfo, bytes]] = []
        self.function_libraries: list[tuple[ZipInfo, bytes]] = []
        self.build_stages: list[tuple[ZipInfo, bytes]] = []
        self.wrapped_stages: list[tuple[ZipInfo, bytes]] = []
        self.custom_stages: list[tuple[ZipInfo, bytes]] = []
        self.custom_stage_attachments: list[tuple[ZipInfo, bytes]] = []
        self.match_specifications: list[tuple[ZipInfo, bytes]] = []
        self.jobs: list[tuple[ZipInfo, bytes]] = []
        self.executables: list[tuple[ZipInfo, bytes]] = []
        self.encrypted: list[tuple[ZipInfo, bytes]] = []
        self.test_cases: list[tuple[ZipInfo, bytes]] = []

    def find_paramset(self, name: str) -> bytes:
        for f_info, f_content in self.paramsets:
            if Path(f_info.filename).stem == name:
                return f_content

        raise KeyError(f"Parameter set '{name}' not found in the zip file.")

    def find_subflow(self, name: str) -> bytes:
        for f_info, f_content in self.subflows:
            if Path(f_info.filename).stem == name:
                return f_content

        raise KeyError(f"Subflow '{name}' not found in the zip file.")

    def find_build_stage(self, name: str) -> bytes:
        for f_info, f_content in self.build_stages:
            if Path(f_info.filename).stem == name:
                return f_content

        raise KeyError(f"Build stage '{name}' not found in the zip file.")

    def find_wrapped_stage(self, name: str) -> bytes:
        for f_info, f_content in self.wrapped_stages:
            if Path(f_info.filename).stem == name:
                return f_content

        raise KeyError(f"Wrapped stage '{name}' not found in the zip file.")

    def find_custom_stage(self, name: str) -> bytes:
        for f_info, f_content in self.custom_stages:
            if Path(f_info.filename).stem == name:
                return f_content

        raise KeyError(f"Custom stage '{name}' not found in the zip file.")

    def find_custom_stage_attachment(self, name: str) -> tuple[ZipInfo, bytes]:
        for f_info, f_content in self.custom_stage_attachments:
            if Path(f_info.filename).stem == name:
                return (f_info, f_content)

        raise KeyError(f"Custom stage attachment'{name}' not found in the zip file.")

    def run(self):
        with ZipFile(self.file_path) as zip_file:
            for f_info in zip_file.infolist():
                f_type = _get_json_type(f_info.filename)
                f_content = zip_file.read(f_info.filename)

                match f_type:
                    case "subflow":
                        self.subflows.append((f_info, f_content))
                    case "flow":
                        self.flows.append((f_info, f_content))
                    case "parameter_set":
                        self.paramsets.append((f_info, f_content))
                    case "data_definition":
                        self.data_definitions.append((f_info, f_content))
                    case "message_handler":
                        self.message_handlers.append((f_info, f_content))
                    case "java_library":
                        self.java_libraries.append((f_info, f_content))
                    case "connection":
                        self.connections.append((f_info, f_content))
                    case "function_library":
                        self.function_libraries.append((f_info, f_content))
                    case "build_stage":
                        self.build_stages.append((f_info, f_content))
                    case "wrapped_stage":
                        self.wrapped_stages.append((f_info, f_content))
                    case "custom_stage":
                        self.custom_stages.append((f_info, f_content))
                    case "custom_stage_attachment":
                        self.custom_stage_attachments.append((f_info, f_content))
                    case "match_specification":
                        self.match_specifications.append((f_info, f_content))
                    case "job":
                        self.jobs.append((f_info, f_content))
                    case "executables":
                        self.executables.append((f_info, f_content))
                    case "encrypted":
                        self.encrypted.append((f_info, f_content))
                    case "test_case":
                        with ZipFile(BytesIO(f_content)) as tc_zip:
                            for tc_f_info in tc_zip.infolist():
                                tc_f_content = tc_zip.read(tc_f_info.filename)
                                if tc_f_info.filename == "data_intg_test_case_metadata":
                                    self.test_cases.append((tc_f_info, tc_f_content))
                                else:
                                    with ZipFile(BytesIO(tc_f_content)) as csv_zip:
                                        for file_name in csv_zip.namelist():
                                            csv_zip.extract(
                                                path="test_case_data_files/",
                                                member=file_name,
                                            )  # Code to extract input and output csv files
                    case _:
                        pass
