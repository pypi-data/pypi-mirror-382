Usage from the Zope ZMI
=======================

The following screen shots show how to use this product through the web in
the :term:`Zope` :term:`ZMI`. 

.. contents::

Adding a MemCache Proxy
-----------------------
Choose `MemCache Proxy` from the drop-down list at the top right.

.. image:: screen01.png

On the add form, give it a memorable name, e.g., `mcproxy`.

.. image:: screen02.png

Click on the new `mcproxy` object and configure it using the
`Properties` :term:`ZMI` tab.  Set the `servers` property to a list of
servers, one per line, where each line is in the format ``<host>:<port>``.
For instance, to use the `memcached` server running on the default port on
your local machine, the value would be ``localhost:11211``.

.. image:: screen03.png


Adding a MemCache Session Data Container
----------------------------------------
At the root of the :term:`ZMI`, choose `MemCache Session Data Container`
from the drop-down list at the top right.

.. image:: screen04.png

On the add form, give it a memorable name, e.g., `mcsdc`.

.. image:: screen05.png

Click on the new `msdc` object and configure it using the `Properties`
:term:`ZMI` tab. Use the `MemCache Proxy` object you created above
(``/mcproxy``).

.. image:: screen06.png


Configuring Zope sessions and testing
-------------------------------------
Finally, on the main tab of your ``session_data_manager`` instance
(typically also in the root of the :term:`ZMI`), change the
`Transient Object Container Path` value to match the location of your new
`MemCache Session Data Container`, e.g. ``/mcsdc``.

.. image:: screen07.png

You can test the memcached configuration on the
`MemCache Session Data Container` "Test" tab in the ZMI.  Enter one or more
lines describing key-value pairs, where the "key" for your session is
separated from the value by the first space character.  Note that the session
values are displayed below the form.

.. image:: screen08.png
