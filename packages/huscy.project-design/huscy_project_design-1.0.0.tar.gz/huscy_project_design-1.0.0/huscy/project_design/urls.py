from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter

from huscy.project_design import views
from huscy.projects.urls import project_router


router = DefaultRouter()
router.register(
    'data-acquisition-method-types',
    views.DataAcquisitionMethodTypeViewSet,
    basename='dataacquisitionmethodtype',
)

project_router.register(
    'experiments',
    views.ExperimentViewSet,
    basename='experiment',
)

experiment_router = NestedDefaultRouter(project_router, 'experiments', lookup='experiment')
experiment_router.register(
    'sessions',
    views.SessionViewSet,
    basename='session',
)

session_router = NestedDefaultRouter(experiment_router, 'sessions', lookup='session')
session_router.register(
    'dataacquisitionmethods',
    views.DataAcquisitionMethodViewSet,
    basename='dataacquisitionmethod',
)


urlpatterns = [
    path('api/', include(router.urls)),
    path('api/', include(project_router.urls)),
    path('api/', include(experiment_router.urls)),
    path('api/', include(session_router.urls)),
]
