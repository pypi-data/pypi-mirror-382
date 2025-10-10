from django.db import transaction
from django.db.models import F

from huscy.project_design.models import (
    DataAcquisitionMethod,
    DataAcquisitionMethodType,
    Experiment,
    Session,
)
from huscy.projects.models import Membership


def create_data_acquisition_method(session, type, duration, location='', stimulus=None):
    order = session.data_acquisition_methods.count()

    return DataAcquisitionMethod.objects.create(
        duration=duration,
        location=location,
        order=order,
        session=session,
        stimulus=stimulus,
        type=type,
    )


@transaction.atomic
def create_experiment(project, description='', sessions=[], title=''):
    if len(sessions) == 0:
        raise ValueError('At least one session is required to create an experiment.')

    order = project.experiments.count()

    experiment = Experiment.objects.create(
        description=description,
        order=order,
        project=project,
        title=title or f'Experiment {order + 1}',
    )

    for session in sessions:
        create_session(experiment, **session)

    return experiment


@transaction.atomic
def create_session(experiment, contacts=[], data_acquisition_methods=[], title=''):
    if len(contacts) > (Membership.objects.filter(project=experiment.project, user__in=contacts)
                                          .count()):
        raise ValueError('The contacts must be project members.')

    if len(data_acquisition_methods) == 0:
        raise ValueError('At least one data acquisition method is required to create a session.')

    order = experiment.sessions.count()

    session = Session.objects.create(
        experiment=experiment,
        order=order,
        title=title or f'Session {order + 1}',
    )

    for data_acquisition_method in data_acquisition_methods:
        create_data_acquisition_method(session, **data_acquisition_method)

    if len(contacts) > 0:
        session.contacts.set(contacts)

    return session


def delete_data_acquisition_method(data_acquisition_method):
    if data_acquisition_method.session.data_acquisition_methods.count() == 1:
        raise ValueError('The last remaining data acquisition method cannot be deleted.')

    (DataAcquisitionMethod.objects.filter(session=data_acquisition_method.session,
                                          order__gt=data_acquisition_method.order)
                                  .update(order=F('order') - 1))

    data_acquisition_method.delete()


def delete_experiment(experiment):
    (Experiment.objects.filter(project=experiment.project, order__gt=experiment.order)
                       .update(order=F('order') - 1))

    experiment.delete()


def delete_session(session):
    if session.experiment.sessions.count() == 1:
        raise ValueError('The last remaining session cannot be deleted.')

    (Session.objects.filter(experiment=session.experiment, order__gt=session.order)
                    .update(order=F('order') - 1))

    session.delete()


def get_data_acquisition_methods(session):
    return session.data_acquisition_methods.select_related('type').all()


def get_experiments(project):
    prefetch_related = (
        'sessions__contacts',
        'sessions__data_acquisition_methods__type',
    )
    return project.experiments.prefetch_related(*prefetch_related).all()


def get_sessions(experiment):
    prefetch_related = (
        'contacts',
        'data_acquisition_methods__type',
    )
    return experiment.sessions.prefetch_related(*prefetch_related).all()


def get_data_acquisition_method_type(short_name):
    return DataAcquisitionMethodType.objects.get(short_name=short_name)


@transaction.atomic
def update_data_acquisition_method(data_acquisition_method, duration=None, location=None,
                                   order=None, stimulus=None):
    update_fields = []

    if duration not in (None, data_acquisition_method.duration):
        data_acquisition_method.duration = duration
        update_fields.append('duration')

    if location not in (None, data_acquisition_method.location):
        data_acquisition_method.location = location
        update_fields.append('location')

    if order not in (None, data_acquisition_method.order):
        data_acquisition_methods_queryset = data_acquisition_method.session.data_acquisition_methods
        data_acquisition_method_count = data_acquisition_methods_queryset.count()

        if order >= data_acquisition_method_count:
            raise ValueError('The value for order is too large. '
                             f'It can be a maximum of {data_acquisition_method_count - 1}.')

        if order < data_acquisition_method.order:
            (data_acquisition_methods_queryset.filter(order__gte=order,
                                                      order__lt=data_acquisition_method.order)
                                              .update(order=F('order') + 1))
        else:
            (data_acquisition_methods_queryset.filter(order__lte=order,
                                                      order__gt=data_acquisition_method.order)
                                              .update(order=F('order') - 1))
        data_acquisition_method.order = order
        update_fields.append('order')

    if stimulus not in (None, data_acquisition_method.stimulus):
        data_acquisition_method.stimulus = stimulus
        update_fields.append('stimulus')

    if update_fields:
        data_acquisition_method.save(update_fields=update_fields)

    return data_acquisition_method


@transaction.atomic
def update_experiment(experiment, description=None, order=None, title=None):
    update_fields = []

    if description not in (None, experiment.description):
        experiment.description = description
        update_fields.append('description')

    if order not in (None, experiment.order):
        experiments_queryset = experiment.project.experiments
        experiment_count = experiments_queryset.count()

        if order >= experiment_count:
            raise ValueError('The value for order is too large. '
                             f'It can be a maximum of {experiment_count - 1}.')

        if order < experiment.order:
            (experiments_queryset.filter(order__gte=order, order__lt=experiment.order)
                                 .update(order=F('order') + 1))
        else:
            (experiments_queryset.filter(order__lte=order, order__gt=experiment.order)
                                 .update(order=F('order') - 1))
        experiment.order = order
        update_fields.append('order')

    if title not in (None, experiment.title):
        experiment.title = title
        update_fields.append('title')

    if update_fields:
        experiment.save(update_fields=update_fields)

    return experiment


@transaction.atomic
def update_session(session, contacts=None, order=None, title=None):
    update_fields = []

    if contacts not in (None, session.contacts):
        if len(contacts) > (Membership.objects.filter(project=session.experiment.project,
                                                      user__in=contacts).count()):
            raise ValueError('The contacts must be project members.')

        session.contacts.set(contacts)

    if order not in (None, session.order):
        sessions_queryset = session.experiment.sessions
        session_count = sessions_queryset.count()

        if order >= session_count:
            raise ValueError('The value for order is too large. '
                             f'It can be a maximum of {session_count - 1}.')

        if order < session.order:
            (sessions_queryset.filter(order__gte=order, order__lt=session.order)
                              .update(order=F('order') + 1))
        else:
            (sessions_queryset.filter(order__lte=order, order__gt=session.order)
                              .update(order=F('order') - 1))
        session.order = order
        update_fields.append('order')

    if title not in (None, session.title):
        session.title = title
        update_fields.append('title')

    if update_fields:
        session.save(update_fields=update_fields)

    return session
