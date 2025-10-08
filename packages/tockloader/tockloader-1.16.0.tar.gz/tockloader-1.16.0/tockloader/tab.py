import argparse
import io
import logging
import os
import shutil
import struct
import tarfile
import tempfile
import textwrap
import urllib.request

import toml

from .app_tab import TabApp
from .app_tab import TabTbf
from .exceptions import TockLoaderException
from .tbfh import TBFHeader
from .tbfh import TBFFooter


class TAB:
    """
    Tock Application Bundle object. This class handles the TAB format.
    """

    def __init__(self, tab_path, args=argparse.Namespace()):
        self.args = args
        self.tab_path = tab_path

        if os.path.exists(tab_path):
            # Fetch it from the local filesystem.
            self.tab = tarfile.open(tab_path)
        else:
            try:
                # Otherwise download it as a URL.
                with urllib.request.urlopen(tab_path) as response:
                    tmp_file = tempfile.TemporaryFile()
                    # Copy the downloaded response to our temporary file.
                    shutil.copyfileobj(response, tmp_file)
                    # Need to seek to the beginning of the file for tarfile
                    # to work.
                    tmp_file.seek(0)
                    self.tab = tarfile.open(fileobj=tmp_file)
            except Exception as e:
                if self.args.debug:
                    logging.error(
                        "Could not download .tab file. This may have happened because:"
                    )
                    logging.error("  - An HTTPS connection could not be established.")
                    logging.error("  - A temporary file could not be created.")
                    logging.error("  - Untarring the TAB failed.")
                    logging.error("Exception: {}".format(e))
                raise TockLoaderException("Could not download .tab file.")

    def extract_app(self, arch):
        """
        Return a `TabApp` object from this TAB, or `None` if the requested
        architecture is not present in the TAB. You must specify the desired MCU
        architecture so the correct App object can be retrieved. Note that an
        architecture may have multiple TBF files if the app is compiled for a
        fixed address, and multiple fixed address versions are included in the
        TAB.
        """
        # Find all filenames that start with the architecture name.
        matching_tbf_filenames = []
        contained_files = self.tab.getnames()
        # A TBF name is in the format: <architecture>.<anything>.tbf
        for contained_file in contained_files:
            name_pieces = contained_file.split(".")
            if len(name_pieces) >= 2 and name_pieces[-1] == "tbf":
                if name_pieces[0] == arch:
                    matching_tbf_filenames.append(contained_file)

        if len(matching_tbf_filenames) == 0:
            # No match for this architecture! Just return None.
            return None

        # Get all of the TBF headers and app binaries to create a TabApp.
        tbfs = []
        for tbf_filename in matching_tbf_filenames:
            binary_tarinfo = self.tab.getmember(tbf_filename)
            binary = self.tab.extractfile(binary_tarinfo).read()

            # Parse binary and add TBF to our list of TBFs for this app.
            tabtbf = self._extract_tbf_from_filebuffer(tbf_filename, binary)
            tbfs.append(tabtbf)

        return TabApp(tbfs)

    def extract_tbf(self, tbf_name):
        """
        Return a `TabApp` object from this TAB. You must specify the
        desired TBF name, and only that TBF will be returned.
        """
        tbf_filename = "{}.tbf".format(tbf_name)
        binary_tarinfo = self.tab.getmember(tbf_filename)
        binary = self.tab.extractfile(binary_tarinfo).read()

        # Parse binary and app with just this one TBF.
        tabtbf = self._extract_tbf_from_filebuffer(tbf_filename, binary)
        return TabApp([tabtbf])

    def update_tbf(self, app):
        """
        Inserts a new or modified `TabApp` into the .tab file.

        Only works with .tab files stored locally.
        """

        # First need to extract everything from the existing tab so we can
        # replace the files that have not been modified.
        allmembers = self.tab.getmembers()
        allfiles = []
        for member in allmembers:
            allfiles.append(self.tab.extractfile(member).read())

        # Close the tab we have open since we need to re-open it for writing.
        self.tab.close()

        # Now need to open tab for writing.
        tab = tarfile.open(self.tab_path, mode="w")

        # Track which files we replaced with new versions.
        replaced_names = []

        # Iterate the new versions and add them to the tab
        names_and_binaries = app.get_names_and_binaries()
        for filename, binary in names_and_binaries:
            tarinfo = tarfile.TarInfo(filename)
            tarinfo.size = len(binary)
            tab.addfile(tarinfo, io.BytesIO(binary))
            # Keep track of what we now have.
            replaced_names.append(filename)

        # Replace what we didn't change.
        for i, member in enumerate(allmembers):
            if not member.name in replaced_names:
                tab.addfile(member, io.BytesIO(allfiles[i]))

        # Close the version for writing.
        tab.close()

        # Re-open the read version
        self.tab = tarfile.open(self.tab_path)

    def is_compatible_with_board(self, board):
        """
        Check if the Tock app is compatible with a particular Tock board.
        """
        only_for_boards = self._get_metadata_key("only-for-boards")

        # If no boards are set, unconditionally return True.
        if only_for_boards == None or only_for_boards == "":
            return True

        # If boards are set, it better be in the list.
        if board and board in only_for_boards:
            return True

        # Otherwise, incompatible.
        return False

    def get_compatible_boards(self):
        """
        Return a list of compatible boards from the metadata file.
        """
        only_for_boards = self._get_metadata_key("only-for-boards") or ""
        return [b.strip() for b in only_for_boards.split(",")]

    def is_compatible_with_kernel_version(self, kernel_version):
        """
        Check if the Tock app is compatible with the version of the kernel.
        Default to yes unless we can be confident the answer is no.

        `kernel_version` should be a string, or None if the kernel API version
        is unknown.
        """
        if kernel_version == None:
            # Bail out early if kernel version is unknown.
            return True

        tock_kernel_version = self._get_metadata_key("tock-kernel-version")
        return (
            tock_kernel_version == None
            or tock_kernel_version == kernel_version
            or tock_kernel_version == ""
        )

    def get_supported_architectures(self):
        """
        Return a list of architectures that this TAB has compiled binaries for.
        Note that this will return all architectures that have any TBF binary,
        but some of those TBF binaries may be compiled for very specific
        addresses. That is, there isn't a guarantee that the TBF file will work
        on any chip with one of the supported architectures.
        """
        archs = set()
        contained_files = self.tab.getnames()
        # A TBF name is in the format: <architecture>.<anything>.tbf
        for contained_file in contained_files:
            name_pieces = contained_file.split(".")
            if len(name_pieces) >= 2 and name_pieces[-1] == "tbf":
                archs.add(name_pieces[0])

        # We used to use the format <architecture>.bin, so for backwards
        # compatibility check that too.
        if len(archs) == 0:
            archs = set([i[:-4] for i in contained_files if i[-4:] == ".bin"])

        return sorted(archs)

    def get_tbf_names(self):
        """
        Returns a list of the names of all of the .tbf files contained in the
        TAB, without the extension.
        """
        tbfs = []
        for f in self.tab.getnames():
            if f[-4:] == ".tbf":
                tbfs.append(f[:-4])
        return sorted(tbfs)

    def get_app_name(self):
        """
        Return the app name from the metadata file.
        """
        return self._get_metadata_key("name") or ""

    def _extract_tbf_from_filebuffer(self, tbf_filename, binary):
        # First get the TBF header from the binary and check that it is valid.
        tbfh = TBFHeader(binary)
        if tbfh.is_valid():
            # Check that total size actually matches the binary that we got.
            if tbfh.get_app_size() < len(binary):
                # It's fine if the binary is smaller, but the binary cannot
                # be longer than the amount of reserved space (`total_size`
                # in the TBF header) for the app.
                raise TockLoaderException(
                    "Invalid TAB, the app binary length ({} bytes) is longer \
than its defined total_size ({} bytes)".format(
                        len(binary), tbfh.get_app_size()
                    )
                )

            # Get indices into the TBF file binary on where elements are
            # located.
            start_of_app_binary = tbfh.get_size_before_app()
            start_of_footers = tbfh.get_binary_end_offset()

            # Get application binary code.
            app_binary = binary[start_of_app_binary:start_of_footers]

            # Extract the footer if any should exist. It is OK if the footer
            # buffer is zero length, the footer object will just be empty.
            tbff = TBFFooter(tbfh, app_binary, binary[start_of_footers:])

            # Finally we can return the TBF.
            return TabTbf(
                tbf_filename,
                tbfh,
                app_binary,
                tbff,
            )
        else:
            raise TockLoaderException("Invalid TBF found in app in TAB: {}", tbfh)

    def _parse_metadata(self):
        """
        Open and parse the included metadata file in the TAB, returning the
        key-value pairs as a dict.
        """
        # Use cached value.
        if hasattr(self, "metadata"):
            return self.metadata

        # Otherwise parse f.toml file.
        metadata_tarinfo = self.tab.getmember("metadata.toml")
        metadata_str = self.tab.extractfile(metadata_tarinfo).read().decode("utf-8")
        self.metadata = toml.loads(metadata_str)
        return self.metadata

    def _get_metadata_key(self, key):
        """
        Return the value for a specific key from the metadata file.
        """
        metadata = self._parse_metadata()
        if metadata["tab-version"] == 1:
            if key in metadata:
                return metadata[key].strip()
        else:
            # If unknown version, print warning.
            logging.warning(
                "Unknown TAB version. You probably need to update tockloader."
            )

        # Default to returning None if key is not found or file is not understood.
        return None

    def __str__(self):
        out = ""
        metadata = self._parse_metadata()
        out += "TAB: {}\n".format(metadata["name"])
        for k, v in sorted(metadata.items()):
            if k == "name":
                continue
            out += "  {}: {}\n".format(k, v)
        out += "  included architectures: {}\n".format(
            ", ".join(self.get_supported_architectures())
        )
        return out
