import re
import subprocess
from enum import Enum
from pathlib import Path
from typing import Any, Type

import jinja2
import pydantic

from ibm_watsonx_data_integration.services.datastage.codegen.conn_mappings import CONN_MAPPINGS
from ibm_watsonx_data_integration.services.datastage.codegen.datasource_mappings import DATASOURCE_MAPPINGS
from ibm_watsonx_data_integration.services.datastage.codegen.label_mappings import LABEL_MAPPINGS
from ibm_watsonx_data_integration.services.datastage.codegen.conn_unified_mappings import CONN_UNIFIED_MAPPINGS
from ibm_watsonx_data_integration.services.datastage.codegen.linker import format_dag
from ibm_watsonx_data_integration.services.datastage.codegen.op_mappings import OP_MAPPINGS
from ibm_watsonx_data_integration.services.datastage.codegen.var_namer import VarNamer
from ibm_watsonx_data_integration.services.datastage.models.flow.dag import DAG, StageNode
from ibm_watsonx_data_integration.services.datastage.models.enums import FIELD
from ibm_watsonx_data_integration.services.datastage.models.flow.datastage_flow import DataStageFlow

from ibm_watsonx_data_integration.services.datastage.models.schema import Schema
from ibm_watsonx_data_integration.services.datastage.models.schema.field.time import Time
from ibm_watsonx_data_integration.services.datastage.models.schema.field.timestamp import Timestamp
from ibm_watsonx_data_integration.services.datastage.models.stage_models.complex_stages.rest import (
    Body,
    ClientCertificate,
    Proxy,
    Request,
    ServerCertificate,
    Variable,
)


def _split_list(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def _split_list(lst: list, n: int):
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


class Templates:
    def __init__(self, j_env):
        self._j_env = j_env
        self.stage_template = self._j_env.get_template("op.py.jinja")
        self.transformer_stage_template = self._j_env.get_template("transformer.py.jinja")
        self.complex_flat_file_stage_template = self._j_env.get_template("complex_flat_file.py.jinja")
        self.rest_template = self._j_env.get_template("rest.py.jinja")
        self.paramset_template = self._j_env.get_template("paramset.py.jinja")
        self.paramset_overflow_template = self._j_env.get_template("paramset_overflow_no_copy.py.jinja")
        self.connection_template = self._j_env.get_template("connection.py.jinja")
        self.data_definition_template = self._j_env.get_template("data_definition.py.jinja")
        self.message_handler_template = self._j_env.get_template("message_handler.py.jinja")
        self.local_message_handler_template = self._j_env.get_template("local_message_handler.py.jinja")
        self.java_library_template = self._j_env.get_template("java_library.py.jinja")
        self.function_library_template = self._j_env.get_template("function_library.py.jinja")
        self.match_specification_template = self._j_env.get_template("match_specification.py.jinja")
        self.localparams_template = self._j_env.get_template("localparams.py.jinja")
        self.schema_template = self._j_env.get_template("schema.py.jinja")
        self.schema_overflow_template = self._j_env.get_template("schema_overflow.py.jinja")
        self.link_template = self._j_env.get_template("link.py.jinja")
        self.runtime_template = self._j_env.get_template("runtime.py.jinja")
        self.job_settings_template = self._j_env.get_template("jobsettings.py.jinja")
        self.subflow_template = self._j_env.get_template("subflow.py.jinja")
        self.local_subflow_template = self._j_env.get_template("local_subflow.py.jinja")
        self.comment_template = self._j_env.get_template("comment.py.jinja")
        self.build_stage_template = self._j_env.get_template("build_stage.py.jinja")
        self.wrapped_stage_template = self._j_env.get_template("wrapped_stage.py.jinja")
        self.custom_stage_template = self._j_env.get_template("custom_stage.py.jinja")
        self.test_case_template = self._j_env.get_template("test_case.py.jinja")


class MasterCodeGenerator:
    def __init__(self):
        self._j_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(Path(__file__).parent / "jinja_templates"),
        )
        self.templates = Templates(self._j_env)
        self.var_namer = VarNamer()

        # Mapping from an arbitrary asset object to the string variable name
        # This allows different areas of the generated code referring to the same object to access the same variable name
        self.obj_var_mapping: dict[int, str] = {}
        self.param_set_objs: dict[str, int] = {}
        self.subflows: dict = {}
        self.local_param_var: str = ""
        # self.local_params: LocalParameters = None
        self.subflow_count: int = 0

    def reserve_var(self, name: str, obj: object | str):
        if isinstance(obj, str) and obj in self.obj_var_mapping:
            return self.obj_var_mapping[obj]
        elif isinstance(obj, object) and id(obj) in self.obj_var_mapping:
            return self.obj_var_mapping[id(obj)]
        var_name = self.var_namer.grant_name(name)
        self.obj_var_mapping[id(obj)] = var_name
        return var_name

    def get_object_var(self, obj: object):
        if id(obj) not in self.obj_var_mapping:
            raise KeyError(f"Could not find {obj} in obj_var_mapping")
        return self.obj_var_mapping[id(obj)]

    def get_params(self, param_str: str):
        params = []
        first = False
        curr_param = ""
        for char in param_str:
            if char == "#":
                if first:
                    params.append(curr_param)
                    curr_param = ""
                first = not first
            else:
                if first:
                    curr_param += char
        return params


def _collect_node_code(nodes_code: list):
    code_blocks: list[str] = []

    for code in nodes_code:
        if code["connection_code"]:
            code_blocks.append("\n# Connections")
            code_blocks.extend(code["connection_code"])

        # if code["schema_code"]:
        #     code_blocks.append("\n# Schemas")
        #     code_blocks.extend(code["schema_code"])

        # if code["java_library_code"]:
        #     code_blocks.append("\n# Java Libraries")
        #     code_blocks.extend(code["java_library_code"])

        if code["node_code"]:
            code_blocks.append("\n# Stages")
            code_blocks.append("\n\n".join(code["node_code"]))

        if code["link_code"]:
            code_blocks.append("\n# Graph")
            code_blocks.extend(code["link_code"])

    return code_blocks


def _get_field_template_items(fields):
    type_mappings = {
        "BIGINT": "BigInt",
        "BINARY": "Binary",
        "BIT": "Bit",
        "CHAR": "Char",
        "DATE": "Date",
        "DECIMAL": "Decimal",
        "DOUBLE": "Double",
        "FLOAT": "Float",
        "INTEGER": "Integer",
        "LONGVARBINARY": "LongVarBinary",
        "LONGVARCHAR": "LongVarChar",
        "LONGNVARCHAR": "LongVarChar",
        "NUMERIC": "Numeric",
        "REAL": "Real",
        "SMALLINT": "SmallInt",
        "TIME": "Time",
        "TIMESTAMP": "Timestamp",
        "TINYINT": "TinyInt",
        "UNKNOWN": "Unknown",
        "VARBINARY": "VarBinary",
        "NCHAR": "NChar",
        "NVARCHAR": "VarChar",
        "VARCHAR": "VarChar",
        "WCHAR": "NChar",
        "WLONGVARCHAR": "LongNVarChar",
        "WVARCHAR": "NVarChar",
    }

    default_precision = {
        "Time": 8,
        "Timestamp": 19,
    }

    field_items = []
    for field in fields:
        field_dict = {}
        field_dict["type"] = type_mappings[field.configuration.app_data.get("odbc_type", field.configuration.odbc_type).upper()]
        field_dict["name"] = field.configuration.name
        properties = ""
        if field.configuration.nullable and callable(getattr(field, "nullable", None)):
            properties += ".nullable()"
        if field.configuration.metadata.is_key and callable(getattr(field, "key", None)):
            properties += ".key()"
        if field.configuration.metadata.source_field_id is not None and callable(getattr(field, "source", None)):
            properties += f'.source("{field.configuration.metadata.source_field_id}")'
        if field.configuration.metadata.max_length is not None and callable(getattr(field, "length", None)):
            properties += f".length({field.configuration.metadata.max_length})"
        if (
            "is_unicode_string" in field.configuration.app_data
            and field.configuration.app_data["is_unicode_string"]
            and callable(getattr(field, "unicode", None))
        ):
            properties += ".unicode()"
        if not field.configuration.metadata.is_signed and callable(getattr(field, "unsigned", None)):
            properties += ".unsigned()"
        if field.configuration.metadata.decimal_precision is not None and callable(getattr(field, "precision", None)):
            default_prec = default_precision[field_dict["type"]] if field_dict["type"] in default_precision else 100
            if field.configuration.metadata.decimal_precision != default_prec:
                properties += f".precision({field.configuration.metadata.decimal_precision})"
        if (
            field.configuration.metadata.decimal_scale is not None
            and field.configuration.metadata.decimal_scale > 0
            and callable(getattr(field, "scale", None))
        ):
            properties += f".scale({field.configuration.metadata.decimal_scale})"
        if "extended_type" in field.configuration.app_data and field.configuration.app_data["extended_type"] is not None:
            if "timezone" in field.configuration.app_data["extended_type"] and callable(getattr(field, "timezone", None)):
                properties += ".timezone()"
            if "microseconds" in field.configuration.app_data["extended_type"] and callable(getattr(field, "microseconds", None)):
                properties += ".microseconds()"
        if (
            "difference" in field.configuration.app_data
            and field.configuration.app_data["difference"]
            and callable(getattr(field, "difference", None))
        ):
            properties += ".difference()"
        if (
            "derivation" in field.configuration.app_data
            and field.configuration.app_data["derivation"]
            and callable(getattr(field, "derivation", field.configuration.app_data["derivation"]))
        ):
            properties += f".derivation({repr(field.configuration.app_data['derivation'])})"
        if (
            "cluster_key_change" in field.configuration.app_data
            and field.configuration.app_data["cluster_key_change"]
            and callable(getattr(field, "cluster_key_change", None))
        ):
            properties += ".cluster_key_change()"
        if (
            "key_change" in field.configuration.app_data
            and field.configuration.app_data["key_change"]
            and callable(getattr(field, "key_change", None))
        ):
            properties += ".key_change()"
        if (
            "pivot_property" in field.configuration.app_data
            and field.configuration.app_data["pivot_property"]
            and callable(getattr(field, "pivot", None))
        ):
            properties += f'.pivot("{field.configuration.app_data["pivot_property"]}")'
        if (
            "change_code" in field.configuration.app_data
            and field.configuration.app_data["change_code"]
            and callable(getattr(field, "change_code", None))
        ):
            properties += ".change_code()"
        if field.configuration.metadata.item_index not in [None, 0] and callable(getattr(field, "level_number", None)):
            properties += f".level_number({field.configuration.metadata.item_index})"
        # if field.configuration.metadata.description not in [None, "", " "]:
        #     properties += f'.description("{field.configuration.metadata.description.replace("\"", "'").replace("\r\n", "\\n").replace("\n", "\\n")}")'
        if (
            "dimension_min_size" in field.configuration.app_data
            and "dimension_max_size" in field.configuration.app_data
            and field.configuration.app_data["dimension_min_size"] == field.configuration.app_data["dimension_max_size"]
            and callable(getattr(field, "vector", None))
            and callable(getattr(field, "vector_occurs", None))
        ):
            properties += ".vector(FIELD.VectorType.vector_occurs)"
            properties += f""".vector_occurs({field.configuration.app_data["dimension_max_size"].strip('"').strip("'")})"""
        elif (
            "dimension_min_size" in field.configuration.app_data
            and field.configuration.app_data["dimension_min_size"] == "0"
            and callable(getattr(field, "vector", None))
        ):
            properties += ".vector(FIELD.VectorType.variable)"
        if (
            "time_scale" in field.configuration.app_data
            and field.configuration.app_data["time_scale"] not in [0, None]
            and (isinstance(field, Time) or isinstance(field, Timestamp))
        ):
            properties += f".scale({field.configuration.app_data['time_scale']})"
        if "apt_field_properties" in field.configuration.app_data:
            apt_str: str = field.configuration.app_data["apt_field_properties"]

            # handling/removal of nested (sub)properties from apt_field_properties str
            cycle_prop = re.search(r"(cycle={.*})", apt_str)
            if cycle_prop and callable(getattr(field, "generate_type", None)):
                properties += ".generate_type(FIELD.GenerateType.cycle)"
                apt_str = apt_str.replace(cycle_prop.group(), "")
                cycle_subprops = [v for v in cycle_prop.group().replace("cycle={", "").replace("}", "").split(",") if v]
                for subprop in cycle_subprops:
                    prop_name, prop_value = tuple(subprop.split("="))
                    if prop_name == "limit":
                        if prop_value.strip("'").strip(" ").isdigit():
                            properties += f".cycle_limit({prop_value})"
                        else:
                            properties += f""".cycle_limit(FIELD.CycleLimit.{FIELD.CycleLimit(prop_value.strip("'")).name})"""
                    elif prop_name == "incr":
                        if prop_value.strip("'").strip(" ").isdigit():
                            properties += f".cycle_increment({prop_value})"
                        else:
                            properties += f""".cycle_increment(FIELD.CycleIncrement.{FIELD.CycleIncrement(prop_value.strip("'")).name})"""
                    elif prop_name == "init":
                        if prop_value.strip("'").strip(" ").isdigit():
                            properties += f".cycle_initial_value({prop_value})"
                        else:
                            properties += (
                                f""".cycle_initial_value(FIELD.CycleInitialValue.{FIELD.CycleInitialValue(prop_value.strip("'")).name})"""
                            )
            if cycle_prop and callable(getattr(field, "generate_algorithm", None)):
                properties += ".generate_algorithm(FIELD.GenerateAlgorithm.cycle)"
                apt_str = apt_str.replace(cycle_prop.group(), "")
                cycle_subprops = cycle_prop.group().replace("cycle={", "").replace("}", "").split(",")
                cycle_values = []
                cycle_value_pattern = r"""value\s*=\s*(?:(['"])(.*?)\1|(\d+))"""
                for subprop in cycle_subprops:
                    matches = re.findall(cycle_value_pattern, subprop)
                    found_cycle_values = [m[1] if m[1] else m[2] for m in matches]
                    cycle_values += found_cycle_values
                properties += f".cycle_values({cycle_values})"

            random_prop = re.search(r"(random=\{.*\})", apt_str)
            if random_prop and callable(getattr(field, "generate_type", None)):
                properties += ".generate_type(FIELD.GenerateType.random)"
                apt_str = apt_str.replace(random_prop.group(), "")
                random_subprops = [v for v in random_prop.group().replace("random={", "").replace("}", "").split(",") if v]
                for subprop in random_subprops:
                    if subprop == "signed":
                        properties += ".random_signed()"
                    else:
                        prop_name, prop_value = tuple(subprop.split("="))
                        if prop_name == "limit":
                            properties += f""".random_limit(FIELD.RandomLimit.{FIELD.RandomLimit(prop_value.strip("'")).name})"""
                        elif prop_name == "seed":
                            properties += f""".random_seed(FIELD.RandomSeed.{FIELD.RandomSeed(prop_value.strip("'")).name})"""
            # Splitting string into properties based on comma separation,
            # but with handling for commas contained inside of property
            # values (e.g. user input strings). Skipped commas are
            # between pairs of single quotes
            name_to_class = {
                "skip": int,
                "delim": FIELD.Delim,
                "position": int,
                "tagcase": int,
                "actual_length": int,
                "null_length": int,
                "delim_string": str,
                "null_field": str,
                "quote": FIELD.Quote,
                "vector_prefix": FIELD.VectorPrefix,
                "reference": str,
                "prefix": FIELD.Prefix,
                "default": str,
                "max_width": int,
                "padchar": FIELD.PadChar,
                "c_format": str,
                "nullseed": int,
                "nulls": int,
                "width": int,
                "out_format": str,
                "alphabet": str,
                "invalids": int,
                "epoch": int,
                "days_since": int,
                "date_format": str,
                "decimal_separator": FIELD.DecimalSeparator,
                "zeros": int,
                "precision": int,
                "round": FIELD.Round,
                "scale": int,
                "_scale": int,
                "timestamp_format": str,
                "time_format": str,
            }
            name_to_method = {
                "skip": "byte_to_skip",
                "delim": "delimiter",
                "position": "start_position",
                "tagcase": "tag_case_value",
                "actual_length": "actual_field_length",
                "null_length": "null_field_length",
                "delim_string": "delimiter_string",
                "null_field": "null_field_value",
                "quote": "quote",
                "vector_prefix": "vector_prefix",
                "reference": "link_field_reference",
                "prefix": "prefix_bytes",
                "default": "default",
                "max_width": "field_max_width",
                "padchar": "padchar",
                "c_format": "c_format",
                "nullseed": "null_seed",
                "nulls": "percent_null",
                "width": "field_width",
                "out_format": "out_format",
                "alphabet": "alphabet",
                "invalids": "percent_invalid",
                "epoch": "epoch",
                "days_since": "days_since",
                "date_format": "format_string",
                "decimal_separator": "decimal_separator",
                "zeros": "percent_zeros",
                "precision": "precision",
                "round": "rounding",
                "scale": "decimal_type_scale",
                "_scale": "scale_factor",
                "timestamp_format": "format_string",
                "time_format": "format_string",
            }

            apt_enums_classes: Type[Enum] = {
                FIELD.DecimalPacked,
                FIELD.CharSet,
                FIELD.DataFormat,
                FIELD.ByteOrder,
                FIELD.SignPosition,
            }

            value_to_class = {}

            for apt_enum_class in apt_enums_classes:
                for enum_value in apt_enum_class:
                    value_to_class[enum_value.value] = apt_enum_class

            enum_class_to_method = {
                FIELD.ByteOrder: "byte_order",
                FIELD.DecimalPacked: "packed",
                FIELD.CharSet: "charset",
                FIELD.DataFormat: "data_format",
                FIELD.SignPosition: "sign_position",
            }

            apt_booleans = {
                "generate",
                "signed",
                "export_ebcdic_as_ascii",
                "midnight_seconds",
                "link_keep",
                "fix_zero",
                "julian",
                "check",
            }
            apt_boolean_methods = {
                "generate": "generate_on_output",
                "signed": "packed_signed",
                "export_ebcdic_as_ascii": "export_ebcdic_as_ascii",
                "midnight_seconds": "is_midnight_seconds",
                "link_keep": "is_link_field",
                "fix_zero": "allow_all_zeros",
                "julian": "julian",
                "check": "check_packed",
            }

            start_index = 0
            while start_index < len(apt_str):
                end_index = start_index
                has_opening_quote = False
                # increment end_index until end of current property
                while end_index < len(apt_str):
                    if not has_opening_quote and apt_str[end_index] == "'":
                        has_opening_quote = True
                        end_index += 1
                    elif has_opening_quote and apt_str[end_index] == "'":
                        end_index += 1
                        break
                    elif not has_opening_quote and apt_str[end_index] == ",":
                        end_index += 1
                        break
                    else:
                        end_index += 1
                prop = apt_str[start_index:end_index].strip(",").strip(" ")
                if prop == "function=rundate" and callable(getattr(field, "use_current_date", None)):
                    properties += ".use_current_date()"
                    prop = ""

                if prop:
                    if "=" in prop:
                        prop_name, prop_value = tuple(prop.split("="))
                        if prop_name in name_to_class and prop_name in name_to_method:
                            prop_class: Type[Enum | str | int] = name_to_class[prop_name]
                            prop_method = name_to_method[prop_name]
                            if callable(getattr(field, prop_method, None)) and issubclass(prop_class, Enum):
                                if not (prop_value.startswith("'") and prop_value.endswith("'")) and prop_value.isdigit():
                                    prop_value = int(prop_value)
                                else:
                                    prop_value = prop_value.strip("'").strip('"')
                                properties += f".{prop_method}(FIELD.{prop_class.__name__}.{prop_class(prop_value).name})"
                            if callable(getattr(field, prop_method, None)) and issubclass(prop_class, str):
                                prop_value = prop_value.strip("'").strip('"')
                                properties += f".{prop_method}({repr(prop_value)})"
                            if callable(getattr(field, prop_method, None)) and issubclass(prop_class, int):
                                properties += f".{prop_method}({prop_value})"
                        else:
                            print(f"Warning: {prop_name} is an unsupported property")
                    else:
                        if prop in apt_booleans:
                            prop_method = apt_boolean_methods[prop]
                            if callable(getattr(field, prop_method, None)):
                                properties += f".{prop_method}()"
                        elif prop in value_to_class:
                            prop_value = prop
                            if (
                                isinstance(prop_value, str)
                                and not (prop_value.startswith("'") and prop_value.endswith("'"))
                                and prop_value.isdigit()
                            ):
                                prop_value = int(prop_value)
                            elif isinstance(prop_value, str):
                                prop_value = prop_value.strip("'").strip('"')
                            prop_class = value_to_class[prop]
                            prop_method = enum_class_to_method[prop_class]

                            properties += f".{prop_method}(FIELD.{prop_class.__name__}.{prop_class(prop_value).name})"

                start_index = end_index

        field_dict["properties"] = properties
        field_items.append(field_dict)
    return field_items


