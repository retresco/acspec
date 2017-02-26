from six import iteritems

OPTIONS_CHARACTER = ":"


def is_option(name):
    return name.startswith(OPTIONS_CHARACTER)


def remove_option_prefix(name):
    if is_option(name):
        return name[len(OPTIONS_CHARACTER):]
    else:
        return name


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


def iterspec(spec, with_options=False):
    for k, v in iteritems(spec):
        if is_option(k):
            if with_options:
                yield k, v, True
            continue

        if with_options:
            yield k, v, False
        else:
            yield k, v
