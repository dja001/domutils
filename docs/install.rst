

Installation
----------------------

- Conda installation is probbly the easiest.

  .. code-block:: bash
  
     conda install -c dja001 domutils 

  Recent versions of cartopy have got super slow, I recommend the following combination
  for decent speed. 

    * cartopy=0.19.0.post1 
    * matplotlib=3.3.4

- Pip installation should also work

  .. code-block:: bash
  
     pip install domutils

- To use the domutils modules in your python code, load the different modules separately. 
  For example:

  >>> import domutils.legs as legs            #doctest:+SKIP 
  >>> import domutils.geo_tools as geo_tools  #doctest:+SKIP 



