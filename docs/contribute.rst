
New feature, bug fix, etc. 
------------------------------------

If you want **domutils** to be modified in any way, start by opening an issue
on github. 

   #. Create an issue on *domutils* `github <https://github.com/dja001/domutils>`_ page. 
      We will discuss the changes to be made and define a strategy for doing so. 

   #. Once the issue is created, fork the project. This will create your own github repo where 
      you can make changes. 

   #. On your computer, clone the source code and go in the package 
      directory

        .. code-block:: bash

           git clone git@github.com:<your-username>/domutils.git 
           cd domutils

   #. Create a new branch whose name is related to the issue you opened at step 1 above.   
      For example:

        .. code-block:: bash

           git checkout -b #666-include-cool-new-feature

   #. Create a clean `Anaconda <https://wiki.cmc.ec.gc.ca/wiki/Anaconda>`_ development environment 
      and activate it. 
      You will need internet access for this.

        .. code-block:: bash

           conda env create --name domutils_dev_env -f docs/environment.yml
           conda activate domutils_dev_env
   
   #. It is a good practice to start by writing a unit test that will pass once your feature/bugfix
      is correctly implemented. Look in the 

        .. code-block:: bash

           test/

      directories of the different _domutils_ modules for examples of such tests.


   #. Modify the code to address the issue. Make sure to include examples and/or tests in the docstrings.  

   #. If applicable, describe the new functionality in the documentation.

   #. Modify the files:

        .. code-block:: bash

           VERSION
           CHANGELOG.md

      To reflect your changes.

   #. Run unittest
        
        .. code-block:: bash
        
            python -m unittest discover

   #. Run doctest

        .. code-block:: bash

           cd docs
           make doctest
      
      Make sure that there are no failures in the tests.

      Note that the first time you run this command internet access is required as the test data 
      will be downloaded from `zenodo <https://doi.org/10.5281/zenodo.3642234>`_ . 

   #. If you modified the documentation in functions docstrings, you probably want to check the 
      changes by creating your local version of the documentation.

        .. code-block:: bash
      
           cd docs
           make html

      You can see the output in any web browser 
      pointing to:

        .. code-block:: bash
  
           domutils/docs/_build/html/

   #. While you are working, it is normal to commit changes several times on you local branch. 
      However, before you push to your fork on github, it is probably a good idea to 
      `squash <https://blog.carbonfive.com/2017/08/28/always-squash-and-rebase-your-git-commits/>`_
      all you intermediate commits into one, or a few commits, that clearly link to the issue 
      being worked on. 
      The resulting squashed commit  should pass the tests. 

   #. Once you are happy with the modifications, push the new version
      on your fork on github

        .. code-block:: bash

           git push -u origin #666-include-cool-new-feature

   #. From the github web interface, create a pull request to me. We will then 
      discuss the changes until they are accepted and merged into the master branch. 


Test data
------------------------------------

Data used in the examples and for running tests can be obtained by running 

    .. code-block:: bash
    
       ./scripts/download_test_data.sh       

in the main directory of this package. This creates a *test_data/* directory 
containing all the test data. 

    

Documentation assets
------------------------------------

Two static directories feed the documentation and they are not interchangeable:

*docs/_static/*
   The reference figures, downloaded from the zenodo archive. It is **erased and
   repopulated on every build** by *scripts/download_test_data.sh*, so anything
   written there by hand is lost. It is also in *.gitignore*.

*docs/_static_custom/*
   The hand written assets, currently the style sheet and the script making code
   blocks collapsible. This one is versioned.

Sphinx merges both into the single *_static/* directory of the generated site,
so urls are the same either way.

Collapsible code blocks
------------------------------------

Long listings that a reader can safely skip, plotting helpers and figure setup
for instance, can be folded behind a *Show code* toggle by giving them the
*collapse-code* class:

    .. code-block:: rst

       .. literalinclude:: ../domutils/radar_tools/tests/test_radar_tutorial.py
          :language: python
          :class: collapse-code
          :start-after: DOCS:plot_img_begins
          :end-before: DOCS:plot_img_ends

Folding is opt in, a block is only collapsed when it asks to be. To instead fold
every long block automatically, set *AUTO_COLLAPSE_LINES* in
*docs/_static_custom/collapsible_code.js* to a number of lines; individual blocks
can then be kept unfolded with *:class: no-collapse-code*.
