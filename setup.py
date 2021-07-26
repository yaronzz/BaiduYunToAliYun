from setuptools import setup, find_packages
from b2a.__init__ import VERSION

setup(
    name='b2a',
    version=VERSION,
    license="MIT",
    description="迁移百度云到阿里云",

    author='Yaronzz',
    author_email="yaronhuang@foxmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["aigpy", "requests", "tqdm", "prettytable", "Cython", "BaiduPCS-Py"],
    entry_points={'console_scripts': ['b2a = b2a:main', ]}
)
