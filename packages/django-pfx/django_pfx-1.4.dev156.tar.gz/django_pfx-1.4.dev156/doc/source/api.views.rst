API Reference
=============

``pfx.pfxcore.middleware``
**************************

.. autoclass:: pfx.pfxcore.middleware.AuthenticationMiddleware
    :show-inheritance:

.. autoclass:: pfx.pfxcore.middleware.LocaleMiddleware
    :show-inheritance:

.. autofunction:: pfx.pfxcore.middleware.locale.get_language_from_request
.. autofunction:: pfx.pfxcore.middleware.locale.get_timezone_from_request


``pfx.pfxcore.models``
**********************

.. autoclass:: pfx.pfxcore.models.ErrorMessageMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.models.JSONReprMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.models.PFXModelMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.models.AbstractPFXBaseUser
    :members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.models.OtpUserMixin
    :members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.models.PFXUser
    :members:
    :show-inheritance:

``pfx.pfxcore.views``
*********************

Query parameters & groups
-------------------------

.. autoclass:: pfx.pfxcore.views.parameters.ListCount
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.ListItems
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.ListMode
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.ListOrder
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.ListSearch
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.MediaRedirect
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.MetaFields
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.groups.MetaFilters
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.groups.MetaOrders
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.groups.SubsetLimit
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.groups.SubsetOffset
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.groups.SubsetPageSize
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.groups.SubsetPageSubset
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.groups.SubsetPage
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.groups.MetaList
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.parameters.groups.List
    :members:
    :undoc-members:
    :show-inheritance:

Base services
-------------

.. autoclass:: pfx.pfxcore.views.AuthenticationView
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.SignupView
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.ForgottenPasswordView
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.OtpEmailView
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.LocaleRestView
    :members:
    :undoc-members:
    :show-inheritance:

View Mixins
-----------

.. autoclass:: pfx.pfxcore.views.ModelMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.ModelResponseMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.BodyMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.ModelBodyMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.DetailRestViewMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.SlugDetailRestViewMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.ListRestViewMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.CreateRestViewMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.UpdateRestViewMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.DeleteRestViewMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.MediaRestViewMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.SecuredRestViewMixin
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.BaseRestView
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.RestView
    :members:
    :undoc-members:
    :show-inheritance:

.. autoclass:: pfx.pfxcore.views.SendMessageTokenMixin
    :members:
    :undoc-members:
    :show-inheritance:
