from setuptools import setup, find_packages

long_description = ''
with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='stardewModPY',
    version='0.3.11',
    packages=find_packages(include=['StardewValley', 'StardewValley.*']),
    install_requires=[
        'prettytable'
    ],
    author='alichan',
    author_email='suportestardewmodspy@gmail.com',
    description='Uma biblioteca para gerar mods com packs de conteúdo em json para Stardew Valley',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',  # O URL do repositório do seu projeto
    project_urls={
        "Documentação": "http://stardewmodpy.kya.app.br/",
        "Suporte": "https://discord.gg/Pxj3EDafsv"
    },
    entry_points={
        'console_scripts': [
            'sdvpy = StardewValley.create:main'
        ]
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.12',
)
