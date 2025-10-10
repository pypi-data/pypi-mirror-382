import setuptools

with open("README.md", "r", encoding='utf-8') as f:
    long_description = f.read()

setuptools.setup(
    name='zaishiyishihejidatabase',
    version='0.0.1',
    author='王梓明',
    author_email='1272660211@qq.com',
    description='王梓明作品展示页',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='',
    packages=setuptools.find_packages(),
    include_package_data=True,
    package_data={
        'zaishiyishihejidatabase': ['db.sqlite3', 'favicon.ico']
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'Flask==3.1.2',
        'SQLAlchemy==2.0.43',
    ],
)