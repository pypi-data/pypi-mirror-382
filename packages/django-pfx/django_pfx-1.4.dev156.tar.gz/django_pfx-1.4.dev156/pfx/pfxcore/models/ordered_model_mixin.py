from django.db import models
from django.db.models import F, Max, Min


class OrderedModelMixin(models.Model):
    ordered_by = []
    ordered_default = 'last'

    seq = models.PositiveBigIntegerField("Séquence")

    class Meta:
        abstract = True

    @property
    def _ordered_by_values(self):
        return {self.serializable_value(f) for f in self.ordered_by}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__previous_ordered_by_values = self._ordered_by_values

    def clean_fields(self, exclude=None):
        if not self.seq:
            self.seq = self._order_default
        super().clean_fields(exclude=exclude)

    def save(self, *args, **kwargs):
        if not self.seq:
            self.seq = self._order_default
        super().save(*args, **kwargs)
        if self.__previous_ordered_by_values != self._ordered_by_values:
            if self.ordered_default == 'first':
                self.top()
            else:
                self.bottom()

    @property
    def _order_qs(self):
        return self.__class__._default_manager.filter(**{
            f: getattr(self, f) for f in self.ordered_by})

    @property
    def _order_max(self):
        return self._order_qs.aggregate(Max('seq'))['seq__max']

    @property
    def _order_min(self):
        return self._order_qs.aggregate(Min('seq'))['seq__min']

    @property
    def _order_default(self):
        if self.ordered_default == 'first':
            min = self._order_min
            res = min is None and 1 or min - 1
            if res == 0:
                self.first._order_shift()
                return 1
            return res
        else:
            return (self._order_max or 0) + 1

    @property
    def previous(self):
        return self._order_qs.filter(
            seq__lt=self.seq).order_by('seq', 'pk').last()

    @property
    def next(self):
        return self._order_qs.filter(
            seq__gt=self.seq).order_by('seq', 'pk').first()

    @property
    def first(self):
        return self._order_qs.order_by('seq', 'pk').first()

    @property
    def last(self):
        return self._order_qs.order_by('seq', 'pk').last()

    def _order_shift(self):
        self._order_qs.filter(seq__gte=self.seq).update(
            seq=F('seq') + 1)

    def _order_switch(self, other):
        other_seq = other.seq
        other.seq = self.seq
        other.save(update_fields=['seq'])
        self.seq = other_seq
        self.save(update_fields=['seq'])

    def up(self):
        previous = self.previous
        if not previous:
            return
        self._order_switch(previous)

    def down(self):
        next = self.next
        if not next:
            return
        self._order_switch(next)

    def top(self):
        first = self.first
        if first.pk == self.pk:
            return
        seq = first.seq - 1
        if seq == 0:
            first._order_shift()
            seq = 1
        self.seq = seq
        self.save(update_fields=['seq'])

    def bottom(self):
        last = self.last
        if last.pk == self.pk:
            return
        self.seq = last.seq + 1
        self.save(update_fields=['seq'])

    def above(self, other):
        prev = other.previous
        if not prev:
            return self.top()
        seq = other.seq - 1
        if seq == prev.seq:
            other._order_shift()
            seq += 1
        self.seq = seq
        self.save(update_fields=['seq'])

    def below(self, other):
        next = other.next
        if not next:
            return self.bottom()
        seq = other.seq + 1
        if seq == next.seq:
            next._order_shift()
        self.seq = seq
        self.save(update_fields=['seq'])
