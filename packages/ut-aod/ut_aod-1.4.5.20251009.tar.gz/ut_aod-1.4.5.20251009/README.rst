######
ut_aod
######

********
Overview
********

.. start short_desc

**Utilities for Arrays of Dictionaries**

.. end short_desc

************
Installation
************

.. start installation

Package ``ut_aod`` can be installed from PyPI.

To install with ``pip``:

.. code-block:: shell

	$ python -m pip install ut_aod

***************
Package logging 
***************

(c.f.: `https://pypi.org/project/ut-log/`)

*************
Package files
*************

Classification
==============

The Package ``ut_aod`` consist of the following file types (c.f.: **Appendix**: `Python Glossary`):

#. **Special files:**

   a. *py.typed*

#. **Special modules:**

   a. *__init__.py*
   #. *__version__.py*

#. **Modules**

   a. *aod.py*

*******
Modules
*******

Module: aod.py
==============

The Module ``aod.py`` contains the static classes ``AoD``.

Class: AoD
----------

The Class ``AoD`` contains the following methods:

Methods
^^^^^^^

  .. Methods-of-class-AoD-label:
  .. table:: *Methods of class AoD*

   +------------------------------------+------------------------------------------------------+
   |Name                                |Short description                                     |
   +====================================+======================================================+
   |add                                 |Append the object to the Array of dictionaries if the |
   |                                    |object is a dictionary or extend it with the objects  |
   |                                    |the the object is a list.                             |
   +------------------------------------+------------------------------------------------------+
   |add_mapped_dic_element              |Add the dictionary element mapped by the function to  |
   |                                    |the array of dictionaries.                            |
   +------------------------------------+------------------------------------------------------+
   |append_unique                       |Append dictionary to array of dictionaries if it does |
   |                                    |not exist in the dictionary.                          |
   +------------------------------------+------------------------------------------------------+
   |apply_function                      |Apply the function to the array of dictionaries.      |
   +------------------------------------+------------------------------------------------------+
   |dic_found_with_empty_value          |Return True or raise an exception if the array of     |
   |                                    |dictionaries contains a dictionary with empty value   |
   |                                    |and the execption switch is True.                     |
   +------------------------------------+------------------------------------------------------+
   |merge_aod                           |Merge two array of dictionaries.                      |
   +------------------------------------+------------------------------------------------------+
   |merge_aod_unpack                    |Merge two array of dictionaries by the unpack method. |
   +------------------------------------+------------------------------------------------------+
   |merge_aod_update                    |Merge two array of dictionaries by the update method. |
   +------------------------------------+------------------------------------------------------+
   |merge_aod_other                     |Merge two arrays of dictionaries by the assignment    |
   |                                    |method.                                               |
   +------------------------------------+------------------------------------------------------+
   |merge_dic                           |Merge array of dictionaries with dictionary.          |
   +------------------------------------+------------------------------------------------------+
   |nvl                                 |Replace empty array of dictionaries.                  |
   +------------------------------------+------------------------------------------------------+
   |put                                 |Write transformed array of dictionaries to a csv file |
   |                                    |file with a selected I/O function.                    |
   +------------------------------------+------------------------------------------------------+
   |sh_doaod_split_by_value_is_not_empty|Converted array of dictionaries to dictionary of array|
   |                                    |of dictionaries by using conditional split.           |
   +------------------------------------+------------------------------------------------------+
   |sh_dod                              |Convert array of dictionaries to dictionaries of      |
   |                                    |dictionaries.                                         |
   +------------------------------------+------------------------------------------------------+
   |sh_key_value_found                  |Show True if an element exists in the array of        |
   |                                    |dictionaries which contains the key, value pair.      |
   +------------------------------------+------------------------------------------------------+
   |sh_unique                           |Deduplicate array of dictionaries.                    |
   +------------------------------------+------------------------------------------------------+
   |split_by_value_is_not_empty         |Split array of dictionaries by the condition "the     |
   |                                    |given key value is not empty".                        |
   +------------------------------------+------------------------------------------------------+
   |to_aoa                              |Convert array of dictionaries to array of arrays      |
   |                                    |controlled by key- and value-switch.                  |
   +------------------------------------+------------------------------------------------------+
   |to_aoa of_keys_values               |Convert array of dictionaries to array of arrays using|
   |                                    |keys of any dictionary and values of all dictionaries.|
   +------------------------------------+------------------------------------------------------+
   |to_aoa of_values                    |Convert array of dictionaries to array of arrays using|
   |                                    |values of all dictionaries.                           |
   +------------------------------------+------------------------------------------------------+
   |to_aoa of_key_values                |Convert array of dictionaries to array using          |
   |                                    |dictionary values with given key.                     |
   +------------------------------------+------------------------------------------------------+
   |to_csv_with_pd                      |Write array of dictionaries to csv file with pandas.  |
   +------------------------------------+------------------------------------------------------+
   |to_csv_with_pl                      |Write array of dictionaries to csv file with polars.  |
   +------------------------------------+------------------------------------------------------+
   |to_doaod_by_key                     |Convert array of dictionaries to dictionary of arrays |
   |                                    |of dictionaries by using the key.                     |
   +------------------------------------+------------------------------------------------------+
   |to_dic_by_key                       |Convert array of dictionaries to dictionary by using  |
   |                                    |the key                                               |
   +------------------------------------+------------------------------------------------------+
   |to_dic_by_lc_keys                   |Convert array of dictionaries to dictionary by using  |
   |                                    |lowercase keys.                                       |
   +------------------------------------+------------------------------------------------------+
   |to_unique_by_key                    |Convert array of dictionaries to unique array of      |
   |                                    |dictionaries by selecting dictionaries with key.      |
   +------------------------------------+------------------------------------------------------+
   |sh_unique                           |Make the array of dictionaries unique.                |
   +------------------------------------+------------------------------------------------------+
   |write_xlsx_wb                       |Write array of dictionaries to xlsx workbook.         |
   +------------------------------------+------------------------------------------------------+

