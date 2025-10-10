from datetime import timedelta
from functools import reduce

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from huscy.projects.models import Project


class Experiment(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='experiments',
                                verbose_name=_('Project'))

    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True, default='')

    order = models.PositiveSmallIntegerField(_('Order'))

    class Meta:
        ordering = 'order',
        verbose_name = _('Experiment')
        verbose_name_plural = _('Experiments')


class Session(models.Model):
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, related_name='sessions',
                                   verbose_name=_('Experiment'))

    title = models.CharField(_('Title'), max_length=255)
    description = models.TextField(_('Description'), blank=True, default='')
    contacts = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='+')

    order = models.PositiveSmallIntegerField(_('Order'))

    class Meta:
        ordering = 'order',
        verbose_name = _('Session')
        verbose_name_plural = _('Sessions')

    @property
    def duration(self):
        return reduce(
            lambda total, data_acquisition_method: total + data_acquisition_method.duration,
            self.data_acquisition_methods.all(),
            timedelta(),
        )


class DataAcquisitionMethodType(models.Model):
    short_name = models.CharField(_('Short name'), max_length=32, primary_key=True, editable=False)
    name = models.CharField(_('Name'), max_length=255)

    class Meta:
        ordering = 'short_name',
        verbose_name = _('Data acquisition method type')
        verbose_name_plural = _('Data acquisition method types')


class DataAcquisitionMethod(models.Model):
    class Stimulus(models.TextChoices):
        auditive = ('auditive', _('Auditive'))
        gustatory = ('gustatory', _('Gustatory'))
        olfactory = ('olfactory', _('Olfactory'))
        somatosensory = ('somatosensory', _('Somatosensory'))
        visual = ('visual', _('Visual'))

    session = models.ForeignKey(Session, on_delete=models.CASCADE,
                                related_name='data_acquisition_methods', verbose_name=_('Session'))

    type = models.ForeignKey(DataAcquisitionMethodType, on_delete=models.PROTECT,
                             verbose_name=_('Type'))
    stimulus = models.CharField(_('Stimulus'), max_length=16, blank=True, null=True,
                                choices=Stimulus.choices)
    duration = models.DurationField(_('Duration'))
    location = models.CharField(_('Location'), max_length=255, blank=True, null=True)

    order = models.PositiveSmallIntegerField(_('Order'))

    class Meta:
        ordering = 'order',
        verbose_name = _('Data acquisition method')
        verbose_name_plural = _('Data acquisition methods')
