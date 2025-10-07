# errors
class OmniplateError(ValueError):
    pass


class FileNotFound(OmniplateError):
    pass


class IgnoreWells(OmniplateError):
    pass


class PlotError(OmniplateError):
    pass


class UnknownDataFrame(OmniplateError):
    pass


class GetSubset(OmniplateError):
    pass


class GetFitnessPenalty(OmniplateError):
    pass


class CorrectAuto(OmniplateError):
    pass


class UnknownPlateReader(OmniplateError):
    pass