AoD Method: add
^^^^^^^^^^^^^^^

Description
"""""""""""

Add object to array of dictionaries.

#. If the objects is a dictionary:

   * the object is appended to the array of dictionaries
  
#. If the objects is an array of dictionaries:

   * the object extends the array of dictionaries

Parameter
"""""""""

  .. AoD-Method-add-Parameter-label:
  .. table:: *AoD-Method-add-Parameter*

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |Array of dictionaries|
   +----+-----+-------+---------------------+
   |obj |TyAny|       |Object               |
   +----+-----+-------+---------------------+

Return Value
""""""""""""

  .. AoD-Method-add-Return-Value-label:
  .. table:: *AoD Method-add: Return Value*

   +----+----+---------------------+
   |Name|Type|Description          |
   +====+====+=====================+
   |    |None|                     |
   +----+----+---------------------+

AoD Method: apply_function
^^^^^^^^^^^^^^^^^^^^^^^^^^

Description
"""""""""""

Create a new array of dictionaries by applying the function to each element
of the array of dictionaries.

Parameter
"""""""""

  .. AoD-Method-apply_function-Parameter-label:
  .. table:: *AoD Method apply_function: Parameter*

   +------+-------+---------------------+
   |Name  |Type   |Description          |
   +======+=======+=====================+
   |aod   |TyAoD  |Array of dictionaries|
   +------+-------+---------------------+
   |fnc   |TN_Call|Object               |
   +------+-------+---------------------+
   |kwargs|TN_Dic |Keyword arguments    |
   +------+-------+---------------------+

Return Value
""""""""""""

  .. AoD-Method-apply_function-Return-Value-label:
  .. table:: *AoD Method apply_function: Return Value*

   +-------+-----+-------------------------+
   |Name   |Type |Description              |
   +=======+=====+=========================+
   |aod_new|TyAoD|new array of dictionaries|
   +-------+-----+-------------------------+

