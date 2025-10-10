import logging
from django.db.models import Q, Min, Max, Count

from datetime import timezone, datetime

from bugsink.moreiterutils import pairwise, map_N_until
from bugsink.utils import assert_, nc_rnd
from performance.context_managers import time_and_query_count

from .storage_registry import get_storage

bugsink_logger = logging.getLogger("bugsink")
performance_logger = logging.getLogger("bugsink.performance.retention")


class EvictionCounts:

    def __init__(self, total, per_issue):
        self.total = total
        self.per_issue = per_issue

    def __add__(self, other):
        return EvictionCounts(
            self.total + other.total,
            {k: self.per_issue.get(k, 0) + other.per_issue.get(k, 0)
             for k in set(self.per_issue) | set(other.per_issue)})

    def __repr__(self):
        return f"EvictionCounts(total={self.total})"


def get_epoch(datetime_obj):
    # The basic rythm for eviction is 'hourly'; we define an 'epoch' for eviction as the number of hours since 1970.
    # Why pick hours rather than something else? It's certainly granular enough for our purposes, and it makes it
    # possible for actual humans to understand what's going on (e.g. when debugging). Note that w.r.t. the outcome of
    # our algorithm, the choice of epoch size translates into a constant addition to the age-based irrelevance. (i.e.
    # when switching to days the age-based irrelvance would come out approximately 4 lower. But this would be corrected
    # in the search for a cut-off value for the total irrelevance, so it doesn't matter in the end.)

    # assuming we use model fields this 'just works' because Django's stores its stuff in timezone-aware UTC in the DB.
    assert_(datetime_obj.tzinfo == timezone.utc)

    return int(datetime_obj.timestamp() / 3600)


def datetime_for_epoch(epoch):
    return datetime.fromtimestamp(epoch * 3600, timezone.utc)


def get_epoch_bounds(lower, upper=None):
    if lower is None and upper is None:
        return Q()

    if lower is None:
        return Q(digested_at__lt=datetime_for_epoch(upper))

    if upper is None:
        return Q(digested_at__gte=datetime_for_epoch(lower))

    return Q(digested_at__gte=datetime_for_epoch(lower), digested_at__lt=datetime_for_epoch(upper))


def nonzero_leading_bits(n):
    """
    Return the non-roundness of a number when represented in binary, i.e. the number of leading bits until the last 1.
    examples:

    100000 -> 1
    101000 -> 3
    110001 -> 6
    """
    s = format(n, 'b')
    return len(s.rstrip('0'))


def get_random_irrelevance(stored_event_count):
    """
    gets a fixed-at-creation irrelevance-score for an Event; the basic idea is: the more events you have for a certain
    issue, the less relevant any new event will be _on average_; but when you have many events you will on average still
    have more relevant events than if you have few events.

    irrelevance is basically determined by `nonzero_leading_bits`; we add some randomization to avoid repeated outcomes
    if `cnt` "hovers" around a certain value (which is likely to happen when there's repeated eviction/fill-up). ×2 is
    simply to correct for random() (which returns .5 on average).
    """
    # assert as a tripwire to check our assumptions; note that the actual calculation actually "succeeds" for < 1, but
    # it becomes non-sensical, so I'd rather have it fail. The present event is part of the count, i.e. always >= 1
    assert_(stored_event_count >= 1)
    return nonzero_leading_bits(round(nc_rnd.random() * stored_event_count * 2))


def should_evict(project, timestamp, stored_event_count):
    # if/when we implement 'just drop' this might go somewhere (maybe not here)
    # if (project.retention_last_eviction is not None and
    #         get_epoch(project.retention_last_eviction) != get_epoch(timestamp)):
    #     return True

    if stored_event_count > project.retention_max_event_count:  # > because: do something when _over_ the max
        return True

    return False


