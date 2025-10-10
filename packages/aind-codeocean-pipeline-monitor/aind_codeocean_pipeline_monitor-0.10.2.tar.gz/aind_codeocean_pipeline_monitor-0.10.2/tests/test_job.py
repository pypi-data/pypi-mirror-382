"""Test methods in job module"""

import json
import os
import unittest
from copy import deepcopy
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, call, patch

from codeocean import CodeOcean
from codeocean.components import (
    EveryoneRole,
    Permissions,
)
from codeocean.computation import (
    Computation,
    ComputationEndStatus,
    ComputationState,
    DataAssetsRunParam,
    DownloadFileURL,
    Folder,
    RunParams,
)
from codeocean.data_asset import (
    AWSS3Target,
    ComputationSource,
    DataAsset,
    DataAssetOrigin,
    DataAssetParams,
    DataAssetState,
    DataAssetType,
    Source,
    SourceBucket,
    Target,
)
from codeocean.error import Error
from codeocean.folder import FolderItem
from requests import Response
from requests.exceptions import HTTPError

from aind_codeocean_pipeline_monitor.job import PipelineMonitorJob
from aind_codeocean_pipeline_monitor.models import (
    CaptureSettings,
    DocDbSettings,
    PipelineMonitorSettings,
)

RESOURCES_DIR = Path(os.path.dirname(os.path.realpath(__file__))) / "resources"