Method: csv_dictwriterows
^^^^^^^^^^^^^^^^^^^^^^^^^          

Description
"""""""""""

Write given array of dictionaries (1.argument) to a csv file with the given path
name (2.argument) using the function "dictwriter" of the builtin path module "csv"

Parameter
"""""""""

  .. Parameter-of method-csv_dictwriterows-label:
  .. table:: *Parameter of Method csv_dictwriterows*

   +----+------+---------------------+
   |Name|Type  |Description          |
   +====+======+=====================+
   |aod |TyAoD |Array of dictionaries|
   +----+------+---------------------+
   |path|TyPath|Path                 |
   +----+------+---------------------+
   
Return Value
""""""""""""

  .. Return-Value-of-method-csv_dictwriterows-label:
  .. table:: *Return Value of method csv_dictwriterows*


   +----+------+---------------------+
   |Name|Type  |Description          |
   +====+======+=====================+
   |    |None  |                     |
   +----+------+---------------------+
   
Method: dic_found_with_empty_value
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^       
   
Description
"""""""""""

#. Set the switch sw_found to True if a dictionary with an empty value for the key is found
   in the given array of dictionaries (1.argument). 
#. If the Argument "sw_raise" is True and the switch "sw_found" is True, then an Exception is raised,
   otherwise the value of "sw_found" is returned.                  

Parameter
"""""""""

  .. Parameter-of-method-csv_dic_found_with_empty_value-of-label:
  .. table:: *AoD Method csv_dictwriterows: Parameter*

   +--------+------+-------+---------------------+
   |Name    |Type  |Default|Description          |
   +========+======+=======+=====================+
   |aod     |TyAoD |       |array of dictionaries|
   +--------+------+-------+---------------------+
   |key     |TyStr |       |Key                  |
   +--------+------+-------+---------------------+
   |sw_raise|TyBool|False  |                     |
   +--------+------+-------+---------------------+

Return Value
""""""""""""

  .. AoD-Method-dic_found_with_empty_value-Return-Value-label:
  .. table:: *AoD Method csv_dictwriterows: Return Value*

   +--------+------+----------------------------+
   |Name    |Type  |Description                 |
   +========+======+============================+
   |sw_found|TyBool|key is found in a dictionary|
   +--------+------+----------------------------+
   
Method: extend_if_not_empty
^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

#. Apply the given function (4.argument) to the value of the given dictionary (2.argument) for
   the key (3.argument).
#. The result is used to extend the given array of dictionaries (1.argument).

Parameter
"""""""""

  .. AoD-Method-extend_if_not_empty-Parameter-label:
  .. table:: *AoD Method extend_if_not_empty: Parameter*

   +--------+------+-------+---------------------+
   |Name    |Type  |Default|Description          |
   +========+======+=======+=====================+
   |aod     |TyAoD |       |Array of dictionaries|
   +--------+------+-------+---------------------+
   |dic     |TyDic |       |Dictionary           |
   +--------+------+-------+---------------------+
   |key     |TN_Any|       |Key                  |
   +--------+------+-------+---------------------+
   |function|TyCall|       |Function             |
   +--------+------+-------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-extend_if_not_empty-Return-Value-label:
  .. table:: *AoD Method extend_if_not_empty: Return Value*

   +-------+-----+-------------------------+
   |Name   |Type |Description              |
   +=======+=====+=========================+
   |aod_new|TyAoD|New array of dictionaries|
   +-------+-----+-------------------------+
   
Method: join_aod
^^^^^^^^^^^^^^^^
  
Description
"""""""""""

join 2 arrays of dictionaries