class FlowCodeGenerator:
    def __init__(
        self,
        flow_name: str = "unnamed_flow",
        fc: DataStageFlow = DataStageFlow(),
        master_gen: MasterCodeGenerator = None,
        offline: bool = False,
        skip_subflows: bool = False,
    ):
        assert isinstance(fc, DataStageFlow)
        self.flow_name = flow_name
        self.fc = fc
        self.dag = fc._dag
        self.master_gen = master_gen
        self.offline = offline
        self.skip_subflows = skip_subflows
        self.extra_imports = set()

    def generate_setup(self, api_key, project_id):
        auth = self.generate_auth(api_key=api_key, base_auth_url="https://cloud.ibm.com")
        platform = self.generate_platform(base_api_url="https://api.ca-tor.dai.cloud.ibm.com")
        project = self.generate_project(project_id=project_id)
        environment = self.generate_environment()
        imports = self.generate_imports()

        code_blocks = [imports, auth, platform, project, environment, "\n"]
        return code_blocks

    def generate_all(self):
        self.dag.compute_metadata()
        code_blocks = [self.generate_create_flow(flow_name=self.flow_name)]

        # if ps_code:
        #     code_blocks.append("\n# Parameter sets")
        #     code_blocks.extend(ps_code)
        # if mh_code:
        #     code_blocks.append("\n# Message Handlers")
        #     code_blocks.extend(mh_code)
        # if lp_code and not (len(lp_code) == 1 and lp_code[0] == ""):
        #     code_blocks.append("\n# Local parameters")
        #     code_blocks.extend(lp_code)
        # if lmh_code and not (len(lmh_code) == 1 and lmh_code[0] == ""):
        #     code_blocks.append("\n# Local Message Handler")
        #     code_blocks.extend(lmh_code)

        nodes_code = self.generate_nodes()
        code_blocks.extend(_collect_node_code(nodes_code))

        # if runtime_code:
        #     code_blocks.append("\n# Runtime")
        #     code_blocks.append(runtime_code)

        code_str = "\n".join(code_blocks)
        try:
            formatted = subprocess.run(
                [
                    "ruff",
                    "format",
                    "--config",
                    Path(__file__).parent / "ruff.toml",
                    "-",
                ],
                check=True,
                input=code_str,
                encoding="utf-8",
                capture_output=True,
            ).stdout
        except subprocess.CalledProcessError as e:
            raise Exception(f"Error while formatting code:\n{code_str}\n{e.stderr}")

        return formatted

    def generate_all_zip(self):
        self.dag.compute_metadata()
        code_blocks = [self.generate_create_flow(flow_name=self.flow_name)]
        # if lp_code and not (len(lp_code) == 1 and lp_code[0] == ""):
        #     code_blocks.append("\n# Local parameters")
        #     code_blocks.extend(lp_code)
        # if lmh_code and not (len(lmh_code) == 1 and lmh_code[0] == ""):
        #     code_blocks.append("\n# Local message handler")
        #     code_blocks.extend(lmh_code)

        nodes_code = self.generate_nodes()
        code_blocks.extend(_collect_node_code(nodes_code))

        # if runtime_code:
        #     code_blocks.append("\n# Runtime")
        #     code_blocks.append(runtime_code)

        code_str = "\n".join(code_blocks)
        try:
            formatted = subprocess.run(
                [
                    "ruff",
                    "format",
                    "--config",
                    Path(__file__).parent / "ruff.toml",
                    "-",
                ],
                check=True,
                input=code_str,
                encoding="utf-8",
                capture_output=True,
            ).stdout
        except subprocess.CalledProcessError as e:
            print(f"Error while formatting code:\n{code_str}\n{e.stderr}")
            # raise Exception(f"Error while formatting code: {e.stderr}")
            return code_str

        return formatted

    def generate_all_zip_one_file(self):
        self.dag.compute_metadata()
        code_blocks = [self.generate_create_flow(flow_name=self.flow_name)]

        # if lp_code and not (len(lp_code) == 1 and lp_code[0] == ""):
        #     code_blocks.append("\n# Local parameters")
        #     code_blocks.extend(lp_code)
        # if lmh_code and not (len(lmh_code) == 1 and lmh_code[0] == ""):
        #     code_blocks.append("\n# Local message handler")
        #     code_blocks.extend(lmh_code)

        nodes_code = self.generate_nodes()
        code_blocks.extend(_collect_node_code(nodes_code))

        # if runtime_code:
        #     code_blocks.append("\n# Runtime")
        #     code_blocks.append(runtime_code)

        code_str = "\n".join(code_blocks)
        try:
            formatted = subprocess.run(
                [
                    "ruff",
                    "format",
                    "--config",
                    Path(__file__).parent / "ruff.toml",
                    "-",
                ],
                check=True,
                input=code_str,
                encoding="utf-8",
                capture_output=True,
            ).stdout
        except subprocess.CalledProcessError as e:
            # print(f"Error while formatting code:\n{code_str}\n{e.stderr}")
            print(f"Error while formatting code:\n{e.stderr}")
            return code_str

        return formatted

    def generate_imports(self):
        return "\n".join(
            {
                "from ibm_watsonx_data_integration import *",
                "from ibm_watsonx_data_integration.services.datastage import *",
                "from ibm_watsonx_data_integration.common.auth import IAMAuthenticator",
            }.union(self.extra_imports)
        )

    def generate_auth(self, api_key, base_auth_url):
        if "os." in api_key:
            self.extra_imports.add("import os")
        else:
            api_key = '"' + api_key + '"'
        return f'api_key = {api_key}\nauth = IAMAuthenticator(\n    api_key=api_key,\n    base_auth_url="{base_auth_url}"\n)'

    def generate_platform(self, base_api_url):
        return f'platform = Platform(auth, base_api_url="{base_api_url}")'

    def generate_project(self, project_id):
        if "os." in project_id:
            self.extra_imports.add("import os")
        else:
            project_id = '"' + project_id + '"'
        return f"project = platform.projects.get(guid={project_id})"

    def generate_environment(self):
        return ""  # Not doing environments for now

    def generate_create_flow(self, flow_name):
        self.composer = self.master_gen.reserve_var("flow", self.fc)
        return f'{self.composer} = project.create_flow(name="{flow_name}", environment=None, flow_type="datastage")'

    def generate_parameter_sets(self):
        ps_code_gen = []
        for param_set in self.fc.parameter_sets:
            ps_code_gen.append(self._generate_param_set(param_set))
        return ps_code_gen

    def generate_local_parameters(self):
        lp_code_gen = []
        lp_code_gen.append(self._generate_local_param(self.fc.local_parameters))
        return lp_code_gen

    # Generate message handler only for json to python conversion
    def generate_message_handlers(self):
        mh_code_gen = []
        for message_handler in self.fc.message_handlers:
            mh_code_gen.append(self._generate_message_handler(message_handler))
        return mh_code_gen

    def generate_local_message_handler(self):
        lmh_code_gen = []
        lmh_code_gen.append(self._generate_local_message_handler(self.fc.local_message_handler))
        return lmh_code_gen

    def generate_runtime(self):
        if not self.fc.runtime.format and not self.fc.runtime.runtime_settings:
            return None
        rt_code_gen = self._generate_runtime(self.fc.runtime)
        return rt_code_gen

    def generate_nodes(self):
        assert self.dag.is_metadata_computed
        subgraphs = self.dag.get_connected_subgraphs()
        nodes_code = []
        for sg in subgraphs:
            sgcg = SubgraphCodeGenerator(
                self.master_gen,
                sg,
                self.offline,
                subflow=False,
                skip_subflows=self.skip_subflows,
                composer=self.composer,
            )
            nodes_code.append(sgcg.generate())
        return nodes_code

    # def _generate_param_set(self, param_set: ParameterSet) -> str:
    #     parameters = []

    #     imported = True if param_set.asset_id is not None else False
    #     asset_id = param_set.asset_id if imported else None

    #     if not imported:
    #         for param in param_set.parameters:
    #             param_dict = {}
    #             param_dict["name"] = param.name
    #             if isinstance(param.value, str):
    #                 param_value = param.value.replace("'", "\\'").replace('"', '\\"')
    #                 if "\n" in param_value:
    #                     param_dict["value"] = f'""{param_value}""'
    #                 else:
    #                     param_dict["value"] = param_value
    #             else:
    #                 param_dict["value"] = param.value
    #             param_dict["extras"] = ""
    #             if param.description:
    #                 param_dict["extras"] += f", description = {repr(param.description)}"
    #             if param.prompt:
    #                 param_dict["extras"] += f", prompt = {repr(param.prompt)}"
    #             if param.type == "multilinestring":
    #                 param_dict["type"] = "MultilineString"
    #                 param_dict["value"] = f'""{param_dict["value"]}""'
    #             elif param.type == "enum":
    #                 param_dict["type"] = "List"
    #             else:
    #                 param_dict["type"] = param.type[0].upper() + param.type[1:]
    #             if param.type == "list" or param.type == "enum":
    #                 param_dict["valid_values"] = param.valid_values
    #             parameters.append(param_dict)

    #     var_name = self.master_gen.reserve_var(param_set.name, param_set)
    #     self.master_gen.param_set_objs[param_set.name] = id(param_set)

    #     for value_set in param_set.value_sets:
    #         for value in value_set:
    #             value = value.replace("'", "\\'").replace('"', '\\"')

    #     return (
    #         self.master_gen.templates.paramset_template.render(
    #             var_name=var_name,
    #             paramset_name=param_set.name,
    #             parameters=parameters,
    #             value_sets=param_set.value_sets,
    #             asset_id=asset_id,
    #             imported=imported,
    #             description=repr(param_set.description),
    #             offline=self.offline,
    #         )
    #         + f"\nflow.use_paramset({var_name})\n"
    #     )

    # def _generate_local_param(self, local_params: LocalParameters):
    #     if not local_params:
    #         return ""
    #     parameters = []
    #     for param in local_params.parameters:
    #         param_dict = {}
    #         param_dict["value"] = repr(param.value)
    #         if param.type == "multilinestring":
    #             param_dict["type"] = "MultilineString"
    #         elif param.type == "enum":
    #             param_dict["type"] = "List"
    #         else:
    #             param_dict["type"] = param.type[0].upper() + param.type[1:]
    #         param_dict["name"] = param.name
    #         param_dict["extras"] = ""
    #         if param.description:
    #             param_dict["extras"] += f", description = {repr(param.description)}"
    #         if param.prompt:
    #             param_dict["extras"] += f', prompt = "{param.prompt}"'
    #         if param.type == "enum":
    #             param_dict["valid_values"] = param.valid_values
    #         parameters.append(param_dict)
    #     var_name = self.master_gen.reserve_var("local_params", local_params)
    #     self.master_gen.local_param_var = var_name
    #     self.master_gen.local_params = local_params

    #     return self.master_gen.templates.localparams_template.render(var_name=var_name, parameters=parameters, composer="flow")

    # # Generate message handler only for json to python conversion
    # def _generate_message_handler(self, message_handler: MessageHandler) -> str:
    #     var_name = self.master_gen.reserve_var("referenced_message_handler", message_handler)

    #     return self.master_gen.templates.message_handler_template.render(
    #         var_name=var_name,
    #         message_handler_name=message_handler.name,
    #         messages=[],
    #         asset_id=message_handler.asset_id,
    #         imported=True,
    #         offline=self.offline,
    #         description=message_handler.description,
    #     )

    # def _generate_local_message_handler(self, local_message_handler: LocalMessageHandler):
    #     if not local_message_handler:
    #         return ""
    #     messages = []
    #     for message in local_message_handler.messages:
    #         message_dict = {}
    #         message_dict["id"] = message.id
    #         message_dict["action"] = repr(message.action)
    #         message_dict["description"] = repr(message.description)
    #         messages.append(message_dict)

    #     var_name = self.master_gen.reserve_var("local_message_handler", local_message_handler)

    #     return self.master_gen.templates.local_message_handler_template.render(var_name=var_name, messages=messages, composer="flow")

    # def _generate_runtime(self, runtime: Runtime):
    #     var_name = self.master_gen.reserve_var("runtime", runtime)
    #     return self.master_gen.templates.runtime_template.render(
    #         var_name=var_name,
    #         runtime_settings=runtime.runtime_settings,
    #         format=runtime.format,
    #     )


