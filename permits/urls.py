from django.urls import path
from .views import (
    HomeView,
    AdminPanelView,
    CreatePermitView,
    PermitFillView,
    PermitDocxView,
)

urlpatterns = [
    path("", HomeView.as_view(), name="home"),
    path("admin-panel/", AdminPanelView.as_view(), name="admin_panel"),
    path("admin-panel/create/", CreatePermitView.as_view(), name="create_permit"),
    path("permit/<uuid:token>/", PermitFillView.as_view(), name="permit_fill"),
    path("permit/<uuid:token>/docx/<str:doc_type>/", PermitDocxView.as_view(), name="permit_docx"),
]
