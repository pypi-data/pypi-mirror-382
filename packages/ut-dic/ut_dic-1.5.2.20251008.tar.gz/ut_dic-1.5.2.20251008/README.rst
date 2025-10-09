######
ut_dic
######

********
Overview
********

.. start short_desc

**Utilities for Management of Dictionaries**

.. end short_desc

************
Installation
************

.. start installation

Package ``ut_dic`` can be installed from PyPI.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ut_dic

.. end installation

***************
Package logging 
***************

(c.f.: **Appendix**: `Package Logging`)

*************
Package files
*************

Classification
==============

The Package ``ut_dic`` consist of the following file types (c.f.: **Appendix**: `Python Glossary`):

#. **Special files:**

   a. *py.typed*

#. **Modules**

   #. **Special modules:**

      a. *__init__.py*
      #. *__version__.py*

   #. **Module for Dictionary**

      a. *dic.py* `Management of Dictionary`

   #. **Modules for Dictionary of basic types**

      a. *doc.py*    **Module for Dictionary of callables**
      #. *doo.py*    **Module for Dictionary of objects**
      #. *douri.py*  **Module for Dictionary of uri's** 

   #. **Modules for Dictionary of dataframe types**
   
      a. *dopddf.py* **Module for Dictionary of pandas dataframes**
      #. *dopldf.py* **Module for Dictionary of polars dataframes**

   #. **Modules for Dictionary of dictionaries**
   
      a. *dodoa.py*  **Module for Dictionary of dictionaries of arrays**
      #. *dodod.py*  **Module for Dictionary of dictionaries of dictionaries**
      #. *dodows.py* **Module for Dictionary of dictionaries of Excel worksheets**
      #. *dod.py*    **Module for Dictionary of dictionaries**

*********************
Module for Dictionary
*********************

Module: dic.py
==============

The Module ``dic.py`` contains the single static class ``Dic`` for the Management of Dictionaries.

Class: Dic
----------

The static class ``Dic`` of Module ``dic.py`` is used to manage dictionaries of different types.
It contains class variables that act as messages,
as well as class or static methods, but no instance methods.
The methods of the Dic class can be classified into the following types:

#. *Miscellenous Methods*
#. *Get Methods*
#. *Locate Methods*
#. *New Methods*
#. *Show Methods*
#. *Set Methods*
#. *Split Methods*
#. *Yield Methods*

Miscellenous Methods
^^^^^^^^^^^^^^^^^^^^

  .. Miscellenous-Methods-of-class-Dic-label:
  .. table:: *Miscellenous Methods of class Dic*

   +------------------------+----------------------------------------------------------+
   |Name                    |Description                                               |
   +========================+==========================================================+
   |add_counter_to_values   |Apply the function "add_counter_with key" to the last key |
   |                        |of the key list and the Dictionary localized by that key. |
   +------------------------+----------------------------------------------------------+
   |add_counter_to_value    |Initialize the unintialized counter with 1 and add it to  |
   |                        |the Dictionary value of the key.                          |
   +------------------------+----------------------------------------------------------+
   |append_to_values        |Apply the function "append with key" to the last key of   |
   |                        |the key list amd the Dictionary localized by that key.    |
   +------------------------+----------------------------------------------------------+
   |append_to_value         |Initialize the unintialized counter with 1 and add it to  |
   |                        |the Dictionary value of the key.                          |
   +------------------------+----------------------------------------------------------+
   |change_keys_by_keyfilter|Change the keys of the Dictionary by the values of the    |
   |                        |keyfilter Dictionary with the same keys.                  |
   +------------------------+----------------------------------------------------------+
   |copy                    |Copy the value for keys from source to target dictionary. |
   +------------------------+----------------------------------------------------------+
   |extend_values           |Appply the function "extend_by_key" to the last key of the|
   |                        |key list and the dictionary localized by that key.        |
   +------------------------+----------------------------------------------------------+
   |extend_value            |Add the item with the key as element to the dictionary if |
   |                        |the key is undefined in the dictionary. Extend the element|
   |                        |value with the value if both supports the extend function.|
   +------------------------+----------------------------------------------------------+
   |increment_values        |Appply the function "increment_by_key" to the last key of |
   |                        |the key list and the Dictionary localized by that key.    |
   +------------------------+----------------------------------------------------------+
   |increment_value         |Increment the value of the key if it is defined in the    |
   |                        |Dictionary, otherwise assign the item to the key          |
   +------------------------+----------------------------------------------------------+
   |is_not                  |Return False if the key is defined in the Dictionary and  |
   |                        |the key value if not empty, othewise returm True.         |
   +------------------------+----------------------------------------------------------+
   |lstrip_keys             |Remove the first string found in the Dictionary keys.     |
   +------------------------+----------------------------------------------------------+
   |merge                   |Merge two Dictionaries.                                   |
   +------------------------+----------------------------------------------------------+
   |new                     |create a new dictionary from keys and values.             |
   +------------------------+----------------------------------------------------------+
   |normalize_value         |Replace every Dictionary value by the first list element  |
   |                        |of the value if it is a list with only one element.       |
   +------------------------+----------------------------------------------------------+
   |nvl                     |Return the Dictionary if it is not None otherwise return  |
   |                        |the empty Dictionary "{}".                                |
   +------------------------+----------------------------------------------------------+
   |rename_key_using_kwargs |Rename old Dictionary key with new one get from kwargs.   |
   +------------------------+----------------------------------------------------------+
   |replace_string_in_keys  |Replace old string contained in keys with new one.        |
   +------------------------+----------------------------------------------------------+
   |rename_key              |Rename old Dictionary key with new one.                   |
   +------------------------+----------------------------------------------------------+
   |round_values            |Round values selected by keys,                            |
   +------------------------+----------------------------------------------------------+
   |to_aod                  |Convert dictionary to array of dictionaries.              |
   +------------------------+----------------------------------------------------------+

Get Methods
^^^^^^^^^^^

  .. Get-Methods-of-class-Dic-label:
  .. table:: *Get Methods of class Dic*

   +------------+--------------------------------------------------------------+
   |Name        |Description                                                   |
   +============+==============================================================+
   |get_by_keys |Return the value of the keys located in the nested dictionary.|
   +------------+--------------------------------------------------------------+
   |get_value_yn|Return the value value_y if the key is contained in the       |
   |            |dictionary otherwise return the value value_n.                |
   +------------+--------------------------------------------------------------+
   |get         |Loop thru the nested dictionary with the keys from the key    |
   |            |list until the key is found. If the last key of the key list  |      
   |            |is found return the value of the key, otherwise return None.  |
   +------------+--------------------------------------------------------------+

Locate Methods
^^^^^^^^^^^^^^

  .. Locate-Methods-of-class-Dic-label:
  .. table:: *Locate Methods of class Dic*

   +-----------------+-------------------------------------------------------------+
   |Name             |Description                                                  |
   +=================+=============================================================+
   |locate           |Return the value of the key reached by looping thru the      |
   |                 |nested Dictionary with the keys from the key list until      |
   |                 |the value is None or the last key of the key list is reached.|
   +-----------------+-------------------------------------------------------------+
   |locate_secondlast|Apply the locate function to the dictionary and the new key  |
   |                 |list which contains all key list items without the last one. |
   +-----------------+-------------------------------------------------------------+

New Methods
^^^^^^^^^^^

  .. New-Methods-of-class-Dic-label:
  .. table:: *New Methods of class Dic*

   +----------------------+----------------------------------------------------------+
   |Name                  |Description                                               |
   +======================+==========================================================+
   |new_by_fset_split_keys|Create new dictionary from old by creating the new keys   |
   |                      |as frozenset of the comma separator split of the old keys.|
   +----------------------+----------------------------------------------------------+
   |new_by_split_keys     |Create new nested dictionary from old by creating the new |
   |                      |keys as the comma separator split of the old keys.        |
   +----------------------+----------------------------------------------------------+
   |new_d_filter          |Create filter dictionary with key, value and method pairs.|
   +----------------------+----------------------------------------------------------+
   |new_d_index_d_values  |Create index and value dictionary from dictionary and     |
   |                      |pivot dictionary.                                         |
   +----------------------+----------------------------------------------------------+
   |new_prefix_keys       |Create new dictionary from old by using prefixed old keys |
   |                      |as new keys and old values as new values.                 |
   +----------------------+----------------------------------------------------------+
   |new_make_values2keys  |Convert the dictionary to a new dictionary by using the   |
   |                      |values as new keys and all keys mapped to the same value  |
   |                      |as new value.                                             |
   +----------------------+----------------------------------------------------------+

Set Methods
^^^^^^^^^^^

  .. Set-Methods-of_class-Dic-label:
  .. table:: *Set Methods of class Dic*

   +-----------------------------------------+-----------------------------------------------------------------+
   |Name                                     |Description                                                      |
   +=========================================+=================================================================+
   |set_kv_not_none                          |Set the given Dictionary key to the given value if both are not  |
   |                                         |are not None.                                                    |
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_by_keys                              |Locate the values in a nested dictionary for the suceeding keys  |
   |                                         |of a key array and replace the last value with the given value   |
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_by_key_pair                          |Replace value of source key by value of target key.              |
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_if_none                              |Locate the values in a nested dictionary for the suceeding keys  |
   |                                         |of a key array and assign the given value to the last key if that|
   |                                         |key does not exist in the dictionary.                            |
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_by_div                               |Replace the source key value by the division of the values of    |
   |                                         |two target keys if the they are of type float and the divisor    |
   |                                         |is not o, otherwise assign None.                                 |
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_first_tgt_with_src_using_d_src2tgt   |Replace value of first dictionary target key found in the source |
   |                                         |to target dictionary by the source value found in the dictionary.|
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_first_tgt_with_src_using_d_tgt2src   |Replace value of first dictionary target key found in the target |
   |                                         |to source dictionary by the source value found in the dictionary.|
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_format_value                         |Replace the dictionary values by the formatted values using the  |
   |                                         |format string.                                                   |
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_multiply_with_factor                 |Replace the dictionary values by the original value multiplied   |
   |                                         |with the factor.                                                 |
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_tgt_with_src                         |Replace source dictionary values by target dictionary values.    |
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_tgt_with_src_using_doaod_tgt2src     |Loop through the target to source dictionaries of the values of  |
   |                                         |the dictionary of the arrays of target to source dictionaries    |
   |                                         |until the return value of the function                           |
   |                                         |"set_nonempty_tgt_with_src_using_d_tgt2src" is defined.          |
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_nonempty_tgt_with_src_using_d_tgt2src|Exceute the function "set_tgt_with_src_using_d_tgt2src" if all   |
   |                                         |dictionary values for the keys provided by the values of the     |
   |                                         |target to source dictionary are defined.                         |
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_first_tgt_with_src_using_d_tgt2src   |Replace value of first dictionary target key found in the target |
   |                                         |to source dictionary by the source value found in the dictionary.|
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_tgt_with_src_using_d_src2tgt         |                                                                 |
   +-----------------------------------------+-----------------------------------------------------------------+
   |set_tgt_with_src_using_d_tgt2src         |                                                                 |
   +-----------------------------------------+-----------------------------------------------------------------+

