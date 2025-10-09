.. _data_manipulation:

Basic data manipulation
=======================

.. currentmodule:: canopy.core.field

.. _reading_files:

Reading files
-------------

The basic way to read a data file into a :class:`Field` object is by using the :meth:`Field.from_file` class method as follows:

.. code-block:: python

   import canopy as cp
   cpool = cp.Field.from_file('/path/to/output/cpool.out.gz', file_format='lpjg_annual', grid_type='lonlat', source='lpjguess:cpool')

This reads the file ``cpool.out.gz``, located at ``/path/to/output/``.

  * The ``file_format`` argument specifies the format of the file (e.g., ``lpjg_annual``, ``lpjg_monthly``, ``fluxnet2015``...)
  * The ``grid_type`` argument specifies the associated grid (e.g., ``lonlat``, ``sites``...)
  * The ``source`` argument specifies the metadata to retrieve. The format for this argument is ``source:field`` (e.g., ``lpjguess:cpool``, ``lpjguess:anpp``...)

.. note::

   LPJ-GUESS output files can be in plain text or *gzipped*; the reader will manage this automatically.

The format ``lpjg_annual`` and the grid type ``lonlat`` are actually the default, so the line below accomplishes the same task:

.. code-block:: python

   cpool = cp.Field.from_file('/path/to/output/cpool.out.gz')

Printing the field gives us some basic information about it:

.. code-block:: python

   print(cpool)

.. code-block:: console

   Data
   ----
   name: [no name]
   units: [no units]
   description: [no description]
   file format: LPJ-GUESS: common output (annual)
   original file: /path/to/output/cpool.out.gz
   
   Grid: lonlat
   ------------
   Longitude: 
   -26.25 to 34.75 (step: 0.5)
   Latitude: 
   35.25 to 71.75 (step: 0.5)
   
   Time series
   -----------
   Span: 1850-01-01 00:00:00 - 2014-12-31 23:59:59.999999999
   Frequency: Y-DEC
   
   History
   -------
   2025-05-08 20:27:57: Data read from /path/to/output/cpool.out.gz


.. _data_sources:

Data sources
------------

.. currentmodule:: canopy.sources.source_abc

A data :class:`Source` object provides a convenient way to access data. The source can be a directory with model output or measurement data:

.. code-block:: python

   import canopy as cp
   my_run = cp.get_source('/path/to/output/', 'lpjguess')
   # Print available fields
   print(my_run)

.. code-block:: console

  Source: LPJ-GUESS
  Path: /path/to/output

  L  M  Field       Description                                            (units)
  -------------------------------------------------------------------------------------------
        aaet        Annual actual evapotranspiration by PFT                (mm year^-1)
        agpp        Annual gross primary productivity by PFT               (kgC m^-2 year^-1)
        anpp        Annual net primary productivity by PFT                 (kgC m^-2 year^-1)
        cflux       Annual carbon flux by pool                             (kgC m^-2 year^-1)
        cmass       Carbon mass in the vegetation pool by PFT              (kgC m^-2)
        cpool       Ecosystem carbon mass by pool                          (kgC m^-2)
        cton_leaf   Leaf carbon to nitrogen ratio by PFT                   (kgC/kgN)
        dens        Number of individuals per unit area, per PFT           (m^-2)
        doc         Dissolved Organic Carbon                               (kgC ha)
        fpc         Fraction of modeled area covered by vegetation by PFT  (1)
        lai         One-sided leaf area per unit of modeled area by PFT    (1)
        nflux       Nitrogen flux by different processes                   (kgN ha year^-1)
        ngases      Flux of nitrogen gases from soil or fire               (kgN ha year^-1)
        nmass       Nitrogen mass stored in the vegetation by PFT          (kgN ha)
        npool       Ecosystem nitrogen mass by pool                        (kgN ha)
        nsources    Nitrogen sources by type                               (kgN ha year^-1)
        soil_nflux  Nitrogen flux from the soil by gaseous species         (kgN ha year^-1)
        soil_npool  Nitrogen storage in the soil by pool                   (kgN ha)
        tot_runoff  Total water runnoff by PFT                             (mm year^-1)


A field can be loaded from disk with the :meth:`Source.load_field` method. The field will appear as *loaded* (``L``):

.. code-block:: python

   my_run.load_field('cpool')
   print(my_run)

.. code-block:: console

  Source: LPJ-GUESS
  Path: /path/to/output

  L  M  Field       Description                                            (units)
  -------------------------------------------------------------------------------------------
        aaet        Annual actual evapotranspiration by PFT                (mm year^-1)
        agpp        Annual gross primary productivity by PFT               (kgC m^-2 year^-1)
        anpp        Annual net primary productivity by PFT                 (kgC m^-2 year^-1)
        cflux       Annual carbon flux by pool                             (kgC m^-2 year^-1)
        cmass       Carbon mass in the vegetation pool by PFT              (kgC m^-2)
  ✓     cpool       Ecosystem carbon mass by pool                          (kgC m^-2)
        cton_leaf   Leaf carbon to nitrogen ratio by PFT                   (kgC/kgN)
        dens        Number of individuals per unit area, per PFT           (m^-2)
        doc         Dissolved Organic Carbon                               (kgC ha)
        fpc         Fraction of modeled area covered by vegetation by PFT  (1)
        lai         One-sided leaf area per unit of modeled area by PFT    (1)
        nflux       Nitrogen flux by different processes                   (kgN ha year^-1)
        ngases      Flux of nitrogen gases from soil or fire               (kgN ha year^-1)
        nmass       Nitrogen mass stored in the vegetation by PFT          (kgN ha)
        npool       Ecosystem nitrogen mass by pool                        (kgN ha)
        nsources    Nitrogen sources by type                               (kgN ha year^-1)
        soil_nflux  Nitrogen flux from the soil by gaseous species         (kgN ha year^-1)
        soil_npool  Nitrogen storage in the soil by pool                   (kgN ha)
        tot_runoff  Total water runnoff by PFT                             (mm year^-1)


The field can be accessed through the dot (``.``) operator. If the field held in the :class:`Source` object is modified, it will be indicated under ``M``:

.. code-block:: python

   # Create a new field 'cpool_av' by averaging in space.
   # This doesn't modify the original field
   cpool_av = my_run.cpool.red_space('av')

   # Average the original field in place (it will appear as modified in the Source object)
   my_run.cpool.red_space('av', inplace=True)
   print(my_run)

.. code-block:: console

  Source: LPJ-GUESS
  Path: /home/belda-d/data/pyguess_test_data/europe_LR_100p/output/
  
  L  M  Field       Description                                            (units)
  -------------------------------------------------------------------------------------------
        aaet        Annual actual evapotranspiration by PFT                (mm year^-1)
        agpp        Annual gross primary productivity by PFT               (kgC m^-2 year^-1)
        anpp        Annual net primary productivity by PFT                 (kgC m^-2 year^-1)
        cflux       Annual carbon flux by pool                             (kgC m^-2 year^-1)
        cmass       Carbon mass in the vegetation pool by PFT              (kgC m^-2)
  ✓  ✓  cpool       Ecosystem carbon mass by pool                          (kgC m^-2)
        cton_leaf   Leaf carbon to nitrogen ratio by PFT                   (kgC/kgN)
        dens        Number of individuals per unit area, per PFT           (m^-2)
        doc         Dissolved Organic Carbon                               (kgC ha)
        fpc         Fraction of modeled area covered by vegetation by PFT  (1)
        lai         One-sided leaf area per unit of modeled area by PFT    (1)
        nflux       Nitrogen flux by different processes                   (kgN ha year^-1)
        ngases      Flux of nitrogen gases from soil or fire               (kgN ha year^-1)
        nmass       Nitrogen mass stored in the vegetation by PFT          (kgN ha)
        npool       Ecosystem nitrogen mass by pool                        (kgN ha)
        nsources    Nitrogen sources by type                               (kgN ha year^-1)
        soil_nflux  Nitrogen flux from the soil by gaseous species         (kgN ha year^-1)
        soil_npool  Nitrogen storage in the soil by pool                   (kgN ha)
        tot_runoff  Total water runnoff by PFT                             (mm year^-1)

.. note::
   The names, descriptions, and units in the source-object-printout are those of the original fields. The source itself does not keep track of the modifications done ``inplace`` to a field; it only shows that the original field was altered.