class TestPipelineMonitorJob(unittest.TestCase):
    """Test PipelineMonitorJob class"""

    @classmethod
    def setUpClass(cls) -> None:
        """Set default example settings"""

        with open(RESOURCES_DIR / "data_description.json", "r") as f:
            expected_data_description = json.dumps(json.load(f))

        no_capture_result_settings = PipelineMonitorSettings(
            run_params=RunParams(
                pipeline_id="abc-123",
            )
        )
        capture_results_settings = PipelineMonitorSettings(
            run_params=RunParams(
                pipeline_id="abc-123",
                version=1,
                data_assets=[
                    DataAssetsRunParam(
                        id="abc-001",
                        mount="ecephys",
                    )
                ],
            ),
            capture_settings=CaptureSettings(
                tags=["derived"],
                docdb_settings=DocDbSettings(
                    docdb_api_gateway="example.com",
                    docdb_database="db",
                    docdb_collection="coll",
                    results_bucket="example_bucket",
                ),
            ),
        )
        capture_settings_with_alert = capture_results_settings.model_copy(
            deep=True
        )
        capture_settings_with_alert.alert_url = "an_alert_url"

        internal_server_error_response = Response()
        internal_server_error_response.status_code = 500
        internal_server_error = HTTPError()
        internal_server_error.response = internal_server_error_response

        co_client = CodeOcean(domain="test_domain", token="token")
        no_capture_job = PipelineMonitorJob(
            job_settings=no_capture_result_settings, client=co_client
        )
        capture_job = PipelineMonitorJob(
            job_settings=capture_results_settings, client=co_client
        )
        capture_job_with_alert = PipelineMonitorJob(
            job_settings=capture_settings_with_alert, client=co_client
        )
        cls.no_capture_job = no_capture_job
        cls.capture_job = capture_job
        cls.capture_job_with_alert = capture_job_with_alert
        cls.internal_server_error = internal_server_error
        cls.expected_data_description = expected_data_description

    @patch("codeocean.computation.Computations.get_computation")
    @patch("codeocean.computation.sleep", return_value=None)
    def test_monitor_pipeline(
        self,
        mock_sleep: MagicMock,
        mock_get_computation: MagicMock,
    ):
        """Tests _monitor_pipeline method with successful completion"""
        completed_comp = Computation(
            id="c123",
            created=0,
            name="c_name",
            state=ComputationState.Completed,
            run_time=100,
        )
        mock_get_computation.side_effect = [
            Computation(
                id="c123",
                created=0,
                name="c_name",
                state=ComputationState.Running,
                run_time=1,
            ),
            completed_comp,
        ]
        response = self.no_capture_job._monitor_pipeline(
            computation=Computation(
                id="c123",
                created=0,
                name="c_name",
                state=ComputationState.Initializing,
                run_time=0,
            )
        )
        self.assertEqual(completed_comp, response)
        mock_sleep.assert_called_once_with(180)

    @patch("codeocean.computation.Computations.get_computation")
    @patch("codeocean.computation.sleep", return_value=None)
    def test_monitor_pipeline_error(
        self,
        mock_sleep: MagicMock,
        mock_get_computation: MagicMock,
    ):
        """Tests _monitor_pipeline method with internal server error"""
        mock_get_computation.side_effect = self.internal_server_error
        with self.assertRaises(HTTPError):
            self.no_capture_job._monitor_pipeline(
                computation=Computation(
                    id="c123",
                    created=0,
                    name="c_name",
                    state=ComputationState.Initializing,
                    run_time=0,
                )
            )
        mock_sleep.assert_not_called()

    @patch("codeocean.computation.Computations.delete_computation")
    @patch("codeocean.computation.Computations.get_computation")
    @patch("codeocean.computation.sleep", return_value=None)
    def test_monitor_pipeline_timeout_error(
        self,
        mock_sleep: MagicMock,
        mock_get_computation: MagicMock,
        mock_delete_computation: MagicMock,
    ):
        """Tests _monitor_pipeline method with a timeout error"""
        mock_get_computation.side_effect = TimeoutError("Comp. timed out")
        with self.assertLogs(level="INFO") as captured:
            with self.assertRaises(TimeoutError):
                self.no_capture_job._monitor_pipeline(
                    computation=Computation(
                        id="c123",
                        created=0,
                        name="c_name",
                        state=ComputationState.Initializing,
                        run_time=0,
                    )
                )
        expected_logs = [
            (
                "ERROR:root:Computation timeout reached: ('Comp. timed out',),"
                " attempting to terminate pipeline"
            )
        ]
        mock_sleep.assert_not_called()
        mock_delete_computation.assert_called_once_with(computation_id="c123")
        self.assertEqual(expected_logs, captured.output)

    @patch("codeocean.computation.Computations.get_computation")
    @patch("codeocean.computation.sleep", return_value=None)
    def test_monitor_pipeline_failed(
        self,
        mock_sleep: MagicMock,
        mock_get_computation: MagicMock,
    ):
        """Tests _monitor_pipeline method with failed completion"""
        failed_comp = Computation(
            id="c123",
            created=0,
            name="c_name",
            state=ComputationState.Failed,
            run_time=100,
        )
        mock_get_computation.side_effect = [
            Computation(
                id="c123",
                created=0,
                name="c_name",
                state=ComputationState.Running,
                run_time=1,
            ),
            failed_comp,
        ]
        with self.assertRaises(Exception) as e:
            self.no_capture_job._monitor_pipeline(
                computation=Computation(
                    id="c123",
                    created=0,
                    name="c_name",
                    state=ComputationState.Initializing,
                    run_time=0,
                )
            )
        self.assertIn("The computation had an error: ", e.exception.args[0])
        mock_sleep.assert_called_once_with(180)

    @patch("codeocean.computation.Computations.get_computation")
    @patch("codeocean.computation.sleep", return_value=None)
    def test_monitor_pipeline_failed_exit_code(
        self,
        mock_sleep: MagicMock,
        mock_get_computation: MagicMock,
    ):
        """Tests _monitor_pipeline method when exit code is 1"""
        failed_comp = Computation(
            id="c123",
            created=0,
            name="c_name",
            state=ComputationState.Completed,
            end_status=ComputationEndStatus.Succeeded,
            exit_code=1,
            run_time=100,
        )
        mock_get_computation.side_effect = [
            Computation(
                id="c123",
                created=0,
                name="c_name",
                state=ComputationState.Running,
                run_time=1,
            ),
            failed_comp,
        ]
        with self.assertRaises(Exception) as e:
            self.no_capture_job._monitor_pipeline(
                computation=Computation(
                    id="c123",
                    created=0,
                    name="c_name",
                    state=ComputationState.Initializing,
                    run_time=0,
                )
            )
        self.assertIn("The computation had an error: ", e.exception.args[0])
        mock_sleep.assert_called_once_with(180)

    @patch("codeocean.data_asset.DataAssets.get_data_asset")
    @patch("codeocean.data_asset.sleep", return_value=None)
    def test_wait_for_data_asset(
        self,
        mock_sleep: MagicMock,
        mock_get_data_asset: MagicMock,
    ):
        """Tests wait for Data asset success."""
        initial_data_asset = DataAsset(
            id="def-123",
            created=1,
            name="da_name",
            mount="da_mount",
            state=DataAssetState.Draft,
            type=DataAssetType.Result,
            last_used=1,
        )
        completed_data_asset = DataAsset(
            id="def-123",
            created=1,
            name="da_name",
            mount="da_mount",
            state=DataAssetState.Ready,
            type=DataAssetType.Result,
            last_used=1,
        )
        mock_get_data_asset.side_effect = [
            initial_data_asset,
            completed_data_asset,
        ]

        response = self.capture_job._wait_for_data_asset(initial_data_asset)

        self.assertEqual(completed_data_asset, response)
        mock_sleep.assert_called_once_with(10)

    @patch("codeocean.data_asset.DataAssets.get_data_asset")
    @patch("codeocean.data_asset.sleep", return_value=None)
    def test_wait_for_data_asset_error(
        self,
        mock_sleep: MagicMock,
        mock_get_data_asset: MagicMock,
    ):
        """Tests _wait_for_data_asset method with internal server error"""
        initial_data_asset = DataAsset(
            id="def-123",
            created=1,
            name="da_name",
            mount="da_mount",
            state=DataAssetState.Draft,
            type=DataAssetType.Result,
            last_used=1,
        )
        mock_get_data_asset.side_effect = self.internal_server_error
        with self.assertRaises(HTTPError):
            self.capture_job._wait_for_data_asset(initial_data_asset)
        mock_sleep.assert_not_called()

    @patch("codeocean.data_asset.DataAssets.get_data_asset")
    @patch("codeocean.data_asset.sleep", return_value=None)
    def test_wait_for_data_asset_failed(
        self,
        mock_sleep: MagicMock,
        mock_get_data_asset: MagicMock,
    ):
        """Tests _monitor_pipeline method with failed completion"""
        initial_data_asset = DataAsset(
            id="def-123",
            created=1,
            name="da_name",
            mount="da_mount",
            state=DataAssetState.Draft,
            type=DataAssetType.Result,
            last_used=1,
        )
        completed_data_asset = DataAsset(
            id="def-123",
            created=1,
            name="da_name",
            mount="da_mount",
            state=DataAssetState.Failed,
            type=DataAssetType.Result,
            last_used=1,
        )
        mock_get_data_asset.side_effect = [
            initial_data_asset,
            completed_data_asset,
        ]
        with self.assertRaises(Exception) as e:
            self.capture_job._wait_for_data_asset(initial_data_asset)
        self.assertIn("Data asset creation failed", e.exception.args[0])
        mock_sleep.assert_called_once_with(10)

    @patch("requests.post")
    def test_send_alert_to_teams(self, mock_post: MagicMock):
        """Tests _send_alert_to_teams method"""

        mock_response = Response()
        mock_response.status_code = 200
        mock_response._content = b'{"msg":"good"}'
        mock_post.return_value = mock_response
        with self.assertLogs(level="INFO") as captured:
            self.capture_job_with_alert._send_alert_to_teams(
                message="Job Success"
            )
        mock_post.assert_called_once()
        expected_logs = ['INFO:root:Alert response: {"msg":"good"}']
        self.assertEqual(expected_logs, captured.output)

    @patch("requests.post")
    def test_send_alert_to_teams_fail(self, mock_post: MagicMock):
        """Tests _send_alert_to_teams method when request fails"""

        mock_response = Response()
        mock_response.status_code = 500
        mock_response._content = b'{"msg":"bad"}'
        mock_post.return_value = mock_response
        with self.assertLogs(level="INFO") as captured:
            self.capture_job_with_alert._send_alert_to_teams(
                message="Job Success"
            )
        mock_post.assert_called_once()
        expected_logs = [
            (
                "WARNING:root:There was an issue sending the alert: "
                "<Response [500]>"
            )
        ]
        self.assertEqual(expected_logs, captured.output)

    @patch("codeocean.computation.Computations.list_computation_results")
    @patch("codeocean.computation.Computations.get_result_file_download_url")
    @patch("aind_codeocean_pipeline_monitor.job.urlopen")
    def test_gather_metadata(
        self,
        mock_url_open: MagicMock,
        mock_get_result_file_url: MagicMock,
        mock_list_comp_results: MagicMock,
    ):
        """Tests _gather_metadata method"""
        mock_list_comp_results.return_value = Folder(
            items=[
                FolderItem(name="output", path="output", type=""),
                FolderItem(
                    name="data_description.json",
                    path="data_description.json",
                    type="",
                ),
            ]
        )
        mock_get_result_file_url.return_value = DownloadFileURL(
            url="some_download_url"
        )
        mock_read = MagicMock()
        mock_read.read.return_value = self.expected_data_description.encode(
            "utf-8"
        )
        mock_url_open.return_value.__enter__.return_value = mock_read
        info = self.capture_job._gather_metadata(
            computation=Computation(
                id="c123",
                created=0,
                name="c_name",
                state=ComputationState.Completed,
                run_time=100,
            )
        )
        expected_info = {
            "data_description": json.loads(self.expected_data_description)
        }
        self.assertEqual(expected_info, info)

    @patch("codeocean.data_asset.DataAssets.get_data_asset")
    def test_get_input_data_name(self, mock_get_data_asset: MagicMock):
        """Tests _get_input_data_name success"""
        mock_get_data_asset.return_value = DataAsset(
            id="abc-001",
            created=0,
            name="ecephys_123456_2020-10-10_00-00-00",
            mount="ecephys",
            state=DataAssetState.Ready,
            type=DataAssetType.Dataset,
            last_used=1,
        )
        input_data_name = self.capture_job._get_input_data_name()
        self.assertEqual("ecephys_123456_2020-10-10_00-00-00", input_data_name)

    @patch("codeocean.data_asset.DataAssets.get_data_asset")
    def test_get_input_data_name_none(self, mock_get_data_asset: MagicMock):
        """Tests _get_input_data_name when no input data attached"""
        input_data_name = self.no_capture_job._get_input_data_name()
        self.assertIsNone(input_data_name)
        mock_get_data_asset.assert_not_called()

    def test_get_name_from_data_description(self):
        """Tests _get_name_from_data_description"""

        core_json = {
            "data_description": json.loads(self.expected_data_description)
        }

        info = self.capture_job._get_name_and_level_from_data_description(
            core_metadata_json=core_json
        )
        expected_info_from_file = {
            "data_level": "derived",
            "name": (
                "ecephys_709351_2024-04-10_14-53-09_sorted_2024-04-19_23-19-34"
            ),
        }
        self.assertEqual(expected_info_from_file, info)

    def test_get_name_from_data_description_none(
        self,
    ):
        """Tests _get_name_from_data_description when no file is found."""
        info = self.capture_job._get_name_and_level_from_data_description(
            core_metadata_json=dict()
        )
        expected_info = {"name": None, "data_level": None}
        self.assertEqual(expected_info, info)

    @patch("aind_codeocean_pipeline_monitor.job.datetime")
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._get_input_data_name"
    )
    def test_get_name(
        self,
        mock_get_input_data_name: MagicMock,
        mock_dt: MagicMock,
    ):
        """Tests _get_name from settings when no data_description found"""

        mock_dt.now.return_value = datetime(2020, 11, 10)
        input_data_name = "ecephys_123456_2020-10-10_00-00-00"
        core_json = dict()
        with self.assertLogs() as captured:

            name = self.capture_job._get_name(
                core_metadata_jsons=core_json, input_data_name=input_data_name
            )
        expected_captured = [
            (
                "WARNING:root:Data level in data description None does not "
                "match expected pattern! Ignoring name in data description "
                "and will attempt to set a default name."
            )
        ]
        expected_name = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )
        self.assertEqual(expected_name, name)
        mock_get_input_data_name.assert_not_called()
        self.assertEqual(expected_captured, captured.output)

    @patch("aind_codeocean_pipeline_monitor.job.datetime")
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._get_input_data_name"
    )
    def test_get_name_from_dd(
        self,
        mock_get_input_data_name: MagicMock,
        mock_dt: MagicMock,
    ):
        """Tests _get_name from data_description file"""

        core_json = {
            "data_description": json.loads(self.expected_data_description)
        }
        input_data_name = "ecephys_709351_2024-04-10_14-53-09"
        mock_dt.now.return_value = datetime(2020, 11, 10)
        name = self.capture_job._get_name(
            core_metadata_jsons=core_json, input_data_name=input_data_name
        )
        self.assertEqual(
            "ecephys_709351_2024-04-10_14-53-09_sorted_2024-04-19_23-19-34",
            name,
        )
        mock_get_input_data_name.assert_not_called()

    @patch("aind_codeocean_pipeline_monitor.job.datetime")
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._get_input_data_name"
    )
    def test_get_name_from_dd_bad_format(
        self,
        mock_get_input_data_name: MagicMock,
        mock_dt: MagicMock,
    ):
        """Tests _get_name from data_description file when name in file is
        not in the correct format."""

        core_json = deepcopy(
            {"data_description": json.loads(self.expected_data_description)}
        )
        core_json["data_description"][
            "name"
        ] = "ecephys_123456_2020-10-1_sorted_2020-11-10_00-00-00"
        input_data_name = "ecephys_123456_2020-10-10_00-00-00"
        mock_dt.now.return_value = datetime(2020, 11, 10)
        with self.assertLogs() as captured:
            name = self.capture_job._get_name(
                core_metadata_jsons=core_json, input_data_name=input_data_name
            )
        expected_logs = [
            "WARNING:root:Name in data description "
            "ecephys_123456_2020-10-1_sorted_2020-11-10_00-00-00 "
            "does not match expected pattern! "
            "Will attempt to set default."
        ]
        self.assertEqual(expected_logs, captured.output)
        self.assertEqual(
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00",
            name,
        )
        mock_get_input_data_name.assert_not_called()

    @patch("aind_codeocean_pipeline_monitor.job.datetime")
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._get_input_data_name"
    )
    def test_get_name_error(
        self,
        mock_get_input_data_name: MagicMock,
        mock_dt: MagicMock,
    ):
        """Tests _get_name when input data name is None and data_description
        name is None"""

        core_json = {
            "data_description": {"name": None, "data_level": "derived"}
        }
        mock_dt.now.return_value = datetime(2020, 11, 10)
        with self.assertRaises(Exception) as e:
            self.capture_job._get_name(
                core_metadata_jsons=core_json, input_data_name=None
            )

        self.assertEqual(
            "Unable to construct data asset name.", e.exception.args[0]
        )
        mock_get_input_data_name.assert_not_called()

    @patch("aind_codeocean_pipeline_monitor.job.PipelineMonitorJob._get_name")
    @patch("aind_codeocean_pipeline_monitor.job.datetime")
    def test_build_data_asset_params(
        self, mock_dt: MagicMock, mock_get_name: MagicMock
    ):
        """Tests _build_data_asset_params method"""

        mock_dt.now.return_value = datetime(2020, 11, 10)
        completed_comp = Computation(
            id="c123",
            created=0,
            name="c_name",
            state=ComputationState.Completed,
            run_time=100,
        )
        mock_get_name.return_value = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )
        core_json = {
            "data_description": json.loads(self.expected_data_description)
        }
        params = self.capture_job._build_data_asset_params(
            monitor_pipeline_response=completed_comp,
            input_data_name=None,
            core_metadata_jsons=core_json,
        )
        expected_name = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )
        expected_params = DataAssetParams(
            name=expected_name,
            tags=["derived"],
            mount=expected_name,
            source=Source(
                computation=ComputationSource(id="c123", path=None),
            ),
        )

        self.assertEqual(expected_params, params)

    @patch("aind_codeocean_pipeline_monitor.job.PipelineMonitorJob._get_name")
    @patch("aind_codeocean_pipeline_monitor.job.datetime")
    def test_build_data_asset_params_with_name_mount(
        self, mock_dt: MagicMock, mock_get_name: MagicMock
    ):
        """Tests _build_data_asset_params method when name and mount are set"""

        mock_get_name.return_value = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )

        mock_dt.now.return_value = datetime(2020, 11, 10)

        core_json = {
            "data_description": json.loads(self.expected_data_description)
        }

        completed_comp = Computation(
            id="c123",
            created=0,
            name="c_name",
            state=ComputationState.Completed,
            run_time=100,
        )
        settings2 = self.capture_job.job_settings.model_copy(deep=True)
        settings2.capture_settings.name = "foo"
        settings2.capture_settings.mount = "bar"
        job = PipelineMonitorJob(
            job_settings=settings2, client=CodeOcean(domain="", token="")
        )
        expected_params = DataAssetParams(
            name="foo",
            tags=["derived"],
            mount="bar",
            source=Source(
                computation=ComputationSource(id="c123", path=None),
            ),
        )
        params = job._build_data_asset_params(
            monitor_pipeline_response=completed_comp,
            input_data_name=None,
            core_metadata_jsons=core_json,
        )

        self.assertEqual(expected_params, params)

    @patch("aind_codeocean_pipeline_monitor.job.PipelineMonitorJob._get_name")
    @patch("aind_codeocean_pipeline_monitor.job.datetime")
    def test_build_data_asset_params_with_target(
        self, mock_dt: MagicMock, mock_get_name: MagicMock
    ):
        """Tests _build_data_asset_params method when target is set"""

        mock_dt.now.return_value = datetime(2020, 11, 10)
        mock_get_name.return_value = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )

        core_json = {
            "data_description": json.loads(self.expected_data_description)
        }
        completed_comp = Computation(
            id="c123",
            created=0,
            name="c_name",
            state=ComputationState.Completed,
            run_time=100,
        )
        settings2 = self.capture_job.job_settings.model_copy(deep=True)
        settings2.capture_settings.target = Target(
            aws=AWSS3Target(bucket="ext_bucket", prefix="")
        )
        job = PipelineMonitorJob(
            job_settings=settings2, client=CodeOcean(domain="", token="")
        )
        expected_name = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )
        expected_params = DataAssetParams(
            name=expected_name,
            tags=["derived"],
            mount=expected_name,
            source=Source(
                computation=ComputationSource(id="c123", path=None),
            ),
            target=Target(
                aws=AWSS3Target(
                    bucket="ext_bucket",
                    prefix=expected_name,
                )
            ),
        )
        params = job._build_data_asset_params(
            monitor_pipeline_response=completed_comp,
            input_data_name=None,
            core_metadata_jsons=core_json,
        )

        self.assertEqual(expected_params, params)

    @patch(
        "aind_codeocean_pipeline_monitor.job.MetadataDbClient"
        ".upsert_one_docdb_record"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.MetadataDbClient"
        ".retrieve_docdb_records"
    )
    def test_update_docdb(
        self, mock_docdb_get: MagicMock, mock_docdb_put: MagicMock
    ):
        """Tests _update_docdb method with internal result"""

        mock_docdb_get.return_value = []
        mock_response = Response()
        mock_response.status_code = 200
        mock_response_content = {"message": "success"}
        mock_response._content = json.dumps(mock_response_content).encode(
            "utf-8"
        )
        mock_docdb_put.return_value = mock_response

        name = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )
        core_json = dict()
        wait_for_data_asset = DataAsset(
            id="def-123",
            created=1,
            name=name,
            mount=name,
            state=DataAssetState.Ready,
            type=DataAssetType.Result,
            last_used=1,
            tags=["derived"],
        )
        with self.assertLogs(level="INFO") as captured:
            self.capture_job._update_docdb(
                core_metadata_jsons=core_json,
                wait_for_data_asset_response=wait_for_data_asset,
                name=name,
            )
        self.assertEqual(
            ["INFO:root:DocDB response: {'message': 'success'}"],
            captured.output,
        )
        mock_docdb_get.assert_called_once_with(
            filter_query={"location": "s3://example_bucket/def-123"},
            projection={"_id": 1, "location": 1, "external_links": 1},
            limit=1,
            paginate=False,
        )
        mock_docdb_put.assert_called_once()

    @patch("aind_codeocean_pipeline_monitor.job.datetime")
    @patch(
        "aind_codeocean_pipeline_monitor.job.MetadataDbClient"
        ".upsert_one_docdb_record"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.MetadataDbClient"
        ".retrieve_docdb_records"
    )
    def test_update_docdb_record_exists(
        self,
        mock_docdb_get: MagicMock,
        mock_docdb_put: MagicMock,
        mock_dt: MagicMock,
    ):
        """Tests _update_docdb method with internal result when record
        already exists in docdb."""

        mock_docdb_get.return_value = [{"_id": "abc"}]
        mock_dt.now.return_value = datetime(2020, 10, 10)
        mock_response = Response()
        mock_response.status_code = 200
        mock_response_content = {"message": "success"}
        mock_response._content = json.dumps(mock_response_content).encode(
            "utf-8"
        )
        mock_docdb_put.return_value = mock_response

        name = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )
        core_json = dict()
        wait_for_data_asset = DataAsset(
            id="def-123",
            created=1,
            name=name,
            mount=name,
            state=DataAssetState.Ready,
            type=DataAssetType.Result,
            last_used=1,
            tags=["derived"],
        )
        with self.assertLogs(level="DEBUG") as captured:
            self.capture_job._update_docdb(
                core_metadata_jsons=core_json,
                wait_for_data_asset_response=wait_for_data_asset,
                name=name,
            )
        expected_captured_output = [
            (
                "WARNING:root:Found an existing record(s) for location "
                "s3://example_bucket/def-123! Will attempt to append "
                "codeocean id to external links."
            ),
            "DEBUG:root:DocDB response: {'message': 'success'}",
        ]
        self.assertEqual(expected_captured_output, captured.output)
        mock_docdb_get.assert_called_once_with(
            filter_query={"location": "s3://example_bucket/def-123"},
            projection={"_id": 1, "location": 1, "external_links": 1},
            limit=1,
            paginate=False,
        )
        mock_docdb_put.assert_called_once_with(
            record={
                "_id": "abc",
                "external_links": ["def-123"],
                "last_modified": "2020-10-10T00:00:00",
            }
        )

    @patch(
        "aind_codeocean_pipeline_monitor.job.MetadataDbClient"
        ".upsert_one_docdb_record"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.MetadataDbClient"
        ".retrieve_docdb_records"
    )
    def test_update_docdb_external(
        self, mock_docdb_get: MagicMock, mock_docdb_put: MagicMock
    ):
        """Tests _update_docdb method with external result"""

        mock_docdb_get.return_value = []
        mock_response = Response()
        mock_response.status_code = 200
        mock_response_content = {"message": "success"}
        mock_response._content = json.dumps(mock_response_content).encode(
            "utf-8"
        )
        mock_docdb_put.return_value = mock_response

        name = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )
        core_json = dict()
        wait_for_data_asset = DataAsset(
            id="def-123",
            created=1,
            name=name,
            mount=name,
            state=DataAssetState.Ready,
            type=DataAssetType.Result,
            last_used=1,
            tags=["derived"],
            source_bucket=SourceBucket(
                origin=DataAssetOrigin.AWS,
                bucket="external",
                prefix=name,
                external=True,
            ),
        )
        with self.assertLogs(level="INFO") as captured:
            self.capture_job._update_docdb(
                core_metadata_jsons=core_json,
                wait_for_data_asset_response=wait_for_data_asset,
                name=name,
            )
        self.assertEqual(
            ["INFO:root:DocDB response: {'message': 'success'}"],
            captured.output,
        )
        mock_docdb_get.assert_called_once_with(
            filter_query={"location": f"s3://external/{name}"},
            projection={"_id": 1, "location": 1, "external_links": 1},
            limit=1,
            paginate=False,
        )
        mock_docdb_put.assert_called_once()

    @patch(
        "aind_codeocean_pipeline_monitor.job.MetadataDbClient"
        ".upsert_one_docdb_record"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.MetadataDbClient"
        ".retrieve_docdb_records"
    )
    def test_update_docdb_error(
        self, mock_docdb_get: MagicMock, mock_docdb_put: MagicMock
    ):
        """Tests _update_docdb method when it is unable to figure out the
        location"""

        mock_docdb_get.return_value = []
        mock_response = Response()
        mock_response.status_code = 200
        mock_response_content = {"message": "success"}
        mock_response._content = json.dumps(mock_response_content).encode(
            "utf-8"
        )
        mock_docdb_put.return_value = mock_response

        name = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )
        core_json = dict()
        wait_for_data_asset = DataAsset(
            id="def-123",
            created=1,
            name=name,
            mount=name,
            state=DataAssetState.Ready,
            type=DataAssetType.Result,
            last_used=1,
            tags=["derived"],
            source_bucket=SourceBucket(
                origin=DataAssetOrigin.GCP,
                bucket="external",
                prefix=name,
                external=True,
            ),
        )
        with self.assertRaises(ValueError):
            self.capture_job._update_docdb(
                core_metadata_jsons=core_json,
                wait_for_data_asset_response=wait_for_data_asset,
                name=name,
            )
        mock_docdb_get.assert_not_called()
        mock_docdb_put.assert_not_called()

    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._send_alert_to_teams"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._get_input_data_name"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._build_data_asset_params"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._wait_for_data_asset"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._monitor_pipeline"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._gather_metadata"
    )
    @patch("codeocean.data_asset.DataAssets.create_data_asset")
    @patch("codeocean.computation.Computations.run_capsule")
    @patch("codeocean.data_asset.DataAssets.update_permissions")
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob._update_docdb"
    )
    @patch("aind_codeocean_pipeline_monitor.job.datetime")
    def test_run_job(
        self,
        mock_datetime: MagicMock,
        mock_update_docdb: MagicMock,
        mock_update_permissions: MagicMock,
        mock_run_capsule: MagicMock,
        mock_create_data_asset: MagicMock,
        mock_gather_metadata: MagicMock,
        mock_monitor_pipeline: MagicMock,
        mock_wait_for_data_asset: MagicMock,
        mock_build_data_asset_params: MagicMock,
        mock_get_input_data_name: MagicMock,
        mock_send_alert: MagicMock,
    ):
        """Tests steps are called in run_job method"""
        mock_get_input_data_name.return_value = (
            "ecephys_123456_2020-10-10_00-00-00"
        )
        mock_datetime.now.return_value = datetime(2020, 11, 10)
        mock_run_capsule.return_value = Computation(
            id="c123",
            created=0,
            name="c_name",
            state=ComputationState.Initializing,
            run_time=0,
        )
        mock_monitor_pipeline.return_value = Computation(
            id="c123",
            created=0,
            name="c_name",
            state=ComputationState.Completed,
            run_time=100,
        )
        mock_gather_metadata.return_value = dict()

        expected_name = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )
        mock_create_data_asset.return_value = DataAsset(
            id="def-123",
            created=1,
            name=expected_name,
            mount=expected_name,
            state=DataAssetState.Draft,
            type=DataAssetType.Result,
            last_used=1,
            tags=["derived"],
        )
        mock_wait_for_data_asset.return_value = DataAsset(
            id="def-123",
            created=1,
            name=expected_name,
            mount=expected_name,
            state=DataAssetState.Ready,
            type=DataAssetType.Result,
            last_used=1,
            tags=["derived"],
        )

        mock_build_data_asset_params.return_value = DataAssetParams(
            name=expected_name,
            tags=["derived"],
            mount=expected_name,
            source=Source(
                computation=ComputationSource(id="c123", path=None),
            ),
        )
        with self.assertLogs(level="INFO") as captured:
            self.capture_job.run_job()

        self.assertEqual(8, len(captured.output))
        mock_update_permissions.assert_called_once_with(
            data_asset_id="def-123",
            permissions=Permissions(everyone=EveryoneRole.Viewer),
        )
        mock_gather_metadata.assert_called_once()
        mock_update_docdb.assert_called_once()
        mock_send_alert.assert_not_called()

    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._send_alert_to_teams"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._get_input_data_name"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._build_data_asset_params"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._wait_for_data_asset"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._monitor_pipeline"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._gather_metadata"
    )
    @patch("codeocean.data_asset.DataAssets.create_data_asset")
    @patch("codeocean.computation.Computations.run_capsule")
    @patch("codeocean.data_asset.DataAssets.update_permissions")
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob._update_docdb"
    )
    @patch("aind_codeocean_pipeline_monitor.job.datetime")
    def test_run_job_with_alerts(
        self,
        mock_datetime: MagicMock,
        mock_update_docdb: MagicMock,
        mock_update_permissions: MagicMock,
        mock_run_capsule: MagicMock,
        mock_create_data_asset: MagicMock,
        mock_gather_metadata: MagicMock,
        mock_monitor_pipeline: MagicMock,
        mock_wait_for_data_asset: MagicMock,
        mock_build_data_asset_params: MagicMock,
        mock_get_input_data_name: MagicMock,
        mock_send_alert: MagicMock,
    ):
        """Tests steps are called in run_job method with alert url settings"""
        mock_get_input_data_name.return_value = (
            "ecephys_123456_2020-10-10_00-00-00"
        )
        mock_datetime.now.return_value = datetime(2020, 11, 10)
        mock_run_capsule.return_value = Computation(
            id="c123",
            created=0,
            name="c_name",
            state=ComputationState.Initializing,
            run_time=0,
        )
        mock_monitor_pipeline.return_value = Computation(
            id="c123",
            created=0,
            name="c_name",
            state=ComputationState.Completed,
            run_time=100,
        )
        mock_gather_metadata.return_value = dict()

        expected_name = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )
        mock_create_data_asset.return_value = DataAsset(
            id="def-123",
            created=1,
            name=expected_name,
            mount=expected_name,
            state=DataAssetState.Draft,
            type=DataAssetType.Result,
            last_used=1,
            tags=["derived"],
        )
        mock_wait_for_data_asset.return_value = DataAsset(
            id="def-123",
            created=1,
            name=expected_name,
            mount=expected_name,
            state=DataAssetState.Ready,
            type=DataAssetType.Result,
            last_used=1,
            tags=["derived"],
        )

        mock_build_data_asset_params.return_value = DataAssetParams(
            name=expected_name,
            tags=["derived"],
            mount=expected_name,
            source=Source(
                computation=ComputationSource(id="c123", path=None),
            ),
        )
        mock_update_docdb.side_effect = Exception("Something went wrong.")
        with self.assertLogs(level="INFO") as captured:
            self.capture_job_with_alert.run_job()

        mock_update_permissions.assert_called_once_with(
            data_asset_id="def-123",
            permissions=Permissions(everyone=EveryoneRole.Viewer),
        )
        mock_gather_metadata.assert_called_once()
        self.assertEqual(9, len(captured.output))
        mock_send_alert.assert_has_calls(
            [
                call(
                    message="Starting ecephys_123456_2020-10-10_00-00-00",
                    extra_text="- pipeline: abc-123\n- version: 1\n",
                ),
                call(message="Finished ecephys_123456_2020-10-10_00-00-00"),
            ]
        )
        self.assertIn(
            (
                "ERROR:root:Error updating DocDB: ('Something went wrong.',)."
                " Continuing with job."
            ),
            captured.output,
        )

    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._send_alert_to_teams"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._get_input_data_name"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._build_data_asset_params"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._wait_for_data_asset"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._monitor_pipeline"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._gather_metadata"
    )
    @patch("codeocean.data_asset.DataAssets.create_data_asset")
    @patch("codeocean.computation.Computations.run_capsule")
    @patch("codeocean.data_asset.DataAssets.update_permissions")
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob._update_docdb"
    )
    @patch("aind_codeocean_pipeline_monitor.job.datetime")
    def test_run_job_with_alerts_co_error(
        self,
        mock_datetime: MagicMock,
        mock_update_docdb: MagicMock,
        mock_update_permissions: MagicMock,
        mock_run_capsule: MagicMock,
        mock_create_data_asset: MagicMock,
        mock_gather_metadata: MagicMock,
        mock_monitor_pipeline: MagicMock,
        mock_wait_for_data_asset: MagicMock,
        mock_build_data_asset_params: MagicMock,
        mock_get_input_data_name: MagicMock,
        mock_send_alert: MagicMock,
    ):
        """Tests steps are called in run_job method when a Code Ocean error is
        raised."""
        mock_get_input_data_name.return_value = (
            "ecephys_123456_2020-10-10_00-00-00"
        )
        mock_datetime.now.return_value = datetime(2020, 11, 10)
        mock_run_capsule.return_value = Computation(
            id="c123",
            created=0,
            name="c_name",
            state=ComputationState.Initializing,
            run_time=0,
        )
        http_error_response = Response()
        http_error_response.status_code = 404
        http_error_response._content = b'{"message": "not found"}'
        mock_monitor_pipeline.side_effect = Error(
            err=HTTPError(response=http_error_response)
        )

        expected_name = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )
        mock_create_data_asset.return_value = DataAsset(
            id="def-123",
            created=1,
            name=expected_name,
            mount=expected_name,
            state=DataAssetState.Draft,
            type=DataAssetType.Result,
            last_used=1,
            tags=["derived"],
        )
        mock_wait_for_data_asset.return_value = DataAsset(
            id="def-123",
            created=1,
            name=expected_name,
            mount=expected_name,
            state=DataAssetState.Ready,
            type=DataAssetType.Result,
            last_used=1,
            tags=["derived"],
        )

        with self.assertLogs(level="INFO") as captured:
            with self.assertRaises(Error) as e:
                self.capture_job_with_alert.run_job()

        self.assertEqual(2, len(captured.output))
        mock_send_alert.assert_has_calls(
            [
                call(
                    message="Starting ecephys_123456_2020-10-10_00-00-00",
                    extra_text="- pipeline: abc-123\n- version: 1\n",
                ),
                call(
                    message="Error with ecephys_123456_2020-10-10_00-00-00",
                    extra_text=(
                        "\n\nMessage: not found\n\n"
                        'Data:\n{\n  "message": "not found"\n}'
                    ),
                ),
            ]
        )
        self.assertEqual(404, e.exception.status_code)
        self.assertEqual("not found", e.exception.message)
        self.assertEqual({"message": "not found"}, e.exception.data)
        mock_gather_metadata.assert_not_called()
        mock_update_docdb.assert_not_called()
        mock_build_data_asset_params.assert_not_called()
        mock_update_permissions.assert_not_called()

    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._send_alert_to_teams"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._get_input_data_name"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._build_data_asset_params"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._wait_for_data_asset"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._monitor_pipeline"
    )
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob"
        "._gather_metadata"
    )
    @patch("codeocean.data_asset.DataAssets.create_data_asset")
    @patch("codeocean.computation.Computations.run_capsule")
    @patch("codeocean.data_asset.DataAssets.update_permissions")
    @patch(
        "aind_codeocean_pipeline_monitor.job.PipelineMonitorJob._update_docdb"
    )
    @patch("aind_codeocean_pipeline_monitor.job.datetime")
    def test_run_job_with_alerts_error(
        self,
        mock_datetime: MagicMock,
        mock_update_docdb: MagicMock,
        mock_update_permissions: MagicMock,
        mock_run_capsule: MagicMock,
        mock_create_data_asset: MagicMock,
        mock_gather_metadata: MagicMock,
        mock_monitor_pipeline: MagicMock,
        mock_wait_for_data_asset: MagicMock,
        mock_build_data_asset_params: MagicMock,
        mock_get_input_data_name: MagicMock,
        mock_send_alert: MagicMock,
    ):
        """Tests steps are called in run_job method when an error is raised."""
        mock_get_input_data_name.return_value = (
            "ecephys_123456_2020-10-10_00-00-00"
        )
        mock_datetime.now.return_value = datetime(2020, 11, 10)
        mock_run_capsule.return_value = Computation(
            id="c123",
            created=0,
            name="c_name",
            state=ComputationState.Initializing,
            run_time=0,
        )
        mock_monitor_pipeline.side_effect = Exception("Something went wrong.")

        expected_name = (
            "ecephys_123456_2020-10-10_00-00-00_processed_2020-11-10_00-00-00"
        )
        mock_create_data_asset.return_value = DataAsset(
            id="def-123",
            created=1,
            name=expected_name,
            mount=expected_name,
            state=DataAssetState.Draft,
            type=DataAssetType.Result,
            last_used=1,
            tags=["derived"],
        )
        mock_wait_for_data_asset.return_value = DataAsset(
            id="def-123",
            created=1,
            name=expected_name,
            mount=expected_name,
            state=DataAssetState.Ready,
            type=DataAssetType.Result,
            last_used=1,
            tags=["derived"],
        )

        with self.assertLogs(level="INFO") as captured:
            with self.assertRaises(Exception) as e:
                self.capture_job_with_alert.run_job()

        self.assertEqual(2, len(captured.output))
        mock_send_alert.assert_has_calls(
            [
                call(
                    message="Starting ecephys_123456_2020-10-10_00-00-00",
                    extra_text="- pipeline: abc-123\n- version: 1\n",
                ),
                call(
                    message="Error with ecephys_123456_2020-10-10_00-00-00",
                    extra_text="Message: ('Something went wrong.',)",
                ),
            ]
        )
        self.assertEqual(("Something went wrong.",), e.exception.args)
        mock_gather_metadata.assert_not_called()
        mock_update_docdb.assert_not_called()
        mock_build_data_asset_params.assert_not_called()
        mock_update_permissions.assert_not_called()


if __name__ == "__main__":
    unittest.main()