# class SubflowCodeGenerator:
#     def __init__(
#         self,
#         subflow: Subflow | SuperNode,
#         master_gen: MasterCodeGenerator,
#         asset_id: str = None,
#         offline: bool = False,
#         zip_structure: bool = False,
#         parent_composer: str = "flow",
#     ):
#         self.subflow = subflow
#         self.dag = subflow.subflow_dag if isinstance(subflow, SuperNode) else subflow.dag
#         self.master_gen = master_gen
#         self.asset_id = asset_id
#         self.offline = offline
#         self.templates = master_gen.templates
#         self.zip_structure = zip_structure

#         self.master_gen.subflow_count += 1
#         if self.subflow.is_local:
#             self.composer = f"lsf_{self.master_gen.subflow_count}" if self.master_gen.subflow_count > 1 else "lsf"
#         else:
#             self.composer = f"sf_{self.master_gen.subflow_count}" if self.master_gen.subflow_count > 1 else "sf"
#         self.parent_composer = parent_composer

#     def generate_all(self):
#         self.dag.compute_metadata()
#         nodes_code = self.generate_nodes()

#         code_blocks = []

#         for code in nodes_code:
#             if code["connection_code"]:
#                 code_blocks.append("\n# Connections")
#                 # code["connection_code"] = ["\t" + line for line in code["connection_code"]]
#                 code_blocks.extend(code["connection_code"])

#             if code["java_library_code"]:
#                 code_blocks.append("\n# Java Libraries")
#                 code_blocks.extend(code["java_library_code"])

#             if code["schema_code"]:
#                 code_blocks.append("\n# Schemas")
#                 # code["schema_code"] = ["\t" + line for line in code["schema_code"]]
#                 # code["schema_code"] = [line.replace("\n", "\n\t") for line in code["schema_code"]]
#                 code_blocks.extend(code["schema_code"])

#             if code["node_code"]:
#                 code_blocks.append("\n# Stages")
#                 # code["node_code"] = ["\t" + line for line in code["node_code"]]
#                 code_blocks.extend(code["node_code"])

#             if code["link_code"]:
#                 code_blocks.append("\n# Graph")
#                 # code["link_code"] = ["\t" + line for line in code["link_code"]]
#                 code_blocks.extend(code["link_code"])

#         if self.subflow.is_local:
#             code_str = "\n".join(code_blocks)
#         else:
#             code_str = "\n".join(code_blocks).replace("\n", "\n    ")

#         var_name = self.master_gen.reserve_var(self.subflow.name, self.subflow)
#         self.master_gen.subflow_count += 1

#         if self.subflow.is_local:
#             return self.templates.local_subflow_template.render(
#                 var_name=var_name,
#                 nodes_code=code_str,
#                 zip_structure=self.zip_structure,
#                 offline=self.offline,
#                 label=self.subflow.name,
#                 composer=self.composer,
#             )

#         parameter_sets = []
#         if hasattr(self.subflow, "parameter_sets"):
#             parameter_sets = [self.master_gen.get_object_var(paramset) for paramset in self.subflow.parameter_sets]

#         local_parameter_code = None
#         if self.subflow.local_parameters is not None:
#             local_parameter_code = self._generate_local_param(local_params=self.subflow.local_parameters).replace("\n", "\n    ")

#         return self.templates.subflow_template.render(
#             var_name=var_name,
#             nodes_code=code_str,
#             zip_structure=self.zip_structure,
#             offline=self.offline,
#             parameter_sets=parameter_sets,
#             local_params=local_parameter_code,
#             name=self.subflow.name,
#             composer=self.composer,
#             parent_composer=self.parent_composer,
#             rcp=self.subflow.rcp if hasattr(self.subflow, "rcp") else False,
#             label=(self.subflow.label if hasattr(self.subflow, "label") else self.subflow.name),
#         )

#     def generate_nodes(self):
#         self.dag.compute_metadata()
#         assert self.dag.is_metadata_computed
#         subgraphs = self.dag.get_connected_subgraphs()
#         nodes_code = []
#         subflow = "local subflow" if self.subflow.is_local else "subflow"
#         for sg in subgraphs:
#             sgcg = SubgraphCodeGenerator(
#                 self.master_gen,
#                 sg,
#                 self.offline,
#                 subflow=subflow,
#                 composer=self.composer,
#             )
#             nodes_code.append(sgcg.generate())
#         return nodes_code

#     def get_imports(self):
#         # TODO: change to include parameter sets
#         return "from ibm.datastage import *"

#     def _generate_local_param(self, local_params: LocalParameters):
#         if not local_params:
#             return ""
#         parameters = []
#         for param in local_params.parameters:
#             param_dict = {}
#             param_dict["value"] = repr(param.value)
#             if param.type == "multilinestring":
#                 param_dict["type"] = "MultilineString"
#             elif param.type == "enum":
#                 param_dict["type"] = "List"
#             else:
#                 param_dict["type"] = param.type[0].upper() + param.type[1:]
#             param_dict["name"] = param.name
#             param_dict["extras"] = ""
#             if param.description:
#                 param_dict["extras"] += f", description = {repr(param.description)}"
#             if param.prompt:
#                 param_dict["extras"] += f', prompt = "{param.prompt}"'
#             if param.type == "enum":
#                 param_dict["valid_values"] = param.valid_values
#             parameters.append(param_dict)
#         var_name = self.master_gen.reserve_var("local_params", local_params)
#         self.master_gen.local_param_var = var_name
#         self.master_gen.local_params = local_params

#         return self.master_gen.templates.localparams_template.render(var_name=var_name, parameters=parameters, composer=self.composer)