Parameter
"""""""""

  .. AoD-Method-join_aod-Parameter-label:
  .. table:: *AoD Method join_aod: Parameter*

   +----+-----+-------+----------------------------+
   |Name|Type |Default|Description                 |
   +====+=====+=======+============================+
   |aod0|TyAoD|       |First array of dictionaries |
   +----+-----+-------+----------------------------+
   |aod1|TyAoD|       |Second array of dictionaries|
   +----+-----+-------+----------------------------+
   
Return Value
""""""""""""

  .. AoD-Method-join_aod-Return-Value-label:
  .. table:: *AoD Method join_aod: Return Value*

   +-------+-----+-------------------------+
   |Name   |Type |Description              |
   +=======+=====+=========================+
   |aod_new|TyAoD|New array of dictionaries|
   +-------+-----+-------------------------+
   
Method: merge_dic
^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

Merge array of dictionaries (1.argument) with the dictionary (2.argument).

#. Each element of the new array of dictionaries is created by merging an element
   of the given array of dictionaries with the given dictionary.
   
Parameter
"""""""""

  .. AoD-Method-merge_dic-Parameter-label:
  .. table:: *AoD Method merge_dic: Parameter*

   +----+------+-------+---------------------+
   |Name|Type  |Default|Description          |
   +====+======+=======+=====================+
   |aod |TN_AoD|       |Array of dictionaries|
   +----+------+-------+---------------------+
   |dic |TN_Dic|       |Dictionary           |
   +----+------+-------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-merge_dic-Return-Value-label:
  .. table:: *AoD Method merge_dic: Return Value*

   +-------+-----+-------------------------+
   |Name   |Type |Description              |
   +=======+=====+=========================+
   |aod_new|TyAoD|New array of dictionaries|
   +-------+-----+-------------------------+
   
Method: nvl
^^^^^^^^^^^
   
Description
"""""""""""

Replace a none value of the first argument with the emty array. 

Parameter
"""""""""

  .. AoD-Method-nvl-Parameter-label:
  .. table:: *AoD Method nvl: Parameter*

   +----+------+-------+---------------------+
   |Name|Type  |Default|Description          |
   +====+======+=======+=====================+
   |aod |TN_AoD|       |Array of dictionaries|
   +----+------+-------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-nvl-Return-Value-label:
  .. table:: *AoD Method nvl: Return Value*

   +-------+-----+-------------------------+
   |Name   |Type |Description              |
   +=======+=====+=========================+
   |aod_new|TyArr|New array of dictionaries|
   +-------+-----+-------------------------+
   
Method: pd_to_csv
^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

#. Convert the given array of dictionaries (1.argument) to a panda dataframe using the panda function "from_dict".
#. Write the result to a csv file with the given path name (2.argument using the panda function "to_csv".

Parameter
"""""""""

  .. AoD-Method-pd_to_csv-Parameter-label:
  .. table:: *AoD Method pd_to_csv: Parameter*

   +------+------+-------+---------------------+
   |Name  |Type  |Default|Description          |
   +======+======+=======+=====================+
   |aod   |TyAoD |       |Array of dictionaries|
   +------+------+-------+---------------------+
   |path  |TyPath|       |Csv file psth        |
   +------+------+-------+---------------------+
   |fnc_pd|TyCall|       |Panda function       |
   +------+------+-------+---------------------+
   
Method: pl_to_csv
^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

#. Convert the given array of dictionaries (1.argument) to a panda dataframe with the panda function "from_dict". 
#. Convert the result to a polars dataframe using the polars function "to_pandas".
#. Apply the given function (3. argument) to the polars dataframe.
#. Write the result to a csv file with the given name (2.argument) using the polars function "to_csv".

Parameter
"""""""""

  .. AoD-Method-pl_to_csv-Parameter-label:
  .. table:: *AoD Method pl_to_csv: Parameter*

   +------+------+-------+---------------------+
   |Name  |Type  |Default|Description          |
   +======+======+=======+=====================+
   |aod   |TyAoD |       |Array of dictionaries|
   +------+------+-------+---------------------+
   |path  |TyPath|       |Csv file path        |
   +------+------+-------+---------------------+
   |fnc_pd|TyCall|       |Polars function      |
   +------+------+-------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-pl_to_csv-Return-Value-label:
  .. table:: *AoD Method pl_to_csv: Return Value*

   +----+----+---------------------+
   |Name|Type|Description          |
   +====+====+=====================+
   |    |None|                     |
   +----+----+---------------------+
   
