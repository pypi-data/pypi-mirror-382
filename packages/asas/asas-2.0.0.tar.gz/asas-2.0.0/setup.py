from setuptools import setup, find_packages

setup(
    name="asas",
    version="2.0.0",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'asas': ['usercustomize.py'],
    },
    description="# The asas library in Python prints the text written inside it, like the print function.\n# Telegram  :  @LAEGER_MO\npip install asas",
    author="Programmer Seo Hook : @LAEGER_MO : @sis_c",
)