class SubgraphCodeGenerator:
    def __init__(
        self,
        master_gen: MasterCodeGenerator,
        subgraph: DAG,
        offline: bool,
        subflow: str = "flow",
        skip_subflows: bool = False,
        composer: str = "flow",
    ):
        self.master_gen = master_gen
        self.subgraph = subgraph
        self._j_env = master_gen._j_env
        self.templates = master_gen.templates
        self.offline = offline
        self.subflow = subflow
        self.skip_subflows = skip_subflows
        self.composer = composer

    def generate(self) -> dict[str, list]:
        top_order = self.subgraph.get_topological_ordering(stages_only=False)
        subgraph_props = {
            "node_code": [],
            "schema_code": dict(),
            "link_code": [],
            "connection_code": [],
            "java_library_code": [],
        }

        # Schema code
        for link in self.subgraph.links():
            if not link.name:
                continue
            self.master_gen.reserve_var(link.name, link)
            if link.schema:
                if not (hasattr(link.src, "model") and link.src.configuration.op_name == "PxCFF"):
                    try:
                        schema_var_name = link.src.label + "_schema"
                    except AttributeError:
                        schema_var_name = "schema"
                    # Add code for defining schemas
                    schema_var_name_final, schema_code = self._generate_schema(link.schema, schema_var_name)
                    subgraph_props["schema_code"][link] = (schema_var_name_final, schema_code)

        for node in top_order:
            # if isinstance(node, GhostNode):
            #     subgraph_props["node_code"].append(self._generate_stub_stage(node))
            #     continue
            # if isinstance(node, SuperNode) or isinstance(node, SuperNodeRef):
            #     if isinstance(node, SuperNodeRef):
            #         var_name = self.master_gen.reserve_var(node.name, node)
            #         subgraph_props["node_code"].append(f"{var_name} = {self.composer}.add_subflow({var_name})")
            #         continue
            #     if self.skip_subflows:
            #         var_name = self.master_gen.get_object_var(node)
            #         subgraph_props["node_code"].append(f"{var_name} = {self.composer}.add_subflow({var_name})")
            #         continue
            #     subgraph_props["node_code"].append(self._generate_super_node_stage(node))
            #     continue
            # if isinstance(node, EntryNode):
            #     subgraph_props["node_code"].append(self._generate_entry_node(node))
            #     continue
            # if isinstance(node, ExitNode):
            #     subgraph_props["node_code"].append(self._generate_exit_node(node))
            #     continue
            # if isinstance(node, MarkdownComment) or isinstance(node, StyledComment):
            #     subgraph_props["node_code"].append(self._generate_comment(node))
            #     continue
            # if isinstance(node, BuildStageStage):
            #     subgraph_props["node_code"].append(self._generate_build_stage_node(node))
            #     continue
            # if isinstance(node, WrappedStageStage):
            #     subgraph_props["node_code"].append(self._generate_wrapped_stage_node(node))
            #     continue
            # if isinstance(node, CustomStageStage):
            #     subgraph_props["node_code"].append(self._generate_custom_stage_node(node))
            #     continue

            if (
                hasattr(node, "configuration")
                and hasattr(node.configuration, "connection")
                and node.configuration.connection
                and not isinstance(node.configuration.connection, str)
            ):
                subgraph_props["connection_code"].append(self._generate_connection(node.configuration.connection))
            if (
                hasattr(node, "configuration")
                and hasattr(node.configuration, "java_library")
                and node.configuration.java_library
                and not isinstance(node.configuration.java_library, str)
            ):
                subgraph_props["java_library_code"].append(self._generate_java_library(node.configuration.java_library))

            subgraph_props["node_code"].append(self._generate_model_stage(node))

        # Add code for linking stages and customizing links
        subgraph_props["link_code"].append(
            format_dag(self.master_gen, self.subgraph, subgraph_props["schema_code"], composer=self.composer)
        )

        return subgraph_props

    # def _generate_stub_stage(self, node: GhostNode):
    #     var_name = self.master_gen.reserve_var("ghost", node)
    #     return f"""{var_name} = flow.add_stage("Peek")"""

    # def _generate_entry_node(self, node: EntryNode):
    #     var_name = self.master_gen.reserve_var(node.label, node)
    #     return f'{var_name} = {self.composer}.add_entry_node("{node.label}")'

    # def _generate_exit_node(self, node: ExitNode):
    #     var_name = self.master_gen.reserve_var(node.label, node)
    #     return f'{var_name} = {self.composer}.add_exit_node("{node.label}")'

    # def _generate_super_node_stage(self, node: SuperNode):
    #     subflow_code_gen = SubflowCodeGenerator(
    #         subflow=node,
    #         master_gen=self.master_gen,
    #         offline=self.offline,
    #         parent_composer=self.composer,
    #     )
    #     return subflow_code_gen.generate_all()

    # def _generate_comment(self, node: MarkdownComment | StyledComment):
    #     if isinstance(node, StyledComment):
    #         var_name = var_name = self.master_gen.reserve_var("annotation", node)
    #         formats = {}
    #         for format in node.configuration.formats:
    #             if "type" in format and "value" in format:
    #                 format_types = {
    #                     "bold": "bold",
    #                     "italics": "italics",
    #                     "fontType": "font",
    #                     "textDecoration": "text_decoration",
    #                     "backgroundColor": "background_color",
    #                     "textColor": "text_color",
    #                     "alignVertically": "vertical_align",
    #                     "alignHorizontally": "horizontal_align",
    #                     "textSize": "text_size",
    #                     "outlineStyle": "outline",
    #                 }
    #                 format_type = format_types[format["type"]] if format["type"] in format_types else format["type"]
    #                 value = format["value"]
    #                 if format_type == "outline":
    #                     value = False if value == "outline-none" else True
    #                 elif format_type == "text_size":
    #                     value = int(value.split("-")[-1])
    #                 else:
    #                     value = repr(value)
    #                 formats[format_type] = value
    #         return self.templates.comment_template.render(
    #             var_name=var_name,
    #             composer=self.composer,
    #             content=repr(node.configuration.content),
    #             styled=True,
    #             formats=formats,
    #         )
    #     if isinstance(node, MarkdownComment):
    #         var_name = self.master_gen.reserve_var("comment", node)
    #         return self.templates.comment_template.render(
    #             var_name=var_name,
    #             composer=self.composer,
    #             content=repr(node.configuration.content),
    #             markdown=True,
    #         )

    # def _generate_build_stage_node(self, node: BuildStageStage):
    #     build_stage_code_gen = BuildStageCodeGenerator(
    #         asset=node.build_stage,
    #         master_gen=self.master_gen,
    #         build_stage=node,
    #         parent_composer=self.composer,
    #         offline=self.offline,
    #     )
    #     return build_stage_code_gen.generate_code()

    # def _generate_wrapped_stage_node(self, node: WrappedStageStage):
    #     wrapped_stage_code_gen = WrappedStageCodeGenerator(
    #         asset=node.wrapped_stage,
    #         master_gen=self.master_gen,
    #         wrapped_stage=node,
    #         parent_composer=self.composer,
    #         offline=self.offline,
    #     )
    #     return wrapped_stage_code_gen.generate_code()

    # def _generate_custom_stage_node(self, node: CustomStageStage):
    #     custom_stage_code_gen = CustomStageCodeGenerator(
    #         asset=node.custom_stage,
    #         master_gen=self.master_gen,
    #         custom_stage=node,
    #         parent_composer=self.composer,
    #         offline=self.offline,
    #     )
    #     return custom_stage_code_gen.generate_code()

    def _generate_model_stage(self, node: StageNode):
        stage_name = node.label
        configuration = node.configuration

        stage_label = LABEL_MAPPINGS[OP_MAPPINGS[configuration.op_name]]

        if stage_label == "Transformer":
            return self._generate_transformer_stage(node)
        if stage_label == "Complex Flat File":
            return self._generate_complex_flat_file_stage(node)
        if stage_label == "Rest":
            return self._generate_rest_stage(node)
        properties = {}
        for prop, value in configuration.model_fields.items():
            exclude = [
                "input_count",
                "output_count",
                "inputcol_properties",
                "outputcol_properties",
                "input_name",
                "output_name",
                "connection",
            ]
            if (
                str(getattr(configuration, prop)) != str(value.default)
                and prop not in exclude
                and not (hasattr(value.default, "value") and str(getattr(configuration, prop)) == str(value.default.value))
            ):
                if "enum" in str(value.annotation) or isinstance(value.default, Enum):
                    try:
                        enum_value = getattr(configuration, prop)
                        if isinstance(enum_value, Enum):
                            enum_stage = OP_MAPPINGS[configuration.op_name].upper().replace(" ", "_")
                            properties[prop] = f"{enum_stage}.{enum_value}"
                        else:
                            properties[prop] = enum_value
                    except Exception:
                        properties[prop] = repr(getattr(configuration, prop))
                else:
                    if prop == "lookup_derivation":
                        properties[prop] = repr(getattr(configuration, prop)).replace("LookupDerivation", "lookup.LookupDerivation")
                    else:
                        properties[prop] = repr(getattr(configuration, prop))
        use_conn = None
        if hasattr(configuration, "connection") and configuration.connection is not None and not isinstance(configuration.connection, str):
            use_conn = self.master_gen.get_object_var(configuration.connection)
        if hasattr(configuration, "java_library") and configuration.java_library is not None:
            properties["java_library"] = self.master_gen.get_object_var(configuration.java_library)

        comments = []
        # for parent in node.metadata["parents"]:
        #     if isinstance(parent, StyledComment) or isinstance(parent, MarkdownComment):
        #         comments.append(self.master_gen.get_object_var(parent))

        var_name = self.master_gen.reserve_var(stage_name, node)

        return self.templates.stage_template.render(
            var_name=var_name,
            stage_name=repr(stage_name),
            stage_label=repr(stage_label),
            properties=properties,
            composer=self.composer,
            comments=comments,
            use_conn=use_conn,
        )

    def _generate_transformer_stage(self, node: StageNode):
        stage_name = node.label
        model = node.configuration
        properties = {}
        loop_variables, stage_variables, triggers, constraints = None, None, None, None

        type_mapping = {
            "WCHAR": "NCHAR",
            "WVARCHAR": "NVARCHAR",
            "WLONGVARCHAR": "LONGNVARCHAR",
        }

        for prop, value in model.model_fields.items():
            exclude = [
                "input_count",
                "output_count",
                "inputcol_properties",
                "outputcol_properties",
                "input_name",
                "output_name",
                "connection",
            ]
            if (
                str(getattr(model, prop)) != str(value.default)
                and prop not in exclude
                and not (hasattr(value.default, "value") and str(getattr(model, prop)) == str(value.default.value))
            ):
                if "enum" in str(value.annotation) or isinstance(value.default, Enum):
                    try:
                        enum_stage = LABEL_MAPPINGS[OP_MAPPINGS[model.op_name]].upper()
                        properties[prop] = f"{enum_stage}.{getattr(model, prop)}"
                    except Exception:
                        properties[prop] = repr(getattr(model, prop))
                elif prop == "loop_variables":
                    loop_variables = [
                        loop_var.model_dump(by_alias=False, exclude_none=True, exclude_defaults=True) for loop_var in getattr(model, prop)
                    ]
                    for loop_var in loop_variables:
                        if "sql_type" in loop_var:
                            loop_var["sql_type"] = f"transformer.SqlType.{loop_var['sql_type']}"
                    loop_variables = [
                        {key: repr(value) if key not in ["sql_type"] else value for key, value in loop_var.items()}
                        for loop_var in loop_variables
                    ]

                elif prop == "stage_variables":
                    stage_variables = [
                        stage_var.model_dump(by_alias=False, exclude_none=True, exclude_defaults=True) for stage_var in getattr(model, prop)
                    ]
                    for stage_var in stage_variables:
                        if "sql_type" in stage_var:
                            sql_type = type_mapping.get(stage_var["sql_type"], stage_var["sql_type"])
                            stage_var["sql_type"] = f"transformer.SqlType.{sql_type}"
                    stage_variables = [
                        {key: repr(value) if key not in ["sql_type"] else value for key, value in stage_var.items()}
                        for stage_var in stage_variables
                    ]

                elif prop == "triggers":
                    triggers = [
                        trigger.model_dump(by_alias=False, exclude_none=True, exclude_defaults=True) for trigger in getattr(model, prop)
                    ]
                    for trigger in triggers:
                        if "before_after" in trigger:
                            trigger["before_after"] = (
                                "transformer.BeforeAfter.before"
                                if "before" in trigger["before_after"].lower()
                                else "transformer.BeforeAfter.after"
                            )
                        if "arguments" in trigger:
                            trigger["arguments"] = [value for value in trigger["arguments"].values()]
                    triggers = [
                        {key: repr(value) if key not in ["before_after"] else value for key, value in trigger.items()}
                        for trigger in triggers
                    ]
                elif prop == "transformer_constraint":
                    constraints = [
                        constraint.model_dump(by_alias=False, exclude_none=True, exclude_defaults=True)
                        for constraint in getattr(model, prop)
                    ]
                    constraints = [
                        {key: repr(value) if key not in [] else value for key, value in constraint.items()} for constraint in constraints
                    ]
                elif prop == "value_derivation":
                    continue
                else:
                    properties[prop] = repr(getattr(model, prop))

        var_name = self.master_gen.reserve_var(stage_name, node)
        return self.templates.transformer_stage_template.render(
            var_name=var_name,
            stage_name=repr(stage_name),
            composer=self.composer,
            properties=properties,
            loop_variables=loop_variables,
            stage_variables=stage_variables,
            triggers=triggers,
            constraints=constraints,
        ).strip()

    def _generate_complex_flat_file_stage(self, node: StageNode):
        stage_name = node.label
        model = node.configuration
        properties = {}
        records, records_id, output_columns, constraints = None, None, None, None
        for prop, value in model.model_fields.items():
            exclude = [
                "input_count",
                "output_count",
                "inputcol_properties",
                "outputcol_properties",
                "input_name",
                "output_name",
                "connection",
            ]
            if (
                str(getattr(model, prop)) != str(value.default)
                and prop not in exclude
                and not (hasattr(value.default, "value") and str(getattr(model, prop)) == str(value.default.value))
            ):
                if "enum" in str(value.annotation) or isinstance(value.default, Enum):
                    try:
                        enum_stage = LABEL_MAPPINGS[OP_MAPPINGS[model.op_name]].upper()
                        properties[prop] = f"{enum_stage}.{getattr(model, prop)}"
                    except Exception:
                        properties[prop] = repr(getattr(model, prop))
                elif prop == "records":
                    records = []
                    for record in getattr(model, prop):
                        columns = []
                        for column in record.columns:
                            column_data = {}
                            for col_prop, col_val in column.model_fields.items():
                                if getattr(column, col_prop) == col_val.default or getattr(column, col_prop) is None:
                                    continue
                                elif isinstance(getattr(column, col_prop), Enum):
                                    column_data[col_prop] = f"complex_flat_file.{getattr(column, col_prop)}"
                                else:
                                    column_data[col_prop] = repr(getattr(column, col_prop))
                            columns.append(column_data)
                        records.append({"name": repr(record.name), "columns": columns})
                elif prop == "records_id":
                    records_id = [
                        record_id.model_dump(
                            exclude={"schema_ref"},
                            by_alias=False,
                            exclude_none=True,
                            exclude_unset=True,
                        )
                        for record_id in getattr(model, prop)
                    ]
                    records_id = [{key: repr(value) for key, value in record_id.items()} for record_id in records_id]
                elif prop == "output_columns":
                    output_columns = [output_column.model_dump(by_alias=False, exclude_none=True) for output_column in getattr(model, prop)]
                    output_columns = [{key: repr(value) for key, value in output_column.items()} for output_column in output_columns]
                elif prop == "constraint":
                    constraints = [
                        constraint.model_dump(by_alias=False, exclude_none=True, exclude_defaults=True)
                        for constraint in getattr(model, prop)
                    ]
                    constraints = [{key: repr(value) for key, value in constraint.items()} for constraint in constraints]
                else:
                    properties[prop] = repr(getattr(model, prop))

        var_name = self.master_gen.reserve_var(stage_name, node)
        return self.templates.complex_flat_file_stage_template.render(
            var_name=var_name,
            composer=self.composer,
            stage_name=repr(stage_name),
            properties=properties,
            records=records,
            records_id=records_id,
            output_columns=output_columns,
            constraints=constraints,
        )

    def _generate_rest_stage(self, node: StageNode):
        stage_name = node.label
        model = node.configuration
        properties = {}
        requests, variables = None, None
        for prop, value in model.model_fields.items():
            exclude = [
                "input_count",
                "output_count",
                "inputcol_properties",
                "outputcol_properties",
                "input_name",
                "output_name",
                "connection",
            ]
            if (
                str(getattr(model, prop)) != str(value.default)
                and prop not in exclude
                and not (hasattr(value.default, "value") and str(getattr(model, prop)) == str(value.default.value))
            ):
                if "enum" in str(value.annotation) or isinstance(value.default, Enum):
                    try:
                        enum_stage = LABEL_MAPPINGS[OP_MAPPINGS[model.op_name]].upper()
                        properties[prop] = f"{enum_stage}.{getattr(model, prop)}"
                    except Exception:
                        properties[prop] = repr(getattr(model, prop))
                elif prop == "requests":
                    requests = []
                    for request in getattr(model, prop):
                        assert isinstance(request, Request)
                        request_dict = {}
                        if request.authentication:
                            if request.authentication.same_config:
                                request_dict["authentication"] = {"same_config": True}
                            else:
                                auth_props = {}
                                for auth_key in request.authentication.model_fields:
                                    auth_val = getattr(request.authentication, auth_key)
                                    if auth_val is None or auth_val == "":
                                        continue
                                    if isinstance(auth_val, Enum):
                                        auth_props[auth_key] = f"rest.{auth_val}"
                                    elif isinstance(auth_val, str):
                                        auth_props[auth_key] = repr(auth_val.strip("`"))
                                    else:
                                        auth_props[auth_key] = repr(auth_val)
                                request_dict["authentication"] = auth_props
                        if request.request:
                            if request.request.same_config:
                                request_dict["request"] = {"properties": {"same_config": True}}
                            else:
                                request_info = {}
                                request_properties = {}
                                for req_key in request.request.model_fields:
                                    req_val = getattr(request.request, req_key)
                                    if req_key == "query_parameters":
                                        query_params = []
                                        for param in req_val:
                                            parameter = {}
                                            for item in param.model_fields:
                                                if getattr(param, item) is not None and getattr(param, item) != "":
                                                    parameter[item] = repr(getattr(param, item))
                                            query_params.append(parameter)
                                        request_info["query_parameters"] = query_params
                                    elif req_key == "custom_headers":
                                        headers = []
                                        for head in req_val:
                                            header = {}
                                            for item in head.model_fields:
                                                if getattr(head, item) is not None and getattr(head, item) != "":
                                                    header[item] = repr(getattr(head, item))
                                            headers.append(header)
                                        request_info["custom_headers"] = headers
                                    elif req_key == "custom_cookies":
                                        cookies = []
                                        for cook in req_val:
                                            cookie = {}
                                            for item in cook.model_fields:
                                                if getattr(cook, item) is not None and getattr(cook, item) != "":
                                                    cookie[item] = repr(getattr(cook, item))
                                            cookies.append(cookie)
                                        request_info["custom_cookies"] = cookies
                                    elif req_key == "body":
                                        assert isinstance(req_val, Body)
                                        body_dict = {}
                                        type = req_val.type.value if hasattr(req_val.type, "value") else req_val.type
                                        if type == "FORM_DATA":
                                            if req_val.form_data:
                                                form_datas = []
                                                for form_data in req_val.form_data:
                                                    form_data_dict = {}
                                                    for item in form_data.model_fields:
                                                        if getattr(form_data, item) is not None and getattr(form_data, item) != "":
                                                            form_data_dict[item] = repr(getattr(form_data, item))
                                                    form_datas.append(form_data_dict)
                                                body_dict["form_data"] = form_datas
                                        if type == "X_WWW_FORM_URLENCODED":
                                            if req_val.form_urlencoded_data:
                                                form_datas = []
                                                for form_data in req_val.form_urlencoded_data:
                                                    form_data_dict = {}
                                                    for item in form_data.model_fields:
                                                        if getattr(form_data, item) is not None and getattr(form_data, item) != "":
                                                            form_data_dict[item] = repr(getattr(form_data, item))
                                                    form_datas.append(form_data_dict)
                                                body_dict["form_urlencoded_data"] = form_datas
                                        body_props = {}
                                        for item in req_val.model_fields:
                                            if item in [
                                                "form_data",
                                                "form_urlencoded_data",
                                            ]:
                                                continue
                                            if getattr(req_val, item) is None or getattr(req_val, item) == "":
                                                continue
                                            if isinstance(getattr(req_val, item), Enum):
                                                body_props[item] = f"rest.{getattr(req_val, item)}"
                                            elif isinstance(getattr(req_val, item), str):
                                                body_props[item] = repr(getattr(req_val, item).strip("`"))
                                            else:
                                                body_props[item] = repr(getattr(req_val, item))
                                        body_dict["properties"] = body_props

                                        request_info["body"] = body_dict
                                    else:
                                        if req_val is None or req_val == "":
                                            continue
                                        if isinstance(req_val, Enum):
                                            request_properties[req_key] = f"rest.{req_val}"
                                        elif isinstance(req_val, str):
                                            request_properties[req_key] = repr(req_val.strip("`"))
                                        else:
                                            request_properties[req_key] = repr(req_val)
                                request_info["properties"] = request_properties
                                request_dict["request"] = request_info
                        if request.response:
                            if request.response.same_config:
                                request_dict["response"] = {"same_config": True}
                            else:
                                response_dict = {}
                                for response_key in request.response.model_fields:
                                    response_val = getattr(request.response, response_key)
                                    if response_val is None or response_val == "":
                                        continue
                                    if isinstance(response_val, Enum):
                                        response_dict[response_key] = f"rest.{response_val}"
                                    elif isinstance(response_val, str):
                                        response_dict[response_key] = repr(response_val.strip("`"))
                                    else:
                                        response_dict[response_key] = repr(response_val)
                                request_dict["response"] = response_dict
                        if request.settings:
                            if request.settings.same_config:
                                request_dict["settings"] = {"properties": {"same_config": True}}
                            else:
                                settings_dict = {}
                                settings_props = {}
                                for settings_key in request.settings.model_fields:
                                    settings_val = getattr(request.settings, settings_key)
                                    if settings_val is None or settings_val == "":
                                        continue
                                    if settings_key == "server_certificate":
                                        server_cert_props = {}
                                        assert isinstance(settings_val, ServerCertificate)
                                        for server_key in settings_val.model_fields:
                                            server_val = getattr(settings_val, server_key)
                                            if server_val is None or server_val == "":
                                                continue
                                            if isinstance(server_val, Enum):
                                                server_cert_props[server_key] = f"rest.{server_val}"
                                            elif isinstance(server_val, str):
                                                server_cert_props[server_key] = repr(server_val.strip("`"))
                                            else:
                                                server_cert_props[server_key] = repr(server_val)
                                        settings_dict["server_certificate"] = server_cert_props
                                    elif settings_key == "client_certificate":
                                        client_cert_props = {}
                                        assert isinstance(settings_val, ClientCertificate)
                                        for client_key in settings_val.model_fields:
                                            client_val = getattr(settings_val, client_key)
                                            if client_val is None or client_val == "":
                                                continue
                                            if isinstance(client_val, Enum):
                                                client_cert_props[client_key] = f"rest.{client_val}"
                                            elif isinstance(client_val, str):
                                                client_cert_props[client_key] = repr(client_val.strip("`"))
                                            else:
                                                client_cert_props[client_key] = repr(client_val)
                                        settings_dict["client_certificate"] = client_cert_props
                                    elif settings_key == "proxy":
                                        proxy_props = {}
                                        assert isinstance(settings_val, Proxy)
                                        for proxy_key in settings_val.model_fields:
                                            proxy_val = getattr(settings_val, proxy_key)
                                            if proxy_val is None or proxy_val == "":
                                                continue
                                            if isinstance(proxy_val, Enum):
                                                proxy_props[proxy_key] = f"rest.{proxy_val}"
                                            elif isinstance(proxy_val, str):
                                                proxy_props[proxy_key] = repr(proxy_val.strip("`"))
                                            else:
                                                proxy_props[proxy_key] = repr(proxy_val)
                                        if len(proxy_props):
                                            settings_dict["proxy"] = proxy_props
                                    elif isinstance(settings_val, Enum):
                                        settings_props[settings_key] = f"rest.{settings_val}"
                                    elif isinstance(settings_val, str):
                                        settings_props[settings_key] = repr(settings_val.strip("`"))
                                    else:
                                        settings_props[settings_key] = repr(settings_val)
                                settings_dict["properties"] = settings_props
                                request_dict["settings"] = settings_dict
                        if request.control:
                            if request.control.same_config:
                                request_dict["control"] = {"same_config": True}
                            else:
                                control_dict = {}
                                for control_key in request.control.model_fields:
                                    control_val = getattr(request.control, control_key)
                                    if control_val is None or control_val == "":
                                        continue
                                    if isinstance(control_val, Enum):
                                        control_dict[control_key] = f"rest.{control_val}"
                                    elif isinstance(control_val, str):
                                        control_dict[control_key] = repr(control_val.strip("`"))
                                    else:
                                        control_dict[control_key] = repr(control_val)
                                request_dict["control"] = control_dict
                        request_dict["properties"] = {}
                        if request.method:
                            request_dict["properties"]["method"] = f"rest.{request.method}"
                        if request.url:
                            request_dict["properties"]["url"] = repr(request.url.strip("`"))
                        if request.use_expression_url:
                            request_dict["properties"]["use_expression_url"] = repr(request.use_expression_url)
                        requests.append(request_dict)
                elif prop == "variables":
                    variables = []
                    for var in getattr(model, prop):
                        assert isinstance(var, Variable)
                        var_dict = {}
                        for var_key in var.model_fields:
                            var_val = getattr(var, var_key)
                            if var_val is None or var_val == "":
                                continue
                            if isinstance(var_val, Enum):
                                var_dict[var_key] = f"rest.{var_val}"
                            elif isinstance(var_val, str):
                                var_dict[var_key] = repr(var_val.strip("`"))
                            else:
                                var_dict[var_key] = repr(var_val)
                        variables.append(var_dict)
                else:
                    properties[prop] = repr(getattr(model, prop))

        var_name = self.master_gen.reserve_var(stage_name, node)
        return self.templates.rest_template.render(
            var_name=var_name,
            composer=self.composer,
            stage_name=repr(stage_name),
            properties=properties,
            requests=requests,
            variables=variables,
        )

    def _generate_connection(self, connection: Any):
        if hasattr(connection, "asset_id") and connection.asset_id is not None:
            conn_id = connection.asset_id
            imported = True
        else:
            conn_id = None
            imported = False

        if connection.datasource_type in DATASOURCE_MAPPINGS:
            op_conn_internal_name = CONN_MAPPINGS[DATASOURCE_MAPPINGS[connection.datasource_type]]
        elif connection.datasource_type in CONN_MAPPINGS:
            op_conn_internal_name = CONN_MAPPINGS[connection.datasource_type]
        if op_conn_internal_name and op_conn_internal_name in CONN_UNIFIED_MAPPINGS:
            unified_datasource_type = CONN_UNIFIED_MAPPINGS[op_conn_internal_name]["datasource_type"]
        op_conn_name = "".join([word[0].upper() + word[1:] for word in op_conn_internal_name.split("_")])
        properties = {}

        if not imported:
            for prop, value in connection.model_fields.items():
                if getattr(connection, prop) != value.default and prop != "name":
                    prop_value = getattr(connection, prop)
                    if "dsmenc" in prop_value or "iisenc" in prop_value:
                        properties[prop] = repr(f"<TODO: insert your {prop}>")
                    else:
                        properties[prop] = repr(f"{prop_value}")

        if id(connection) in self.master_gen.obj_var_mapping:
            var_name = self.master_gen.get_object_var(connection)
        else:
            if connection.name is None:
                connection.name = op_conn_internal_name
            var_name = self.master_gen.reserve_var(connection.name, connection)

        return self.templates.connection_template.render(
            var_name=var_name,
            imported=imported,
            conn_name=repr(connection.name),
            conn_id=conn_id,
            op_conn_name=op_conn_name,
            properties=properties,
            offline=self.offline,
            datasource_type=unified_datasource_type,
        )

    def _generate_java_library(self, java_library: Any):
        if hasattr(java_library, "asset_id") and java_library.asset_id is not None:
            jl_id = java_library.asset_id
            imported = True
        else:
            jl_id = None
            imported = False

        var_name = self.master_gen.reserve_var(java_library.name, java_library)

        return self.templates.java_library_template.render(
            var_name=var_name,
            imported=imported,
            java_library_name=java_library.name,
            asset_id=jl_id,
            primary_file=java_library.primary_file,
            secondary_files=java_library.secondary_files,
            offline=self.offline,
        )

    def _generate_schema(self, schema: Schema, desired_var_name: str):
        fields = _get_field_template_items(schema.fields)
        var_name = self.master_gen.reserve_var(desired_var_name, schema)

        for field in fields:
            field["type"] = field["type"].upper()

        if len(fields) > 100:
            fields = list(_split_list(fields, 50))
            return var_name, self.templates.schema_overflow_template.render(fields=fields, var_name=var_name)

        return var_name, self.templates.schema_template.render(fields=fields, var_name=var_name)