Method: put
^^^^^^^^^^^
   
Description
"""""""""""

#. Transform array of dictionaries (1.argument) with a transformer function (3.argument)
#. If the I/O function is defined for the given dataframe type (4.argument).
   #. write result to a csv file with the given path name (2.argument).

Parameter
"""""""""

  .. AoD-Method-put-Parameter-label:
  .. table:: *AoD Method put: Parameter*

   +-------+------+-------+---------------------+
   |Name   |Type  |Default|Description          |
   +=======+======+=======+=====================+
   |aod    |TyAoD |       |Array of dictionaries|
   +-------+------+-------+---------------------+
   |path   |TyPath|       |Csv file path        |
   +-------+------+-------+---------------------+
   |fnc_aod|TyAoD |       |AoD function         |
   +-------+------+-------+---------------------+
   |df_type|TyStr |       |Dataframe type       |
   +-------+------+-------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-put-Return-Value-label:
  .. table:: *AoD Method put: Return Value*

   +----+----+--------------------+
   |Name|Type|Description         |
   +====+====+====================+
   |    |None|                    |
   +----+----+--------------------+
   
Method: sh_doaod_split_by_value_is_not_empty
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

#. Create 2-dimensional dict. of array of dictionaries from given array of dict. (1.argument)
and key (2.argument) to split the array of dictionaries into 2 array of dictionaries by
the two conditions

   #. "the key is contained in the dictionary and the value empty".

   #. "the key is contained in the dictionary and the value is not empty".

#. The first array of dictionaries is created by the condition and is assigned to 
   the new dictionary of array of dictionaries using the given key (3.argument).

#. The second array of dictionaries is created by the negation of the condition 
   and is assigned to the new dictionary of array of dictionaries using the given
   key (4.argument).

Parameter
"""""""""

  .. AoD-Method-sh_doaod_split_by_value_is_not_empty-Parameter-label:
  .. table:: *AoD Method sh_doaod_split_by_value_is_not_empty: Parameter*

   +-----+-----+-------+--------------------------------------+
   |Name |Type |Default|Description                           |
   +=====+=====+=======+======================================+
   |aod  |TyAoD|       |Array of dictionaries                 |
   +-----+-----+-------+--------------------------------------+
   |key  |Any  |       |Key                                   |
   +-----+-----+-------+--------------------------------------+
   |key_n|Any  |       |key of the array of dictionaries      |
   |     |     |       |wich satisfies the condition.         |
   +-----+-----+-------+--------------------------------------+
   |key_y|Any  |       |key of the array of dictionaries which|
   |     |     |       |does not satisfies the condition.     |
   +-----+-----+-------+--------------------------------------+
   
  .. AoD-Method-sh_doaod_split_by_value_is_not_empty-Return-Value-label:
  .. table:: *AoD Method sh_doaod_split_by_value_is_not_empty: Return Value*

   +-----+-------+-----------------------------------+
   |Name |Type   |Description                        |
   +=====+=======+===================================+
   |doaod|TyDoAoD|Dictionary of array of dictionaries|
   +-----+-------+-----------------------------------+
   
Method: sh_dod
^^^^^^^^^^^^^^
   
Description
"""""""""""

Create dictionary of dicionaries from the array of dictionaries (1.argument) and the key (2.argument).       

Parameter
"""""""""

  .. AoD-Method-sh_dod-Parameter-label:
  .. table:: *AoD Method sh_dod: Parameter*

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |Array of dictionaries|
   +----+-----+-------+---------------------+
   |key |Any  |       |Key                  |
   +----+-----+-------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-sh_dod-Return-Value-label:
  .. table:: *AoD Method sh_dod: Return Value*

   +----+-----+--------------------------+
   |Name|Type |Description               |
   +====+=====+==========================+
   |dod |TyDoD|Dictionary of dictionaries|
   +----+-----+--------------------------+
   
Method: sh_unique
^^^^^^^^^^^^^^^^^

Description
"""""""""""

