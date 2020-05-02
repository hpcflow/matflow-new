class IncompatibleWorkflow(Exception):
    pass


class IncompatibleTaskNesting(IncompatibleWorkflow):
    pass


class MissingMergePriority(IncompatibleTaskNesting):
    pass


class IncompatibleSequence(Exception):
    'For task sequence definitions that are not logically consistent.'


class SequenceError(Exception):
    'For malformed sequence definitions.'


class TaskError(Exception):
    'For malformed task definitions.'


class TaskSchemaError(Exception):
    'For nonsensical task schema definitions.'


class TaskParameterError(Exception):
    'For incorrectly parametrised tasks.'