.. currentmodule:: canopy.core.field

Slicing data
------------

Space- and time- slicing
^^^^^^^^^^^^^^^^^^^^^^^^

The data can be sliced along the ``lon``, ``lat``, and ``time`` axes by invoking the :meth:`Field.sel_slice` *(select slice)* method:

.. code-block:: python

   # Spain bounding box: [9.5W - 3.5E] [35.5N - 44N]
   cpool_spain = my_run.cpool.sel_slice(lon_slice=(-9.5,3.5), lat_slice=(35.5,44), time_slice=(1901,2000))
   print(cpool_spain)

.. code-block:: console

  Data
  ----
  name: [no name]
  units: [no units]
  description: [no description]
  
  Grid: lonlat
  ------------
  Longitude: 
  -9.25 to 3.25 (step: 0.5)
  Latitude: 
  35.75 to 43.75 (step: 0.5)
  
  Time series
  -----------
  Span: 1901-01-01 00:00:00 - 2000-12-31 23:59:59.999999999
  Frequency: Y-DEC
  
  History
  -------
  2025-05-09 12:55:41: Data read from /home/belda-d/data/pyguess_test_data/europe_LR_100p/output/cpool.out.gz
  2025-05-09 12:56:17: Sliced 'lon': (-9.5, 3.5)
  2025-05-09 12:56:17: Sliced 'lat': (35.5, 44)
  2025-05-09 12:56:17: Sliced 'time': (1901, 2000)


.. note::

   The ``time_slice`` argument takes a tuple of two integers, representing the years to be sliced out. In a future version, time slicing will allow for finer selection with date objects instead of integers.

.. note::

   Automatic metadata and units handling is planned for a future version of **canopy**.


Layer selection
^^^^^^^^^^^^^^^

To select layers, either the :meth:`Field.sel_layers` or square-bracket notation can be used. The argument can be the name of a layer or a list of names. To discard layers, use the :meth:`Field.drop_layers` method:

.. code-block:: python

   print(f"Current field layers: {cpool_spain.layers}")
   # Using sel_slice to select the 'Total' carbon pool
   cpool_tot = cpool_spain.sel_slice('Total')
   print(f"Just the 'Total' layer (sel_slice): {cpool_tot.layers}")
   # Using square brackets to select the 'Total' layer
   cpool_tot2 = cpool_spain['Total']
   print(f"Just the 'Total' layer (using []): {cpool_tot.layers}")
   # Selecting more than one layer:
   cpool_nonveg = cpool_spain[['SoilC', 'LitterC']]
   print(f"Layers of cpool_nonveg: {cpool_nonveg.layers}")
   # Drop 'Total' layer
   cpool_notot = cpool_spain.drop_layers('Total')
   print(f"Layers of cpool_notot: {cpool_notot.layers}")

.. code-block:: console

  Current field layers: ['VegC', 'LitterC', 'SoilC', 'Total']
  Just the 'Total' layer (sel_slice): ['VegC', 'LitterC', 'SoilC', 'Total']
  Just the 'Total' layer (using []): ['VegC', 'LitterC', 'SoilC', 'Total']
  Layers of cpool_nonveg: ['SoilC', 'LitterC']
  Layers of cpool_notot: ['VegC', 'LitterC', 'SoilC']

Reducing data
-------------

Spatial reductions
^^^^^^^^^^^^^^^^^^

The data can be reduced along the ``lon`` and ``lat`` axes by invoking the :meth:`Field.red_space` *(reduce in space)* method, which takes as arguments the grid reduction operation (*gridop*, one of ``av``, ``sum``), and the axis along which to perform the reduction (``lat``, ``lon``, or ``both``, the default value). The average/sum will be weighted by geometrical factors according to the field's grid type.

.. code-block:: python

   cpool_sum_lon = cpool_spain.red_space('sum', axis='lon') # Aggregate along the longitudinal axis
   cpool_sum = cpool_spain.red_space('sum') # Aggregate on both axes
   cpool_av = cpool_spain.red_space('av') # Average on both axes
   print(cpool_av)