Deduplicate array of dictionaries (1.argument).
   
Parameter
"""""""""

  .. AoD-Method-sh_unique-Parameter-label:
  .. table:: *AoD Method sh_unique: Parameter*

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |Array of dictionaries|
   +----+-----+-------+---------------------+
   |key |Any  |       |Key                  |
   +----+-----+-------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-sh_unique-Return-Value-label:
  .. table:: *AoD Method sh_unique: Return Value*

   +-------+-----+-------------------------+
   |Name   |Type |Description              |
   +=======+=====+=========================+
   |aod_new|TyAoD|New array of dictionaties|
   +-------+-----+-------------------------+
   
Method: split_by_value_is_not_empty
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^      
   
Description
"""""""""""

Split the given array of dictionary into 2 arrays of dictionary by the condition 
"the key is contained in the dictionary and the value is not empty"

Parameter
"""""""""

  .. AoD-Method-split_by_value_is_not_empty-Parameter-label:
  .. table:: *AoD Method split_by_value_is_not_empty: Parameter*

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |array of dictionaries|
   +----+-----+-------+---------------------+
   |key |Any. |       |Key                  |
   +----+-----+-------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-split_by_value_is_not_empty-Return-Value-label:
  .. table:: *AoD Method split_by_value_is_not_empty: Return Value*

   +--------------+--------+---------------------------------+
   |Name          |Type    |Description                      |
   +==============+========+=================================+
   |(aod_n, aod_y)|Ty2ToAoD|Tuple of 2 arrays of dictionaries|
   +--------------+--------+---------------------------------+
   
Method: sw_key_value_found
^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

Set the condition to True if:
* the key is contained in a dictionary of the array of dictionaries and
* the key value is not empty"

Parameter
"""""""""

  .. AoD-Method-sw_key_value_found-Parameter-label:
  .. table:: *AoD Method sw_key_value_found: Parameter*

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |Array of dictionaries|
   +----+-----+-------+---------------------+
   |key |Any  |       |Key                  |
   +----+-----+-------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-sw_key_value_found-Return-Value-label:
  .. table:: *AoD Method sw_key_value_found: Return Value*

   +----+------+-------+--------------------------------+
   |Name|Type  |Default|Description                     |
   +====+======+=======+================================+
   |sw  |TyBool|       |key is contained in a dictionary|
   |    |      |       |of the array of dictionaries    |
   +----+------+-------+--------------------------------+
   
Method: to_aoa
^^^^^^^^^^^^^^
   
Description
"""""""""""

Create array of arrays from given array of dictionaries (1.argument).

#. If switch sw_keys (2.argument) is True:

   Create the first element of the array of arrays as the list of dict. keys of the
   first elements of the array of dictionaries.

#. If the switch sw_values (3. argument) is True:

   Create the other elemens of the array of dictionries as list of dict. values of the
   elements of the array of dictionaries.

Parameter
"""""""""

  .. AoD-Method-to_aoa-Parameter-label:
  .. table:: *AoD Method to_aoa: Parameter*

   +---------+------+-------+---------------------+
   |Name     |Type  |Default|Description          |
   +=========+======+=======+=====================+
   |aod      |TyAoD |       |array of dictionaries|
   +---------+------+-------+---------------------+
   |sw_keys  |TyBool|       |keys switch          |
   +---------+------+-------+---------------------+
   |sw_values|TyBool|       |values switch        |
   +---------+------+-------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-to_aoa-Return-Value-label:
  .. table:: *AoD Method to_aoa: Return Value*

   +----+-----+---------------+
   |Name|Type |Description    |
   +====+=====+===============+
   |aoa |TyAoA|array of arrays|
   +----+-----+---------------+
   
AoD Method: to_aoa of_key_values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

Convert the given array of dictionary (1.argument) into an array of arrays.
#. Create first element of the new array of arrays as the keys-list of the first dictionary.
#. Create other elements as the values-lists of the dictionaries of the array of dictionaries.

