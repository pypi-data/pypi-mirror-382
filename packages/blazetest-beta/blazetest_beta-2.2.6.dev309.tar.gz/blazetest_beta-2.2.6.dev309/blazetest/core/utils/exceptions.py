class ConfigurationValidationException(Exception):
    pass


class AWSRegionNotFound(Exception):
    pass


class ConfigurationFileNotFound(Exception):
    pass


class ConfigurationMissingValue(Exception):
    pass


class ConfigurationFieldWrongType(Exception):
    pass


class S3BucketNotFound(Exception):
    pass


class LambdaNotCreated(Exception):
    pass


class LicenseNotSpecified(Exception):
    pass


class LicenseNotValid(Exception):
    pass


class LicenseExpired(Exception):
    pass


class CommandExecutionException(Exception):
    pass


class UnsupportedInfraSetupTool(Exception):
    pass


class ReportNotAvailable(Exception):
    pass


class ReportNotUploaded(Exception):
    pass


class ReportNotMerged(Exception):
    pass


class NoTestsToRun(Exception):
    pass


class SessionNotFound(Exception):
    pass


class DepotTokenNotProvided(Exception):
    pass


class ImagePushError(Exception):
    pass


class AWSLambdaFunctionNotCreated(Exception):
    pass
