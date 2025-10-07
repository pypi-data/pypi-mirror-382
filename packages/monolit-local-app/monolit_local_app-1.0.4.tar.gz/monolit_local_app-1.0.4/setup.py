from io import open
from setuptools import setup

version = "1.0.4"

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="monolit_local_app",
    version=version,

    author="Ars2011",
    author_email="arseniylazarev2011@yandex.ru",

    description="Simple package for fast writing local sites and desktop apps, with html, css and javascript",
    long_description=long_description,
    long_description_content_type="text/markdown",

    url="https://github.com/arseniylazarev7-ctrl/Monolit",
    download_url="https://github.com/arseniylazarev7-ctrl/Monolit/archive/v{}.zip".format(version),

    license="MIT",

    packages=["monolit_local_app"],
    install_requires=["flask"],

    classifiers=[
        #"Development Status :: 4 - Beta",  # Или на какую стадию больше похоже
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Software Development :: User Interfaces", # Добавил, так как для UI
        "Topic :: Desktop Environment", # Добавил, так как для десктопных приложений
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12", # Добавил, если поддерживается
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',  # Укажи минимальную версию Python
    keywords='web, desktop, application, framework, local', # Добавил ключевые слова
    project_urls={ # Добавил ссылки на проект
        'Documentation': 'https://github.com/arseniylazarev7-ctrl/Monolit/blob/main/README.md', # Если есть документация
        'Source': 'https://github.com/arseniylazarev7-ctrl/Monolit',
    },
)