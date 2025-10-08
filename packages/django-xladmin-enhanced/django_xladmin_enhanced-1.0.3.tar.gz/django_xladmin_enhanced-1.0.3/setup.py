from setuptools import setup, find_packages
import os

# Read the contents of your README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='django-xladmin-enhanced',
    version='1.0.3',
    description='Enhanced Django xAdmin - A modern admin interface for Django',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Enhanced Team',
    author_email='enhanced@example.com',
    url='https://github.com/enhanced-team/django-xladmin-enhanced',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 3.2',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    python_requires='>=3.8',
    install_requires=[
        'Django>=3.2',
        'django-crispy-forms>=1.14.0',
        'django-import-export>=2.8.0',
        'django-reversion>=5.0.0',
        'future>=0.18.2',
        'httplib2>=0.20.4',
        'six>=1.16.0',
        'Pillow>=9.0.0',
        'xlwt>=1.3.0',
        'xlsxwriter>=3.0.0',
    ],
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'pytest-django>=4.5.0',
            'coverage>=6.0.0',
        ],
    },
    keywords='django admin xladmin enhanced interface',
    project_urls={
        'Bug Reports': 'https://github.com/enhanced-team/django-xladmin-enhanced/issues',
        'Source': 'https://github.com/enhanced-team/django-xladmin-enhanced',
        'Documentation': 'https://django-xladmin-enhanced.readthedocs.io/',
    },
)