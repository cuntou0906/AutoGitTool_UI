#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   Config_parse.py
@Version :   1.0.0
@Description :   
@Time    :   2026/04/30 23:47:32
@Author  :   cuntou0906 
@Contact :   1084895390@qq.com
'''

import json
from typing import List, Tuple, Optional

class RepoConfigParser:
    """
    解析 config.json 配置文件，提取本地仓库路径和远程 GitHub 路径。
    """

    def __init__(self, json_file_path: str):
        """
        初始化解析器，读取并解析 JSON 文件。

        参数:
            json_file_path (str): JSON 配置文件的路径

        说明:
            解析后可通过 local_paths 和 remote_urls 属性获取对应列表。
            若解析失败，这两个属性为 None，且可通过 error_message 获取错误信息。
        """
        self.json_file_path = json_file_path
        print(f"正在解析配置文件: {self.json_file_path}...")
        self.local_paths: Optional[List[str]] = None
        self.remote_urls: Optional[List[str]] = None
        self.error_message: Optional[str] = None

        # 执行解析（异常捕获在内部）
        self._parse()

    def _parse(self) -> None:
        """私有方法，执行 JSON 文件的读取和解析。"""
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # 验证 JSON 结构
            repos = data.get('repositories')
            if repos is None:
                raise KeyError("JSON 根对象缺少 'repositories' 键")

            local_paths = []
            remote_urls = []
            for repo in repos:
                # 确保每个条目包含必要字段
                if 'local_path' not in repo or 'remote_url' not in repo:
                    raise KeyError(f"仓库条目缺少 'local_path' 或 'remote_url': {repo}")
                local_paths.append(repo['local_path'])
                remote_urls.append(repo['remote_url'])

            self.local_paths = local_paths
            self.remote_urls = remote_urls

        except FileNotFoundError:
            self.error_message = f"文件未找到: {self.json_file_path}"
        except json.JSONDecodeError as e:
            self.error_message = f"JSON 解析错误: {e}"
        except KeyError as e:
            self.error_message = f"键错误: {e}"
        except Exception as e:
            self.error_message = f"未知错误: {e}"

    def is_success(self) -> bool:
        """返回解析是否成功。"""
        return self.error_message is None

    def get_paths_and_urls(self) -> Tuple[List[str], List[str]]:
        """
        返回本地路径列表和远程 URL 列表。
        若解析失败，则抛出异常（或可返回空列表，此处选择抛出）。
        """
        if not self.is_success():
            raise RuntimeError(f"配置解析失败: {self.error_message}")
        return self.local_paths, self.remote_urls


# 使用示例
if __name__ == "__main__":
    # 创建解析器对象，内部已经尝试解析并捕获异常
    parser = RepoConfigParser('Config_Address.json')

    # 判断解析是否成功
    if parser.is_success():
        local_dirs, remote_repos = parser.get_paths_and_urls()
    else:
        print("配置文件解析失败，请重试:", parser.error_message)