.. code-block:: console

  Data
  ----
  name: [no name]
  units: [no units]
  description: [no description]

  Grid: lonlat
  ------------
  Longitude: 
  reduced (gridop = av)
  Latitude: 
  reduced (gridop = av)

  Time series
  -----------
  Span: 1901-01-01 00:00:00 - 2000-12-31 23:59:59.999999999
  Frequency: Y-DEC

  History
  -------
  2025-05-09 12:55:41: Data read from /home/belda-d/data/pyguess_test_data/europe_LR_100p/output/cpool.out.gz
  2025-05-09 12:56:17: Sliced 'lon': (-9.5, 3.5)
  2025-05-09 12:56:17: Sliced 'lat': (35.5, 44)
  2025-05-09 12:56:17: Sliced 'time': (1901, 2000)
  2025-05-09 13:26:22: Spatial reduction: 'av', 'both'

Time reductions
^^^^^^^^^^^^^^^

Reductions along the ``time`` axis are applied through the :meth:`Field.red_time` *(reduce in time)* method. This method takes as arguments the time reduction operation (``timeop``, one of ``av`` or ``sum``) and the frequency (``freq``) of the reduction, in the format ``nP``, where ``n`` is an integer number, and ``P`` is a time period. For example, to average every 5 years, the ``freq`` argument would be the string ``5Y``.

.. code-block:: python

   # Time aggregation
   cpool_timesum = cpool_spain.red_time('sum')
   # Time average
   cpool_tav = cpool_spain.red_time('av')
   # Time average every 5 years
   cpool_tav_5year = cpool_spain.red_time('av', '5Y')
   print(cpool_tav_5year)

.. code-block:: console

  Data
  ----
  name: [no name]
  units: [no units]
  description: [no description]

  Grid: lonlat
  ------------
  Longitude: 
  -9.25 to 3.25 (step: 0.5)
  Latitude: 
  35.75 to 43.75 (step: 0.5)

  Time series
  -----------
  Span: 1901-01-01 00:00:00 - 2000-12-31 23:59:59.999999999
  Frequency: 5Y-DEC
  Reduction: 'av'

  History
  -------
  2025-05-09 12:55:41: Data read from /home/belda-d/data/pyguess_test_data/europe_LR_100p/output/cpool.out.gz
  2025-05-09 12:56:17: Sliced 'lon': (-9.5, 3.5)
  2025-05-09 12:56:17: Sliced 'lat': (35.5, 44)
  2025-05-09 12:56:17: Sliced 'time': (1901, 2000)
  2025-05-09 15:12:38: Time reduction: av, 5Y


Layer reductions
^^^^^^^^^^^^^^^^

The method :meth:`Field.red_layers` allows to create a new layer from two or more existing layers. The method accepts the following arguments:

  * ``redop``: The reduction operation; currently one of ``sum``, ``av``, ``maxLay``, ``/``.
  * ``layers``: A list of layer names to be reduced.
  * ``name``: The name of the new layer.
  * ``drop``: A boolean indicating whether to drop the original layers (default: ``False``).

.. code-block:: python

   print("Original data:")
   print(cpool_spain.data)
   # Calculate the Total C
   layers = cpool_spain.layers # ['VegC', 'LitterC', 'SoilC', 'Total']
   layers.remove('Total') # ['VegC', 'LitterC', 'SoilC']
   cpool_spain.red_layers('sum', layers, name='TotalC2', inplace=True)
   # Calculate the ratio of VegC to Total
   cpool_spain.red_layers('/', ['VegC', 'Total'], name='VegC_ratio', inplace=True)
   print("After layer reductions:")
   print(cpool_spain.data)

