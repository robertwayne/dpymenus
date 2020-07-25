import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
        name='dpymenus',
        version='0.3.4',
        author='Rob Wagner',
        author_email='rob.wagner@outlook.com',
        license='License :: OSI Approved :: MIT License',
        description='Dynamic, composable menus and polls for use with the discord.py library.',
        long_description=long_description,
        long_description_content_type='text/markdown',
        url='https://github.com/robertwayne/dpymenus',
        packages=setuptools.find_packages(),
        classifiers=[
            'Programming Language :: Python :: 3.9',
            'Operating System :: OS Independent',
            'Typing :: Typed',
            'Topic :: Communications :: Chat',
            'Intended Audience :: Developers',
            'Development Status :: 4 - Beta',
        ],
        python_requires='>=3.8',
)
