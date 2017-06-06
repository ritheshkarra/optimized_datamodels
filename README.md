# datamodels
Algorithms

 [Falcon](https://github.com/falconry/falcon) framework. Uses [gunicorn](https://github.com/benoitc/gunicorn) as the WSGI HTTP server and [meinheld](https://github.com/mopemope/meinheld) as the gunicorn worker.


## Server deployment nosetests

Installing Falcon in ubuntu server : [Here](https://www.digitalocean.com/community/tutorials/how-to-deploy-falcon-web-applications-with-gunicorn-and-nginx-on-ubuntu-16-04)

To run the tests:

```
$ nosetests -v
```

## API Documentation
 [Main Page](https://github.com/paradigmC/opendata-falcon-app/blob/master/api_doc/main.md)

===============
##Installations
==============
## The below modules and packages were mandatory to run the atlantis Gunicorn server and APP.

#Python version

-> python >3

# Install below Python modules required to run APP. You can install the below packages using PIP(eg. pip install falcon).

-> falcon>=1.0   

                Falcon is a minimalist WSGI library for building speedy web APIs and app backends.

-> gunicorn>=19.6  
         
                 GreenUnicorn is a Python WSGI HTTP Server for UNIX. It's a pre-fork worker model.

->  meinheld>=0.5   

                 Meinheld is a high-performance WSGI-compliant web server.

->  pandas>=0.20.1  
     
                 Pandas is an open source and easy-to-use data structures and data analysis tools for the Python programming language.

->  ipython>=6.0.0 

                  IPython is a command shell for interactive computing in multiple programming languages, originally developed for the Python programming language, that offers introspection, rich media, shell syntax, tab completion, and history.


->  psycopg2>=2.7.1
  
                 It is the PostgreSQL database adapter for the Python programming language. Its main features are the complete implementation of the Python DB API 2.0 specification and the thread safety (several threads can share the same connection). It was designed for heavily multi-threaded applications that create and destroy lots of cursors and make a large number of concurrent INSERTs or UPDATEs.

->  statsmodels>=0.8.0

                It is a Python module that provides classes and functions for the estimation of many different statistical models, as well as for conducting statistical tests, and statistical data exploration.

-> sklearn>=0.18.1

              scikit-learn. Machine Learning in Python. Simple and efficient tools for data mining and data analysis.

-> logbook>=1.0.0

              Logbook is a logging system for Python that replaces the standard library’s logging module.

-> thermo>=0.1.33

              Thermo is open-source software for engineers, scientists, technicians and anyone trying to understand the universe in more detail. It facilitates the retrieval of constants of chemicals, the calculation of temperature and pressure dependent chemical properties (both thermodynamic and transport), the calculation of the same for chemical mixtures (including phase equilibria), and assorted information of a regulatory or legal nature about chemicals.


-> folium>=0.3.0

                 Folium makes it easy to visualize data that’s been manipulated in Python on an interactive Leaflet map. It enables both the binding of data to a map for choropleth visualizations as well as passing Vincent/Vega visualizations as markers on the map.          

->   matplotlib>=2.0.2

               Matplotlib is a Python 2D plotting library which produces publication quality figures in a variety of hardcopy formats and interactive environments across platforms. Matplotlib can be used in Python scripts, the Python and IPython shell, the jupyter notebook, web application servers, and four graphical user interface toolkits.

->  tweepy>=3.5.0

          It is a python library for accessing the Twitter API.

-> nose>=1.3

          It’s is a fairly well known python unit test framework, and can run doctests, unittests, and “no boilerplate” tests.

-> pyopenssl - SSL for python

-> pyasn1 

-> ndg-httpsclient


-> python3-tk
             
                Install tkinter package.The tkinter package (“Tk interface”) is the standard Python interface to the Tk GUI toolkit. It is a thin object-oriented layer on top of Tcl/Tk. 

                                          apt-get install python3-tk
====================
Status Codes:
====================
200 - OK
     The request is succesfull

204 - No content
      No data available for requested resource
            
400 - Bad Request
     The requested URL is malformed or trying to fetch data with wrong request

404 - Not Found
      Requested resource not found issue

500 - Internal Server Error
      Issue while executing the resource(Run time errors)

503 - Service Unavailable
      If the service is unavilable

408: Request Time Out
     If the request resource timed out like DB connections, server connections

