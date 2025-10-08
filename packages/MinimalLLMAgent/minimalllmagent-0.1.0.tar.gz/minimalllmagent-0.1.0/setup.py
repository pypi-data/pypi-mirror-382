from setuptools import setup, find_packages

setup(
    name                          = "MinimalLLMAgent",                              # 包名
    version                       = "0.1.0",                                        # 版本号
    author                        = "Yue Lin",                                      # 作者名字
    author_email                  = "linyue3h1@gmail.com",                          # 作者邮箱
    description                   = "A minimal LLM agent with memory management.",                # 简短描述
    long_description              = open("README.md").read(),                       # 长描述，通常是README文件
    long_description_content_type = "text/markdown",                                # 长描述内容的格式，这里为Markdown
    url                           = "https://github.com/YueLin301/min_llm_agent", # 项目的URL，通常是GitHub的URL
    packages                      = find_packages(where='src'),
    package_dir                   = {'': 'src'},
    install_requires              = [
        "LyPythonToolbox==0.1.4",
        "openai==2.2.0", 
    ],
    classifiers=[
        "Programming Language :: Python :: 3",  # 3.x
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",  # suitable for any OS.
    ],
)