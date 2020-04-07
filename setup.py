import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
        name='dpymenus',
        version='0.1.9',
        author='Rob Wagner',
        author_email='rob.wagner@outlook.com',
        description='Dynamic, composable dpymenus for use with the discord.py library.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/robertwayne/dpymenus',
        packages=setuptools.find_packages(),
        classifiers=[
            'Programming Language :: Python :: 3.8',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Typing :: Typed',
            'Topic :: Communications :: Chat',
            'Intended Audience :: Developers',
            'Development Status :: 4 - Beta',
        ],
        python_requires='>=3.8',
)
