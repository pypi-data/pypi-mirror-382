from pathlib import Path
from setuptools import find_namespace_packages, setup

# Load packages from requirements.txt
BASE_DIR = Path(__file__).parent
with open(Path(BASE_DIR, "requirements.txt"), "r") as file:
    required_packages = [ln.strip() for ln in file.readlines()]

# Define our package
setup(
    name="CloudApiRequest",
    version="1.1.0",
    author="天润-测试",
    author_email="wangwd@ti-net.com.cn",
    description="天润cloud接口测试库",
    url="https://www.ti-net.com.cn/",
    packages=find_namespace_packages(),
    python_requires=">=3.7",
    install_requires=[required_packages],
    license='MIT',
) 



#username = wangwdcloud
# password = Showmethe1$
# python setup.py sdist bdist_wheel
# twine upload dist/*
# twine upload --repository pypi --config-file .pypirc dist/*
# 账号: __token__
# 密码:pypi-AgEIcHlwaS5vcmcCJDQ3MzE3NjEwLTRhOTAtNDJiMS1iMDA0LTI2YjRhMzFjYjBiYgACKlszLCI1OWUxNWIyOS03YzdjLTRjYjYtYTJhNi1iMGY0MjY5MzNlODEiXQAABiC_1cRv1u_OI0Fsfu1qZtfiY997IU9O5VW0O-bp0t-QtQ
#PyPI recovery codes
#72b1f58861b20b08
#eb2b2e56ddf63156
#820eb7c177cfe576
#215154af293893bd
#e861fc2baf4a5f2b
#375d18d1b89de79e
#113714d7f812d237
#7be81361e84c2f1f


# username = wangwdcloud
# password = Showmethe1$
# python setup.py sdist bdist_wheel
# twine upload dist/*
# twine upload --repository testpypi --config-file .pypirc dist/*
# 账号: __token__
# 密码:pypi-AgENdGVzdC5weXBpLm9yZwIkNmMyOTg0NWEtZDg2Yi00OGVlLWJiZDAtNzAyZGU0Y2RlMWUyAAIqWzMsIjFhOGNjODUyLTkwNjItNDU5Yi1hNjQzLWI4MTI4YzlkZTYxMSJdAAAGIFu7HNytLTHb6caaWeQIX19QIufLfT4rEUxYMN-EgmI5
#testPyPI recovery codes
#e7d4638b0e6e38c0
#b8e69995b38c13e2
#9db436d2b3d1f20f
#5e312d3f97ee177e
#e3cc8debde6a47cc
#aed38c17471f4e45
#7798c75dabc853d6
#bc7fb28eaaa48a27