# class ParamSetCodeGenerator:
#     def __init__(self, param_set: ParameterSet, master_gen: MasterCodeGenerator = None):
#         self.param_set = param_set
#         self.master_gen = master_gen or MasterCodeGenerator()

#     def generate_code(self):
#         parameters = []
#         for param in self.param_set.parameters:
#             param_dict = {}
#             param_dict["name"] = param.name
#             param_dict["value"] = repr(param.value)
#             param_dict["extras"] = ""
#             if param.description:
#                 param_dict["extras"] += f", description = {repr(param.description)}"
#             if param.prompt:
#                 param_dict["extras"] += f", prompt = {repr(param.prompt)}"
#             if param.type == "multilinestring":
#                 param_dict["type"] = "MultilineString"
#             elif param.type == "enum":
#                 param_dict["type"] = "List"
#             else:
#                 param_dict["type"] = param.type[0].upper() + param.type[1:]
#             if param.type == "list" or param.type == "enum":
#                 param_dict["valid_values"] = param.valid_values
#             parameters.append(param_dict)

#         var_name = self.master_gen.reserve_var(self.param_set.name, self.param_set)
#         self.master_gen.param_set_objs[self.param_set.name] = id(self.param_set)

#         for value_set in self.param_set.value_sets:
#             for value in value_set.values:
#                 value.value = repr(value.value)

#         if len(parameters) > 100 or len(self.param_set.value_sets) > 100:
#             parameters = list(_split_list(parameters, 50))
#             value_sets = list(_split_list(self.param_set.value_sets, 50))
#             value_set_overflow = len(self.param_set.value_sets) > 100
#             return self.master_gen.templates.paramset_overflow_template.render(
#                 var_name=var_name,
#                 paramset_name=self.param_set.name,
#                 parameters=parameters,
#                 value_sets=value_sets,
#                 asset_id=None,
#                 imported=False,
#                 description=repr(self.param_set.description),
#                 value_set_overflow=value_set_overflow,
#             )

#         return self.master_gen.templates.paramset_template.render(
#             var_name=var_name,
#             paramset_name=self.param_set.name,
#             parameters=parameters,
#             value_sets=self.param_set.value_sets,
#             asset_id=None,
#             imported=False,
#             description=repr(self.param_set.description),
#         )

#     def get_imports(self):
#         return "from ibm.datastage import *"


class ConnectionCodeGenerator:
    def __init__(self, connection: pydantic.BaseModel, master_gen: MasterCodeGenerator):
        self.connection = connection
        self.master_gen = master_gen
        self.used_parameter_sets = []

    def generate_code(self):
        conn_name = self.connection.name
        op_conn_name = CONN_MAPPINGS[DATASOURCE_MAPPINGS[self.connection.datasource_type]].split("_")
        op_conn_name = [word[0].upper() + word[1:] for word in op_conn_name]
        op_conn_name = "".join(op_conn_name)
        properties = {}
        for prop, value in self.connection.model_fields.items():
            exclude = []
            if str(getattr(self.connection, prop)) != str(value.default) and prop not in exclude:
                # if "#" in str(getattr(self.connection, prop)) and self.master_gen.get_params(str(getattr(self.connection, prop))):
                #     params = self.master_gen.get_params(str(getattr(self.connection, prop)))
                #     original = repr(str(getattr(self.connection, prop)))
                #     original = original.replace("{iisenc}", "{{iisenc}}")
                #     for param in params:
                #         if "." in param:
                #             paramset_props = param.split(".")
                #             if paramset_props[0] in self.master_gen.param_set_objs:
                #                 ps_obj = self.master_gen.param_set_objs[paramset_props[0]]
                #                 ps_var_name = self.master_gen.obj_var_mapping[ps_obj]
                #                 original = original.replace(f"#{param}#", f'{{{ps_var_name}["{paramset_props[-1]}"]}}')
                #         else:
                #             if self.master_gen.local_param_var:
                #                 if param in self.master_gen.local_params:
                #                     original = original.replace(f"#{param}#", f'{{{self.master_gen.local_param_var}["{param}"]}}')
                #     properties[prop] = f"f{original}"
                if "enum" in str(value.annotation) or isinstance(value.default, Enum):
                    try:
                        enum = type(value.default)(getattr(self.connection, prop))
                        enum_stage = CONN_MAPPINGS[DATASOURCE_MAPPINGS[self.connection.datasource_type]].upper() + "_CONNECTION"
                        enum_name = enum.__class__.__name__
                        properties[prop] = f"{enum_stage}.{enum_name}.{enum.name}"
                    except Exception:
                        properties[prop] = f'"{getattr(self.connection, prop)}"'
                elif "str" in str(value.annotation):
                    val = getattr(self.connection, prop).replace("'", "\\'").replace('"', '\\"')
                    if "\n" in getattr(self.connection, prop):
                        properties[prop] = f'"""{val}"""'
                    else:
                        properties[prop] = f'"{val}"'
                else:
                    if getattr(self.connection, prop) == "false":
                        properties[prop] = False
                    elif getattr(self.connection, prop) == "true":
                        properties[prop] = True
                    elif isinstance(getattr(self.connection, prop), int):
                        properties[prop] = f"{getattr(self.connection, prop)}"
                    else:
                        properties[prop] = f'"{getattr(self.connection, prop)}"'
        var_name = self.master_gen.reserve_var(conn_name, self.connection)

        return self.master_gen.templates.connection_template.render(
            properties=properties,
            var_name=var_name,
            op_conn_name=op_conn_name,
            conn_name=conn_name,
        )

    def get_imports(self):
        imports = []
        imports.append("from ibm.datastage import *")
        for paramset in self.used_parameter_sets:
            imports.append(f"from parameter_set.{paramset} import *")

        return "\n".join(imports)


