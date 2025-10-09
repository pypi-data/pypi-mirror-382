"""A DataFileStreamHandler that triggers some arbitrary local code when full files are available"""

import datetime
from openmsistream.data_file_io.actor.data_file_stream_processor import (
    DataFileStreamProcessor,
)
from alpss.commands import alpss_main_with_config
import json
from openmsistream.girder.girder_upload_stream_processor import (
    GirderUploadStreamProcessor,
)
from openmsistream.data_file_io.entity.data_file import DataFile
from openmsistream.data_file_io.entity.download_data_file import DownloadDataFileToMemory
from pathlib import Path
import pickle
import numpy as np
from io import BytesIO
import pandas as pd
import os
import hashlib


class ALPSStreamProcessor(DataFileStreamProcessor):
    """
    A class to consume :class:`~.data_file_io.entity.data_file_chunk.DataFileChunk` messages
    into memory and perform some operation(s) when entire files are available.
    This is a base class that cannot be instantiated on its own.

    :param config_path: Path to the config file to use in defining the Broker connection
        and Consumers
    :type config_path: :class:`pathlib.Path`
    :param topic_name: Name of the topic to which the Consumers should be subscribed
    :type topic_name: str
    :param output_dir: Path to the directory where the log and csv registry files should be kept
        (if None a default will be created in the current directory)
    :type output_dir: :class:`pathlib.Path`, optional
    :param mode: a string flag determining whether reconstructed data files should
        have their contents stored only in "memory" (the default, and the fastest),
        only on "disk" (in the output directory, to reduce the memory footprint),
        or "both" (for flexibility in processing)
    :type mode: str, optional
    :param datafile_type: the type of data file that recognized files should be reconstructed as.
        Default options are set automatically depending on the "mode" argument.
        (must be a subclass of :class:`~.data_file_io.DownloadDataFile`)
    :type datafile_type: :class:`~.data_file_io.DownloadDataFile`, optional
    :param n_threads: the number of threads/consumers to run
    :type n_threads: int, optional
    :param consumer_group_id: the group ID under which each consumer should be created
    :type consumer_group_id: str, optional
    :param filepath_regex: If given, only messages associated with files whose paths match
        this regex will be consumed
    :type filepath_regex: :type filepath_regex: :func:`re.compile` or None, optional

    :raises ValueError: if `datafile_type` is not a subclass of
        :class:`~.data_file_io.DownloadDataFileToMemory`, or more specific as determined
        by the "mode" argument
    """

    def __init__(
        self,
        config,
        topic_name,
        alpss_config_path,
        **kwargs,
    ):
        super().__init__(config_file=config, topic_name=topic_name, **kwargs)

        self.url = kwargs.pop("girder_api_url")
        self.api_key = kwargs.pop("girder_api_key")
        self.girder_root_folder_id = kwargs.pop("girder_root_folder_id")
        self.output_dir = kwargs.pop("output_dir")

        self.girder_uploader = GirderUploadStreamProcessor(self.url, self.api_key, config_file=config, topic_name=topic_name, girder_root_folder_id=self.girder_root_folder_id, delete_on_disk_mode=False)

        self.alpss_config_path = alpss_config_path

        try:
            with open(self.alpss_config_path, "r") as f:
                self.alpss_config = json.load(f)
        except Exception as e:
            raise Exception(f"Unexpected error while loading ALPSS config: {str(e)}")

        self.alpss_config["out_files_dir"] = self.output_dir

        self.config_folder_id = "68b05cdac2245ec1371aac2d"

        self.cfg_checksum_sha256 = self._sha256_of_path(self.alpss_config_path)
        cfg_basename = os.path.basename(self.alpss_config_path)

        config_exists = False
        # Check if a file with the same name and checksum already exists in the folder
        for resp in self.girder_client.listItem(self.config_folder_id, name=cfg_basename):
            existing_sha256 = resp.get("meta", {}).get("alpss_config_checksum_sha256")
            if existing_sha256 == self.cfg_checksum_sha256:
                errmsg = (
                    f"WARNING: found an existing Item named {cfg_basename} with the same "
                    f"checksum in folder {self.config_folder_id}. Skipping upload."
                )
                self.logger.warning(errmsg)
                config_exists = True
                break

        if not config_exists:
            config_file_item = self.girder_client.uploadFileToFolder(
                self.config_folder_id, str(self.alpss_config_path)
            )
            self.girder_client.addMetadataToItem(
                config_file_item["itemId"],
                {"alpss_config_checksum_sha256": self.cfg_checksum_sha256}
            )


    @property
    def girder_client(self):
        return self.girder_uploader._GirderUploadStreamProcessor__girder_client

    def safe_delete_file(self, filepath):
        path = Path(filepath)
        
        try:
            if path.is_file():
                path.unlink()
                return f"File successfully deleted: {filepath}"
            else:
                return f"File cannot be deleted: does not exist or is not a file: {filepath}"
        except Exception as e:
            raise 
    
    def _sha256_of_path(self, path):
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
    
    def _json_safe_for_girder(self, val):
        if isinstance(val, Path):
            return str(val)

        try:
            json.dumps(val, default=str)
            return val
        except Exception:
            return str(val)

    def _process_downloaded_data_file(self, datafile, lock):
        """
        Perform some arbitrary operation(s) on a given data file that has been fully read
        from the stream. Can optionally lock other threads using the given lock.

        Not implemented in the base class.

        :param datafile: A :class:`~.data_file_io.DownloadDataFileToMemory` object that
            has received all of its messages from the topic
        :type datafile: :class:`~.data_file_io.DownloadDataFileToMemory`
        :param lock: Acquiring this :class:`threading.Lock` object would ensure that
            only one instance of :func:`~_process_downloaded_data_file` is running at once
        :type lock: :class:`threading.Lock`

        :return: None if processing was successful, an Exception otherwise
        """
        with lock:
            try:
                file_path = os.path.join(self.output_dir, datafile.relative_filepath)
                self.alpss_config["filepath"] = file_path
                self.alpss_config["relative_filepath"] = datafile.relative_filepath
                self.alpss_config["filename"] = datafile.filename

                fig, alpss_outputs = alpss_main_with_config(self.alpss_config)
                for output_name, output in alpss_outputs.items():
                    if output_name == "results":
                        continue
                    meta_base = {
                        "alpss_config_checksum_sha256": self.cfg_checksum_sha256,
                    }

                    uploaded_file = self.girder_client.uploadFileToFolder(self.girder_root_folder_id, output[-1])
                    # self.logger.info(uploaded_file)

                    try:
                        item_id = uploaded_file.get("itemId")
                        if item_id:
                            per_item_meta = dict(meta_base)
                            per_item_meta["alpss_output_name"] = output_name

                            # Add every key/value from the config dict as individual metadata fields
                            for k, v in self.alpss_config.items():
                                if k in ["out_files_dir", "filepath"]:
                                    continue
                                per_item_meta[str(k)] = self._json_safe_for_girder(v)

                            self.girder_client.addMetadataToItem(item_id, per_item_meta)
                    except Exception as meta_e:
                        self.logger.error(f"Error adding metadata to item: {meta_e}")
                        raise


                    if self.mode == "disk" and self.delete_on_disk_mode:
                        msg = self.safe_delete_file(Path(output[-1]))
                        msg += " (artefact generated from ALPSS)"
                        self.logger.debug(msg)
            except Exception as e:
                self.logger.error(f"alpss processor caught an exception: {e}")
        return None

    @classmethod
    def get_command_line_arguments(cls):
        superargs, superkwargs = super().get_command_line_arguments()
        girder_args, girder_superkwargs = (
            GirderUploadStreamProcessor.get_command_line_arguments()
        )
        args = [
            *superargs,
        ]
        args.extend(girder_args)
        kwargs = {**superkwargs}
        return args, kwargs

    @classmethod
    def run_from_command_line(cls, args=None):
        """
        Run the stream-processed analysis code from the command line
        """
        # make the argument parser
        parser = cls.get_argument_parser()
        parser.add_argument(
            "--alpss_config_path", help="Path to the config file containing ALPSS parameter"
        )
    
        args = parser.parse_args(args=args)

        # make the stream processor
        alpss_analysis = cls(
            args.config,
            args.topic_name,
            args.alpss_config_path,
            delete_on_disk_mode=args.delete_on_disk_mode,
            filepath_regex=args.download_regex,
            mode=args.mode,
            n_threads=args.n_threads,
            update_secs=args.update_seconds,
            consumer_group_id=args.consumer_group_id,
            girder_api_url=args.girder_api_url,
            girder_api_key=args.girder_api_key,
            girder_root_folder_id=args.girder_root_folder_id,
            output_dir=args.output_dir
        )

        # start the processor running (returns total number of messages read, processed, and names of processed files)
        run_start = datetime.datetime.now()
        msg = (
            f"Listening to the {args.topic_name} topic for flyer image files to analyze"
        )
        alpss_analysis.logger.info(msg)
        (
            n_read,
            n_processed,
            processed_filepaths,
        ) = alpss_analysis.process_files_as_read()
        alpss_analysis.close()
        run_stop = datetime.datetime.now()
        # shut down when that function returns
        msg = "ALPSS analysis stream processor "
        if args.output_dir is not None:
            msg += f"writing to {args.output_dir} "
        msg += "shut down"
        alpss_analysis.logger.info(msg)
        msg = f"{n_read} total messages were consumed"
        if len(processed_filepaths) > 0:
            msg += f", {n_processed} messages were successfully processed,"
            msg += f" and the following {len(processed_filepaths)} file"
            msg += " " if len(processed_filepaths) == 1 else "s "
            msg += f"had analysis results added to {args.db_connection_str}"
        else:
            msg += f" and {n_processed} messages were successfully processed"
        msg += f" from {run_start} to {run_stop}"
        for fn in processed_filepaths:
            msg += f"\n\t{fn}"
        alpss_analysis.logger.info(msg)


def main(args=None):
    ALPSStreamProcessor.run_from_command_line(args=args)

if __name__ == "__main__":
    main()
