import glob
import logging
import os
import shutil
from tempfile import TemporaryDirectory, gettempdir
from typing import Optional
import zipfile
import tarfile

from spyt.dependency_utils import require_yt_client
require_yt_client()

from yt.wrapper.common import is_arcadia_python  # noqa: E402


logger = logging.getLogger(__name__)

extracted_spyt_dir: Optional[TemporaryDirectory] = None
extracted_spark_dir: Optional[TemporaryDirectory] = None

spark_distrib_dir = "yt/spark/spark-over-yt/spyt-package/src/main/spark/"


def _make_executables(directory):
    logger.debug(f"Making executables files in {directory}")
    for name in os.listdir(directory):
        os.chmod(os.path.join(directory, name), 0o755)


def _extract_resources(resource_key_prefix: str, remove_prefix: str, destination_dir: str):
    from library.python import resource
    if len(remove_prefix) > 0 and remove_prefix[-1] != '/':
        logger.warn("Last symbol in remove_prefix is not '/', you may try unpack to machine's root")
    logger.debug(f"Finding resource files with prefix {resource_key_prefix}")
    resource_paths = resource.resfs_files(resource_key_prefix)
    logger.debug(f"Found {len(resource_paths)} files. Extracting...")
    extracted_files = []
    for resource_path in resource_paths:
        assert resource_path.startswith(remove_prefix)
        relative_resource_path = resource_path[len(remove_prefix):]
        destination_path = os.path.join(destination_dir, relative_resource_path)
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        with open(destination_path, 'bw') as out:
            out.write(resource.resfs_read(resource_path))
        extracted_files.append(destination_path)
    return extracted_files


def _spark_tar_members(tar_file, ):
    for member in tar_file.getmembers():
        slash_pos = member.path.find('/')
        if slash_pos > 0:
            member.path = member.path[slash_pos + 1:]
            yield member


# Return true if a PID found and  a process is alive
def _check_pid_in_dir(dir: str) -> bool:
    pid_file = os.path.join(dir, '.pid')
    if not os.path.exists(pid_file):
        return False
    try:
        with open(pid_file, 'r') as f:
            pid = int(f.read())
        os.kill(pid, 0)  # 0 - check signal. If it didn't fail (OSError) then the process is alive
        return True
    except Exception:
        return False


def _create_tmpdir_with_pid(prefix: str):
    temp_dir = TemporaryDirectory(prefix=prefix, ignore_cleanup_errors=True)
    with open(os.path.join(temp_dir.name, '.pid'), 'w') as f:
        f.write(str(os.getpid()))
    return temp_dir


def _extract_spark():
    temp_dir = _create_tmpdir_with_pid("spark_yamake_")
    logger.info(f"Created Spark temp dir {temp_dir}")
    files = _extract_resources(spark_distrib_dir, spark_distrib_dir, temp_dir.name)
    with tarfile.open(files[0], 'r:gz') as tar_file:
        tar_file.extractall(temp_dir.name, members=_spark_tar_members(tar_file), filter='tar')
    logger.info("Spark files extracted successfully")
    return temp_dir


def _extract_spyt():
    temp_dir = _create_tmpdir_with_pid("spyt_yamake_")
    logger.info(f"Created Spyt temp dir {temp_dir}")
    spyt_original_dir = "yt/spark/spark-over-yt/spyt-package/src/main/spyt_cluster/"
    build_dir = temp_dir.name
    files = _extract_resources(spyt_original_dir, spyt_original_dir, build_dir)
    with zipfile.ZipFile(files[0], 'r') as zip_ref:
        zip_ref.extractall(build_dir)
    package_dir = build_dir + "/spyt-package"
    for file_name in os.listdir(package_dir):
        os.rename(package_dir + "/" + file_name, build_dir + "/" + file_name)
    logger.info("Spyt files extracted successfully")
    return temp_dir


def checked_extract_spyt() -> Optional[str]:
    if not is_arcadia_python():
        return None

    global extracted_spyt_dir
    logger.debug("Arcadia python found")
    if not extracted_spyt_dir:
        extracted_spyt_dir = _extract_spyt()
    logger.debug(f"Current extracted Spyt location {extracted_spyt_dir}")
    return extracted_spyt_dir.name


def checked_extract_spark() -> Optional[str]:
    if not is_arcadia_python():
        return None

    global extracted_spark_dir
    logger.debug("Arcadia python found")
    if not extracted_spark_dir:
        extracted_spark_dir = _extract_spark()
        os.environ["SPARK_HOME"] = extracted_spark_dir.name
    logger.debug(f"Current extracted Spark location {extracted_spark_dir}")
    return extracted_spark_dir.name


def _remove_from_tempdir(prefix: str, only_dead: bool):
    tempdir = gettempdir()
    for old_tempdir in glob.glob(os.path.join(tempdir, prefix + "*")):
        if not only_dead or not _check_pid_in_dir(old_tempdir):
            logger.info(f"Removing temp dir {old_tempdir}")
            shutil.rmtree(old_tempdir)


def clean_extracted():
    global extracted_spark_dir, extracted_spyt_dir
    if extracted_spark_dir:
        extracted_spark_dir.cleanup()
        extracted_spark_dir = None
    if extracted_spyt_dir:
        extracted_spyt_dir.cleanup()
        extracted_spyt_dir = None


def remove_all_temp_files(only_dead=True):
    _remove_from_tempdir("spark_yamake_", only_dead)
    _remove_from_tempdir("spyt_yamake_", only_dead)