# class DataDefinitionCodeGenerator:
#     def __init__(
#         self,
#         data_definition: DataDefinition,
#         master_gen: MasterCodeGenerator = None,
#         asset_id: str = None,
#         imported: bool = False,
#         offline: bool = False,
#     ):
#         self.data_definition = data_definition
#         self.master_gen = master_gen or MasterCodeGenerator()
#         self.asset_id = asset_id
#         self.imported = imported
#         self.offline = offline

#     def generate_code(self):
#         dd_name = self.data_definition.name
#         self.data_definition.select_fields([col.name for col in self.data_definition.columns])
#         fields = _get_field_template_items(self.data_definition._get_fields())

#         for field in fields:
#             field["type"] = field["type"].upper()

#         var_name = self.master_gen.reserve_var(dd_name, self.data_definition)

#         extended_prop_items = self._get_extended_prop_items()

#         return self.master_gen.templates.data_definition_template.render(
#             var_name=var_name,
#             data_definition_name=self.data_definition.name,
#             asset_id=self.asset_id,
#             fields=fields,
#             extended_prop_items=extended_prop_items,
#             imported=self.imported,
#             offline=self.offline,
#         )

#     def get_imports(self):
#         return "from ibm.datastage import *"

#     def _get_extended_prop_items(self):
#         prop_to_class = {
#             "record_level_fill_char": FIELD.Fill,
#             "record_level_final_delimiter": FIELD.FinalDelim,
#             "record_level_final_delimiter_string": str,
#             "record_level_intact": str,
#             "record_level_check_intact": bool,
#             "record_level_record_delimiter": FIELD.RecordDelim,
#             "record_level_record_delimiter_string": str,
#             "record_level_record_length": FIELD.RecordLength,
#             "record_level_record_prefix": FIELD.RecordPrefix,
#             "record_level_record_type": FIELD.Format,
#             "field_defaults_actual_field_length": int,
#             "field_defaults_delimiter": FIELD.Delim,
#             "field_defaults_delimiter_string": str,
#             "field_defaults_null_field_length": int,
#             "field_defaults_null_field_value": str,
#             "field_defaults_null_field_value_separator": FIELD.ValueSeparator,
#             "field_defaults_prefix_bytes": FIELD.Prefix,
#             "field_defaults_print_field": bool,
#             "field_defaults_quote": FIELD.Quote,
#             "field_defaults_vector_prefix": FIELD.VectorPrefix,
#             "general_byte_order": FIELD.ByteOrder,
#             "general_char_set": FIELD.CharSet,
#             "general_data_format": FIELD.DataFormat,
#             "general_max_width": int,
#             "general_pad_char": FIELD.PadChar,
#             "general_width": int,
#             "string_export_ebcdic_as_ascii": bool,
#             "string_import_ascii_as_ebcdic": bool,
#             "decimal_allow_all_zeros": bool,
#             "decimal_separator": FIELD.DecimalSeparator,
#             "decimal_packed": FIELD.DecimalPacked,
#             "decimal_sign_position": FIELD.SignPosition,
#             "decimal_packed_signed": bool,
#             "decimal_precision": int,
#             "decimal_rounding": FIELD.Round,
#             "decimal_scale": int,
#             "numeric_c_format": str,
#             "numeric_in_format": str,
#             "numeric_out_format": str,
#             "date_days_since": int,
#             "date_format_string": str,
#             "date_is_julian": bool,
#             "time_format_string": str,
#             "time_midnight_seconds": bool,
#             "timestamp_format_string": str,
#         }
#         dd_props = sorted(list(prop_to_class.keys()))
#         items = []
#         for prop in dd_props:
#             prop_class = prop_to_class[prop]
#             prop_value = getattr(self.data_definition, prop)
#             if prop_value is None:
#                 continue
#             if isinstance(prop_class, bool) or isinstance(prop_class, int):
#                 items.append(f".set_{prop}({prop_value})")
#             elif isinstance(prop_class, str):
#                 items.append(f'.set_{prop}("{prop_value}")')
#             elif prop == "general_pad_char" and prop_value == 32:
#                 items.append(f".set_{prop}(FIELD.PadChar.space)")
#             elif issubclass(prop_class, Enum):
#                 items.append(f".set_{prop}(FIELD.{prop_class.__name__}.{prop_class(prop_value).name})")

#         return items


# class MessageHandlerCodeGenerator:
#     def __init__(
#         self,
#         message_handler: MessageHandler,
#         master_gen: MasterCodeGenerator = None,
#         asset_id: str = None,
#         imported: bool = False,
#         offline: bool = False,
#     ):
#         self.message_handler = message_handler
#         self.master_gen = master_gen or MasterCodeGenerator()
#         self.asset_id = asset_id
#         self.imported = imported
#         self.offline = offline

#     def generate_code(self):
#         messages = []
#         if not self.imported:
#             for message in self.message_handler.messages:
#                 message_dict = {}
#                 message_dict["id"] = message.id
#                 message_dict["action"] = repr(message.action)
#                 message_dict["description"] = repr(message.description)
#                 messages.append(message_dict)

#         var_name = self.master_gen.reserve_var(self.message_handler.name, self.message_handler)

#         return self.master_gen.templates.message_handler_template.render(
#             var_name=var_name,
#             message_handler_name=self.message_handler.name,
#             messages=messages,
#             asset_id=self.asset_id,
#             imported=self.imported,
#             offline=self.offline,
#             description=self.message_handler.description,
#         )

#     def get_imports(self):
#         return "from ibm.datastage import *"


# class JavaLibraryCodeGenerator:
#     def __init__(
#         self,
#         java_library: JavaLibrary,
#         output_path: str,
#         master_gen: MasterCodeGenerator = None,
#     ):
#         self.java_library = java_library
#         self.master_gen = master_gen or MasterCodeGenerator()
#         self.output_path = Path(output_path)

#     def generate_code(self):
#         var_name = self.master_gen.reserve_var(self.java_library.name, self.java_library)

#         return self.master_gen.templates.java_library_template.render(
#             var_name=var_name,
#             java_library_name=self.java_library.name,
#             primary_file=self.java_library.primary_file,
#             secondary_files=self.java_library.secondary_files,
#             asset_id=None,
#             imported=False,
#             description=self.java_library.description,
#             output_path=self.output_path,
#         )

#     def get_imports(self):
#         return "from ibm.datastage import *"


# class TestCaseCodeGenerator:
#     def __init__(
#         self,
#         test_case_composer: TestCaseComposer,
#         master_gen: MasterCodeGenerator = None,
#     ):
#         self.test_case_composer = test_case_composer
#         self.master_gen = master_gen or MasterCodeGenerator()

#     def generate_code(self):
#         return self.master_gen.templates.test_case_template.render(
#             test_case_name=self.test_case_composer.name,
#             test_case_description=self.test_case_composer.description,
#             test_case_flow_name=self.test_case_composer.flow_name,
#             test_case_flow_id=self.test_case_composer.flow_id,
#             input_test_data=self.test_case_composer.input_test_data_files,
#             output_test_data=self.test_case_composer.output_test_data_files,
#             capture_data=self.test_case_composer.capture_data,
#             parameters=self.test_case_composer.parameters,
#             additional_properties=self.test_case_composer.additional_properties,
#             asset_id=None,
#             imported=False,
#         )

#     def get_imports(self):
#         return "from ibm.datastage import *"


# class JobSettingsCodeGenerator:
#     def __init__(self, job_settings: JobSettings, master_gen: MasterCodeGenerator):
#         self.job_settings = job_settings
#         self.master_gen = master_gen

#     def generate_code(self):
#         schedule = self.job_settings.schedule
#         if schedule:
#             schedule.start = (
#                 str(datetime.datetime.fromtimestamp(schedule.start / 1000)).replace(":", "-") if (schedule.start) else schedule.start
#             )
#             schedule.end = str(datetime.datetime.fromtimestamp(schedule.end / 1000)).replace(":", "-") if (schedule.end) else schedule.end
#         runtime_parameters = None
#         if (
#             self.job_settings.runtime_parameters
#             and self.job_settings.runtime_parameters.value_sets
#             and len(self.job_settings.runtime_parameters.value_sets) > 0
#         ):
#             runtime_parameters = self.job_settings.runtime_parameters

#         var_name = self.master_gen.reserve_var("job_settings", self.job_settings)

#         return self.master_gen.templates.job_settings_template.render(
#             schedule=schedule, runtime_parameters=runtime_parameters, var_name=var_name
#         )

#     def get_imports(self):
#         return "from ibm.datastage import *"


# class FunctionLibraryCodeGenerator:
#     def __init__(
#         self,
#         function_library: FunctionLibrary,
#         output_path: str,
#         master_gen: MasterCodeGenerator = None,
#     ):
#         self.function_library = function_library
#         self.master_gen = master_gen or MasterCodeGenerator()
#         self.output_path = Path(output_path)

#     def generate_code(self):
#         var_name = self.master_gen.reserve_var(self.function_library.name, self.function_library)

#         return self.master_gen.templates.function_library_template.render(
#             var_name=var_name,
#             function_library_name=self.function_library.name,
#             library_path=self.function_library.library_path,
#             asset_id=None,
#             imported=False,
#             description=self.function_library.description,
#             output_path=self.output_path,
#         )

#     def get_imports(self):
#         return "from ibm.datastage import *"


# class BuildStageCodeGenerator:
#     def __init__(
#         self,
#         asset: BuildStage | str = None,
#         master_gen: MasterCodeGenerator = None,
#         build_stage: BuildStageStage = None,
#         parent_composer: str = "fc",
#         offline: bool = False,
#     ):
#         self.build_stage = build_stage
#         self.asset = asset
#         self.master_gen = master_gen
#         self.parent_composer = parent_composer
#         self.offline = offline

#     def generate_code(self):
#         asset = bool(self.asset) and isinstance(self.asset, BuildStage)
#         stage = bool(self.build_stage)

#         asset_id = None
#         imported = False

#         if asset:
#             imported = True if self.asset.asset_id is not None else False
#             asset_id = self.asset.asset_id if imported else None

#             if not imported:
#                 props = self.asset.model_dump(
#                     include={
#                         "name",
#                         "short_description",
#                         "long_description",
#                         "show_on_palette",
#                         "operator",
#                         "execution_mode",
#                         "pre_loop",
#                         "post_loop",
#                         "per_record",
#                     },
#                     by_alias=False,
#                     exclude_none=True,
#                 )

#                 for key, val in props.items():
#                     if not isinstance(val, Enum):
#                         props[key] = repr(val)
#                     else:
#                         props[key] = f"BUILDSTAGE.{val}"

#                 properties = [] if len(self.asset.properties) else None
#                 for prop in self.asset.properties:
#                     prop_data = {}
#                     type_ = prop.data_type.lower()
#                     prop_data["type"] = (type_[0].upper() + type_[1:]).replace("column", "Column")
#                     # keep in mind field serializer
#                     prop_data["props"] = {}
#                     prop_dump = prop.model_dump(exclude={"data_type"}, exclude_none=True, by_alias=False)
#                     for key, val in prop_dump.items():
#                         if val == "":
#                             continue
#                         if key == "required":
#                             val = True if val == "Yes" else False
#                         if key == "hidden_property":
#                             val = True if val.lower() == "true" else False
#                         if key == "list_values":
#                             val = val.replace("[", "").replace("]", "").replace('"', "").split(",")
#                         if not isinstance(val, Enum):
#                             prop_data["props"][key] = repr(val)
#                         else:
#                             prop_data["props"][key] = f"BUILDSTAGE.{val}"
#                     properties.append(prop_data)

#                 data_definitions = []

#                 default_precision = {
#                     "Time": 8,
#                     "Timestamp": 19,
#                 }

#                 data_def_vars = {}

#                 for input in self.asset.inputs:
#                     if input.data_definition:
#                         if input.data_definition.name in data_def_vars:
#                             continue
#                         var_name = self.master_gen.reserve_var(input.data_definition.name, input.data_definition)
#                         data_def = {
#                             "var_name": var_name,
#                             "name": repr(input.data_definition.name),
#                         }
#                         fields = []
#                         for field in input.data_definition.columns:
#                             field_dict = {}
#                             field_dict["type"] = field.app_data["odbc_type"].upper()
#                             field_dict["name"] = field.name
#                             field_properties = ""
#                             if field.nullable and callable(getattr(field, "nullable", None)):
#                                 field_properties += ".nullable()"
#                             if field.metadata.is_key and callable(getattr(field, "key", None)):
#                                 field_properties += ".key()"
#                             if field.metadata.source_field_id is not None and callable(getattr(field, "source", None)):
#                                 field_properties += f'.source("{field.metadata.source_field_id}")'
#                             if field.metadata.max_length is not None and callable(getattr(field, "length", None)):
#                                 field_properties += f".length({field.metadata.max_length})"
#                             if (
#                                 "is_unicode_string" in field.app_data
#                                 and field.app_data["is_unicode_string"]
#                                 and callable(getattr(field, "unicode", None))
#                             ):
#                                 field_properties += ".unicode()"
#                             if not field.metadata.is_signed and callable(getattr(field, "unsigned", None)):
#                                 field_properties += ".unsigned()"
#                             if field.metadata.decimal_precision is not None and callable(getattr(field, "precision", None)):
#                                 default_prec = default_precision[field_dict["type"]] if field_dict["type"] in default_precision else 100
#                                 if field.metadata.decimal_precision != default_prec:
#                                     field_properties += f".precision({field.metadata.decimal_precision})"
#                             if (
#                                 field.metadata.decimal_scale is not None
#                                 and field.metadata.decimal_scale > 0
#                                 and callable(getattr(field, "scale", None))
#                             ):
#                                 field_properties += f".scale({field.metadata.decimal_scale})"
#                             if "extended_type" in field.app_data and field.app_data["extended_type"] is not None:
#                                 if "timezone" in field.app_data["extended_type"] and callable(getattr(field, "timezone", None)):
#                                     field_properties += ".timezone()"
#                                 if "microseconds" in field.app_data["extended_type"] and callable(getattr(field, "microseconds", None)):
#                                     field_properties += ".microseconds()"
#                             if field_dict["type"] == "Timestamp":
#                                 field_properties += ".microseconds()"
#                             if (
#                                 "difference" in field.app_data
#                                 and field.app_data["difference"]
#                                 and callable(getattr(field, "difference", None))
#                             ):
#                                 field_properties += ".difference()"
#                             if (
#                                 "derivation" in field.app_data
#                                 and field.app_data["derivation"]
#                                 and callable(
#                                     getattr(
#                                         field,
#                                         "derivation",
#                                         field.app_data["derivation"],
#                                     )
#                                 )
#                             ):
#                                 field_properties += f".derivation({repr(field.app_data['derivation'])})"
#                             if (
#                                 "cluster_key_change" in field.app_data
#                                 and field.app_data["cluster_key_change"]
#                                 and callable(getattr(field, "cluster_key_change", None))
#                             ):
#                                 field_properties += ".cluster_key_change()"
#                             if (
#                                 "key_change" in field.app_data
#                                 and field.app_data["key_change"]
#                                 and callable(getattr(field, "key_change", None))
#                             ):
#                                 field_properties += ".key_change()"
#                             if (
#                                 "pivot_property" in field.app_data
#                                 and field.app_data["pivot_property"]
#                                 and callable(getattr(field, "pivot", None))
#                             ):
#                                 field_properties += f'.pivot("{field.app_data["pivot_property"]}")'
#                             if (
#                                 "change_code" in field.app_data
#                                 and field.app_data["change_code"]
#                                 and callable(getattr(field, "change_code", None))
#                             ):
#                                 field_properties += ".change_code()"

