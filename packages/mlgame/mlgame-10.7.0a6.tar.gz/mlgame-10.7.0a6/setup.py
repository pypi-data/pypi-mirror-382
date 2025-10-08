import sys

import setuptools

# readme.md = github readme.md, 這裡可接受markdown寫法
# 如果沒有的話，需要自己打出介紹此專案的檔案，再讓程式知道
sys.path.append(r".")
import mlgame.version

with open("README.md", "r") as fh:
    long_description = fh.read()

def _read_requirements(file_path: str) -> list:
    requirements = []
    try:
        with open(file_path, "r") as rf:
            for raw_line in rf:
                line = raw_line.strip()
                if not line or line.startswith("#"):
                    continue
                if line.startswith(("-r", "--requirement")):
                    # support nested requirement files: -r other.txt
                    parts = line.split(maxsplit=1)
                    if len(parts) == 2:
                        requirements.extend(_read_requirements(parts[1]))
                    continue
                if line.startswith(("-e", "--editable")):
                    # ignore editable installs
                    continue
                requirements.append(line)
    except FileNotFoundError:
        # 如果發佈包中沒有 requirements.txt，不要阻斷安裝流程
        requirements = []
    return requirements

setuptools.setup(
    name="mlgame",  #
    version=mlgame.version.version,
    author="PAIA-Tech",
    author_email="service@paia-tech.com",
    description="A machine learning game framework based on Pygame",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/PAIA-Playful-AI-Arena/MLGame",
    packages=setuptools.find_packages(
        exclude=["tests"]
    ),
    classifiers=[
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.10.0, <3.13.0',
    include_package_data=True,
    keywords=["AI", "machine learning", 'game', 'framework'],

    install_requires=_read_requirements("requirements.txt")

)
