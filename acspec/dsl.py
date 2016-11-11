from six import iteritems

OPTIONS_CHARACTER = ":"


def has_option(spec, name):
    return (OPTIONS_CHARACTER + name) in spec


def get_option(spec, name, default=None):
    options_name = OPTIONS_CHARACTER + name
    if default is not None:
        return spec.get(options_name, default)
    else:
        return spec[options_name]


def add_option(spec, name, value):
    spec[OPTIONS_CHARACTER + name] = value


def iterspec(spec):
    for k, v in iteritems(spec):
        if k.startswith(OPTIONS_CHARACTER):
            continue
        yield k, v
