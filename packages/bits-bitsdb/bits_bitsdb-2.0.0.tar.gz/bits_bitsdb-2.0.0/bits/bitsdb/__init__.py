"""BITSdb class file."""

from bits.bitsdb.cloudfunctions import CloudFunctions
from bits.bitsdb.update import Update


class BITSdb:
    """BITSdb class."""

    def __init__(self, auth=None, verbose=False):
        """Initialize a class instance."""
        self.auth = auth
        self.verbose = verbose

        # define a list of supported applications
        self.apps = []

    def cloudfunctions(self, project, region):
        """Return an instance of the CloudFunctions class."""
        return CloudFunctions(project, region, self.auth, self.verbose)

    def update(self, mri_bucket=None):
        """Return an instance of the Update class."""
        return Update(self, mri_bucket=mri_bucket)
