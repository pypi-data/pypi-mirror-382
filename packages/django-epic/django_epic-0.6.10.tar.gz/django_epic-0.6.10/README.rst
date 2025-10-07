====
EPIC
====

EPIC stands for Electronics Parts Inventory Center and is a Django app
to track and order parts needed during Printed Circuit Boards (PCBs)
assembly.

Features:
	- automatically generate parts orders based on ordered PCBs and
          current stock at warehouses

	- parts orders take into account expected losses during assembly
	  via overage-percentage and orders are rounded up to standard-package
	  size (e.g., 10,000 parts for reels)

	- track life-time status of parts (preview, active,
          deprecated, or obsolete) and manage substitute parts

	- track shipments of parts and PCBs from vendor to destination
	  warehouse or shipments from one warehouse to another

	- view stock of each warehouse or of all warehouses together
	  for any date, e.g., for tax reporting purposes

	- see any orders that are overdue or close to being overdue

	- automatically track actual parts costs vs. expected (target) cost
	  both for individual parts and entire PCBs

	- each part links to Octopart search and can link to its data-sheet

	- each part may have one or more vendors, with automatic link to
	  vendor's page (e.g., DigiKey, Mouser, or Arrow)

	- autocompletion for part numbers, PCB footprints, orders, etc.

	- automatically generate BOM from, e.g., KiCad schematics

	- export orders, shipments, inventories and current stock to Excel

	- for KiCad users, automatically assign footprints for KiCad designs

	- JSON API to access/update EPIC database through the web.

Typical workflow:

1) Enter vendors from which you order parts and at least
   one vendor from which you order PCBs (i.e., your assembly house).

2) Enter warehouses to which parts should be shipped.  You must
   create a warehouse for each assembly house since it must receive
   parts before it can assemble them into a PCB.

3) Enter the parts you plan on using in EPIC.  For example, you'd
   enter the parts value (e.g., 1k), it's footprint, standard-package
   size (e.g., 10,000 pieces/reel), minimum overage, price, and the
   vendor(s) you're purchasing it from.

4) Design a PCB with your favorite EDA tool, for example KiCad
   (http://www.kicad-pcb.org/).

5) Export the Bill-of-Materials (BOM) from the EDA tool to EPIC.

   For KiCad, there is a module epic.kicad that provides the means to
   accomplish this easily.  Specifically, epic.kicad.scripts.epic_bom()
   provides a command-line interface that can be called as a Eeschema
   BOM plug in.  See the epic-bom command in django-epic-sample for a
   complete example of how to use this.  This module works with
   KiCad v6 or newer.

6) Create a purchase-order for your favorite assembly-house for
   a certain quantity of your newly designed PCB.

7) EPIC uses the BOM and parts information to create one or more
   parts orders.  You can export these orders as Excel files and
   submit them to your parts vendor(s).

8) Parts get shipped from the vendor to your favorite assembly house.
   You enter these shipments into EPIC as they happen.

9) At any time, you can see if all the parts required for a PCB have
   arrived at the assembly-house.

10) Once all the parts have arrived, the assembly house builds the PCBs
    and ships the finished goods to you.  Again, you enter these shipments
    into EPIC, which will then subtract the parts used for those PCBs
    (including any overages).

11) Rinse and repeat.

Detailed documentation is in the "docs" directory.

Quick start
-----------

The quickest way to get a feel for how EPIC works is to install the
django-epic-sample package.

See https://pypi.python.org/pypi/django-epic-sample/ for details.

This sample project has a couple of sample parts, an assembly (PCB)
and some parts orders and shipments, to hopefully give you a good idea
of what working with EPIC looks like.  The look-and-feel is
minimalistic, since this is intended to be the most minimal amount of
code to get a fully working EPIC.

Setup Instructions
------------------

To use EPIC as part of your own Django project, complete the following
steps:

1. Apart from the standard Django apps, ensure "epic" and its
   pre-requisites are mentioned in INSTALLED_APPS::

    INSTALLED_APPS = (
        ...
        'django.contrib.humanize',
        'dal',
        'dal_select2',
        'crispy_forms',
        'bootstrap3_datetime',
        'epic',
	...
    )

2. Add this to the URLconf in your project's urls.py::

    re_path(r'^epic/', include(('epic.urls', 'epic'), namespace='epic'))

3. Make sure you have a base template called 'base_epic.html'.  EPIC
   expects this template to define two blocks: "extrahead" and "content".
   The former must be inside the <head> tag and is used to add style-sheets
   javascript code and other pre-requisites.  The latter must be inside a
   <body> and is used to insert the actual web content.

   base_epic.html also must include jquery, bootstrap, and bootstrap-table.
   This can be accomplished with something along these lines::

    <script type="text/javascript"
	  src="{% static "jquery/js/jquery-2.1.3.min.js" %}>"
    </script>
    <script type="text/javascript"
	  src="{% static "bootstrap/js/bootstrap.min.js" %}>"
    </script>
    <script type="text/javascript"
	  src="{% static "bootstrap-table-1.12.1/bootstrap-table.min.js" %}">
    </script>
    <link rel="stylesheet" type="text/css"
	href="{% static "bootstrap/css/bootstrap.min.css" %}"/>
    <link rel="stylesheet" type="text/css"
	href="{% static "bootstrap-table-1.12.1/bootstrap-table.min.css" %}"/>

3. Customize EPIC by setting these variables in your project's settings.py
   file:

     EPIC_BILL_TO_ADDRESS:
	The billing address of your company (may consist of multiple lines).

     EPIC_SHIPPING_TYPE:
	Your preferred shipping service (e.g., "FedEx Ground" or
	"UPS Next Day").

     EPIC_SHIPPING_ACCOUNT:
	Your preferred shipping account number or "n/a" if you don't have one.

     EPIC_MANUFACTURER:
	The name of your company.  This will be used for parts that represent
	PCBs designed by your company.

     EPIC_DATASHEET_DIR:
	The name of the directory inside media where you want datasheets
	uploaded. The default is 'epic/datasheets'.

     EPIC_DATASHEET_MAX_SIZE:
	Maximum size (in bytes) of a datasheet that may be uploaded.

     EPIC_KICAD_FOOTPRINTS_DIR:
	The name of the directory containing KiCad footprints (used for
	autocompleting footprints in the part editor).

4. Run `python manage.py migrate` to create the EPIC models.
