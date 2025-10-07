"""
TPT (Teradata Parallel Transporter) operators for Dagster.

This module provides operators for executing DDL statements and TPT load operations
on Teradata databases. It supports both local and remote execution via SSH.
"""

import subprocess
from typing import Optional, cast

import paramiko
from dagster import DagsterError

from dagster_teradata.ttu.utils.tpt_util import (
    prepare_tpt_ddl_script,
    get_remote_temp_directory,
    prepare_tdload_job_var_file,
    is_valid_remote_job_var_file,
    is_valid_file,
    read_file,
)

from dagster_teradata.ttu.tpt_executer import (
    execute_ddl,
    _execute_tdload_via_ssh,
    _execute_tdload_locally,
    execute_tdload,
)

from dagster_teradata.ttu.utils.encryption_utils import (
    SecureCredentialManager,
    get_stored_credentials,
)

from paramiko.client import SSHClient


class DdlOperator:
    """Operator for executing DDL statements on Teradata using TPT."""

    def __init__(self, connection, teradata_connection_resource, log):
        """
        Initialize the DDL Operator.

        Args:
            connection: Database connection object
            teradata_connection_resource: Teradata connection resource configuration
            log: Logger instance for logging operations
        """
        # DDL operation parameters
        self.ddl = None
        self.error_list = None
        self.remote_working_dir = None
        self.ddl_job_name = None

        # Connection and logging
        self.connection = connection
        self.log = log
        self.teradata_connection_resource = teradata_connection_resource

        # SSH and credential management
        self.cred_manager = SecureCredentialManager()
        self.ssh_client = None
        self.remote_host = None
        self.remote_user = None
        self.remote_remote_password = None
        self.ssh_key_path = None
        self.remote_port = None

    def _setup_ssh_connection(
        self,
        host: str,
        user: Optional[str],
        password: Optional[str],
        key_path: Optional[str],
        port: int,
    ) -> bool:
        """
        Establish SSH connection using either password or key authentication.

        Args:
            host: Remote hostname
            user: Remote username
            password: Remote password (optional if key_path provided)
            key_path: Path to SSH private key (optional if password provided)
            port: SSH port

        Returns:
            bool: True if connection succeeded, False otherwise

        Raises:
            DagsterError: If connection fails

        Note:
            - Tries stored credentials if no password provided
            - Prompts for password if no credentials available
            - Stores new credentials if successfully authenticated
        """
        try:
            # Initialize SSH client with auto-add policy for host keys
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Authenticate using SSH key if provided
            if key_path:
                key = paramiko.RSAKey.from_private_key_file(key_path)
                self.ssh_client.connect(host, port=port, username=user, pkey=key)
            else:
                # If no password provided, try to retrieve stored credentials
                if not password:
                    if user is None:
                        raise ValueError(
                            "Username is required to fetch stored credentials"
                        )
                    # Attempt to retrieve stored credentials
                    creds = get_stored_credentials(self, host, user)
                    password = (
                        self.cred_manager.decrypt(creds["password"]) if creds else None
                    )

                # Connect using username and password
                self.ssh_client.connect(
                    host, port=port, username=user, password=password
                )

            self.log.info(f"SSH connected to {user}@{host}")
            return True
        except Exception as e:
            raise DagsterError(f"SSH connection failed: {e}")

    def ddl_operator(
        self,
        ddl: list[str] = None,
        error_list: Optional[str] = None,
        remote_working_dir: str = "/tmp",
        ddl_job_name: Optional[str] = None,
        remote_host: Optional[str] = None,
        remote_user: Optional[str] = None,
        remote_password: Optional[str] = None,
        ssh_key_path: Optional[str] = None,
        remote_port: int = 22,
    ) -> int | None:
        """Execute DDL operations on Teradata."""
        # Set instance variables from parameters
        self.ddl = ddl
        self.error_list = error_list
        self.remote_working_dir = remote_working_dir
        self.ddl_job_name = ddl_job_name
        self.remote_host = remote_host
        self.remote_user = remote_user
        self.remote_remote_password = remote_password
        self.ssh_key_path = ssh_key_path
        self.remote_port = remote_port

        # Validate DDL input
        if (
            not self.ddl
            or not isinstance(self.ddl, list)
            or not all(isinstance(stmt, str) and stmt.strip() for stmt in self.ddl)
        ):
            raise ValueError("DDL must be  non-empty list of valid SQL statements.")

        # Normalize error list to standard format
        normalized_error_list = self._normalize_error_list(self.error_list)

        try:
            # Prepare TPT DDL script with provided parameters
            tpt_ddl_script = prepare_tpt_ddl_script(
                sql=self.ddl,
                error_list=normalized_error_list,
                teradata_connection_resource=self.teradata_connection_resource,
                job_name=self.ddl_job_name,
            )

            # Set up SSH connection if remote host is specified
            if self.remote_host:
                if not self._setup_ssh_connection(
                    host=self.remote_host,
                    user=cast(str, self.remote_user),
                    password=self.remote_remote_password,
                    key_path=self.ssh_key_path,
                    port=self.remote_port,
                ):
                    raise DagsterError(
                        "Failed to establish SSH connection. Please check the provided credentials."
                    )

            # Determine remote working directory if not specified
            if self.ssh_client and not self.remote_working_dir:
                self.remote_working_dir = get_remote_temp_directory(
                    self.ssh_client, self.log
                )

            # Default to /tmp if no working directory specified
            if not self.remote_working_dir:
                self.remote_working_dir = "/tmp"

            # Execute the DDL operation
            return execute_ddl(self, tpt_ddl_script, self.remote_working_dir)
        except Exception as e:
            self.log.error("DDL execution failed: %s", str(e))
            raise

    def _normalize_error_list(self, error_list: int | list[int] | None) -> list[int]:
        """
        Convert error_list to standardized list format.

        Args:
            error_list: Error code(s) to ignore during DDL execution

        Returns:
            list[int]: Normalized list of error codes

        Raises:
            ValueError: If error_list is not an int or list of ints
        """
        if error_list is None:
            return []
        if isinstance(error_list, int):
            return [error_list]
        if isinstance(error_list, list) and all(
            isinstance(err, int) for err in error_list
        ):
            return error_list
        raise ValueError("error_list must be an int or list of ints")

    def on_kill(self):
        """Terminate any running subprocesses gracefully."""
        conn = self.connection
        process = conn.get("sp")
        if process:
            try:
                # Try to terminate process gracefully
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if process doesn't terminate in time
                self.log.warning("Forcing subprocess kill...")
                process.kill()
            except Exception as e:
                self.log.error("Process termination failed: %s", str(e))