#                             field_dict["properties"] = field_properties
#                             fields.append(field_dict)
#                         data_def["fields"] = fields
#                         data_definitions.append(data_def)
#                         data_def_vars[input.data_definition.name] = var_name

#                 for output in self.asset.outputs:
#                     if output.data_definition:
#                         if output.data_definition.name in data_def_vars:
#                             continue
#                         var_name = self.master_gen.reserve_var(output.data_definition.name, output.data_definition)
#                         data_def = {
#                             "var_name": var_name,
#                             "name": repr(output.data_definition.name),
#                         }
#                         fields = []
#                         for field in output.data_definition.columns:
#                             field_dict = {}
#                             field_dict["type"] = field.app_data["odbc_type"].upper()
#                             field_dict["name"] = field.name
#                             field_properties = ""
#                             if field.nullable and callable(getattr(field, "nullable", None)):
#                                 field_properties += ".nullable()"
#                             if field.metadata.is_key and callable(getattr(field, "key", None)):
#                                 field_properties += ".key()"
#                             if field.metadata.source_field_id is not None and callable(getattr(field, "source", None)):
#                                 field_properties += f'.source("{field.metadata.source_field_id}")'
#                             if field.metadata.max_length is not None and callable(getattr(field, "length", None)):
#                                 field_properties += f".length({field.metadata.max_length})"
#                             if (
#                                 "is_unicode_string" in field.app_data
#                                 and field.app_data["is_unicode_string"]
#                                 and callable(getattr(field, "unicode", None))
#                             ):
#                                 field_properties += ".unicode()"
#                             if not field.metadata.is_signed and callable(getattr(field, "unsigned", None)):
#                                 field_properties += ".unsigned()"
#                             if field.metadata.decimal_precision is not None and callable(getattr(field, "precision", None)):
#                                 default_prec = default_precision[field_dict["type"]] if field_dict["type"] in default_precision else 100
#                                 if field.metadata.decimal_precision != default_prec:
#                                     field_properties += f".precision({field.metadata.decimal_precision})"
#                             if (
#                                 field.metadata.decimal_scale is not None
#                                 and field.metadata.decimal_scale > 0
#                                 and callable(getattr(field, "scale", None))
#                             ):
#                                 field_properties += f".scale({field.metadata.decimal_scale})"
#                             if "extended_type" in field.app_data and field.app_data["extended_type"] is not None:
#                                 if "timezone" in field.app_data["extended_type"] and callable(getattr(field, "timezone", None)):
#                                     field_properties += ".timezone()"
#                                 if "microseconds" in field.app_data["extended_type"] and callable(getattr(field, "microseconds", None)):
#                                     field_properties += ".microseconds()"
#                             if field_dict["type"] == "Timestamp":
#                                 field_properties += ".microseconds()"
#                             if (
#                                 "difference" in field.app_data
#                                 and field.app_data["difference"]
#                                 and callable(getattr(field, "difference", None))
#                             ):
#                                 field_properties += ".difference()"
#                             if (
#                                 "derivation" in field.app_data
#                                 and field.app_data["derivation"]
#                                 and callable(
#                                     getattr(
#                                         field,
#                                         "derivation",
#                                         field.app_data["derivation"],
#                                     )
#                                 )
#                             ):
#                                 field_properties += f".derivation({repr(field.app_data['derivation'])})"
#                             if (
#                                 "cluster_key_change" in field.app_data
#                                 and field.app_data["cluster_key_change"]
#                                 and callable(getattr(field, "cluster_key_change", None))
#                             ):
#                                 field_properties += ".cluster_key_change()"
#                             if (
#                                 "key_change" in field.app_data
#                                 and field.app_data["key_change"]
#                                 and callable(getattr(field, "key_change", None))
#                             ):
#                                 field_properties += ".key_change()"
#                             if (
#                                 "pivot_property" in field.app_data
#                                 and field.app_data["pivot_property"]
#                                 and callable(getattr(field, "pivot", None))
#                             ):
#                                 field_properties += f'.pivot("{field.app_data["pivot_property"]}")'
#                             if (
#                                 "change_code" in field.app_data
#                                 and field.app_data["change_code"]
#                                 and callable(getattr(field, "change_code", None))
#                             ):
#                                 field_properties += ".change_code()"

#                             field_dict["properties"] = field_properties
#                             fields.append(field_dict)
#                         data_def["fields"] = fields
#                         data_definitions.append(data_def)
#                         data_def_vars[output.data_definition.name] = var_name

#                 inputs = (
#                     [
#                         {key: repr(value) for key, value in input.model_dump(exclude={"id"}, by_alias=False, exclude_none=True).items()}
#                         for input in self.asset.inputs
#                     ]
#                     if len(self.asset.inputs)
#                     else None
#                 )

#                 for input in inputs:
#                     if "table_name" in input:
#                         if input["table_name"].strip("'\"") in data_def_vars:
#                             input["data_definition"] = data_def_vars[input["table_name"].strip("'\"")]
#                             del input["table_name"]

#                 outputs = (
#                     [
#                         {key: repr(value) for key, value in output.model_dump(exclude={"id"}, by_alias=False, exclude_none=True).items()}
#                         for output in self.asset.outputs
#                     ]
#                     if len(self.asset.outputs)
#                     else None
#                 )

#                 for output in outputs:
#                     if "table_name" in output:
#                         if output["table_name"].strip("'\"") in data_def_vars:
#                             output["data_definition"] = data_def_vars[output["table_name"].strip("'\"")]
#                             del output["table_name"]

#                 transfers = (
#                     [
#                         {key: repr(value) for key, value in transfer.model_dump(by_alias=False, exclude_none=True).items()}
#                         for transfer in self.asset.transfers
#                     ]
#                     if len(self.asset.transfers)
#                     else None
#                 )
#             else:
#                 props, properties, data_definitions, inputs, outputs, transfers = (
#                     None,
#                     None,
#                     None,
#                     None,
#                     None,
#                     None,
#                 )

#             asset_var_name = self.master_gen.reserve_var(self.asset.name, self.asset)
#         else:
#             (
#                 props,
#                 properties,
#                 data_definitions,
#                 inputs,
#                 outputs,
#                 transfers,
#                 asset_var_name,
#             ) = (None, None, None, None, None, None, None)

#         if stage:
#             stage_var_name = self.master_gen.reserve_var(self.build_stage.label, self.build_stage)
#             stage_properties = {repr(key): repr(value) for key, value in self.build_stage.properties.items()}
#             config_properties = {}
#             for item, val in self.build_stage.configuration.model_fields.items():
#                 default = val.default.value if hasattr(val.default, "value") else val.default
#                 value = getattr(self.build_stage.configuration, item)
#                 if value != default and item not in [
#                     "op_name",
#                     "input_cardinality",
#                     "output_cardinality",
#                     "input_count",
#                     "output_count",
#                 ]:
#                     if isinstance(value, Enum):
#                         value = value.value
#                     config_properties[item] = repr(value)
#             label = repr(self.build_stage.label)
#             if isinstance(self.asset, str):
#                 asset_var_name = self.asset
#         else:
#             stage_var_name, stage_properties, label, config_properties = (
#                 None,
#                 None,
#                 None,
#             )

#         return self.master_gen.templates.build_stage_template.render(
#             props=props,
#             properties=properties,
#             inputs=inputs,
#             outputs=outputs,
#             transfers=transfers,
#             asset_var_name=asset_var_name,
#             stage_var_name=stage_var_name,
#             label=label,
#             stage_properties=stage_properties,
#             parent_composer=self.parent_composer,
#             asset=asset,
#             stage=stage,
#             offline=self.offline,
#             asset_id=asset_id,
#             imported=imported,
#             config_properties=config_properties,
#             data_definitions=data_definitions,
#         )

#     def get_imports(self):
#         return "from ibm.datastage import *"


# class WrappedStageCodeGenerator:
#     def __init__(
#         self,
#         asset: WrappedStage | str = None,
#         master_gen: MasterCodeGenerator = None,
#         wrapped_stage: WrappedStageStage = None,
#         parent_composer: str = "fc",
#         offline: bool = False,
#     ):
#         self.wrapped_stage = wrapped_stage
#         self.asset = asset
#         self.master_gen = master_gen
#         self.parent_composer = parent_composer
#         self.offline = offline

#     def generate_code(self):
#         asset = bool(self.asset) and isinstance(self.asset, WrappedStage)
#         stage = bool(self.wrapped_stage)

#         asset_id = None
#         imported = False

#         if asset:
#             imported = True if self.asset.asset_id is not None else False
#             asset_id = self.asset.asset_id if imported else None

#             if not imported:
#                 props = self.asset.model_dump(
#                     include={
#                         "name",
#                         "short_description",
#                         "long_description",
#                         "show_on_palette",
#                         "command",
#                         "execution_mode",
#                         "wrapper_name",
#                         "all_exit_codes_successful",
#                     },
#                     by_alias=False,
#                     exclude_none=True,
#                 )

#                 for key, val in props.items():
#                     if not isinstance(val, Enum):
#                         props[key] = repr(val)
#                     else:
#                         props[key] = f"WRAPPEDSTAGE.{val}"

#                 properties = [] if len(self.asset.properties) else None
#                 for prop in self.asset.properties:
#                     prop_data = {}
#                     type_ = prop.data_type.lower()
#                     prop_data["type"] = (type_[0].upper() + type_[1:]).replace("column", "Column")
#                     # keep in mind field serializer
#                     prop_data["props"] = {}
#                     prop_dump = prop.model_dump(exclude={"data_type"}, exclude_none=True, by_alias=False)
#                     for key, val in prop_dump.items():
#                         if val == "":
#                             continue
#                         if key == "required":
#                             val = True if val == "Yes" else False
#                         if key == "repeats":
#                             val = True if val == "Yes" else False
#                         if key == "hidden_property":
#                             val = True if val.lower() == "true" else False
#                         if key == "list_values":
#                             val = val.replace("[", "").replace("]", "").replace('"', "").split(",")
#                         if not isinstance(val, Enum):
#                             prop_data["props"][key] = repr(val)
#                         else:
#                             prop_data["props"][key] = f"WRAPPEDSTAGE.{val}"
#                     properties.append(prop_data)

#                 data_definitions = []

#                 default_precision = {
#                     "Time": 8,
#                     "Timestamp": 19,
#                 }

#                 data_def_vars = {}

#                 for input in self.asset.inputs:
#                     if input.data_definition:
#                         if input.data_definition.name in data_def_vars:
#                             continue
#                         var_name = self.master_gen.reserve_var(input.data_definition.name, input.data_definition)
#                         data_def = {
#                             "var_name": var_name,
#                             "name": repr(input.data_definition.name),
#                         }
#                         fields = []
#                         for field in input.data_definition.columns:
#                             field_dict = {}
#                             field_dict["type"] = field.app_data["odbc_type"].upper()
#                             field_dict["name"] = field.name
#                             field_properties = ""
#                             if field.nullable and callable(getattr(field, "nullable", None)):
#                                 field_properties += ".nullable()"
#                             if field.metadata.is_key and callable(getattr(field, "key", None)):
#                                 field_properties += ".key()"
#                             if field.metadata.source_field_id is not None and callable(getattr(field, "source", None)):
#                                 field_properties += f'.source("{field.metadata.source_field_id}")'
#                             if field.metadata.max_length is not None and callable(getattr(field, "length", None)):
#                                 field_properties += f".length({field.metadata.max_length})"
#                             if (
#                                 "is_unicode_string" in field.app_data
#                                 and field.app_data["is_unicode_string"]
#                                 and callable(getattr(field, "unicode", None))
#                             ):
#                                 field_properties += ".unicode()"
#                             if not field.metadata.is_signed and callable(getattr(field, "unsigned", None)):
#                                 field_properties += ".unsigned()"
#                             if field.metadata.decimal_precision is not None and callable(getattr(field, "precision", None)):
#                                 default_prec = default_precision[field_dict["type"]] if field_dict["type"] in default_precision else 100
#                                 if field.metadata.decimal_precision != default_prec:
#                                     field_properties += f".precision({field.metadata.decimal_precision})"
#                             if (
#                                 field.metadata.decimal_scale is not None
#                                 and field.metadata.decimal_scale > 0
#                                 and callable(getattr(field, "scale", None))
#                             ):
#                                 field_properties += f".scale({field.metadata.decimal_scale})"
#                             if "extended_type" in field.app_data and field.app_data["extended_type"] is not None:
#                                 if "timezone" in field.app_data["extended_type"] and callable(getattr(field, "timezone", None)):
#                                     field_properties += ".timezone()"
#                                 if "microseconds" in field.app_data["extended_type"] and callable(getattr(field, "microseconds", None)):
#                                     field_properties += ".microseconds()"
#                             if field_dict["type"] == "Timestamp":
#                                 field_properties += ".microseconds()"
#                             if (
#                                 "difference" in field.app_data
#                                 and field.app_data["difference"]
#                                 and callable(getattr(field, "difference", None))
#                             ):
#                                 field_properties += ".difference()"
#                             if (
#                                 "derivation" in field.app_data
#                                 and field.app_data["derivation"]
#                                 and callable(
#                                     getattr(
#                                         field,
#                                         "derivation",
#                                         field.app_data["derivation"],
#                                     )
#                                 )
#                             ):
#                                 field_properties += f".derivation({repr(field.app_data['derivation'])})"
#                             if (
#                                 "cluster_key_change" in field.app_data
#                                 and field.app_data["cluster_key_change"]
#                                 and callable(getattr(field, "cluster_key_change", None))
#                             ):
#                                 field_properties += ".cluster_key_change()"
#                             if (
#                                 "key_change" in field.app_data
#                                 and field.app_data["key_change"]
#                                 and callable(getattr(field, "key_change", None))
#                             ):
#                                 field_properties += ".key_change()"
#                             if (
#                                 "pivot_property" in field.app_data
#                                 and field.app_data["pivot_property"]
#                                 and callable(getattr(field, "pivot", None))
#                             ):
#                                 field_properties += f'.pivot("{field.app_data["pivot_property"]}")'
#                             if (
#                                 "change_code" in field.app_data
#                                 and field.app_data["change_code"]
#                                 and callable(getattr(field, "change_code", None))
#                             ):
#                                 field_properties += ".change_code()"

