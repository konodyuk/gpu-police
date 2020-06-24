import setuptools

setuptools.setup(
    name="gpu-police",
    version="0.0.1",
    author="Nikita Konodyuk",
    author_email="konodyuk@gmail.com",
    description="Simple tool for setting rules on a multi-GPU server",
    url="https://github.com/konodyuk/gpu-police",
    packages=setuptools.find_packages(),
    install_requires=[
        "rich",
        "toml",
        "click",
        "python-box",
        "gspread",
    ],
    entry_points={
        "console_scripts": ["gpu-police=gpu_police.cli:cli", "wtf-police=gpu_police.cli:wtf"]
    },
    include_package_data=True
)