Show Methods
^^^^^^^^^^^^

  .. Show-Methods-of-class-Dic-label:
  .. table:: *Show Methods of class Dic*

   +-----------------+-----------------------------------------------------+
   |Name             |Description                                          |
   +=================+=====================================================+
   |sh_keys          |Show array of keys of key list found in dictionary.  |
   +-----------------+-----------------------------------------------------+
   |show_sorted_keys |Show sorted array of keys of dictionary.             |
   +-----------------+-----------------------------------------------------+
   |sh_value_by_keys |Show value of dictionary element selected by keys    |
   +-----------------+-----------------------------------------------------+
   |sh_values_by_keys|Convert the dictionary into an array by using a key  |
   |                 |filter. The array elements are the values of all     |
   |                 |dictionary elements where the key is the given single|
   |                 |key or where the key is contained in the key list.   |
   +-----------------+-----------------------------------------------------+

Split Methods
^^^^^^^^^^^^^

  .. Split-Methods-of class-Dic-label:
  .. table:: *Split Methods of class Dic*

   +----------------------+-----------------------------------------------------------------+
   |Name                  |Description                                                      |
   +======================+=================================================================+
   |split_by_value_endwith|Split the dictionary into a tuple of dictionaries using the      |
   |                      |condition "the dictionary value ends with the given value".      |
   |                      |The first tuple element is the dictionary of all dictionary      |
   |                      |elements whose value ends with the given value; the second       |
   |                      |one is the dictionary of the other elements.                     |
   +----------------------+-----------------------------------------------------------------+
   |split_by_value        |Split the dictionary into a tuple of dictionaries using the      |
   |                      |condition "the dictionary value is equal to the given value". The|
   |                      |value. The first tuple element is the dictionary of all elements |
   |                      |whose value is equal to the given value; the second one is the   | 
   |                      |dictionary of the other elements.                                |
   +----------------------+-----------------------------------------------------------------+
   |split_by_value_is_int |Split the dictionary into a tuple of dictionaries using the      |
   |                      |condition "the element value is of type integer". The first tuple|
   |                      |element is the dictionary of all elements whose value is of type |
   |                      |integer; the second one is the dictionary of the other elements. |
   +----------------------+-----------------------------------------------------------------+

Yield Methods
^^^^^^^^^^^^^

  .. Yield-Methods-of-class-Dic-label:
  .. table:: *Yield Methods of class Dic*

   +---------------------------+----------------------------------------------------------------------------+
   |Name                       |Description                                                                 |
   +===========================+============================================================================+
   |yield_values_with_keyfilter|Yield the values of all elements which are selected by the given key filter.|
   +---------------------------+----------------------------------------------------------------------------+

*************************************
Modules for Dictionary of basic types
*************************************

Module: doc.py
==============

The Module ``doc.py`` is used to manage dictionary of callables; It contains the static class ``DoC``.

Class DoC
---------

The static Class ``DoC`` contains the subsequent methods; it contains only class- or static-methods
for the execution of callables referenced by commands.

Methods
^^^^^^^

  .. Methods-of-class-DoC-label:
  .. table:: *Methods of class DoC*

   +------+------+--------------------------------------------------+
   |Name  |Type  |Description                                       |
   +======+======+==================================================+
   |ex_cmd|class |Get the command cmd from the arguments and keyword|
   |      |      |arguments list args_kwargs and call the ex        |
   |      |      |function with the given cmd.                      |
   +------+------+--------------------------------------------------+
   |ex    |class |Show and execute the function located as the value|
   |      |      |of the given cmd in the function dictionary.      |
   +------+------+--------------------------------------------------+
   |sh    |static|Show(get) the function located as the value of the|       
   |      |      |given key in the function dictionary              |       
   +------+------+--------------------------------------------------+

Method: ex_cmd
^^^^^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-Method-ex_cmd-label:
  .. table:: *Parameter of Method ex_cmd*

   +------+-----+-----------------------+
   |Name  |Type |Description            |
   +======+=====+=======================+
   |cls   |class|current class          |
   +------+-----+-----------------------+
   |doc   |TnDoC|Dictionary of Callables|
   +------+-----+-----------------------+
   |kwargs|TyDic|Keyword arguments      |                           
   +------+-----+-----------------------+

Return Value
""""""""""""

  .. Return-value-of-Method-ex_cmd-label:
  .. table:: Return value of Method ex_cmd*

   +----+----+-------------------------------+
   |Name|Type|Description                    |
   +====+====+===============================+
   |    |Any |Result of the command execution|
   +----+----+-------------------------------+

Method: ex
^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-Method-ex-label:
  .. table:: *Parameter of Method ex*

   +-----------+--------+------------------------------+
   |Name       |Type    |Description                   |
   +===========+========+==============================+
   |cls        |class   |current class                 |
   +-----------+--------+------------------------------+
   |doc        |TnDoC   |Dictionary of Callables       |
   +-----------+--------+------------------------------+
   |key        |TnDoc   |key                           |
   +-----------+--------+------------------------------+
   |args_kwargs|TnArrDoc|arguments or keyword arguments|
   +-----------+--------+------------------------------+