.. code-block:: console

  Original data:
                      VegC  LitterC  SoilC   Total
  lon   lat   time                                
  -9.25 38.75 1901   3.779    1.046  4.305   9.130
              1902   3.717    1.087  4.299   9.102
              1903   3.648    1.112  4.307   9.067
              1904   3.755    1.064  4.308   9.127
              1905   3.824    1.078  4.307   9.209
  ...                  ...      ...    ...     ...
   3.25 43.75 1996  15.585    7.749  8.903  32.237
              1997  15.680    7.696  8.900  32.275
              1998  15.552    7.878  8.897  32.327
              1999  15.636    7.783  8.897  32.316
              2000  15.554    7.856  8.896  32.306

  [30200 rows x 4 columns]
  After layer reductions:
                      VegC  LitterC  SoilC   Total  TotalC2  VegC_ratio
  lon   lat   time                                                     
  -9.25 38.75 1901   3.779    1.046  4.305   9.130    9.130    0.413910
              1902   3.717    1.087  4.299   9.102    9.103    0.408372
              1903   3.648    1.112  4.307   9.067    9.067    0.402338
              1904   3.755    1.064  4.308   9.127    9.127    0.411417
              1905   3.824    1.078  4.307   9.209    9.209    0.415246
  ...                  ...      ...    ...     ...      ...         ...
   3.25 43.75 1996  15.585    7.749  8.903  32.237   32.237    0.483451
              1997  15.680    7.696  8.900  32.275   32.276    0.485825
              1998  15.552    7.878  8.897  32.327   32.327    0.481084
              1999  15.636    7.783  8.897  32.316   32.316    0.483847
              2000  15.554    7.856  8.896  32.306   32.306    0.481459

  [30200 rows x 6 columns]


The RedSpec object
^^^^^^^^^^^^^^^^^^

.. currentmodule:: canopy.core.redspec

The :class:`RedSpec` *(Reduction Specification)* class can hold information about a number of reduction operations, and can be passed to the :meth:`Field.reduce` method. This can be used to, for example, apply the same slicing/reduction to a number of fields:

.. code-block:: python

   rs = cp.RedSpec(lat_slice=(35.5,44),
                   lon_slice=(-9.5,3.5),
                   time_slice=(1901,2000),
                   gridop='av',
                   axis='both',
                   layers='Total')
   aaet = my_run.load_field('aaet')
   anpp = my_run.load_field('anpp')
   agpp = my_run.load_field('agpp')
   reduced_fields = []
   for field in [aaet, anpp, agpp]:
       reduced_fields.append(field.reduce(rs))
   for field in reduced_fields:
       print(field)

Filtering data
--------------

.. currentmodule:: canopy.core.field

Use the :meth:`Field.filter` method to extract rows from a Field object that match a boolean condition, expressed as a query string using layers. 

.. code-block:: python

   # Load field
   anpp = Field.from_file("/path/to/file/anpp.out")

   # Keep only rows where 'Total' > 100
   anpp_above5 = anpp.filter('Total > 0.5')

   # In-place filtering with multiple conditions
   anpp.filter('Total > 0.5 and Abi_alb < 0.3', inplace=True)

By default, :meth:`Field.filter` remove non-matching rows, but you can keep them and set their values to NaN using ``fill_nan=True``.

.. note::

   See pandas documentation for `DataFrame.query() <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.query.html>`_ for more details on the query string.

Changing the units
------------------

The units of a Field can be changed with the :meth:`Field.convert_units` method, which takes two arguments:

* ``factor``: The *multiplicative* factor to apply.
* ``units``: The new units (a string).

.. code-block:: python

   # Change evapotranspiration units from mm to m
   print("Before unit change:")
   print(aaet)
   print(aaet.data)
   aaet.convert_units(1.e-3, 'm')
   print("After unit change:")
   print(aaet.data)
  

