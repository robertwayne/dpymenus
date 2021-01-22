import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
        name='dpymenus',
        version='1.3.1',
        author='Rob Wagner',
        author_email='rob.wagner@outlook.com',
        license='MIT',
        description='Simplified menus for discord.py developers.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/robertwayne/dpymenus',
        packages=setuptools.find_packages(),
        classifiers=[
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Typing :: Typed',
            'Topic :: Communications :: Chat',
            'Intended Audience :: Developers',
            'Development Status :: 5 - Production/Stable',
        ],
        python_requires='>=3.7',
        install_requires=[
            'discord.py>=1.6.0',
            'emoji==0.6.0'
        ]
)