Parameter
"""""""""

  .. AoD-Method-to_aoa of_key_values-Parameter-label:
  .. table:: *AoD Method to_aoa of_key_values: Parameter*

   +----+-----+--------+---------------------+
   |Name|Type |Default |Description          |
   +====+=====+========+=====================+
   |aod |TyAoD|        |Array of dictionaries|
   +----+-----+--------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-to_aoa of_key_values-Return-Value-label:
  .. table:: *AoD Method to_aoa of_key_values: Return Value*

   +----+-----+---------------+
   |Name|Type |Description    |
   +====+=====+===============+
   |aoa |TyAoA|Array of arrays|
   +----+-----+---------------+
   
AoD Method: to_aoa_of_values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  
Description
"""""""""""

Convert the given array of dictionaries (1.argument) into an array of arrays.
The elements of the new array of arrays are the values-lists of the dictionaries
of the array of dictionaries.

Parameter
"""""""""

  .. AoD-Method-to_aoa_of_values-Parameter-label:
  .. table:: *AoD Method to_aoa_of_values: Parameter*

   +----+-----+--------+---------------------+
   |Name|Type |Default |Description          |
   +====+=====+========+=====================+
   |aod |TyAoD|        |Array of dictionaries|
   +----+-----+--------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-to_aoa_of_values-Return-Value-label:
  .. table:: *AoD Method to_aoa_of_values: Return Value*

   +----+-----+--------+---------------+
   |Name|Type |Default |Description    |
   +====+=====+========+===============+
   |aoa |TyAoA|        |Array of arrays|
   +----+-----+--------+---------------+
   
AoD Method: to_arr of_key_values
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Description
"""""""""""

Convert the given array of dictionaries (1.argument) to an array. The elements of the new
array are the selected values of each dictionary of the array of dictionaries with the 
given key (2.argument).

