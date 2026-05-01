#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   git_Add_Commit_Push_operations.py
@Version :   1.0.0
@Description :   
@Time    :   2026/04/30 23:47:07
@Author  :   cuntou0906 
@Contact :   1084895390@qq.com
'''

import subprocess
import os

class GitPush_AutoGit():
    def __init__(self, local_repos, remote_urls):
        self.local_repos = local_repos
        self.remote_urls = remote_urls
        self.PushRepo_ErrorNum = 0  # 记录推送失败的仓库数量

    def update_remote_url_local_repos(self, local_repos, remote_urls): 
        self.local_repos = local_repos
        self.remote_urls = remote_urls

    def is_git_repo(self,folder_path):
        try:
            # 进入指定目录
            result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], cwd=folder_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # 如果命令执行成功，说明是一个Git仓库
            if result.returncode == 0:
                return True
            else:
                return False
            
        except FileNotFoundError:
            # 如果git命令不可用，可能是因为没有安装git或者不在PATH中
            return False   

    def run_git_command(self, command, repo_dir):
        """Run a git command in the specified repository directory."""
        try:
            result = subprocess.run(
                command,
                cwd=repo_dir,
                text=True,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            # Only print if there is meaningful output
            output = result.stdout.strip()
            if output:
                print(output)
            return True
        except subprocess.CalledProcessError as e:
            error_output = e.stderr.strip()
            if error_output:
                print(f"Error: {error_output}")
            return False

    def configure_origin(self, repo_dir, remote_url):
        """Configure the origin remote for the repository."""
        try:
            # Check if origin already exists
            result = subprocess.run(
                "git remote get-url origin",
                cwd=repo_dir,
                text=True,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            current_url = result.stdout.strip()
            if current_url != remote_url:
                print(f"将目前远端URL仓库Origin：{current_url} 更新为：{remote_url}！")
                self.run_git_command(f"git remote set-url origin {remote_url}", repo_dir)
            else:
                print(f"远端URL仓库Origin已经设置为 {remote_url}.")
        except subprocess.CalledProcessError:
            # If origin does not exist, add it
            print(f"配置远端URL仓库Origin为：{remote_url}...")
            self.run_git_command(f"git remote add origin {remote_url}", repo_dir)

    def update_gitignore(self, repo_dir, file_path):
        """Add a file path to .gitignore if it's not already present."""
        gitignore_path = os.path.join(repo_dir, '.gitignore')
        # Read existing .gitignore content
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as gitignore_file:
                lines = gitignore_file.readlines()
        else:
            lines = []

        # Get the relative path for the file
        relative_path = os.path.relpath(file_path, repo_dir)
        relative_path = relative_path.replace('\\', '/')  # Replace backslashes with forward slashes

        # Check if the relative path is already in .gitignore
        if relative_path + '\n' not in lines:
            print(f"添加文件{file_path} 到.gitignore (文件大小超过100MB)！")
            with open(gitignore_path, 'a', encoding='utf-8') as gitignore_file:
                gitignore_file.write(f"{relative_path}\n")

    def is_tracked(self, file_path, repo_dir):
        """Check if a file is tracked by git."""
        result = subprocess.run(
            f"git ls-files --error-unmatch \"{file_path}\"",
            cwd=repo_dir,
            text=True,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        # Check if the command was successful
        if result.returncode == 0:
            return True
        else:
            # If the file is not tracked, return False
            return False

    def git_add_commit_push(self, repo_dir, message, remote='origin', branch='master'):
        """Add, commit, and push changes to the remote repository."""
        # print("处理大文件：更新.gitignore！")
        # Find all files in the repo directory
        for root, dirs, files in os.walk(repo_dir):
            # Ignore the .git directory
            if '.git' in dirs:
                dirs.remove('.git')  # This will prevent os.walk from going into the .git directory

            for file in files:
                file_path = os.path.join(root, file)
                # Check file size
                if os.path.getsize(file_path) > 100 * 1024 * 1024:  # 100MB
                    print(f"发现大文件: {file_path}")
                    self.update_gitignore(repo_dir, file_path)
                    # Remove the file from git tracking if it is tracked
                    # if self.is_tracked(file_path, repo_dir):
                    #     self.run_git_command(f"git rm --cached \"{file_path}\"", repo_dir)

        # Use 'git add .' to include all changes except those in .gitignore
        print("Adding changes...")
        AddInfo = self.run_git_command("git add .", repo_dir)

        print("Committing changes...")
        CommitInfo = self.run_git_command(f"git commit -m \"{message}\"", repo_dir)
        
        print("Pushing changes...")
        PushInfo = self.run_git_command(f"git push {remote} {branch}", repo_dir)
        if PushInfo:
            print("推送至远程仓库成功!")

        return PushInfo

    def git_pull(self, repo_dir, remote='origin', branch='master'):
        """Pull changes from the remote repository."""
        print("Pulling changes...")
        self.run_git_command(f"git pull {remote} {branch}", repo_dir)

    def is_git_repo(self,folder_path):
        try:
            # 进入指定目录
            result = subprocess.run(['git', 'rev-parse', '--is-inside-work-tree'], cwd=folder_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            # 如果命令执行成功，说明是一个Git仓库
            if result.returncode == 0:
                return True
            else:
                return False
            
        except FileNotFoundError:
            # 如果git命令不可用，可能是因为没有安装git或者不在PATH中
            return False  

    def update_remote_url_local_repos(self, local_repos, remote_urls): 
        self.local_repos = local_repos
        self.remote_urls = remote_urls   

    def process_result(self, local_repos, remote_urls):

        self.PushRepo_ErrorNum = 0  # 重置拉取失败的仓库数量记录
            
        self.update_remote_url_local_repos(local_repos, remote_urls) # 更新本地仓库路径和远程URL列表

        # Ensure the lists are of the same length
        if len(self.local_repos) != len(self.remote_urls):
            print("Error: 本地存储库和远程url的数量必须匹配，且一一对应！")
        else:
            # Iterate over each repository
            for repo_directory, remote_url in zip(self.local_repos, self.remote_urls):

                print(f"\n##############################################################")
                print(f"处理仓库: {repo_directory}")
                # Ensure the directory exists
                if not os.path.isdir(repo_directory):
                    print(f"Error: 本地仓库 {repo_directory} 不存在！")
                    self.PushRepo_ErrorNum = self.PushRepo_ErrorNum + 1
                else:
                    # 检查是否是一个Git仓库，如果不是则初始化为Git仓库
                    if not self.is_git_repo(repo_directory):
                        print(f"{repo_directory} 不是一个Git仓库，初始化为Git仓库...")
                        self.run_git_command("git init", repo_directory)   
                        
                    # 检查是否仅包含一个名为 '.git' 的文件夹，并且没有其他文件或文件夹，如果是，则认为仓库为空，不需要提交
                    items_filedir = os.listdir(repo_directory)
                    if len(items_filedir) == 1 and items_filedir[0] == '.git':
                        print(f"Pass: 本地仓库 {repo_directory} 为空，不需要提交！")
                    else:         
                        # Configure origin
                        self.configure_origin(repo_directory, remote_url)

                        # Perform git operations
                        Total_push_Info = self.git_add_commit_push(repo_directory, "Your commit message")

                        if not Total_push_Info:
                            print(f"推送至远程仓库失败！请检查网络或远程仓库配置是否正确。")
                            self.PushRepo_ErrorNum = self.PushRepo_ErrorNum + 1
          
                        
            print(f"\n##############################################################") 
            print(f"总共{len(self.local_repos)}个仓库处理完成！推送失败的仓库数量：{self.PushRepo_ErrorNum} 个。")
            print(f"##############################################################\n") 

    
