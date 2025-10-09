Primary keys
============

Defining primary keys in ``dy.Schema``
--------------------------------------

When working with tabular data, it is often useful to define a `primary key <https://en.wikipedia.org/wiki/Primary_key>`_. A primary key is a set of one or multiple column, the combined values of which form a unique identifier for every record in a table.

Dataframely supports marking columns as part of the primary key when defining a ``dy.Schema`` by setting ``primary_key=True`` on the respective column(s).

.. note::

  Primary key columns must not be nullable.

Single primary keys
^^^^^^^^^^^^^^^^^^^

For example, when managing data about users, we might use an ``id`` column to uniquely identify users:

::

    class UserSchema(dy.Schema):
      name = dy.String(primary_key=True)
      name = dy.String()

When we later validate data with this schema, ``dataframely`` checks that the values of the primary key are unique, i.e. there are no two users with the same value of ``id``. Having multiple users with the same ``name`` but different ``id`` but be allowed in this case.

Composite primary keys
^^^^^^^^^^^^^^^^^^^^^^

In another scenario, we might be tracking line items on invoices. We have many invoices, and each invoice may contain any number of line items. To uniquely identify a line item, we need to specify the invoice, as well as the line items position within the invoice. To encode this, we set ``primary_key=True`` on both the ``invoice_id`` and ``item_id`` columns:

::

    class LineItemSchema(dy.Schema):
      invoice_id = dy.Int64(primary_key=True)
      item_id = dy.Int64(primary_key=True)
      price = dy.Decimal()

Validation will now ensure that all pairs of (``invoice_id``, ``item_id``) are unique.


Primary keys in ``dy.Collection``
---------------------------------

The central idea behind ``dy.Collection`` is to unify multiple tables relating to the same set of underlying entities.
This is useful because it allows us to write ``dy.filter``s that use information from multiple tables to identify whether the underlying entity is valid or not. If any ``dy.filter``s are defined, ``dataframely`` requires the tables in a ``dy.Collection`` to have an overlapping primary key (i.e., there must be at least one column that is a primary key in all tables).