Parameter
"""""""""

  .. AoD-Method-to_arr of_key_values-Parameter-label:
  .. table:: *AoD Method to_arr of_key_values: Parameter*

   +----+-----+--------+---------------------+
   |Name|Type |Default |Description          |
   +====+=====+========+=====================+
   |aod |TyAoD|        |Array of dictionaries|
   +----+-----+--------+---------------------+
   |key |Any  |        |Key                  |
   +----+-----+--------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-to_arr of_key_values-Return-Value-label:
  .. table:: *AoD Method to_arr of_key_values: Return Value*

   +----+-----+-----------+
   |Name|Type |Description|
   +====+=====+===========+
   |arr |TyAoD|New array  |
   +----+-----+-----------+
   
AoD Method: to_doaod_by_key
^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. AoD-Method-to_doaod_by_key-Parameter-label:
  .. table:: *AoD Method to_doaod_by_key: Parameter*

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |Array of dictionaries|
   +----+-----+-------+---------------------+
   |key |Any  |       |Key                  |
   +----+-----+-------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-to_doaod_by_key-Return-Value-label:
  .. table:: *AoD Method to_doaod_by_key: Return Value*

   +-----+-----+-----------------------------------+
   |Name |Type |Description                        |
   +=====+=====+===================================+
   |doaod|TyAoD|Dictionary of array of dictionaries|
   +-----+-----+-----------------------------------+
   
AoD Method: to_dod_by_key
^^^^^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. AoD-Method-to_dod_by_key-Parameter-label:
  .. table:: *AoD Method to_dod_by_key: Parameter*

   +----+-----+-------+-------------+
   |Name|Type |Default|Description  |
   +====+=====+=======+=============+
   |aod |TyAoD|       |             |
   +----+-----+-------+-------------+
   |key |Any  |       |             |
   +----+-----+-------+-------------+
   
Return Value
""""""""""""

  .. AoD-Method-to_dod_by_key-Return-Value-label:
  .. table:: *AoD Method to_dod_by_key: Return Value*

   +----+-----+-------------+
   |Name|Type |Description  |
   +====+=====+=============+
   |dic |TyDic|             |
   +----+-----+-------------+
   
   
AoD Method: to_doa_by_lc_keys
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. AoD-Method-to_doa_by_lc_keys-Parameter-label:
  .. table:: *AoD Method to_doa_by_lc_keys: Parameter*

   +----+-----+-------+-------------+
   |Name|Type |Default|Description  |
   +====+=====+=======+=============+
   |aod |TyAoD|       |             |
   +----+-----+-------+-------------+
   |key |Any  |       |             |
   +----+-----+-------+-------------+
   
Return Value
""""""""""""

  .. AoD-Method-to_doa_by_lc_keys-Return-Value-label:
  .. table:: *AoD Method to_doa_by_lc_keys: Return Value*

   +----+-----+-------------+
   |Name|Type |Description  |
   +====+=====+=============+
   |doa |TyDoA|             |
   +----+-----+-------------+
   
AoD method: to_unique_by_key
^^^^^^^^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. AoD-Method-to_unique_by_key-Parameter-label:
  .. table:: *AoD Method to_unique_by_key: Parameter*

   +----+-----+-------+-------------+
   |Name|Type |Default|Description  |
   +====+=====+=======+=============+
   |aod |TyAoD|       |             |
   +----+-----+-------+-------------+
   |key |Any  |       |             |
   +----+-----+-------+-------------+
   
Return Value
""""""""""""

  .. AoD-Method-to_unique_by_key-Return-Value-label:
  .. table:: *AoD Method csv_dictwriterows: Return Value*

   +-------+-----+-------+-------------+
   |Name   |Type |Default|Description  |
   +=======+=====+=======+=============+
   |aod_new|TyAoD|       |             |
   +-------+-----+-------+-------------+
   
AoD method: write_xlsx_wb
^^^^^^^^^^^^^^^^^^^^^^^^^
   
Parameter
"""""""""

  .. AoD-Method-write_xlsx_wb-Parameter-label:
  .. table:: *AoD Method write_xlsx_wb: Parameter*

   +----+-----+-------+---------------------+
   |Name|Type |Default|Description          |
   +====+=====+=======+=====================+
   |aod |TyAoD|       |array of dictionaries|
   +----+-----+-------+---------------------+
   
Return Value
""""""""""""

  .. AoD-Method-write_xlsx_wb-Return-Value-label:
  .. table:: *AoD Method write_xlsx_wb: Return Value*

   +----+-----+-----------+
   |Name|Type |Description|
   +====+=====+===========+
   |    |None |           |
   +----+-----+-----------+
   
Module: aodpath.py
==================

The Module ``aodpath.py`` contains only the static class ``AoDPath``;

Class: AoDoPath
---------------

Methods
^^^^^^^

  .. Methods-of-class-AoDoPath-label:
  .. table:: *Methods of class AoDoPath*

   +---------+----------------------------------------------+
   |Name     |short Description                             |
   +=========+==============================================+
   |sh_aopath|Show array of paths for array of dictionaries.|
   +---------+----------------------------------------------+

AoDPath Method: sh_a_path
^^^^^^^^^^^^^^^^^^^^^^^^^

Convert Array of Path-Disctionaries to Array of Paths.

Parameter
"""""""""

  .. AoD-Method-sh_aopath-Parameter-label:
  .. table:: *AoD Method sh_aopath: Parameter*

   +----+-----+-------+---------------------------+
   |Name|Type |Default|Description                |
   +====+=====+=======+===========================+
   |aod |TyAoD|       |Array of Path-Dictionaries.|
   +----+-----+-------+---------------------------+
   
Return Value
""""""""""""

  .. AoD-Method-sh_aopath-Return-Value-label:
  .. table:: *AoD Method sh_aopath: Return Value*

   +----+--------+--------------+
   |Name|Type    |Description   |
   +====+========+==============+
   |    |TyAoPath|Array of paths|
   +----+--------+--------------+
   
########
Appendix
########

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