.. code-block:: console

  Before unit change:
  Data
  ----
  name: Annual AET
  units: mm
  description: Annual actual evapotranspiration by PFT
  file format: LPJ-GUESS: common output (annual)
  original file: /home/belda-d/data/pyguess_test_data/europe_LR_100p/output/aaet.out.gz
  source: LPJ-GUESS

  Grid: lonlat
  ------------
  Longitude: 
  -26.25 to 34.75 (step: 0.5)
  Latitude: 
  35.25 to 71.75 (step: 0.5)

  Time series
  -----------
  Span: 1850-01-01 00:00:00 - 2014-12-31 23:59:59.999999999
  Frequency: Y-DEC

  History
  -------
  2025-05-13 16:06:19: Data read from /home/belda-d/data/pyguess_test_data/europe_LR_100p/output/aaet.out.gz
                     Abi_alb   BES  Bet_pen  ...  Til_cor  C3_gr   Total
  lon    lat   time                          ...                        
  -26.25 69.25 1850      0.0  0.00      0.0  ...      0.0   0.00    0.00
               1851      0.0  0.00      0.0  ...      0.0   0.00    0.00
               1852      0.0  0.00      0.0  ...      0.0   0.00    0.00
               1853      0.0  0.00      0.0  ...      0.0   0.00    0.00
               1854      0.0  0.00      0.0  ...      0.0   0.00    0.00
  ...                    ...   ...      ...  ...      ...    ...     ...
   34.75 69.25 2010      0.0  0.25      0.0  ...      0.0   1.19  105.49
               2011      0.0  0.27      0.0  ...      0.0   1.28  117.36
               2012      0.0  0.31      0.0  ...      0.0   1.61  136.71
               2013      0.0  0.29      0.0  ...      0.0   1.30  128.72
               2014      0.0  0.29      0.0  ...      0.0   1.28  128.42
  After unit change:
  Data
  ----
  name: Annual AET
  units: m
  description: Annual actual evapotranspiration by PFT
  file format: LPJ-GUESS: common output (annual)
  original file: /home/belda-d/data/pyguess_test_data/europe_LR_100p/output/aaet.out.gz
  source: LPJ-GUESS

  Grid: lonlat
  ------------
  Longitude: 
  -26.25 to 34.75 (step: 0.5)
  Latitude: 
  35.25 to 71.75 (step: 0.5)

  Time series
  -----------
  Span: 1850-01-01 00:00:00 - 2014-12-31 23:59:59.999999999
  Frequency: Y-DEC

  History
  -------
  2025-05-13 16:06:19: Data read from /home/belda-d/data/pyguess_test_data/europe_LR_100p/output/aaet.out.gz
                     Abi_alb      BES  Bet_pen  Bet_pub  ...  Que_rob  Til_cor    C3_gr    Total
  lon    lat   time                                      ...                                    
  -26.25 69.25 1850      0.0  0.00000      0.0  0.00000  ...      0.0      0.0  0.00000  0.00000
               1851      0.0  0.00000      0.0  0.00000  ...      0.0      0.0  0.00000  0.00000
               1852      0.0  0.00000      0.0  0.00000  ...      0.0      0.0  0.00000  0.00000
               1853      0.0  0.00000      0.0  0.00000  ...      0.0      0.0  0.00000  0.00000
               1854      0.0  0.00000      0.0  0.00000  ...      0.0      0.0  0.00000  0.00000
  ...                    ...      ...      ...      ...  ...      ...      ...      ...      ...
   34.75 69.25 2010      0.0  0.00025      0.0  0.00000  ...      0.0      0.0  0.00119  0.10549
               2011      0.0  0.00027      0.0  0.00001  ...      0.0      0.0  0.00128  0.11736
               2012      0.0  0.00031      0.0  0.00001  ...      0.0      0.0  0.00161  0.13671
               2013      0.0  0.00029      0.0  0.00000  ...      0.0      0.0  0.00130  0.12872
               2014      0.0  0.00029      0.0  0.00000  ...      0.0      0.0  0.00128  0.12842


Merging fields
--------------

.. currentmodule:: canopy.util.fieldops

The function :func:`merge_fields` To merge fields defined on compatible grids (for example, lonlat grids with the same resolution).

A possible use case is to merge data from separate simulations into a single field for easier manipulation. Assume you have split a large LPJ-GUESS gridlist into three smaller gridlists so that you keep within walltime restrictions in your HPC. You run the three separate simuations, and then merge the outputs as follows:

.. code-block:: python

   import canopy as cp

   field1 = cp.Field.from_file('/path/to/simulation1/output/aaet.out.gz', grid_type='lonlat')
   field2 = cp.Field.from_file('/path/to/simulation2/output/aaet.out.gz', grid_type='lonlat')
   field3 = cp.Field.from_file('/path/to/simulation3/output/aaet.out.gz', grid_type='lonlat')

   # The merge_fields function takes in a list of fields and returns a field with the merged data
   field = cp.merge_fields([field1, field2, field3])

.. currentmodule:: canopy.grid.grid_lonlat

.. note::

    The function checks if the grids associated to the data are compatible, as defined by the grid object's `is_compatible` method (e.g. :meth:`GridLonLat.is_compatible`). Fields are required to have the same layers.
