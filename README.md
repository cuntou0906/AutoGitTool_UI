# AutoGitTool

这是一个使用PyQt5开发的可视化Git工具应用程序，用于本地Git仓库和远程仓库的协同。

## 功能特性

1. **仓库配置对管理** - 显示本地仓库路径和对应的远程URL
2. **Git操作按钮** - 提供一键执行Git Add/Commit/Push和Git Pull操作
3. **添加仓库对** - 可以添加、修改、删除本地仓库路径和远程URL配置对，支持配置文件方式

## 使用方法

1. 运行应用程序：
   ```
   python AutoGitTool.py
   ```

2. 应用程序将显示当前配置的仓库配对列表

3. 选择一个仓库对，然后点击以下按钮之一：
   - "Git Add/Commit/Push" - 执行添加、提交和推送操作
   - "Git Pull" - 执行拉取操作
   - "添加" - 添加新的仓库配对
   - "修改" - 修改新的仓库配对
   - "删除" - 删除新的仓库配对

## 配置文件

仓库路径和URL存储在 `Config_Address.json` 文件中，并于`UI`页面的仓库对同步，包含多项，每一项包含两个值：
- `local_repos`: 本地仓库路径
- `remote_urls`: 对应的远程仓库URL

## 与现有脚本集成

该应用程序与以下现有脚本集成：
- `git_Add_Commit_Push_operations.py` - 执行Git添加、提交和推送操作
- `git_Pull_operations.py` - 执行Git拉取操作

## 依赖

- 详见`uv`的`pyproject.toml`

## 打包EXE

​	1. 安装依赖并打包

```bash
pip install pyinstaller

# 已经打包过一次就可以不用运行这个，直接修改`AutoGitTool.spec`文件
pyinstaller -D --onefile --name=AutoGitTool --windowed AutoGitTool.py  
pyinstaller -D -w --clean --noconfirm --onefile --name=AutoGitTool --icon=Img/AutoGitTool_Logo.ico  AutoGitTool.py
```

​	2. 链接资源文件，即修改生成的AutoGitTool.spec`中的`Analysis`部分：

```bash
a = Analysis(
    ...
    datas=[('Img/*.png', 'Img'),('Img/*.ico', 'Img')],
    ...
)
```

 3. 重新打包

    ```bash
    pyinstaller .\AutoGitTool.spec
    ```

 4. 运行`dist`目录下的`AutoGitTool.exe`。