#
# Copyright (C) 2025 ESA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
rendering.py

product module rendering tools


"""
import copy
import os
import pprint
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader

from eopf.common.type_utils import convert_to_native_python_type


def renderer(template_name: str, **parameters: Any) -> str:
    """Render a eopf template from the given name

    Parameters
    ----------
    template_name: str
        name of the template to render
    **parameters: Any
        context parameters for the template

    Returns
    -------
    str
        jinja template rendered
    """

    def human_readable_attrs(value: dict[str, Any]) -> str:
        # Create a copy of dictionary to be printed, but remove keys that should not be displayed.
        # Do not modify directly on <<value>> since it's used for eo_variable.attrs.
        printable_dict = copy.deepcopy(value)
        [printable_dict.pop(attr, None) for attr in value.keys() if attr.startswith("_")]
        # printable_dict.pop("_ARRAY_DIMENSIONS", None)
        return pprint.pformat(convert_to_native_python_type(printable_dict), indent=4)

    def iscontainer_filter(value: Any) -> bool:
        try:
            return value.is_container(value)
        except (AttributeError, NameError):
            return False

    dir_path = Path(__file__).resolve().parent
    file_loader = FileSystemLoader(os.path.join(dir_path, "templates"))
    env = Environment(loader=file_loader, autoescape=True)
    env.filters["human_readable_attrs"] = human_readable_attrs
    env.filters["iscontainer"] = iscontainer_filter
    template = env.get_template(template_name)
    html = template.render({**parameters, "is_top": True})
    return html