Return Value
""""""""""""

  .. Return-value-of-Method-ex-label:
  .. table:: *Return value of Method ex*

   +----+----+-------------------------------+
   |Name|Type|Description                    |
   +====+====+===============================+
   |    |Any |Result of the command execution|
   +----+----+-------------------------------+

Method: sh
^^^^^^^^^^

Parameter
"""""""""

  .. Parameter-of-Method-sh-label:
  .. table:: *Parameter of Method-sh*

   +----+-----+------------------------------+
   |Name|Type |Description                   |
   +====+=====+==============================+
   |cls |class|current class                 |
   +----+-----+------------------------------+
   |doc |TnDoC|Dictionary of Callables       |
   +----+-----+------------------------------+
   |key |TnDoc|key                           |
   +----+-----+------------------------------+

Return Value
""""""""""""

  .. Return-value-of-Method-sh-label:
  .. table:: *Return value of Method-sh*

   +----+----------+-----------+
   |Name|Type      |Description|
   +====+==========+===========+
   |fnc |TyCallable|Function   |
   +----+----------+-----------+

**************************************
Modules for Dictionary of dictionaries
**************************************

  .. Modules-for-Dictionary-of-dictionaries-label:
  .. table:: *Modules for Dictionary of dictionaries*

   +---------+---------------------------------------------------------+
   |Name     |Description                                              |
   +=========+=========================================================+
   |dodoa.py |Management of Dictionary of dictionaries of arrays.      |
   +---------+---------------------------------------------------------+
   |dodod.py |Management of Dictionary of dictionaries of dictionaries.|
   +---------+---------------------------------------------------------+
   |dodows.py|Management of Dictionary of dictionaries of worksheets.  |
   +---------+---------------------------------------------------------+
   |dod.py   |Management of Dictionary of dictionaries.                |
   +---------+---------------------------------------------------------+

Module: dodoa.py
================

The Module ``dodoa.py`` contains the static class ``DoDoA``:

Class: DoDoA
------------

The static Class ``DoDoA`` is used to manage Dictionary of Dictionaries of Arrays;
it contains the subsequent methods.

Methods
^^^^^^^

  .. Methods-of-class-DoDoA-label:
  .. table:: *Methods of class DoDoA*

   +-------------+------------------------------------------------------+
   |Name         |Description                                           |
   +=============+======================================================+
   |append       |                                                      |
   +-------------+------------------------------------------------------+
   |sh_union     |                                                      |
   +-------------+------------------------------------------------------+

Module: dodod.py
================

Classes
-------

The Module ``dodod.py`` contains the static Class ``DoDoD``:

Class: DoDoD
------------

The static Class ``DoDoD`` is used to manage Dictionary of Dictionaries of Dictionaries;
it contains the subsequent methods.

Methods
^^^^^^^

  .. Methods-of-class-DoDoD-label:
  .. table:: *Methods of class DoDoD*

   +------------+------------------------------------------------------+
   |Name        |Description                                           |
   +============+======================================================+
   |set         |                                                      |
   +------------+------------------------------------------------------+
   |yield_values|                                                      |
   +------------+------------------------------------------------------+

Module: dod.py
==============

Classes
-------

The Module ``dod.py`` contains the static Class ``DoD``:


Class: DoD
----------

The static Class ``DoD`` is used to manage ``Dictionary of Dictionaries``;
it contains the subsequent methods.

Methods
^^^^^^^

  .. Methods-of_class-DoD-label:
  .. table:: *DoD Methods*

   +---------------+-------------------------------------------------------+
   |Name           |Description                                            |
   +===============+=======================================================+
   |nvl            |Return the Dictionary of Dictionaries if it is not None|
   |               |otherwise return the empty Dictionary "{}".            |
   +---------------+-------------------------------------------------------+
   |replace_keys   |Recurse through the Dictionary while building a new one|
   |               |with new keys and old values; the old keys are         |
   |               |translated to new ones by the keys Dictionary.         |
   +---------------+-------------------------------------------------------+
   |yield_values   |                                                       |
   +---------------+-------------------------------------------------------+

Module: dodows.py
=================

Classes
-------

The Module ``dodows.py`` contains the static Class ``DoDoWs``:

Class: DoDoWs
-------------

The static Class ``DoDoWs`` is used to manage ``Dictionary of Dictionaries of Worksheets``;
it contains the subsequent methods.

Methods
^^^^^^^

  .. Methods-of-class-DoDoWs-label:
  .. table:: *Methods of class DoDoWs*

   +--------------+------------------------------------------------------------------+
   |Name          |Description                                                       |
   +==============+==================================================================+
   |write_workbook|Write a workbook using a Dictionary of Dictionaries of worksheets.|
   +--------------+------------------------------------------------------------------+

********************************
Module for Dictionary of Objects
********************************

The Module Type ``Dictionary of Objects`` contains the following Modules:

  .. Dictionaries-of-Ojects-Module-label:
  .. table:: *Dictionaries of Ojects Module*

   +------+------------------------------------+
   |Name  |Description                         |
   +======+====================================+
   |doo.py|Management of Dictionary of Objects.|
   +------+------------------------------------+

Module: doo.py
==============

The Module ``doo.py`` contains the static Classes ``DoO``.

Class: DoO
----------

The static Class ``DoO`` is used to manage ``Dictionary of Objects``; it contains the subsequent methods.

Methods
^^^^^^^

  .. DoO-Methods-label:
  .. table:: *DoO Methods*

   +------------+---------------------------------------------------------------+
   |Name        |Description                                                    |
   +============+===============================================================+
   |replace_keys|Replace the keys of the given Dictionary by the values found in|
   |            |the given keys Dictionary if the values are not Dictionaries;  |
   |            |otherwise the function is called with these values.            |
   +------------+---------------------------------------------------------------+

************************************
Modules for Dictionary of Dataframes
************************************

Modules
=======

The Module Type ``Dictionary of Dataframes`` contains the following Modules:

  .. Dictionary-of-Dataframes-Modules-label:
  .. table:: *Dictionary of Dataframes Modules*

   +---------+----------------------------------------------+
   |Name     |Description                                   |
   +=========+==============================================+
   |dopddf.py|Management of Dictionary of Panda Dataframes. |
   +---------+----------------------------------------------+
   |dopldf.py|Management of Dictionary of Polars Dataframes.|
   +---------+----------------------------------------------+

Module: dopddf.py
=================

The Module ``dopddf.py`` contains only the static Class ``DoPdDf``.


Class: DoPdDf
-------------

The static Class ``DoPdDf`` is used to manage ``Dictionaries of Panda Dataframes``;
it contains the subsequent methods.

Methods
^^^^^^^

  .. Methods-of-class-DoPdDf-label:
  .. table:: *Methodsc of class DoPdDf*

   +----------------------+-----------------------------------------------------+
   |Name                  |Description                                          |
   +======================+=====================================================+
   |set_ix_drop_key_filter|Apply Function set_ix_drop_col_filter to all Panda   |
   |                      |Dataframe values of given Dictionary.                |
   +----------------------+-----------------------------------------------------+
   |to_doaod              |Replace NaN values of Panda Dataframe values of given|
   |                      |Dictionary and convert them to Array of Dictionaries.|
   +----------------------+-----------------------------------------------------+

Module: dopldf.py
==================

The Module ``dopldf.py`` contains only the static Class ``DoPlDf``:


Class: DoPlDf
-------------

The static Class ``DoPlDf`` is used to manage ``Dictionary of Polars Dataframes``;
it contains the subsequent Methods.

Methods
^^^^^^^

  .. Methods-of-class-DoPlDf-label:
  .. table:: *Methods of class DoPlDf*

   +--------+------------------------------------------------------+
   |Name    |Description                                           |
   +========+======================================================+
   |to_doaod|Replace NaN values of Polars Dataframe values of given|
   |        |Dictionary and convert them to Array of Dictionaries. |
   +--------+------------------------------------------------------+

########
Appendix
########

***************
Package Logging
***************

Description
===========

Logging use the module **log.py** of the logging package **ut_log**.
The module supports two Logging types:

#. **Standard Logging** (std) or 
#. **User Logging** (usr).

The Logging type can be defined by one of the values 'std' or 'usr' of the parameter log_type; 'std' is the default.
The different Logging types are configured by one of the following configuration files:

#. **log.std.yml** or 
#. **log.usr.yml** 
  
The configuration files can be stored in different configuration directories (ordered by increased priority):

#. <package directory of the log package **ut_log**>/**cfg**,
#. <package directory of the application package **ui_eviq_srr**>/**cfg**,
#. <application directory of the application **eviq**>/**cfg**,

The active configuration file is the configuration file in the directory with the highest priority.

Examples
========
  
Site-packages-path = **/appl/eviq/.pyenv/versions/3.11.12/lib/python3.11/site-packages**
Log-package = **ut_log**
Application-package = **ui_eviq_srr**
Application-home-path = **/appl/eviq**
  
.. Examples-of-log-configuration-files-label:
.. table:: **Examples of log configuration-files**

   +-----------------------------------------------------------------------------------+
   |Log Configuration                                                                  |
   +----+-------------------+----------------------------------------------+-----------+
   |Type|Directory Type     |Directory                                     |File       |
   +====+===================+==============================================+===========+
   |std |Log package        |<Site-packages-path>/<Log-package>/cfg        |log.std.yml|
   |    +-------------------+----------------------------------------------+           |
   |    |Application package|<Site-packages-path>/<application-package>/cfg|           |
   |    +-------------------+----------------------------------------------+           |
   |    |Application        |<application-home-path>/cfg                   |           |
   +----+-------------------+----------------------------------------------+-----------+
   |usr |Log package        |<site-packages-path>/ut_log/cfg               |log.usr.yml|
   |    +-------------------+----------------------------------------------+           |
   |    |Application package|<site-packages-path>/ui_eviq_srr/cfg          |           |
   |    +-------------------+----------------------------------------------+           |
   |    |Application        |<application-path>/cfg                        |           |
   +----+-------------------+----------------------------------------------+-----------+

Log message types
=================

Logging defines log file path names for the following log message types: .

#. *debug*
#. *info*
#. *warning*
#. *error*
#. *critical*

Log types and Log directories
-----------------------------

Single or multiple Application log directories can be used for each message type:

.. Log-types-and-Log-directories-label:
.. table:: *Log types and directoriesg*

   +--------------+---------------+
   |Log type      |Log directory  |
   +--------+-----+--------+------+
   |long    |short|multiple|single|
   +========+=====+========+======+
   |debug   |dbqs |dbqs    |logs  |
   +--------+-----+--------+------+
   |info    |infs |infs    |logs  |
   +--------+-----+--------+------+
   |warning |wrns |wrns    |logs  |
   +--------+-----+--------+------+
   |error   |errs |errs    |logs  |
   +--------+-----+--------+------+
   |critical|crts |crts    |logs  |
   +--------+-----+--------+------+

Application parameter for logging
---------------------------------

.. Application-parameter-used-in-log-naming-label:
.. table:: *Application parameter used in log naming*

   +-----------------+--------------+-----+------------------+-------+-----------+
   |Name             |Decription    |Value|Description       |Default|Example    |
   +=================+==============+=====+==================+=======+===========+
   |appl_data        |data directory|     |                  |       |/data/eviq |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |tenant           |tenant name   |UMH  |                  |       |UMH        |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |package          |package name  |     |                  |       |ui_eviq_srr|
   +-----------------+--------------+-----+------------------+-------+-----------+
   |cmd              |command       |     |                  |       |evupreg    |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |log_type         |Logging Type  |std: |Standard logging  |std    |std        |
   |                 |              +-----+------------------+       |           |
   |                 |              |usr: |User Logging      |       |           |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |log_ts_type      |Logging       |ts:  |Sec since 1.1.1970|ts     |ts         |
   |                 |timestamp     +-----+------------------+       |           |
   |                 |type          |dt:  |Datetime          |       |           |
   +-----------------+--------------+-----+------------------+-------+-----------+
   |log_sw_single_dir|Use single log|True |use single dir.   |True   |True       |
   |                 |directory     +-----+------------------+       |           |
   |                 |              |False|use muliple dir.  |       |           |
   +-----------------+--------------+-----+------------------+-------+-----------+

Log files naming
----------------

Naming Conventions (table format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Naming-conventions-for-logging-file-paths-label:
.. table:: *Naming conventions for logging file paths*

   +--------+----------------------------------------------+-------------------+
   |Type    |Directory                                     |File               |
   +========+==============================================+===================+
   |debug   |/<appl_data>/<tenant>/RUN/<package>/<cmd>/debs|debs_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |critical|/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|crts_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |error   |/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|errs_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |info    |/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|infs_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+
   |warning |/<appl_data>/<tenant>/RUN/<package>/<cmd>/logs|rnsg_<ts>_<pid>.log|
   +--------+----------------------------------------------+-------------------+

Naming Conventions (tree format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

::

 <appl_data>   Application data folder
 │
 └── <tenant>  Application tenant folder
     │
     └── RUN  Applications RUN folder for Application log files
         │
         └── <package>  RUN folder of Application package: <package>
             │
             └── <cmd>  RUN folder of Application command <cmd>
                 │
                 ├── debs  Application command debug messages folder
                 │   │
                 │   └── debs_<ts>_<pid>.log  debug messages for
                 │                            run of command <cmd>
                 │                            with pid <pid> at <ts>
                 │
                 └── logs  Application command log messages folder
                     │
                     ├── crts_<ts>_<pid>.log  critical messages for
                     │                        run of command <cmd>
                     │                        with pid <pid> at <ts>
                     ├── errs_<ts>_<pid>.log  error messages for
                     │                        run of command <cmd>
                     │                        with pid <pid> at <ts>
                     ├── infs_<ts>_<pid>.log  info messages for
                     │                        run of command <cmd>
                     │                        with pid <pid> at <ts>
                     └── wrns_<ts>_<pid>.log  warning messages for
                                              run of command <cmd>
                                              with pid <pid> at <ts>

Naming Examples (table format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Naming-conventions-for-logging-file-paths-label:
.. table:: *Naming conventions for logging file paths*

   +--------+--------------------------------------------+--------------------------+
   |Type    |Directory                                   |File                      |
   +========+============================================+==========================+
   |debug   |/appl/eviq/UMH/RUN/ui_eviq_srr/evdomap/debs/|debs_1750096540_354710.log|
   +--------+--------------------------------------------+--------------------------+
   |critical|/appl/eviq/UMH/RUN/ui_eviq_srr/evdomap/logs/|crts_1749971151_240257.log|
   +--------+                                            +--------------------------+
   |error   |                                            |errs_1749971151_240257.log|
   +--------+                                            +--------------------------+
   |info    |                                            |infs_1750096540_354710.log|
   +--------+                                            +--------------------------+
   |warning |                                            |wrns_1749971151_240257.log|
   +--------+--------------------------------------------+--------------------------+

Naming Examples (tree format)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: text

  /data/eviq/UMH/RUN/ui_eviq_srr/evdomap  Run folder of
  │                                       of function evdomap
  │                                       of package ui_eviq_srr
  │                                       for teanant UMH
  │                                       of application eviq
  │
  ├── debs  debug folder of Application function: evdomap
  │   │
  │   └── debs_1748609414_314062.log  debug messages for run 
  │                                   of function evdomap     
  │                                   using pid: 314062 at: 1748609414
  │
  └── logs  log folder of Application function: evdomap
      │
      ├── errs_1748609414_314062.log  error messages for run
      │                               of function evdomap     
      │                               with pid: 314062 at: 1748609414
      ├── infs_1748609414_314062.log  info messages for run
      │                               of function evdomap     
      │                               with pid: 314062 at: 1748609414
      └── wrns_1748609414_314062.log  warning messages for run
                                      of function evdomap     
                                      with pid: 314062 at: 1748609414

Configuration files
===================

log.std.yml (jinja2 yml file)
-----------------------------

Content
^^^^^^^

.. log.std.yml-label:
.. code-block:: jinja

 version: 1

 disable_existing_loggers: False

 loggers:

     # standard logger
     std:
         # level: NOTSET
         level: DEBUG
         handlers:
             - std_debug_console
             - std_debug_file
             - std_info_file
             - std_warning_file
             - std_error_file
             - std_critical_file

 handlers:
 
     std_debug_console:
         class: 'logging.StreamHandler'
         level: DEBUG
         formatter: std_debug
         stream: 'ext://sys.stderr'

     std_debug_file:
         class: 'logging.FileHandler'
         level: DEBUG
         formatter: std_debug
         filename: '{{dir_run_debs}}/debs_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_info_file:
         class: 'logging.FileHandler'
         level: INFO
         formatter: std_info
         filename: '{{dir_run_infs}}/infs_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_warning_file:
         class: 'logging.FileHandler'
         level: WARNING
         formatter: std_warning
         filename: '{{dir_run_wrns}}/wrns_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_error_file:
         class: 'logging.FileHandler'
         level: ERROR
         formatter: std_error
         filename: '{{dir_run_errs}}/errs_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true
 
     std_critical_file:
         class: 'logging.FileHandler'
         level: CRITICAL
         formatter: std_critical
         filename: '{{dir_run_crts}}/crts_{{ts}}_{{pid}}.log'
         mode: 'a'
         delay: true

     std_critical_mail:
         class: 'logging.handlers.SMTPHandler'
         level: CRITICAL
         formatter: std_critical_mail
         mailhost : localhost
         fromaddr: 'monitoring@domain.com'
         toaddrs:
             - 'dev@domain.com'
             - 'qa@domain.com'
         subject: 'Critical error with application name'
 
 formatters:

     std_debug:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_info:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_warning:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_error:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_critical:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'
     std_critical_mail:
         format: '%(asctime)-15s %(levelname)s-%(name)s-%(process)d::%(module)s.%(funcName)s|%(lineno)s:: %(message)s'
         datefmt: '%Y-%m-%d %H:%M:%S'

Jinja2-variables
^^^^^^^^^^^^^^^^

.. log.std.yml-Jinja2-variables-label:
.. table:: *log.std.yml Jinja2 variables*

   +------------+-----------------------------+-------------------------------------------+
   |Name        |Definition                   |Example                                    |
   +============+=============================+===========================================+
   |dir_run_debs|debug run directory          |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/debs|
   +------------+-----------------------------+-------------------------------------------+
   |dir_run_infs|info run directory           |/data/eviq/UMH/RUN/ui_eviq_srr/evupreg/logs|
   +------------+-----------------------------+                                           |
   |dir_run_wrns|warning run directory        |                                           |
   +------------+-----------------------------+                                           |
   |dir_run_errs|error run directory          |                                           |
   +------------+-----------------------------+                                           |
   |dir_run_crts|critical error run directory |                                           |
   +------------+-----------------------------+-------------------------------------------+
   |ts          |Timestamp since 1970 in [sec]|1749483509                                 |
   |            |if log_ts_type == 'ts'       |                                           |
   |            +-----------------------------+-------------------------------------------+
   |            |Datetime in timezone Europe/ |20250609 17:38:29 GMT+0200                 |
   |            |Berlin if log_ts_type == 'dt'|                                           |
   +------------+-----------------------------+-------------------------------------------+
   |pid         |Process ID                   |79133                                      |
   +------------+-----------------------------+-------------------------------------------+

***************
Python Glossary
***************

.. _python-modules:

Python Modules
==============

Overview
--------

  .. Python-Modules-label:
  .. table:: *Python Modules*

   +--------------+---------------------------------------------------------+
   |Name          |Definition                                               |
   +==============+==========+==============================================+
   |Python modules|Files with suffix ``.py``; they could be empty or contain|
   |              |python code; other modules can be imported into a module.|
   +--------------+---------------------------------------------------------+
   |special Python|Modules like ``__init__.py`` or ``main.py`` with special |
   |modules       |names and functionality.                                 |
   +--------------+---------------------------------------------------------+

.. _python-functions:

Python Function
===============

Overview
--------

  .. Python-Function-label:
  .. table:: *Python Function*

   +---------------+---------------------------------------------------------+
   |Name           |Definition                                               |
   +===============+==========+==============================================+
   |Python function|Files with suffix ``.py``; they could be empty or contain|
   |               |python code; other modules can be imported into a module.|
   +---------------+---------------------------------------------------------+
   |special Python |Modules like ``__init__.py`` or ``main.py`` with special |
   |modules        |names and functionality.                                 |
   +---------------+---------------------------------------------------------+

.. _python-packages:

Python Packages
===============

Overview
--------

  .. Python Packages-Overview-label:
  .. table:: *Python Packages Overview*

   +---------------------+---------------------------------------------+
   |Name                 |Definition                                   |
   +=====================+=============================================+
   |Python package       |Python packages are directories that contains|
   |                     |the special module ``__init__.py`` and other |
   |                     |modules, sub packages, files or directories. |
   +---------------------+---------------------------------------------+
   |Python sub-package   |Python sub-packages are python packages which|
   |                     |are contained in another python package.     |
   +---------------------+---------------------------------------------+
   |Python package       |directory contained in a python package.     |
   |sub-directory        |                                             |
   +---------------------+---------------------------------------------+
   |Python package       |Python package sub-directories with a special|
   |special sub-directory|meaning like data or cfg                     |
   +---------------------+---------------------------------------------+

Special python package sub-directories
--------------------------------------

  .. Special-python-package-sub-directory-Examples-label:
  .. table:: *Special python package sub-directories*

   +-------+------------------------------------------+
   |Name   |Description                               |
   +=======+==========================================+
   |bin    |Directory for package scripts.            |
   +-------+------------------------------------------+
   |cfg    |Directory for package configuration files.|
   +-------+------------------------------------------+
   |data   |Directory for package data files.         |
   +-------+------------------------------------------+
   |service|Directory for systemd service scripts.    |
   +-------+------------------------------------------+

.. _python-files:

Python Files
============

Overview
--------

  .. Python-files-label:
  .. table:: *Python files*

   +--------------+---------------------------------------------------------+
   |Name          |Definition                                               |
   +==============+==========+==============================================+
   |Python modules|Files with suffix ``.py``; they could be empty or contain|
   |              |python code; other modules can be imported into a module.|
   +--------------+---------------------------------------------------------+
   |Python package|Files within a python package.                           |
   |files         |                                                         |
   +--------------+---------------------------------------------------------+
   |Python dunder |Python modules which are named with leading and trailing |
   |modules       |double underscores.                                      |
   +--------------+---------------------------------------------------------+
   |special       |Files which are not modules and used as python marker    |
   |Python files  |files like ``py.typed``.                                 |
   +--------------+---------------------------------------------------------+
   |special Python|Modules like ``__init__.py`` or ``main.py`` with special |
   |modules       |names and functionality.                                 |
   +--------------+---------------------------------------------------------+

.. _python-special-files:

Python Special Files
--------------------

  .. Python-special-files-label:
  .. table:: *Python special files*

   +--------+--------+--------------------------------------------------------------+
   |Name    |Type    |Description                                                   |
   +========+========+==============================================================+
   |py.typed|Type    |The ``py.typed`` file is a marker file used in Python packages|
   |        |checking|to indicate that the package supports type checking. This is a|
   |        |marker  |part of the PEP 561 standard, which provides a standardized   |
   |        |file    |way to package and distribute type information in Python.     |
   +--------+--------+--------------------------------------------------------------+

.. _python-special-modules:

Python Special Modules
----------------------

  .. Python-special-modules-label:
  .. table:: *Python special modules*

   +--------------+-----------+----------------------------------------------------------------+
   |Name          |Type       |Description                                                     |
   +==============+===========+================================================================+
   |__init__.py   |Package    |The dunder (double underscore) module ``__init__.py`` is used to|
   |              |directory  |execute initialisation code or mark the directory it contains   |
   |              |marker     |as a package. The Module enforces explicit imports and thus     |
   |              |file       |clear namespace use and call them with the dot notation.        |
   +--------------+-----------+----------------------------------------------------------------+
   |__main__.py   |entry point|The dunder module ``__main__.py`` serves as package entry point |
   |              |for the    |point. The module is executed when the package is called by the |
   |              |package    |interpreter with the command **python -m <package name>**.      |
   +--------------+-----------+----------------------------------------------------------------+
   |__version__.py|Version    |The dunder module ``__version__.py`` consist of assignment      |
   |              |file       |statements used in Versioning.                                  |
   +--------------+-----------+----------------------------------------------------------------+

Python classes
==============

Overview
--------

  .. Python-classes-overview-label:
  .. table:: *Python classes overview*

   +-------------------+---------------------------------------------------+
   |Name               |Description                                        |
   +===================+===================================================+
   |Python class       |A class is a container to group related methods and|
   |                   |variables together, even if no objects are created.|
   |                   |This helps in organizing code logically.           |
   +-------------------+---------------------------------------------------+
   |Python static class|A class which contains only @staticmethod or       |
   |                   |@classmethod methods and no instance-specific      |
   |                   |attributes or methods.                             |
   +-------------------+---------------------------------------------------+

Python methods
==============

Overview
--------

  .. Python-methods-overview-label:
  .. table:: *Python methods overview*

   +--------------+-------------------------------------------+
   |Name          |Description                                |
   +==============+===========================================+
   |Python method |Python functions defined in python modules.|
   +--------------+-------------------------------------------+
   |Python class  |Python functions defined in python classes.|
   |method        |                                           |
   +--------------+-------------------------------------------+
   |Python special|Python class methods with special names and|
   |class method  |functionalities.                           |
   +--------------+-------------------------------------------+

Python class methods
--------------------

  .. Python-class-methods-label:
  .. table:: *Python class methods*

   +--------------+----------------------------------------------+
   |Name          |Description                                   |
   +==============+==============================================+
   |Python no     |Python function defined in python classes and |
   |instance      |decorated with @classmethod or @staticmethod. |
   |class method  |The first parameter conventionally called cls |
   |              |is a reference to the current class.          |
   +--------------+----------------------------------------------+
   |Python        |Python function defined in python classes; the|
   |instance      |first parameter conventionally called self is |
   |class method  |a reference to the current class object.      |
   +--------------+----------------------------------------------+
   |special Python|Python class functions with special names and |
   |class method  |functionalities.                              |
   +--------------+----------------------------------------------+

Python special class methods
----------------------------

  .. Python-methods-examples-label:
  .. table:: *Python methods examples*

   +--------+-----------+--------------------------------------------------------------+
   |Name    |Type       |Description                                                   |
   +========+===========+==============================================================+
   |__init__|class      |The special method ``__init__`` is called when an instance    |
   |        |object     |(object) of a class is created; instance attributes can be    |
   |        |constructor|defined and initalized in the method. The method us a single  |
   |        |method     |parameter conventionally called ``self`` to access the object.|
   +--------+-----------+--------------------------------------------------------------+

#################
Table of Contents
#################

.. contents:: **Table of Content**