#                             field_dict["properties"] = field_properties
#                             fields.append(field_dict)
#                         data_def["fields"] = fields
#                         data_definitions.append(data_def)
#                         data_def_vars[input.data_definition.name] = var_name

#                 for output in self.asset.outputs:
#                     if output.data_definition:
#                         if output.data_definition.name in data_def_vars:
#                             continue
#                         var_name = self.master_gen.reserve_var(output.data_definition.name, output.data_definition)
#                         data_def = {
#                             "var_name": var_name,
#                             "name": repr(output.data_definition.name),
#                         }
#                         fields = []
#                         for field in output.data_definition.columns:
#                             field_dict = {}
#                             field_dict["type"] = field.app_data["odbc_type"].upper()
#                             field_dict["name"] = field.name
#                             field_properties = ""
#                             if field.nullable and callable(getattr(field, "nullable", None)):
#                                 field_properties += ".nullable()"
#                             if field.metadata.is_key and callable(getattr(field, "key", None)):
#                                 field_properties += ".key()"
#                             if field.metadata.source_field_id is not None and callable(getattr(field, "source", None)):
#                                 field_properties += f'.source("{field.metadata.source_field_id}")'
#                             if field.metadata.max_length is not None and callable(getattr(field, "length", None)):
#                                 field_properties += f".length({field.metadata.max_length})"
#                             if (
#                                 "is_unicode_string" in field.app_data
#                                 and field.app_data["is_unicode_string"]
#                                 and callable(getattr(field, "unicode", None))
#                             ):
#                                 field_properties += ".unicode()"
#                             if not field.metadata.is_signed and callable(getattr(field, "unsigned", None)):
#                                 field_properties += ".unsigned()"
#                             if field.metadata.decimal_precision is not None and callable(getattr(field, "precision", None)):
#                                 default_prec = default_precision[field_dict["type"]] if field_dict["type"] in default_precision else 100
#                                 if field.metadata.decimal_precision != default_prec:
#                                     field_properties += f".precision({field.metadata.decimal_precision})"
#                             if (
#                                 field.metadata.decimal_scale is not None
#                                 and field.metadata.decimal_scale > 0
#                                 and callable(getattr(field, "scale", None))
#                             ):
#                                 field_properties += f".scale({field.metadata.decimal_scale})"
#                             if "extended_type" in field.app_data and field.app_data["extended_type"] is not None:
#                                 if "timezone" in field.app_data["extended_type"] and callable(getattr(field, "timezone", None)):
#                                     field_properties += ".timezone()"
#                                 if "microseconds" in field.app_data["extended_type"] and callable(getattr(field, "microseconds", None)):
#                                     field_properties += ".microseconds()"
#                             if field_dict["type"] == "Timestamp":
#                                 field_properties += ".microseconds()"
#                             if (
#                                 "difference" in field.app_data
#                                 and field.app_data["difference"]
#                                 and callable(getattr(field, "difference", None))
#                             ):
#                                 field_properties += ".difference()"
#                             if (
#                                 "derivation" in field.app_data
#                                 and field.app_data["derivation"]
#                                 and callable(
#                                     getattr(
#                                         field,
#                                         "derivation",
#                                         field.app_data["derivation"],
#                                     )
#                                 )
#                             ):
#                                 field_properties += f".derivation({repr(field.app_data['derivation'])})"
#                             if (
#                                 "cluster_key_change" in field.app_data
#                                 and field.app_data["cluster_key_change"]
#                                 and callable(getattr(field, "cluster_key_change", None))
#                             ):
#                                 field_properties += ".cluster_key_change()"
#                             if (
#                                 "key_change" in field.app_data
#                                 and field.app_data["key_change"]
#                                 and callable(getattr(field, "key_change", None))
#                             ):
#                                 field_properties += ".key_change()"
#                             if (
#                                 "pivot_property" in field.app_data
#                                 and field.app_data["pivot_property"]
#                                 and callable(getattr(field, "pivot", None))
#                             ):
#                                 field_properties += f'.pivot("{field.app_data["pivot_property"]}")'
#                             if (
#                                 "change_code" in field.app_data
#                                 and field.app_data["change_code"]
#                                 and callable(getattr(field, "change_code", None))
#                             ):
#                                 field_properties += ".change_code()"

#                             field_dict["properties"] = field_properties
#                             fields.append(field_dict)
#                         data_def["fields"] = fields
#                         data_definitions.append(data_def)
#                         data_def_vars[output.data_definition.name] = var_name

#                 inputs = (
#                     [
#                         {
#                             key: (repr(value) if not isinstance(value, Enum) else f"WRAPPEDSTAGE.{value}")
#                             for key, value in input.model_dump(exclude={"id"}, by_alias=False, exclude_none=True).items()
#                         }
#                         for input in self.asset.inputs
#                     ]
#                     if len(self.asset.inputs)
#                     else None
#                 )

#                 for input in inputs:
#                     if "table_name" in input:
#                         if input["table_name"].strip("'\"") in data_def_vars:
#                             input["data_definition"] = data_def_vars[input["table_name"].strip("'\"")]
#                             del input["table_name"]

#                 outputs = (
#                     [
#                         {
#                             key: (repr(value) if not isinstance(value, Enum) else f"WRAPPEDSTAGE.{value}")
#                             for key, value in output.model_dump(exclude={"id"}, by_alias=False, exclude_none=True).items()
#                         }
#                         for output in self.asset.outputs
#                     ]
#                     if len(self.asset.outputs)
#                     else None
#                 )

#                 for output in outputs:
#                     if "table_name" in output:
#                         if output["table_name"].strip("'\"") in data_def_vars:
#                             output["data_definition"] = data_def_vars[output["table_name"].strip("'\"")]
#                             del output["table_name"]

#                 environment_variables = (
#                     [
#                         {key: repr(value) for key, value in env_var.model_dump(by_alias=False, exclude_none=True).items()}
#                         for env_var in self.asset.environment_variables
#                     ]
#                     if len(self.asset.environment_variables)
#                     else None
#                 )
#                 success_codes = (
#                     [
#                         {key: repr(value) for key, value in success_code.model_dump(by_alias=False, exclude_none=True).items()}
#                         for success_code in self.asset.success_codes
#                     ]
#                     if len(self.asset.success_codes)
#                     else None
#                 )
#                 failure_codes = (
#                     [
#                         {key: repr(value) for key, value in failure_code.model_dump(by_alias=False, exclude_none=True).items()}
#                         for failure_code in self.asset.failure_codes
#                     ]
#                     if len(self.asset.failure_codes)
#                     else None
#                 )

#             else:
#                 (
#                     props,
#                     properties,
#                     data_definitions,
#                     inputs,
#                     outputs,
#                     environment_variables,
#                     success_codes,
#                     failure_codes,
#                 ) = (
#                     None,
#                     None,
#                     None,
#                     None,
#                     None,
#                     None,
#                     None,
#                     None,
#                 )

#             asset_var_name = self.master_gen.reserve_var(self.asset.name, self.asset)
#         else:
#             (
#                 props,
#                 properties,
#                 data_definitions,
#                 inputs,
#                 outputs,
#                 environment_variables,
#                 success_codes,
#                 failure_codes,
#                 asset_var_name,
#             ) = (
#                 None,
#                 None,
#                 None,
#                 None,
#                 None,
#                 None,
#                 None,
#                 None,
#                 None,
#             )

#         if stage:
#             stage_var_name = self.master_gen.reserve_var(self.wrapped_stage.label, self.wrapped_stage)
#             stage_properties = {repr(key): repr(value) for key, value in self.wrapped_stage.properties.items()}
#             config_properties = {}
#             for item, val in self.wrapped_stage.configuration.model_fields.items():
#                 default = val.default.value if hasattr(val.default, "value") else val.default
#                 value = getattr(self.wrapped_stage.configuration, item)
#                 if value != default and item not in [
#                     "op_name",
#                     "input_cardinality",
#                     "output_cardinality",
#                     "input_count",
#                     "output_count",
#                 ]:
#                     if isinstance(value, Enum):
#                         value = value.value
#                     config_properties[item] = repr(value)
#             label = repr(self.wrapped_stage.label)
#             if isinstance(self.asset, str):
#                 asset_var_name = self.asset
#         else:
#             stage_var_name, stage_properties, label, config_properties = (
#                 None,
#                 None,
#                 None,
#                 None,
#             )

#         return self.master_gen.templates.wrapped_stage_template.render(
#             props=props,
#             properties=properties,
#             inputs=inputs,
#             outputs=outputs,
#             environment_variables=environment_variables,
#             success_codes=success_codes,
#             failure_codes=failure_codes,
#             asset_var_name=asset_var_name,
#             stage_var_name=stage_var_name,
#             label=label,
#             stage_properties=stage_properties,
#             parent_composer=self.parent_composer,
#             asset=asset,
#             stage=stage,
#             offline=self.offline,
#             asset_id=asset_id,
#             imported=imported,
#             config_properties=config_properties,
#             data_definitions=data_definitions,
#         )

#     def get_imports(self):
#         return "from ibm.datastage import *"


# class CustomStageCodeGenerator:
#     def __init__(
#         self,
#         asset: CustomStage | str = None,
#         master_gen: MasterCodeGenerator = None,
#         custom_stage: CustomStageStage = None,
#         parent_composer: str = "fc",
#         offline: bool = False,
#     ):
#         self.custom_stage = custom_stage
#         self.asset = asset
#         self.master_gen = master_gen
#         self.parent_composer = parent_composer
#         self.offline = offline

#     def generate_code(self):
#         asset = bool(self.asset) and isinstance(self.asset, CustomStage)
#         stage = bool(self.custom_stage)

#         asset_id = None
#         imported = False

#         if asset:
#             imported = True if self.asset.asset_id is not None else False
#             asset_id = self.asset.asset_id if imported else None

#             if not imported:
#                 props = self.asset.model_dump(
#                     include={
#                         "name",
#                         "short_description",
#                         "long_description",
#                         "show_on_palette",
#                         "operator",
#                         "custom_operator_file_path",
#                         "execution_mode",
#                         "mappingpreserve_partitioning",
#                         "partitioning",
#                         "collecting",
#                         "min_input_links",
#                         "max_input_links",
#                         "min_output_links",
#                         "max_output_links",
#                         "enable_format_options_for_schema_properties",
#                     },
#                     by_alias=False,
#                     exclude_none=True,
#                 )

#                 for key, val in props.items():
#                     if not isinstance(val, Enum):
#                         props[key] = repr(val)
#                     else:
#                         props[key] = f"CUSTOMSTAGE.{val}"

#                 properties = [] if len(self.asset.properties) else None
#                 for prop in self.asset.properties:
#                     prop_data = {}
#                     type_ = prop.data_type.lower()
#                     prop_data["type"] = (type_[0].upper() + type_[1:]).replace("column", "Column")
#                     # keep in mind field serializer
#                     prop_data["props"] = {}
#                     prop_dump = prop.model_dump(exclude={"data_type"}, exclude_none=True, by_alias=False)
#                     for key, val in prop_dump.items():
#                         if val == "":
#                             continue
#                         if key in ["required", "repeats", "use_quoting"]:
#                             val = True if val == "Yes" else False
#                         if key == "hidden_property":
#                             val = True if val.lower() == "true" else False
#                         if key == "list_values":
#                             val = val.replace("[", "").replace("]", "").replace('"', "").split(",")
#                         if not isinstance(val, Enum):
#                             prop_data["props"][key] = repr(val)
#                         else:
#                             prop_data["props"][key] = f"CUSTOMSTAGE.{val}"
#                     properties.append(prop_data)

#                 mapping_additions = (
#                     [
#                         {
#                             key: (repr(value) if not isinstance(value, Enum) else f"CUSTOMSTAGE.{value}")
#                             for key, value in mapping_addition.model_dump(exclude={"id"}, by_alias=False, exclude_none=True).items()
#                         }
#                         for mapping_addition in self.asset.mapping_additions
#                     ]
#                     if len(self.asset.mapping_additions)
#                     else None
#                 )
#             else:
#                 props, properties, mapping_additions = (
#                     None,
#                     None,
#                     None,
#                 )

#             asset_var_name = self.master_gen.reserve_var(self.asset.name, self.asset)
#         else:
#             props, properties, mapping_additions, asset_var_name = (
#                 None,
#                 None,
#                 None,
#                 None,
#             )

#         if stage:
#             stage_var_name = self.master_gen.reserve_var(self.custom_stage.label, self.custom_stage)
#             stage_properties = {repr(key): repr(value) for key, value in self.custom_stage.properties.items()}
#             config_properties = {}
#             for item, val in self.custom_stage.configuration.model_fields.items():
#                 default = val.default.value if hasattr(val.default, "value") else val.default
#                 value = getattr(self.custom_stage.configuration, item)
#                 if value != default and item not in [
#                     "op_name",
#                     "input_cardinality",
#                     "output_cardinality",
#                     "input_count",
#                     "output_count",
#                 ]:
#                     if isinstance(value, Enum):
#                         value = value.value
#                     config_properties[item] = repr(value)
#             label = repr(self.custom_stage.label)
#             if isinstance(self.asset, str):
#                 asset_var_name = self.asset
#         else:
#             stage_var_name, stage_properties, label, config_properties = (
#                 None,
#                 None,
#                 None,
#                 None,
#             )

#         return self.master_gen.templates.custom_stage_template.render(
#             props=props,
#             properties=properties,
#             mapping_additions=mapping_additions,
#             asset_var_name=asset_var_name,
#             stage_var_name=stage_var_name,
#             label=label,
#             stage_properties=stage_properties,
#             parent_composer=self.parent_composer,
#             asset=asset,
#             stage=stage,
#             offline=self.offline,
#             asset_id=asset_id,
#             imported=imported,
#             config_properties=config_properties,
#         )

#     def get_imports(self):
#         return "from ibm.datastage import *"


# class MatchSpecificationCodeGenerator:
#     def __init__(
#         self,
#         match_specification: MatchSpecification,
#         output_path: str,
#         master_gen: MasterCodeGenerator = None,
#     ):
#         self.match_specification = match_specification
#         self.master_gen = master_gen or MasterCodeGenerator()
#         self.output_path = Path(output_path)

#     def generate_code(self):
#         var_name = self.master_gen.reserve_var(self.match_specification.name, self.match_specification)

#         ms_model = self.match_specification.model_dump(exclude_none=True, exclude={"asset_id", "proj_id"}, warnings=False)
#         _, _, new_entity = CreateMatchSpecification.make_data_from_entity(ms_model)

#         return self.master_gen.templates.match_specification_template.render(
#             var_name=var_name,
#             match_specification_name=self.match_specification.name,
#             mat_json=new_entity["mat"],
#             passes_json=new_entity["passes"],
#             description=self.match_specification.description,
#         )

#     def get_imports(self):
#         return "from ibm.datastage import *"
