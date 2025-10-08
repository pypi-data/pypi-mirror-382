from setuptools import setup


# 手动指定包，避免自动发现locales目录
packages = [
    "IdeaSearch_fit",
    "IdeaSearch_fit.miscellaneous",
    "IdeaSearch_fit.utils",
]

setup(
    name = "IdeaSearch-fit",
    version = "0.0.3",
    packages = packages,
    description = "Extension of IdeaSearch for data fitting",
    author = "parkcai",
    author_email = "sun_retailer@163.com",
    url = "https://github.com/IdeaSearch/IdeaSearch-fit",
    include_package_data = False,
    package_data = {
        "IdeaSearch_fit": [
            "locales/*/LC_MESSAGES/*.mo",
            "locales/*/LC_MESSAGES/*.po",
            "locales/*.pot",
        ],
    },
    python_requires = ">=3.8",
    install_requires = [
        "numpy>=1.21.0",
        "numexpr>=2.7.0",
        "pywheels>=0.6.6",
    ],
)
