# 翻译智能体使用说明

## 第一步：拉取当前代码

使用管理员权限在指定的目录打开Powershell，输入下面的命令：
```
git clone https://github.com/EasonAndLily/AiTranslateAgent.git
```

## 第二步：进入当前仓库：AiTranslateAgent

使用Powershell命令进入当前项目：
```
cd AiTranslateAgent
```

## 第三步：配置Config文件

复制需要翻译的文件到当前根目录下面，修改`config.py`文件，更改其文件名称，sheet名称，翻译的模式等。

## 第四步：执行PS文件来翻译

使用Powershell命令运行下面脚本：
```
translate.ps1
```

## 注意事项：

如果你的Powershell不支持运行PS脚本，请执行如下命令解除限制：
```
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
```
