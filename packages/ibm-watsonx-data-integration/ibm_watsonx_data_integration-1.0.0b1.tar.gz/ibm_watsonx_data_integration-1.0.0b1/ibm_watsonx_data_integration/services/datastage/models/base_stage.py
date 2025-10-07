from enum import Enum
from pydantic import BaseModel, Field


class BufMode(Enum):
    default = "default"
    auto_buffer = "autobuffer"
    buffer = "buffer"
    no_buffer = "nobuffer"


class BaseStage(BaseModel):
    buf_mode: BufMode | str = Field(BufMode.default, alias="buf_mode")
    max_mem_buf_size: int = Field(3145728, alias="max_mem_buf_size")
    buf_free_run: int = Field(50, alias="buf_free_run")
    queue_upper_size: int = Field(0, alias="queue_upper_size")
    disk_write_inc: int = Field(1048576, alias="disk_write_inc")

    def validate(self):
        include = set()
        exclude = set()

        (
            include.add("max_mem_buf_size")
            if (
                ((hasattr(self.buf_mode, "value") and self.buf_mode.value != "default") or self.buf_mode != "default")
                and (
                    (hasattr(self.buf_mode, "value") and self.buf_mode.value != "no_buffer")
                    or self.buf_mode.value != "nobuffer"
                )
            )
            else exclude.add("max_mem_buf_size")
        )
        (
            include.add("buf_free_run")
            if (
                ((hasattr(self.buf_mode, "value") and self.buf_mode.value != "default") or self.buf_mode != "default")
                and (
                    (hasattr(self.buf_mode, "value") and self.buf_mode.value != "no_buffer")
                    or self.buf_mode.value != "nobuffer"
                )
            )
            else exclude.add("buf_free_run")
        )
        (
            include.add("queue_upper_size")
            if (
                ((hasattr(self.buf_mode, "value") and self.buf_mode.value != "default") or self.buf_mode != "default")
                and (
                    (hasattr(self.buf_mode, "value") and self.buf_mode.value != "no_buffer")
                    or self.buf_mode.value != "nobuffer"
                )
            )
            else exclude.add("queue_upper_size")
        )
        (
            include.add("disk_write_inc")
            if (
                ((hasattr(self.buf_mode, "value") and self.buf_mode.value != "default") or self.buf_mode != "default")
                and (
                    (hasattr(self.buf_mode, "value") and self.buf_mode.value != "no_buffer")
                    or self.buf_mode.value != "nobuffer"
                )
            )
            else exclude.add("disk_write_inc")
        )

        return include, exclude

    def get_advanced_props(self):
        include, exclude = self.validate()
        return self.model_dump(include=include, exclude=exclude, by_alias=True, exclude_none=True)
