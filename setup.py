from distutils.core import setup
    
setup(
    name = 'sgt',      
    packages = ['sgt'],   
    # package_data={'sgt': ['scripts/*.csv', 'scripts/*.md']},
    version = '0.0.0',   
    license='MIT',        
    description = 'SGT is a collection of python function for the processing of geographical data',  
    author = 'Pierrick Rambaud',                   
    author_email = 'pierrick.rambaud49@gmail.com',  
    url = 'https://github.com/12rambau/sepal_geospatial_toolkit',
    download_url = 'https://github.com/12rambau/sepal_geospatial_toolkit/archive/v_0.0.0.tar.gz',
    keywords = ['Python', 'sepal', 'geospatial'], 
    install_requires=[
        'geopandas',
        'rasterio',
        'coverage',
        'scipy',
        'numpy',
        'pandas',
        'geocube'
    ],
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',  
        'Programming Language :: Python :: 3.6',
    ],
)
