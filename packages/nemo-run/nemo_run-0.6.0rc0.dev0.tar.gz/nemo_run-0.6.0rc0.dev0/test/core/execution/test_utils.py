# SPDX-FileCopyrightText: Copyright (c) 2024 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from nemo_run.core.execution.utils import fill_template


def test_fill_template_file_not_found():
    template_name = "non_existing_template.j2"
    variables = {"var1": "value1"}

    with pytest.raises(FileNotFoundError):
        fill_template(template_name, variables)


def test_fill_template_invalid_extension():
    template_name = "invalid_extension.txt"
    variables = {"var1": "value1"}

    with pytest.raises(AssertionError):
        fill_template(template_name, variables)
