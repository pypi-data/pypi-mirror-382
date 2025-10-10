from setuptools import setup, find_namespace_packages
import byzh

setup(
    name='byzh-ai',
    version=byzh.__version__,
    author="byzh_rc",
    description="更方便的深度学习",
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    packages=find_namespace_packages(include=["byzh.*"]),
    install_requires=[
        'byzh-core>=0.0.9.0', # !!!!!
        # 'thop', # 自己装
        # 'matplotlib',
        # 'seaborn',
    ],
)