class TdLoadOperator:
    """Operator for Teradata Parallel Transporter (TPT) operations."""

    def __init__(
        self,
        connection,
        teradata_connection_resource,
        target_teradata_connection_resource,
        log,
    ) -> None:
        """
        Initialize the TPT Load Operator.

        Args:
            connection: Database connection object
            teradata_connection_resource: Source Teradata connection configuration
            target_teradata_connection_resource: Target Teradata connection configuration
            log: Logger instance for logging operations
        """
        # Connection configurations
        self.teradata_connection_resource = teradata_connection_resource
        self.target_teradata_connection_resource = target_teradata_connection_resource
        self.log = log

        # TPT operation parameters
        self.source_table = None
        self.select_stmt = None
        self.insert_stmt = None
        self.target_table = None
        self.source_file_name = None
        self.target_file_name = None
        self.source_format = None
        self.source_text_delimiter = None
        self.target_format = None
        self.target_text_delimiter = None
        self.tdload_options = None
        self.tdload_job_name = None
        self.tdload_job_var_file = None
        self.remote_working_dir = None

        # SSH and credential management
        self.cred_manager = SecureCredentialManager()
        self.ssh_client = None
        self.remote_host = None
        self.remote_user = None
        self.remote_remote_password = None
        self.ssh_key_path = None
        self.remote_port = None

    def _setup_ssh_connection(
        self,
        host: str,
        user: Optional[str],
        password: Optional[str],
        key_path: Optional[str],
        port: int,
    ) -> bool:
        """
        Establish SSH connection using either password or key authentication.

        Args:
            host: Remote hostname
            user: Remote username
            password: Remote password (optional if key_path provided)
            key_path: Path to SSH private key (optional if password provided)
            port: SSH port

        Returns:
            bool: True if connection succeeded, False otherwise

        Raises:
            DagsterError: If connection fails

        Note:
            - Tries stored credentials if no password provided
            - Prompts for password if no credentials available
            - Stores new credentials if successfully authenticated
        """
        try:
            # Initialize SSH client with auto-add policy for host keys
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Authenticate using SSH key if provided
            if key_path:
                key = paramiko.RSAKey.from_private_key_file(key_path)
                self.ssh_client.connect(host, port=port, username=user, pkey=key)
            else:
                # If no password provided, try to retrieve stored credentials
                if not password:
                    if user is None:
                        raise ValueError(
                            "Username is required to fetch stored credentials"
                        )
                    # Attempt to retrieve stored credentials
                    creds = get_stored_credentials(self, host, user)
                    password = (
                        self.cred_manager.decrypt(creds["password"]) if creds else None
                    )

                # Connect using username and password
                self.ssh_client.connect(
                    host, port=port, username=user, password=password
                )

            self.log.info(f"SSH connected to {user}@{host}")
            return True
        except Exception as e:
            raise DagsterError(f"SSH connection failed: {e}")

    def tdload_operator(
        self,
        source_table: Optional[str] = None,
        select_stmt: Optional[str] = None,
        insert_stmt: Optional[str] = None,
        target_table: Optional[str] = None,
        source_file_name: Optional[str] = None,
        target_file_name: Optional[str] = None,
        source_format: Optional[str] = None,
        source_text_delimiter: Optional[str] = None,
        target_format: Optional[str] = None,
        target_text_delimiter: Optional[str] = None,
        tdload_options: Optional[str] = None,
        tdload_job_name: Optional[str] = None,
        tdload_job_var_file: Optional[str] = None,
        remote_working_dir: Optional[str] = None,
        remote_host: Optional[str] = None,
        remote_user: Optional[str] = None,
        remote_password: Optional[str] = None,
        ssh_key_path: Optional[str] = None,
        remote_port: int = 22,
    ) -> int | None:
        """Execute TPT load operation based on configuration."""
        # Set instance variables from parameters
        self.source_table = source_table
        self.select_stmt = select_stmt
        self.insert_stmt = insert_stmt
        self.target_table = target_table
        self.source_file_name = source_file_name
        self.target_file_name = target_file_name
        self.source_format = source_format or "Delimited"
        self.source_text_delimiter = source_text_delimiter or ","
        self.target_format = target_format or "Delimited"
        self.target_text_delimiter = target_text_delimiter or ","
        self.tdload_options = tdload_options
        self.tdload_job_name = tdload_job_name
        self.tdload_job_var_file = tdload_job_var_file
        self.remote_working_dir = remote_working_dir
        self.remote_host = remote_host
        self.remote_user = remote_user
        self.remote_remote_password = remote_password
        self.ssh_key_path = ssh_key_path
        self.remote_port = remote_port

        # Validate parameters and determine operation mode
        mode = self._validate_and_determine_mode()

        try:
            tdload_job_var_content = None
            tdload_job_var_file = self.tdload_job_var_file

            # Prepare job variable content if no file provided
            if not tdload_job_var_file:
                tdload_job_var_content = self._prepare_job_var_content(mode)
                self.log.info("Prepared job vars for mode '%s'", mode)

            # Set up SSH connection if remote host specified
            if self.remote_host:
                if not self._setup_ssh_connection(
                    host=self.remote_host,
                    user=cast(str, self.remote_user),
                    password=self.remote_remote_password,
                    key_path=self.ssh_key_path,
                    port=self.remote_port,
                ):
                    raise DagsterError(
                        "Failed to establish SSH connection. Please check the provided credentials."
                    )

            # Determine remote working directory if not specified
            if self.remote_host and not self.remote_working_dir:
                self.remote_working_dir = get_remote_temp_directory(
                    self.ssh_client, self.log
                )
            if not self.remote_working_dir:
                self.remote_working_dir = "/tmp"

            # Execute TPT operation based on configuration
            return self._execute_based_on_configuration(
                tdload_job_var_file, tdload_job_var_content
            )
        except Exception as e:
            self.log.error("TPT operation failed in mode '%s': %s", mode, str(e))
            raise

    def _validate_and_determine_mode(self) -> str:
        """
        Validate parameters and determine operation mode.

        Returns:
            str: Operation mode (file_to_table, table_to_file, table_to_table, job_var_file)

        Raises:
            ValueError: If parameter combination is invalid
        """
        # Validate mutually exclusive parameters
        if self.source_table and self.select_stmt:
            raise ValueError("Cannot specify both source_table and select_stmt")

        if self.insert_stmt and not self.target_table:
            raise ValueError("insert_stmt requires target_table")

        # Determine operation mode based on parameter combination
        if self.source_file_name and self.target_table:
            mode = "file_to_table"
            # Use source connection as target if not specified
            if self.target_teradata_connection_resource is None:
                self.target_teradata_connection_resource = (
                    self.teradata_connection_resource
                )
        elif (self.source_table or self.select_stmt) and self.target_file_name:
            mode = "table_to_file"
        elif (self.source_table or self.select_stmt) and self.target_table:
            mode = "table_to_table"
            # Target connection is required for table transfers
            if self.target_teradata_connection_resource is None:
                raise ValueError("Target connection required for table transfers")
        else:
            # If no specific mode detected, use job variable file mode
            if not self.tdload_job_var_file:
                raise ValueError("Invalid parameter combination for TPT operation")
            mode = "job_var_file"

        return mode

    def _prepare_job_var_content(self, mode: str) -> str:
        """
        Generate job variable file content for the specified mode.

        Args:
            mode: Operation mode (file_to_table, table_to_file, table_to_table)

        Returns:
            str: Job variable file content
        """
        return prepare_tdload_job_var_file(
            mode=mode,
            source_table=self.source_table,
            select_stmt=self.select_stmt,
            insert_stmt=self.insert_stmt,
            target_table=self.target_table,
            source_file_name=self.source_file_name,
            target_file_name=self.target_file_name,
            source_format=self.source_format,
            target_format=self.target_format,
            source_text_delimiter=self.source_text_delimiter,
            target_text_delimiter=self.target_text_delimiter,
            source_conn=self.teradata_connection_resource,
            target_conn=self.target_teradata_connection_resource,
        )

    def _execute_based_on_configuration(
        self,
        tdload_job_var_file: str | None,
        tdload_job_var_content: str | None,
    ) -> int | None:
        """
        Execute TPT operation based on configuration.

        Args:
            tdload_job_var_file: Path to job variable file (optional)
            tdload_job_var_content: Job variable content (optional)

        Returns:
            int | None: Exit code of the TPT operation

        Raises:
            ValueError: If configuration is invalid
        """
        # Remote execution path
        if self.remote_host:
            if tdload_job_var_file:
                # Use existing remote job variable file
                if self.ssh_client:
                    if is_valid_remote_job_var_file(
                        self.ssh_client, tdload_job_var_file, self.log
                    ):
                        return self._handle_remote_job_var_file(
                            ssh_client=self.ssh_client, file_path=tdload_job_var_file
                        )
                    raise ValueError("Invalid remote job var file path")
            else:
                # Execute with generated job variable content
                return execute_tdload(
                    self,
                    log=self.log,
                    ssh_client=self.ssh_client,
                    remote_working_dir=self.remote_working_dir or "/tmp",
                    job_var_content=tdload_job_var_content,
                    tdload_options=self.tdload_options,
                    tdload_job_name=self.tdload_job_name,
                )
        else:
            # Local execution path
            if tdload_job_var_file:
                # Use existing local job variable file
                if is_valid_file(tdload_job_var_file):
                    return self._handle_local_job_var_file(
                        file_path=tdload_job_var_file
                    )
                raise ValueError("Invalid local job var file path")
            else:
                # Execute with generated job variable content
                return execute_tdload(
                    self,
                    log=self.log,
                    remote_working_dir=self.remote_working_dir or "/tmp",
                    job_var_content=tdload_job_var_content,
                    tdload_options=self.tdload_options,
                    tdload_job_name=self.tdload_job_name,
                )

    def _handle_remote_job_var_file(
        self, ssh_client: SSHClient, file_path: str | None
    ) -> int | None:
        """
        Execute TPT using remote job variable file.

        Args:
            ssh_client: Connected SSH client instance
            file_path: Path to remote job variable file

        Returns:
            int | None: Exit code of the TPT operation

        Raises:
            ValueError: If file path is invalid or execution fails
        """
        if not file_path:
            raise ValueError("Remote job var file path required")

        try:
            # Open SFTP connection to read remote file
            sftp = ssh_client.open_sftp()
            try:
                with sftp.open(file_path, "r") as remote_file:
                    tdload_job_var_content = remote_file.read().decode("UTF-8")
            finally:
                sftp.close()

            # Execute TPT operation remotely
            if self.remote_host:
                return _execute_tdload_via_ssh(
                    self.remote_working_dir or "/tmp",
                    tdload_job_var_content,
                    self.tdload_options,
                    self.tdload_job_name,
                )
            raise ValueError("Remote execution not configured")
        except Exception as e:
            self.log.error("Remote job var file handling failed: %s", str(e))
            raise

    def _handle_local_job_var_file(
        self,
        file_path: str | None,
    ) -> int | None:
        """
        Execute TPT using local job variable file.

        Args:
            file_path: Path to local job variable file

        Returns:
            int | None: Exit code of the TPT operation

        Raises:
            ValueError: If file path is invalid or execution fails
        """
        if not file_path:
            raise ValueError("Local job var file path required")

        if not is_valid_file(file_path):
            raise ValueError("Invalid local job var file")

        try:
            # Read local job variable file
            tdload_job_var_content = read_file(file_path, encoding="UTF-8")

            # Execute TPT operation locally
            if self.remote_host:
                return _execute_tdload_locally(
                    tdload_job_var_content,
                    self.tdload_options,
                    self.tdload_job_name,
                )
            raise ValueError("Local execution not configured")
        except Exception as e:
            self.log.error("Local job var file handling failed: %s", str(e))
            raise

    def on_kill(self):
        """Terminate any running subprocesses gracefully."""
        conn = self.connection
        process = conn.get("sp")
        if process:
            try:
                # Try to terminate process gracefully
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if process doesn't terminate in time
                self.log.warning("Forcing subprocess kill...")
                process.kill()
            except Exception as e:
                self.log.error("Process termination failed: %s", str(e))
