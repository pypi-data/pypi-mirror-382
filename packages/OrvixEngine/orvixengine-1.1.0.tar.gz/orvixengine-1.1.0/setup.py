from setuptools import setup, find_packages

setup(
    name='OrvixEngine',
    version='1.1.0', 
    packages=find_packages(),
    
    install_requires=[
        'pygame >= 2.0.0', 
    ],
    
    description='OrvixEngine: The modular 2D Game Engine SDK built on Pygame for rapid development.',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    
    author='ORVIX GAMES',
    author_email='help@orvixgames.com',
    maintainer='ORVIX GAMES Geliştirme Ekibi',
    license='MIT',
    
    # ✨ Düzeltildi: Sadece HTTP/HTTPS URL'leri kullanıldı
    project_urls={
        'Homepage': 'https://orvixgames.com/modul/orvix-engine-sdk/',
        'Documentation': 'https://orvixgames.com/modul/orvix-engine-sdk/docs', 
        'Issue Tracker': 'https://orvixgames.com/support/issues', 
        'Support': 'https://orvixgames.com/support', 
        'Source Code': 'https://orvixgames.com/modul/orvix-engine-sdk/source',
    },
    
    classifiers=[
        'Development Status :: 4 - Beta',
        
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Topic :: Software Development :: Libraries',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Arcade',
        
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12', 
    ],
    keywords='game-engine 2d pygame platformer physics sdk modular framework',
)