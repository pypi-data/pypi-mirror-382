from setuptools import setup, find_packages

setup(
    name='OrvixEngine',
    version='0.0.2',  
    packages=find_packages(),
    
    # Kütüphane Bağımlılıkları
    install_requires=[
        'pygame',
    ],
    
    # Temel Paket Bilgileri
    description='OrvixEngine: Full-featured modular 2D game engine SDK',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    
    # Yapımcı ve İletişim Bilgileri
    author='ORVIX GAMES',
    author_email='help@orvixgames.com',
    maintainer='ORVIX GAMES Geliştirme Ekibi',
    license='MIT',
    url='https://orvixgames.com/modul/orvix-engine-sdk/', 
    
    # PyPI Sınıflandırıcıları (geçerli olanlar)
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    keywords='game-engine 2d pygame',
)
