import re
import keyword
from six import iteritems

from acspec.dsl import has_option, get_option


def topological_iteritems(specs, pre_emitted=[]):
    pending = [(name, _get_bases(spec)) for name, spec in iteritems(specs)]
    emitted = pre_emitted[:]
    available = set(list(specs.keys()) + emitted)
    while pending:
        next_pending = []
        next_emitted = []
        for entry in pending:
            name, bases = entry
            bases.difference_update(emitted)
            if bases and bases.issubset(available):
                next_pending.append(entry)
            else:
                yield name, specs[name]
                emitted.append(name)
                next_emitted.append(name)
        if not next_emitted:
            raise ValueError("Cyclic inheritance: {}".format(
                _print_cycle(next_pending)
            ))
        pending = next_pending
        emitted = next_emitted


def _get_bases(spec):
    if has_option(spec, "bases"):
        return set(get_option(spec, "bases"))
    else:
        return set()


def _print_cycle(pending):
    pending = sorted(pending, key=lambda x: x[0])
    names = [name for name, _ in pending]

    def relevant_base(bases):
        bases = [b for b in bases if b in names]
        assert bases, "{} are not cyclic".format(names)
        return bases[0]
    pending_map = dict({
        k: relevant_base(bases) for k, bases in pending
    })
    chain = [names[0]]
    current = pending_map[chain[0]]
    while True:
        chain.append(current)
        current = pending_map[current]
        if current in chain[0]:
            return " < ".join(chain + [current])


def underscore(name):
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def camelize(s):
    # camelize with lower first character
    return re.sub(r"(?:^|_)(.)", lambda m: m.group(1).upper(), s)


def is_valid_identifier(name):
    if not name:
        return False
    return re.match(
        "[_A-Za-z][_a-zA-Z0-9]*$", name
    ) is not None and not keyword.iskeyword(name)


def sanitize_identifier(original_name):
    # remove leading and trailing invalid characters
    name = re.sub('(^[^0-9a-zA-Z_]+|[^0-9a-zA-Z_]+$)', '', original_name)

    # Replace invalid characters by underscore and squeeze
    name = re.sub('[^0-9a-zA-Z_]', '_', name)
    name = re.sub('_+', '_', name)

    if not name or name.count("_") == len(name):
        raise ValueError(
            "Cannot transform '{}' to valid identifier".format(original_name)
        )

    # append _ for digits
    if name[0].isdigit():
        name = "_{}".format(name)

    return name
