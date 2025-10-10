from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions

from huscy.project_design import models, permissions, serializer, services
from huscy.projects.models import Project


class ExperimentViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin,
                        mixins.UpdateModelMixin, viewsets.GenericViewSet):
    http_method_names = 'delete', 'get', 'head', 'options', 'post', 'put', 'trace'
    permission_classes = (
        IsAuthenticated,
        permissions.ChangeProjectPermission,
        permissions.ViewProjectPermission,
    )

    def initial(self, request, *args, **kwargs):
        self.project = get_object_or_404(Project, pk=self.kwargs['project_pk'])
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return services.get_experiments(self.project)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializer.CreateExperimentSerializer
        else:
            return serializer.ExperimentSerializer

    def perform_create(self, serializer):
        serializer.save(project=self.project)

    def perform_destroy(self, experiment):
        services.delete_experiment(experiment)


class SessionViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin, mixins.UpdateModelMixin,
                     viewsets.GenericViewSet):
    http_method_names = 'delete', 'get', 'head', 'options', 'post', 'put', 'trace'
    permission_classes = (IsAuthenticated, permissions.ChangeProjectPermission)

    def initial(self, request, *args, **kwargs):
        self.experiment = get_object_or_404(
            models.Experiment.objects.select_related('project'),
            pk=self.kwargs['experiment_pk'],
            project=self.kwargs['project_pk']
        )
        self.project = self.experiment.project
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return services.get_sessions(self.experiment)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializer.CreateSessionSerializer
        else:
            return serializer.SessionSerializer

    def perform_create(self, serializer):
        serializer.save(experiment=self.experiment)

    def perform_destroy(self, session):
        services.delete_session(session)


class DataAcquisitionMethodViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                                   mixins.UpdateModelMixin, viewsets.GenericViewSet):
    http_method_names = 'delete', 'get', 'head', 'options', 'post', 'put', 'trace'
    permission_classes = (IsAuthenticated, permissions.ChangeProjectPermission)

    def initial(self, request, *args, **kwargs):
        self.session = get_object_or_404(
            models.Session.objects.select_related('experiment__project'),
            experiment=self.kwargs['experiment_pk'],
            pk=self.kwargs['session_pk'],
            experiment__project=self.kwargs['project_pk']
        )
        self.project = self.session.experiment.project
        super().initial(request, *args, **kwargs)

    def get_queryset(self):
        return services.get_data_acquisition_methods(self.session)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializer.CreateDataAcquisitionMethodSerializer
        else:
            return serializer.DataAcquisitionMethodSerializer

    def perform_create(self, serializer):
        serializer.save(session=self.session)

    def perform_destroy(self, data_acquisition_method):
        services.delete_data_acquisition_method(data_acquisition_method)


class DataAcquisitionMethodTypeViewSet(viewsets.ModelViewSet):
    permission_classes = (DjangoModelPermissions, )
    queryset = models.DataAcquisitionMethodType.objects.all()
    serializer_class = serializer.DataAcquisitionMethodTypeSerializer