def get_age_for_irrelevance(age_based_irrelevance):
    # age based irrelevance is defined as `log(age + 1, 4)`
    #
    # (This is what we chose because we want 0-aged to have an age-based irrelevance of 0); i.e. that's where the +1
    # comes from.
    #
    # The base of 4 was chosen after some experimentation/consideration; it's certainly not a scientific choice. Note
    # that the age based irrelevance is the easiest to tune out of the 2, because it's a simple logarithm (i.e. we don't
    # need to count bits/leading zeroes) and because it is calculated on demand rather than stored in the DB.
    #
    # Why we picked 4: if you consider quota in the range of 10_000 - 1_000_000, the nonzero_leading_bits will lead to
    # event-irrelevances of max 15 - 21 respectively. However, after evicting for max events I've observed this to be in
    # the 8 - 12 range for the 10_000 case. Choosing 4 as the base for age-based means that the irrelevance for an event
    # that is 1 year old is about 6.5 (log(24 * 365, 4)), which makes it so that even 1 year old events are not
    # necessarily evicted if they were "the most relevant ones".
    #
    # Another way of thinking about this: for the value of 4, the change in irrelevance for an event going from one week
    # old to one month old, or an event going from a bit over a day to a week old is comparable to an event being one of
    # twice as many events. This feels more correct than e.g. using base 2, where the change in irrelevance takes a
    # "step" at each doubling.
    #
    # at the integer values for irrelevance this works out like so:
    # age = 0 => irrelevance = 0
    # age = 1 => irrelevance = 0.5
    # age = 2 => irrelevance = 0.792
    # age = 3 => irrelevance = 1
    # age = 15 => irrelevance = 2
    #
    # to work back from a given integer "budget" of irrelevance (after the (integer) item-based irrelevance has been
    # subtracted from the total max), we can simply take `4^budget - 1` to get the 'age of eviction', the number of
    # epochs we must go back. The following code helps me understand this:
    #
    # >>> for budget in range(20):
    # ...     age = pow(4, budget) - 1
    # ...     print("budget: %s, age: %s" % (budget, age))

    return pow(4, age_based_irrelevance) - 1


def get_epoch_bounds_with_irrelevance(project, current_timestamp, qs_kwargs={"never_evict": False}):
    """Returns the epoch bounds for the project (newest first), with the age-based irrelevance for each epoch."""
    # newest-first is something we rely on in the below; e.g. in our 'single age-based UB-check'. Why this was chosen
    # originally, I can't tell for sure, but it seems somewhat natural in the light of the newest epochs being the ones
    # with the most variation in irrelevance (high-irrelevance events which have not yet been evicted are most likely to
    # live in fresh epochs)

    from .models import Event

    oldest = Event.objects.filter(project=project, **qs_kwargs).aggregate(val=Min('digested_at'))['val']
    first_epoch = get_epoch(oldest) if oldest is not None else get_epoch(current_timestamp)

    current_epoch = get_epoch(current_timestamp)

    difference = current_epoch - first_epoch

    ages = list(map_N_until(get_age_for_irrelevance, difference))  # e.g. [0, 3, 15]
    epochs = [current_epoch - age for age in ages]  # e.g. [100, 97, 85]
    swapped_bounds = pairwise([None] + epochs + [None])  # e.g. [(None, 100), (100, 97), (97, 85), (85, None)]

    # because ages and epochs are constructed new-to-old, we get (newer, older) pairs but we need the reverse
    bounds = [(older, newer) for (newer, older) in swapped_bounds]  # e.g [(100, None), (97, 100), ...]

    # age based irrelevance is simply "counting back" now; e.g. [((100, None), 0), ((97, 100), 1), ...]
    return [((lb, ub), age_based_irrelevance) for (age_based_irrelevance, (lb, ub)) in enumerate(bounds)]


def get_irrelevance_pairs(project, epoch_bounds_with_irrelevance, qs_kwargs={"never_evict": False}):
    """tuples of `age_based_irrelevance` and, per associated period, the max observed (evictable) event irrelevance"""
    from .models import Event

    for (lower_bound, upper_bound), age_based_irrelevance in epoch_bounds_with_irrelevance:
        d = Event.objects.filter(
            get_epoch_bounds(lower_bound, upper_bound),
            project=project,
            **qs_kwargs,
        ).aggregate(Max('irrelevance_for_retention'))
        max_event_irrelevance = d["irrelevance_for_retention__max"] or 0

        yield (age_based_irrelevance, max_event_irrelevance)


def filter_for_work(epoch_bounds_with_irrelevance, pairs, max_total_irrelevance):
    # Here, we filter out epoch bounds for which there is obviously no work to be done, based on the pairs that we have
    # selected at the beginning of the algo. We compare the selected irrelevances with the total, and if they do not
    # exceed it no work will need to be done for that set of epochs.

    # Since it uses only the (already available) information that was gathered at the beginning of the algo, it is not a
    # full filter for avoiding useless deletions, but at least we use the available info (from queries) to the fullest.
    for pair, ebwi in zip(pairs, epoch_bounds_with_irrelevance):
        if sum(pair) > max_total_irrelevance:  # > because only if it is strictly greater will anything be evicted.
            yield ebwi


