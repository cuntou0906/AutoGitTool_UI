#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   git_tool_app.py
@Version :   1.0.0
@Description :   
@Time    :   2026/04/30 23:46:34
@Author  :   cuntou0906
@Contact :   1084895390@qq.com
'''

import sys
import os
import json
import subprocess
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                          QHBoxLayout, QPushButton, QListWidget, QListWidgetItem,
                          QInputDialog, QMessageBox, QFileDialog, QGroupBox,
                          QLineEdit, QLabel, QTextEdit, QDialog,QDesktopWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon
import ctypes
from PyQt5 import QtCore

from git_Add_Commit_Push_operations import GitPush_AutoGit
from git_Pull_operations import GitPull_AutoGit
from Config_parse import RepoConfigParser

##############################################################################
# 设置pyqt5的路径 解决
# This application failed to start because it could not find or load the Qt platform plugin "windows"
# in "E:\??????\???????????\CTfishControl\venv\Lib\site-packages\PyQt5\Qt\plugins".
##############################################################################
os.environ["QT_QPA_PLATFORM_PLUGIN_PATH"] = \
    os.path.join(os.path.dirname(QtCore.__file__), "Qt\plugins\platforms")
os.environ["QT_PLUGIN_PATH"] = \
    os.path.join(os.path.dirname(QtCore.__file__), "Qt\plugins")

class GitOutputDialog(QDialog):
    # This dialog will display the output of git operations in real-time
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AutoGitTool")
        self.setGeometry(200, 200, 600, 400)
        self.setModal(True)  # Make it modal to block the main window

        layout = QVBoxLayout()

        self.output_text = QTextEdit()
        self.output_text.setReadOnly(True)
        layout.addWidget(QLabel("Git Log"))
        layout.addWidget(self.output_text)

        # Add a close button
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)

        self.setLayout(layout)

        self.output_buffer = []

    def append_output(self, text):
        self.output_buffer.append(text)
        self.output_text.append(text)

    def closeEvent(self, event):
        self.output_text.append("Git 操作完成！ 可以关闭窗口啦~.")
        super().closeEvent(event)

class GitWorker(QThread):
    output_signal = pyqtSignal(str)
    finished_signal = pyqtSignal()

    def __init__(self, operation_type, local_repos, remote_urls, git_obj, parent=None):
        super().__init__(parent)
        self.operation_type = operation_type
        self.local_repos = local_repos
        self.remote_urls = remote_urls
        self.git_obj = git_obj

    def run(self):
        # Store original print function
        import builtins
        original_print = builtins.print

        # Create a custom print function that emits signals
        def custom_print(*args, **kwargs):
            output = ' '.join(str(arg) for arg in args)
            self.output_signal.emit(output)
            original_print(*args, **kwargs)

        # Temporarily replace the print function
        builtins.print = custom_print

        try:
            # Perform the git operation
            if self.operation_type == "push":
                self.git_obj.process_result(self.local_repos, self.remote_urls)
            elif self.operation_type == "pull":
                self.git_obj.process_result(self.local_repos, self.remote_urls)
        finally:
            # Restore original print function
            builtins.print = original_print

        self.finished_signal.emit()

class GitToolApp(QMainWindow):
    def __init__(self):

        super().__init__()
        self.local_repos = []
        self.remote_urls = []
        self.config_file = './Config_Address.json'  # Store config file path in the class
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("AutoGitTool")
        self.window_width = 900
        self.window_height = 600 

        # 获取屏幕分辨率
        self.screen = QDesktopWidget().screenGeometry()  
        self.setGeometry(int((self.screen.width() - self.window_width) / 2), int((self.screen.height() - self.window_height) / 2), self.window_width, self.window_height)
        
        base_path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)
        icon_path = os.path.join(base_path, 'Img/AutoGitTool_Logo16.ico')
        # print(icon_path)
        self.setWindowIcon(QIcon(icon_path))                # 设置图标
        # 这是id，这样任务栏的图标就能显示
        self.myappid = "AutoGitTool"  # 任意字符串，最好使用你的项目名或公司名
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(self.myappid)

        # Status bar
        self.status_bar = self.statusBar()

    def init_ui_heavy(self):

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        # Configuration file selection group
        config_group = QGroupBox("配置文件")
        config_layout = QHBoxLayout()

        self.config_file_input = QLineEdit()
        self.config_file_input.setReadOnly(True)
        self.config_file_input.setPlaceholderText(self.config_file)
        config_layout.addWidget(self.config_file_input)

        self.config_browse_btn = QPushButton("选择配置文件")
        self.config_browse_btn.clicked.connect(self.browse_config_file)
        config_layout.addWidget(self.config_browse_btn)

        config_group.setLayout(config_layout)
        main_layout.addWidget(config_group)

        # Repository list group
        repo_group = QGroupBox("本地-远程仓库 | 配置对列表")
        repo_layout = QVBoxLayout()

        # Repository list
        self.repo_list = QListWidget()
        self.repo_list.itemSelectionChanged.connect(self.on_repo_selected)
        self.repo_list.setAlternatingRowColors(True)
        repo_layout.addWidget(self.repo_list)
        repo_group.setLayout(repo_layout)
        main_layout.addWidget(repo_group)

        # Buttons
        button_layout = QHBoxLayout()

        # Add repository button
        self.add_btn = QPushButton("添加仓库配置对")
        self.add_btn.clicked.connect(self.add_repository_pair)
        button_layout.addWidget(self.add_btn)

        # Delete repository button
        self.delete_btn = QPushButton("删除仓库配置对")
        self.delete_btn.clicked.connect(self.delete_repository_pair)
        self.delete_btn.setEnabled(False)
        button_layout.addWidget(self.delete_btn)

        # Modify repository button
        self.modify_btn = QPushButton("修改仓库配置对")
        self.modify_btn.clicked.connect(self.modify_repository_pair)
        self.modify_btn.setEnabled(False)
        button_layout.addWidget(self.modify_btn)

        # Git operations buttons
        self.add_commit_push_btn = QPushButton("Git Add/Commit/Push")
        self.add_commit_push_btn.clicked.connect(self.git_add_commit_push)
        button_layout.addWidget(self.add_commit_push_btn)

        self.pull_btn = QPushButton("Git Pull")
        self.pull_btn.clicked.connect(self.git_pull)
        button_layout.addWidget(self.pull_btn)

        button_layout.addStretch()
        main_layout.addLayout(button_layout)


    def load_repo_data(self, config_file=None):
        """Load repository data from the configuration using Config_parse.py"""
        if config_file is None:
            config_file = './Config_Address.json'

        try:
            config_parser = RepoConfigParser(config_file)
            if config_parser.local_paths is not None and config_parser.remote_urls is not None:
                self.local_repos = config_parser.local_paths
                self.remote_urls = config_parser.remote_urls
            else:
                print(f"Configuration parsing failed: {config_parser.error_message}")
                self.local_repos = []
                self.remote_urls = []
        except Exception as e:
            print(f"Error loading configuration: {e}")
            self.local_repos = []
            self.remote_urls = []

        # Initialize Git operation objects with the loaded data
        self.git_push_obj = GitPush_AutoGit(self.local_repos, self.remote_urls)
        self.git_pull_obj = GitPull_AutoGit(self.local_repos, self.remote_urls)

        self.refresh_repo_list()

    def refresh_repo_list(self):
        """Refresh the repository list display"""
        self.repo_data = []
        for i, (local_path, remote_url) in enumerate(zip(self.local_repos, self.remote_urls)):
            self.repo_data.append({
                'name': f"Repository {i+1}",
                'path': local_path,
                'url': remote_url
            })
        self.repo_list.clear()
        for repo in self.repo_data:
            item = QListWidgetItem(f"{repo['path']} -> {repo['url']}")
            self.repo_list.addItem(item)

    def on_repo_selected(self):
        """Handle repository selection"""
        current_item = self.repo_list.currentItem()
        if current_item:
            self.add_commit_push_btn.setEnabled(True)
            self.pull_btn.setEnabled(True)
            self.delete_btn.setEnabled(True)
            self.modify_btn.setEnabled(True)
        else:
            self.add_commit_push_btn.setEnabled(False)
            self.pull_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.modify_btn.setEnabled(False)

    def add_repository_pair(self):
        """Add a new repository pair"""
        # Get local repository path
        local_path = QFileDialog.getExistingDirectory(self, "选择本地仓库/目录")
        if not local_path:
            return

        # Get remote URL
        remote_url, ok = QInputDialog.getText(self, "远端URL", "请输入远程仓库 URL：")
        if not ok or not remote_url:
            return

        # Add to configuration
        self.local_repos.append(local_path)
        self.remote_urls.append(remote_url)
        self.repo_data.append({
            'name': os.path.basename(local_path),
            'path': local_path,
            'url': remote_url
        })
        self.save_config_to_file(self.config_file)
        self.refresh_repo_list()
        self.status_bar.showMessage("仓库配置对添加成功~", 3000)

    def delete_repository_pair(self):
        current_row = self.repo_list.currentRow()
        if current_row >= 0:
            repo = self.repo_data.pop(current_row)
            self.local_repos.pop(current_row)
            self.remote_urls.pop(current_row)
            self.save_config_to_file(self.config_file)
            self.refresh_repo_list()
            self.status_bar.showMessage(f"已删除仓库配置对: {repo['name']}！", 3000)

    def modify_repository_pair(self):
        current_row = self.repo_list.currentRow()
        print(current_row)
        if current_row >= 0:
            # Get local repository path
            Modi_local_path = QFileDialog.getExistingDirectory(self, "选择本地仓库/目录")
            if not Modi_local_path:
                return

            # Get remote URL
            Modi_remote_url, ok = QInputDialog.getText(self, "远端URL", "请输入远程仓库 URL：")
            if not ok or not Modi_remote_url:
                return
            
            repo = self.repo_data[current_row]
            self.local_repos[current_row] = Modi_local_path
            self.remote_urls[current_row] = Modi_remote_url
            self.save_config_to_file(self.config_file)
            self.refresh_repo_list()
            self.status_bar.showMessage("仓库配置对修改成功！", 3000)

    def git_add_commit_push(self):
        """Execute git add, commit, and push operations using the existing class"""
        try:
            # Create and show the output dialog
            self.output_dialog = GitOutputDialog(self)  
            self.Output_dialogWidth = 700   
            self.Output_dialogHeight = 500
            self.output_dialog.setGeometry(int((self.screen.width() - self.Output_dialogWidth) / 2), int((self.screen.height() - self.Output_dialogHeight) / 2), self.Output_dialogWidth, self.Output_dialogHeight)
            self.output_dialog.show()

            # Create a worker thread for the git operation
            self.git_worker = GitWorker("push", self.local_repos, self.remote_urls, self.git_push_obj)

            # Connect worker signals to dialog slots
            self.git_worker.output_signal.connect(self.output_dialog.append_output)
            self.git_worker.finished_signal.connect(lambda: self.output_dialog.append_output("Git 操作完成！ 可以关闭窗口啦~."))
            self.git_worker.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"执行Git添加/提交/推送操作失败: {str(e)}")

    def git_pull(self):
        """Execute git pull operations using the existing class"""
        try:
            # Create and show the output dialog
            self.output_dialog = GitOutputDialog(self)  
            self.Output_dialogWidth = 700   
            self.Output_dialogHeight = 500
            self.output_dialog.setGeometry(int((self.screen.width() - self.Output_dialogWidth) / 2), int((self.screen.height() - self.Output_dialogHeight) / 2), self.Output_dialogWidth, self.Output_dialogHeight)
            self.output_dialog.show()

            # Create a worker thread for the git operation
            self.git_worker = GitWorker("pull", self.local_repos, self.remote_urls, self.git_pull_obj)

            # Connect worker signals to dialog slots
            self.git_worker.output_signal.connect(self.output_dialog.append_output)
            self.git_worker.finished_signal.connect(lambda: self.output_dialog.append_output("Git 操作完成！ 可以关闭窗口啦~."))
            self.git_worker.start()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"执行Git拉取操作失败: {str(e)}")

    def browse_config_file(self):
        """Open a file dialog to select a configuration file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择配置文件", "", "JSON Files (*.json)")

        if file_path:
            self.config_file = file_path  # Update the config file path in the class
            self.config_file_input.setText(file_path)
            self.load_repo_data(file_path)

    def save_config_to_file(self, config_file=None):
        """Save the current repository configuration to a JSON file"""
        if config_file is None:
            config_file = './Config_Address.json'

        # Prepare the data structure
        repo_list = []
        for local_path, remote_url in zip(self.local_repos, self.remote_urls):
            repo_list.append({
                'local_path': local_path,
                'remote_url': remote_url
            })

        # Create the full configuration structure
        config_data = {
            'repositories': repo_list
        }

        # Write to file
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, ensure_ascii=False, indent=2)
            self.status_bar.showMessage(f"配置已保存到 {config_file}", 3000)
        except Exception as e:
            self.status_bar.showMessage(f"保存配置时出错: {str(e)}", 3000)

    def ShowGitOutputDialog(self):
        if self.is_git_installed() and self.is_git_email_configured():
            msg = "Git已经安装，且邮箱配置正确，尽情使用把~"
            print(msg)
            self.status_bar.showMessage(msg, 3000)
            pass
        else:
            print("Git未安装或邮箱未配置，强制提示用户安装Git并配置账户信息！")
            self.msgBox = QMessageBox()
            self.msgBox.setIcon(QMessageBox.Information)
            self.msgBox.setText("请确保Git安装，并配置好了账户信息，否则无法使用！")
            self.msgBox.setWindowTitle("强制提示")
            self.msgBox.setStandardButtons(QMessageBox.Ok)
            self.msgBox.finished.connect(self.closeWindow)
            self.msgBox.exec_()

    def is_git_installed(self):
        # Check if Git is installed by running 'git --version'
        try:
            subprocess.run(['git', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def is_git_email_configured(self):
        try:
            # 调用git命令获取邮箱配置
            result = subprocess.run(['git', 'config', 'user.email'], capture_output=True, text=True, check=True)
            # 如果邮箱配置存在，则返回True
            if result.stdout.strip():
                return True
            else:
                return False
        except subprocess.CalledProcessError:
            # 如果git命令执行失败（例如git不在环境变量中），返回False
            return False

    def closeWindow(self, event):
            # 直接强制退出，不响应系统的关闭事件
            os._exit(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GitToolApp()
    window.show()
    window.ShowGitOutputDialog()
    window.init_ui_heavy()
    window.load_repo_data(window.config_file)
    sys.exit(app.exec_())