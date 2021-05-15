from setuptools import setup

setup(
    name="s-tool",
    version="1.0.0",
    description="Custom serializers for TOML and JSON,"
                + " other two are based on defaults.",
    packages=["serializers"],
    python_requires=">=3.8",
    author="Alexey Lavrenovich",
    author_email="lavrenovichae@gmail.com",
    entry_points={
        "console_scripts": [
            "convert = serializers.main:main"
            ]
        }
    )
