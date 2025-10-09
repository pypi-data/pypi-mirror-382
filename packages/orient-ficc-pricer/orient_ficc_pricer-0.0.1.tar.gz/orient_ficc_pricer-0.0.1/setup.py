from setuptools import setup


VERSION = "0.0.1"


setup(name="orient_ficc_pricer",
      version=VERSION,
      author="zhanghongyu",
      description="orient securities ficc option pricing module",
      python_requires=">=3.7",
      include_package_data=True,
      platforms="any",
      install_requires=['numpy', 'scipy', 'pandas', 'numba_stats']
      )


# py -m pip install --upgrade setuptools wheel
# py -m pip install twine
# pip list | findstr numpy


# 删除dist\build中旧的文件 在terminal中运行
# py setup.py sdist bdist_wheel
# py -m twine upload .\dist\* --repository-url=http://10.17.75.129:9001
# py -m twine upload .\dist\* --repository-url=http://10.3.212.1:9001 -u user -p pypi2023
# py -m twine upload dist/*
# user, pypi2023
# pip install ht-option-pricer --upgrade -i http://10.17.75.129:9001 --trusted-host 10.17.75.129
# pip install ht-option-pricer --upgrade -i http://10.3.212.1:9001 --trusted-host 10.3.212.1
# pip install ht-option-pricer==0.0.1 -i http://10.3.212.1:9001 --trusted-host 10.3.212.1

# pip uninstall ht-option-pricer
# pip install ht_option_pricer==0.1.10 -i http://10.3.212.1:9001 --trusted-host 10.3.212.1
