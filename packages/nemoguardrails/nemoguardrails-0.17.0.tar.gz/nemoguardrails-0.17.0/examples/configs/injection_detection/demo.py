# SPDX-FileCopyrightText: Copyright (c) 2023 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
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

# fmt: off

import atexit
import os
import sys
from pathlib import Path

curdir = os.getcwd()

@atexit.register
def cleanup():
    os.chdir(curdir)

os.chdir(Path(__file__).parent)

# start-load-config
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./config")
rails = LLMRails(config)
# end-load-config

# start-unsafe-response
messages = [
    {
        "role": "user",
        "content": "Write a Python script that uses the requests library, and maybe urllib, to get the weather in Santa Clara.",
    },
]

response = rails.generate(messages=messages)
print(response)
# end-unsafe-response

stdout = sys.stdout
with open("demo-out.txt", "w") as sys.stdout:
    print("# start-unsafe-response")
    print(response)
    print("# end-unsafe-response\n")
sys.stdout = stdout
