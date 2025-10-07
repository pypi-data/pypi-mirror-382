Emeral is a Python package for creating small games, developed based on Pygame, with the aim of changing the loop-refresh method to a multithreaded approach. The Emeral library is suitable for making 2D games and currently has four modules: display, events, image, and entity, with more modules planned for development. Emeral is currently in the beta version.


Installation
============

Before downloading the Emeral library, you must ensure that Python is already installed on your computer, and the Python version should be above 3.7. Version 3.7 is only the minimum requirement, and some advanced functions may not be available when using it. Once you have installed Python, you can use the following command to install the Emeral library from the command line.

.. code-block:: bash

   pip install emeral

After installing the Emeral library, you can use the following command to ensure that the library was installed successfully.

.. code-block:: bash

   pip list

If the Python library 'emeral' appears in the list, it means you have successfully installed it.


Help
====

Our documentation is actively being written. To view the basic help documentation, please write the following code in your Python program.

.. code-block:: python

   import emeral
   help(emeral)


Quick Start
===========

· Basic framework:

.. code-block:: python

   import emeral

   window=emeral.display.Window() # Create a window object.

   room=emeral.display.Room(window) # Create a room on the window.
   room.set_caption("NewGame") # Set caption for the room, which will show on title bar.
   room.switch() # Switch to the window.

   window.listen() # Window Mainloop.

· Create a Animation of sprite and show it on window

.. code-block:: python

   import emeral

   window=emeral.display.Window() # Create a window.

   room=emeral.display.Room(window) # Create a room.
   room.switch()

   img=emeral.image.Animation(path="xxx.gif")
   sp=emeral.entity.Sprite(room,img,position=(100,100)) # Create a sprite object.

   emeral.events.When(window,emeral.events.EACH_FRAME_STEP()).do(lambda:sp.next_texture()) # Change to next texture.

   window.listen() # Mainloop.


Changelog
=========

· 0.8.0 beta version : Develop the four main Python packages and have the ability to create basic games.

· 0.8.2 beta version : Fixed the bug that prevented packages from being imported.

· 0.8.5 beta version : Added some methods to the Sprite object, and added a Camera object to the display module.


License
=======
MIT License - Check the LICENSE file for details.