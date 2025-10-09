"""
   Copyright 2025 Timandes White

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""
from importlib.resources import files
import yaml

def load_config():
    """
    加载内置的默认配置文件。
    """
    try:
        # 使用 importlib.resources 安全读取包内资源
        config_content = files("mcp_gateway.data").joinpath("config.yaml").read_text(encoding="utf-8")
        return yaml.safe_load(config_content)
    except FileNotFoundError:
        raise RuntimeError("内置配置文件 'config.yaml' 未找到，请检查打包是否正确。")