def eviction_target(max_event_count, stored_event_count):
    # Calculate a target number of events to evict, which is a balancing act between 2 things:
    #
    # 1. large enough to avoid having to evict again immediately after we've just evicted (eviction is relatively
    #    expensive, so we want to avoid doing it too often)
    # 2. not too large to avoid [a] throwing too much data away unnecessarily and [b] avoid blocking too
    #    long on a single eviction (both on a single query, to avoid timeouts, but also on the eviction as a whole,
    #    because it would block other threads/processes and trigger timeouts there).
    #
    # Inputs into the calculation are (see test_eviction_target to understand the min/maxing):
    #
    # * the constant value of 500
    # * the over-targetness
    # * and a percentage of 5% of the target
    #
    # On the slow VPS we've observed deletions taking in the order of 1-4ms per event, so 500 would put us at 2s, which
    # is still less than 50% of the timeout value.
    #
    # Although eviction triggers "a lot" of queries, "a lot" is in the order of 25, so after amortization this is far
    # less than 1 query extra per event (as a result of the actual eviction, checking for the need to evict is a
    # different story). 5% seems small enough to stem the "why was so much deleted" questions.
    return min(
               max(
                   int(max_event_count * 0.05),
                   stored_event_count - max_event_count,
               ),
               500,
           )


def evict_for_max_events(project, timestamp, stored_event_count, include_never_evict=False):
    # This function evicts, with a number-based target of events in mind. It does so by repeatedly calling
    # evict_for_irrelevance (i.e. irrelevance-based target), lowering the target irrelevance until the target number of
    # events has been evicted.
    #
    # Before any actual work is done, we map out the terrain:
    #
    # * epoch_bounds_with_irrelevance: pairs of epoch bounds with their age_based_irrelevance
    # * pairs: adds to that the observed max irrelevance for each epoch
    #
    # epoch bounds are passed to the irrelevance-based eviction; pairs is used to determine the starting max irrelevance
    # and in an optimization (skipping epochs where it's obvious no work is needed).

    qs_kwargs = {} if include_never_evict else {"never_evict": False}

    with time_and_query_count() as phase0:
        epoch_bounds_with_irrelevance = get_epoch_bounds_with_irrelevance(project, timestamp, qs_kwargs)

        # we start off with the currently observed max total irrelevance
        pairs = list(get_irrelevance_pairs(project, epoch_bounds_with_irrelevance, qs_kwargs))
        max_total_irrelevance = orig_max_total_irrelevance = max(sum(pair) for pair in pairs)

    with time_and_query_count() as phase1:
        evicted = EvictionCounts(0, {})
        target = eviction_target(project.retention_max_event_count, stored_event_count)
        while evicted.total < target:
            # -1 at the beginning of the loop; this means the actually observed max value is precisely the first thing
            # that will be evicted (since `evict_for_irrelevance` will evict anything above (but not including) the
            # given value)
            max_total_irrelevance -= 1

            epoch_bounds_with_irrelevance_with_possible_work = list(
                filter_for_work(epoch_bounds_with_irrelevance, pairs, max_total_irrelevance))

            evicted += evict_for_irrelevance(
                project,
                max_total_irrelevance,
                epoch_bounds_with_irrelevance_with_possible_work,
                include_never_evict,
                target - evicted.total,
            )

            if evicted.total < target and max_total_irrelevance <= -1:
                # if max_total_irrelevance <= -1 the analogous check for max_total_irrelevance in evict_for_irrelevance
                # will certainly have fired (item_irr <= total_irr) which means "no more can be achieved".

                if not include_never_evict:
                    # everything that remains is 'never_evict'. 'never say never' and evict those as a last measure
                    return evicted + evict_for_max_events(project, timestamp, stored_event_count - evicted.total, True)

                # "should not happen", let's log it and break out of the loop
                # the reason I can think of this happening is when stored_event_count is wrong (too high).
                bugsink_logger.error(
                    "Failed to evict enough events; %d < %d (max %d, stored %d)", evicted.total, target,
                    project.retention_max_event_count, stored_event_count)
                break

    # phase 0: SELECT statements to identify per-epoch observed irrelevances
    # phase 1: SELECT with LIMIT for deletions and DELETE themselves (evictions)
    performance_logger.info(
        "%6.2fms EVICT; down to %d, max irr. from %d to %d in %dms+%dms and %d+%d queries",
        phase0.took + phase1.took,
        stored_event_count - evicted.total - 1,  # down to: -1, because the +1 happens post-eviction
        orig_max_total_irrelevance, max_total_irrelevance, phase0.took, phase1.took, phase0.count, phase1.count)

    return evicted


def evict_for_irrelevance(
        project, max_total_irrelevance, epoch_bounds_with_irrelevance, include_never_evict=False, max_event_count=0):
    # max_total_irrelevance: the total may not exceed this (but it may equal it)
    evicted = EvictionCounts(0, {})

    for (_, epoch_ub_exclusive), irrelevance_for_age in epoch_bounds_with_irrelevance:
        max_item_irrelevance = max_total_irrelevance - irrelevance_for_age

        current_max = max_event_count - evicted.total
        evicted += evict_for_epoch_and_irrelevance(
            project, epoch_ub_exclusive, max_item_irrelevance, current_max, include_never_evict)

        if max_item_irrelevance <= -1:
            # break: we've just done the most aggressive eviction possible: we're done for all epochs. (because the test
            # on max_item_irrelevance in evict_for_epoch is done exclusively (i.e. `gt`), and the lowest existing value
            # is 0, and because we don't do a LB check when deleting, a single call for -1 deletes all that can be
            # deleted (respecting include_never_evict, max_event_count)).
            break

        if evicted.total >= max_event_count:
            # We've reached the target; we don't need to evict from further epochs. In this case not all events with
            # greater than max_total_irr will have been evicted; if this is the case older items are more likely to be
            # spared (because epochs are visited in reverse order).
            break

    return evicted


def evict_for_epoch_and_irrelevance(project, max_epoch, max_irrelevance, max_event_count, include_never_evict):
    from issues.models import TurningPoint
    from .models import Event
    from tags.models import EventTag
    # evicting "at", based on the total irrelevance split out into 2 parts: max item irrelevance, and an epoch as
    # implied by the age-based irrelevance.

    # (both max_epoch and max_irrelevance are _exclusive_)

    # Note: we simply use a single age-based UB-check to delete; an alternative is to also use associated time-based-LB
    # for a given `irrelevance_for_age`; in practice it doesn't matter, because in the same `evict_for_irrelevance` call
    # the older epochs will be visited later with an even lower value for `max_irrelevance` which would delete the same.
    # But we might use this fact at some point in the future (e.g. for performance considerations, or to evict in
    # smaller steps).
    #
    # As a picture (time on X, irrelevance on the Y axis, lower rows have higher irrelevance as in the simulation):
    #
    #  . . . . . . .
    #          B B .
    #  a a a a x x A
    #
    # As implemented, we evict the points marked `A`, `x` and `a` all in a single go. The alternative would be: `A` in
    # this call, and only when `B` is cleaned will the points `x` be cleaned. (as-is, they are part of the selection,
    # but will already have been deleted)

    qs_kwargs = {} if include_never_evict else {"never_evict": False}
    qs = Event.objects.filter(project=project, irrelevance_for_retention__gt=max_irrelevance, **qs_kwargs)

    if max_epoch is not None:
        qs = qs.filter(digested_at__lt=datetime_for_epoch(max_epoch))

    if include_never_evict:
        # we need to manually ensure that no FKs to the deleted items exist:
        TurningPoint.objects.filter(triggering_event__in=qs).update(triggering_event=None)

    # We generate the list of events-to-delete (including the LIMIT) before proceeding; this allows us:
    #
    # A. to have a portable delete_with_limit (e.g. Django does not support that, nor does Postgres).
    # B. to apply deletions of Events and their consequences (cleanup_events_on_storage(), EventTag) on the same list.
    # C. count per-issue
    #
    # Implementation notes:
    # 1. We force evaluation here with a `list()`; this means subsequent usages do _not_ try to "just use an inner
    #    query". Although inner queries are attractive in the abstract, the literature suggests that performance may be
    #    unpredictable (e.g. on MySQL). By using a list, we lift the (max 500) ids-to-match to the actual query, which
    #    is quite ugly, but predictable and (at least on sqlite where I tested this) lightning-fast.
    # 2. order_by: "pick something" to ensure the 2 usages of the "subquery" point to the same thing. (somewhat
    #    superceded by [1] above; but I like to be defensive and predictable). tie-breaking on digest_order seems
    #    consistent with the semantics of eviction.
    pks_to_delete = list(qs.order_by("digest_order")[:max_event_count].values_list("pk", flat=True))

    if len(pks_to_delete) > 0:
        cleanup_events_on_storage(
            Event.objects.filter(pk__in=pks_to_delete).exclude(storage_backend=None)
            .values_list("id", "storage_backend")
        )
        deletions_per_issue = {
            d['issue_id']: d['count'] for d in
            Event.objects.filter(pk__in=pks_to_delete).values("issue_id").annotate(count=Count("issue_id"))}

        # Rather than rely on Django's implementation of CASCADE, we "just do this ourselves"; Reason is: Django does an
        # extra, expensive (all-column), query on Event[...](id__in=pks_to_delete) to extract the Event ids (which we
        # already have). If Django ever gets DB-CASCADE, this may change: https://code.djangoproject.com/ticket/21961
        EventTag.objects.filter(event_id__in=pks_to_delete).delete()
        nr_of_deletions = Event.objects.filter(pk__in=pks_to_delete).delete()[1].get("events.Event", 0)
    else:
        nr_of_deletions = 0
        deletions_per_issue = {}

    return EvictionCounts(nr_of_deletions, deletions_per_issue)


def cleanup_events_on_storage(todos):
    for event_id, storage_backend in todos:
        try:
            get_storage(storage_backend).delete(event_id)
        except Exception as e:
            # in a try/except such that we can continue with the rest of the batch
            bugsink_logger.error("Error during cleanup of %s on %s: %s", event_id, storage_backend, e)
