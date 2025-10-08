import io
import json
import logging
import sys
import uuid
from decimal import Decimal
from enum import Enum
from pathlib import Path
from typing import Optional

import msal
import pandas as pd
import requests

from .exceptions import (
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    DataverseAPIError,
    EntityError,
)


class DecimalEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle Decimal objects"""

    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


logger = logging.getLogger(__name__)


# For user config directory
def user_config_dir(app_name: str, company: str) -> Path:
    # Config paths (cross-platform)
    if sys.platform.startswith("win"):
        # Windows: Use AppData/Local
        app_config_dir = Path.home() / "AppData/Local" / company / app_name
    else:
        # Linux/Unix: Use XDG config directory
        app_config_dir = Path.home() / ".config" / company / app_name
    return app_config_dir


class SingletonMeta(type):
    """Metaclass for creating a Singleton."""

    _instances: dict = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class DataverseClient(metaclass=SingletonMeta):
    def __init__(self, config_path=None, *args):
        if hasattr(self, "_initialized"):
            return  # Prevent reinitialization

        self.connected = False
        self.session = requests.Session()
        self.environment_uri: str = ""
        self.app = None  # Store MSAL application instance
        self.token_cache = None  # Store the token cache
        self.account = None  # Store the logged-in account
        self.config_path = config_path

        if "xml" in args:
            self.filetype = "xml"
        else:
            self.filetype = "json"

        # Stored values for this session
        self._table_metadata = {}
        self._global_choices = {}
        self._guid_mapping = {}
        self._table_definitions = {}
        self._relationships = {}

    # === CONNECTION, AUTHENTICATION, TEST
    def get_authenticated_session(self, config_json: Optional[str | Path] = None):
        if config_json is None and self.config_path is None:
            raise ConfigurationError(
                "No configuration file provided. Please specify config_json or set config_path during initialization."
            )

        config_file = config_json or self.config_path
        logger.info(f"Loading config from: {config_file}")
        config = json.load(open(config_file))
        logger.info("Config loaded successfully")

        authority = config["authorityBase"] + config["tenantID"]
        self.environment_uri = config["environmentURI"]
        scope = [self.environment_uri + config["scopeSuffix"]]

        logger.info("Getting token cache...")
        self.token_cache, cache_file = self.get_token_cache()
        logger.info(f"Token cache initialized, cache file: {cache_file}")
        self.app = msal.PublicClientApplication(
            config["clientID"], authority=authority, token_cache=self.token_cache
        )
        logger.info("MSAL application created")
        logger.info("Attempting silent authentication...")

        accounts = self.app.get_accounts()
        logger.info(f"Found {len(accounts)} cached accounts")
        if accounts:
            self.account = accounts[0]
            logger.info("Acquiring token silently")
            result = self.app.acquire_token_silent(scopes=scope, account=self.account)
            logger.info(
                f"Silent token result: {result.keys() if isinstance(result, dict) else type(result)}"
            )
        else:
            logger.info("A local browser window will open for you to sign in. CTRL+C to cancel.")
            result = self.app.acquire_token_interactive(scope)
            logger.info(
                f"Interactive token result: {result.keys() if isinstance(result, dict) else type(result)}"
            )

        if "access_token" in result:
            logger.info("Token received successfully")
            self.session.headers.update(
                {
                    "Authorization": f"Bearer {result['access_token']}",
                    "OData-MaxVersion": "4.0",
                    "OData-Version": "4.0",
                    "If-None-Match": "null",
                    "Prefer": 'odata.include-annotations="*"',
                    "Accept": f"application/{self.filetype}",
                }
            )
            with open(cache_file, "w") as f:
                f.write(self.token_cache.serialize())

            self.connected = True
        else:
            error_msg = f"Authentication failed: {result.get('error', 'Unknown error')}"
            logger.error(error_msg)
            logger.error(f"Description: {result.get('error_description', 'No description')}")
            raise AuthenticationError(error_msg)

    @staticmethod
    def get_token_cache():
        """Returns a persistent token cache stored in the user's config directory."""
        # Create app-specific config directory
        app_config_dir = user_config_dir("SurfDataverse", "ionysis")
        app_config_dir.mkdir(parents=True, exist_ok=True)

        # Token cache file path
        cache_file = app_config_dir / "token_cache.bin"
        cache = msal.SerializableTokenCache()

        if cache_file.exists():
            logger.info(f"Found existing cache file: {cache_file}")
            try:
                with open(cache_file, "r") as f:
                    cache_content = f.read()
                    logger.info(f"Cache file size: {len(cache_content)} bytes")
                    if not cache_content.strip():
                        logger.warning("Cache file is empty, removing it")
                        cache_file.unlink()
                    else:
                        cache.deserialize(cache_content)
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Corrupted cache file detected: {e}. Removing and starting fresh.")
                cache_file.unlink()
            except Exception as e:
                logger.warning(f"Error reading cache file: {e}. Removing and starting fresh.")
                cache_file.unlink()

        logger.info(f"Using token cache: {cache_file}")

        return cache, cache_file

    def test_connection(self):
        request_uri = f"{self.environment_uri}api/data/v9.2/"
        try:
            response = self.session.get(request_uri)

            if response.status_code != 200:
                error_msg = f"Connection test failed with status {response.status_code}"
                logger.error(error_msg)
                raise ConnectionError(f"{error_msg}: {response.text}")
            else:
                logger.info("Connection successful")
                return response.json()
        except requests.RequestException as e:
            raise ConnectionError(f"Network error during connection test: {str(e)}")

    # === RELATIONSHIPS
    @property
    def relationships(self):
        if not self._relationships:
            request_uri = f"{self.environment_uri}api/data/v9.2/RelationshipDefinitions"
            response = self.session.get(request_uri)
            if response.status_code == 200:
                self._relationships = response.json()
            else:
                logger.error(f"Error fetching relationships: {response.text}")
                raise DataverseAPIError(
                    f"Failed to fetch relationships: {response.text}",
                    response.status_code,
                    response.text,
                )
        return self._relationships

    # === FLOWS
    def get_flows(self):
        request_uri = f"{self.environment_uri}api/data/v9.2/workflows"
        response = self.session.get(request_uri)
        if response.status_code == 401:
            raise AuthenticationError("Unauthorized. Check your credentials and permissions.")
        elif response.status_code != 200:
            raise DataverseAPIError(
                f"Failed to get flows: {response.text}", response.status_code, response.text
            )
        return response.json()

    # === GLOBAL CHOICES
    @property
    def global_choices(self):
        """Fetch all global choices (option sets) from Dataverse"""
        if not self._global_choices:
            request_uri = f"{self.environment_uri}api/data/v9.2/GlobalOptionSetDefinitions"
            response = self.session.get(request_uri)

            if response.status_code == 200:
                choices_data = response.json().get("value", [])
                global_choices = {}

                for choice in choices_data:
                    name = choice["Name"]
                    options = {
                        opt["Label"]["UserLocalizedLabel"]["Label"]: opt["Value"]
                        for opt in choice.get("Options", [])
                    }
                    global_choices[name] = options

                self._global_choices = global_choices

            else:
                logger.error(f"Failed to retrieve choices: {response.text}")
                raise DataverseAPIError(
                    f"Failed to retrieve global choices: {response.text}",
                    response.status_code,
                    response.text,
                )

        return self._global_choices

    # === TABLES
    def get_table_definitions(self):
        if not self._table_definitions:
            request_uri = f"{self.environment_uri}api/data/v9.2/EntityDefinitions"
            response = self.session.get(request_uri)
            if response.status_code == 200:
                self._table_definitions = response.json()
            else:
                logger.error(f"Error fetching table definitions: {response.text}")
                raise DataverseAPIError(
                    f"Failed to fetch table definitions: {response.text}",
                    response.status_code,
                    response.text,
                )
        return self._table_definitions

    def get_table_metadata_raw(self, table_logical_name):
        """Fetch column metadata for a specific Dataverse table"""
        request_uri = f"{self.environment_uri}api/data/v9.2/EntityDefinitions(LogicalName='{table_logical_name}')?$expand=Attributes"
        response = self.session.get(request_uri)

        if response.status_code == 200:
            return response.json()  # Full metadata response
        else:
            error_msg = f"Failed to retrieve metadata for {table_logical_name}: {response.text}"
            logger.error(error_msg)
            raise DataverseAPIError(error_msg, response.status_code, response.text)

    def get_table_metadata(self, table_logical_name):
        """Finds fields that users can set in create/update operations"""
        if table_logical_name not in self._table_metadata:
            raw_metadata = self.get_table_metadata_raw(table_logical_name)
            if not raw_metadata:
                return {}

            metadata = {}
            for attribute in raw_metadata.get("Attributes", []):
                logical_name_column = attribute["LogicalName"]
                store_attributes = [
                    "DefaultValue",
                    "SourceType",
                    "IsValidForCreate",
                    "IsValidForUpdate",
                    "IsValidForRead",
                    "IsManaged",
                    "AttributeType",
                    "SchemaName",
                    "TargetEntity",
                ]
                metadata[logical_name_column] = {}
                for key in store_attributes:
                    metadata[logical_name_column][key] = attribute.get(key, None)

            self._table_metadata[table_logical_name] = metadata

        return self._table_metadata[table_logical_name]

    def get_table_data(
        self, logical_name=None, entity_set_name=None, polars=False
    ) -> pd.DataFrame | None:
        """Fetches actual data from a given table (by LogicalName)
        Args:
            logical_name: The logical name of the table
            entity_set_name: The entity set name (alternative to logical_name)
            polars: Return Polars DataFrame instead of pandas
        """

        def entity_to_df(entity_data):
            data_list = entity_data["value"]
            df = pd.DataFrame(data_list)
            return df

        def entity_to_polars(entity_data):
            import polars as pl

            data_list = entity_data["value"]
            df = pl.DataFrame(data_list)
            return df

        if entity_set_name:
            pass
        elif logical_name and not entity_set_name:
            entity_set_name = self.get_table_entity_set_name(logical_name=logical_name)
        else:
            logger.info("Please provide logical or entity set name")
            return None

        request_uri = f"{self.environment_uri}api/data/v9.2/{entity_set_name}"
        response = self.session.get(request_uri)

        if response.status_code == 200:
            return entity_to_polars(response.json()) if polars else entity_to_df(response.json())
        else:
            error_msg = f"Failed to retrieve data for {entity_set_name}: {response.text}"
            logger.error(error_msg)
            raise DataverseAPIError(error_msg, response.status_code, response.text)

    def download_tables_as_df(self, schema_filter=None):
        """Download all tables as DataFrames, optionally filtered by schema name

        Args:
            schema_filter: Optional string to filter tables by schema name (e.g., 'prefix')
        """
        tables = self.get_table_definitions()

        _table_definitions = {}
        _table_data = {}
        _table_metadata = {}
        # Add nodes for tables
        for table in tables["value"]:
            # Apply optional schema filter
            if schema_filter and schema_filter not in table["SchemaName"]:
                continue

            if table["DisplayName"]["UserLocalizedLabel"]:
                logical_name = table["LogicalName"]
                table_name = logical_name

                # Get selected definitions
                _table_definitions[table_name] = table

                # Get data
                _table_data[table_name] = self.get_table_data(logical_name=logical_name)
                if _table_data[table_name] is None:
                    return

                # Get metadata
                _table_metadata[table_name] = self.get_table_metadata(logical_name) or {}

        return _table_definitions, _table_data, _table_metadata

    def transform_dataframe_columns(self, df, logical_name):
        """Transform DataFrame to show user-friendly column names and values"""
        if df.empty:
            return df

        df_transformed = df.copy()
        metadata = self.get_table_metadata(logical_name)

        # Dictionary to store renamed columns
        column_renames = {}
        columns_to_drop = []

        for col in df.columns:
            # Skip system columns that start with @
            if col.startswith("@"):
                columns_to_drop.append(col)
                continue

            # Handle formatted display values (these are the readable versions)
            if "@OData.Community.Display.V1.FormattedValue" in col:
                base_col = col.replace("@OData.Community.Display.V1.FormattedValue", "")

                # For choice fields, use the formatted value and rename appropriately
                if base_col in metadata:
                    attr_type = metadata[base_col].get("AttributeType")
                    if attr_type in ["Picklist", "State", "Status"]:
                        # This is a choice field - use the formatted value
                        column_renames[col] = f"{base_col}_display"
                        # Mark the raw numeric column for dropping
                        if base_col in df.columns:
                            columns_to_drop.append(base_col)
                    elif attr_type in ["DateTime"]:
                        # Use formatted datetime
                        column_renames[col] = f"{base_col}_formatted"
                        # Keep both raw and formatted for dates
                continue

            # Handle lookup value columns (these show the GUID)
            if col.startswith("_") and col.endswith("_value"):
                # Check if we have the formatted display value
                formatted_col = f"{col}@OData.Community.Display.V1.FormattedValue"
                if formatted_col in df.columns:
                    # Use the formatted value instead and give it a clean name
                    base_name = col[1:-6]  # Remove leading _ and trailing _value
                    column_renames[formatted_col] = f"{base_name}_name"
                    columns_to_drop.append(col)  # Drop the GUID version

                    # Also drop the lookup metadata columns
                    lookup_meta_cols = [
                        f"{col}@Microsoft.Dynamics.CRM.lookuplogicalname",
                        f"{col}@Microsoft.Dynamics.CRM.associatednavigationproperty",
                    ]
                    for meta_col in lookup_meta_cols:
                        if meta_col in df.columns:
                            columns_to_drop.append(meta_col)
                continue

        # Apply column renames
        df_transformed = df_transformed.rename(columns=column_renames)

        # Drop unwanted columns
        columns_to_drop = [col for col in columns_to_drop if col in df_transformed.columns]
        df_transformed = df_transformed.drop(columns=columns_to_drop)

        return df_transformed

    # === RECORDS
    def get_record(self, entity_set_name, record_id):
        """Fetches a newly created record by ID to retrieve auto-generated fields."""
        request_uri = f"{self.environment_uri}api/data/v9.2/{entity_set_name}({record_id})"
        response = self.session.get(request_uri)

        if response.status_code == 200:
            return response.json()  # Return the full record with auto-filled values
        else:
            error_msg = f"Error fetching record: {response.text}"
            logger.error(error_msg)
            raise DataverseAPIError(error_msg, response.status_code, response.text)

    # === HELPER METHODS
    def get_guid_by_casual_name(self, table_name, data, name_column=None) -> uuid.UUID | None:
        """
        Map display names to GUIDs if row exists

        Args:
            table_name: logical_name of table
            data: data which holds the name to map to guid
            name_column: The column name to use for lookup (if not provided, will be inferred)

        Returns:

        """
        # If name_column not provided, try to infer it
        if not name_column:
            # Extract prefix from table name
            if "_" in table_name:
                prefix = table_name.split("_")[0] + "_"
                table_suffix = table_name.replace(prefix, "")

                if table_suffix == "recipe":
                    name_column = f"{prefix}namecasual"
                elif table_suffix == "article":
                    name_column = f"{prefix}name"
                elif table_suffix == "r2rsession":
                    name_column = f"{prefix}sessionid"
                else:
                    name_column = f"{prefix}name"  # Default fallback
            else:
                raise EntityError(
                    f"Cannot infer name column for {table_name}. Please provide name_column parameter."
                )

        guid_column = table_name + "id"

        name = data[name_column]

        entity_set_name = self.get_table_entity_set_name(logical_name=table_name)
        request_uri = f"{self.environment_uri}api/data/v9.2/{entity_set_name}?$select={name_column},{guid_column}"

        response = self.session.get(request_uri)

        if response.status_code == 200:
            records = response.json().get("value", [])
            mapping = {
                record[name_column]: record[guid_column]
                for record in records
                if name_column in record and guid_column in record
            }
            return mapping.get(name, None)
        else:
            error_msg = (
                f"Error fetching data from {table_name} for row existence check: {response.text}"
            )
            logger.error(error_msg)
            raise DataverseAPIError(error_msg, response.status_code, response.text)

    def name_to_guid(self, table_name, name=None, name_column=None) -> uuid.UUID | None:
        """
        Fetches a mapping of unique names to GUIDs in a Dataverse table

        Args:
            table_name: logical_name of table
            name: name to map to guid
            name_column: The column name to use for lookup (if not provided, will be inferred)

        Returns:

        """
        # If name_column not provided, try to infer it
        if not name_column:
            # Extract prefix from table name
            if "_" in table_name:
                prefix = table_name.split("_")[0] + "_"
                table_suffix = table_name.replace(prefix, "")

                if table_suffix in ["article", "batch"]:
                    name_column = table_name + "nr"
                elif table_suffix == "r2rsession":
                    name_column = f"{prefix}sessionid"
                else:
                    name_column = f"{prefix}name"  # Default fallback
            else:
                # For tables without prefix, assume standard naming
                name_column = table_name + "name"

        guid_column = table_name + "id"

        def update_mapping():
            entity_set_name = self.get_table_entity_set_name(logical_name=table_name)
            request_uri = f"{self.environment_uri}api/data/v9.2/{entity_set_name}?$select={name_column},{guid_column}"

            response = self.session.get(request_uri)

            if response.status_code == 200:
                records = response.json().get("value", [])
                mapping = {
                    record[name_column]: record[guid_column]
                    for record in records
                    if name_column in record and guid_column in record
                }
                self._guid_mapping[table_name] = mapping
            else:
                error_msg = (
                    f"Error fetching data from {table_name} for guid mapping: {response.text}"
                )
                logger.error(error_msg)
                raise DataverseAPIError(error_msg, response.status_code, response.text)

        if table_name not in self._guid_mapping:
            update_mapping()

        if name:
            guid = self._guid_mapping[table_name].get(name, None)
            if not guid:
                raise EntityError(f"{name} not found in {table_name}")
            else:
                return guid
        else:
            return None

    def get_table_of_guid(self, guid):
        return next(
            (
                key
                for key, value in self._guid_mapping.items()
                if guid in [guid for guid in value.values()]
            ),
            None,
        )

    def get_table_entity_set_name(self, schema_name=None, logical_name=None):
        tables = self.get_table_definitions()

        if schema_name:
            key = "SchemaName"
            name = schema_name
        elif logical_name:
            key = "LogicalName"
            name = logical_name
        else:
            raise ValueError("Please input schema or logical name")

        for entity in tables["value"]:
            if name == entity[key]:
                return entity["EntitySetName"]
        raise EntityError(f"{key} not found for {name}")


def is_valid_guid(value: str) -> bool:
    """Returns True if the value is a valid GUID, otherwise False."""
    try:
        uuid_obj = uuid.UUID(value)  # Ensure it's a valid UUID
        return str(uuid_obj) == value.lower()  # Ensure correct format
    except ValueError:
        return False


class DataverseTable:
    """Generic class for Dataverse entities"""

    def __init__(self, table_logical_name, table_prefix="prefix_"):
        """
        Args:
            table_logical_name: The pluralized name of the Dataverse table
            table_prefix: The prefix used for custom table/column names (default: "prefix_")
        """
        self.dataverse = DataverseClient()
        if isinstance(table_logical_name, Enum):
            table_logical_name = str(table_logical_name)
        self.logical_name = table_logical_name
        self.table_prefix = table_prefix
        self.table_name = table_logical_name.replace(self.table_prefix, "").title()
        self.col_metadata = self.dataverse.get_table_metadata(self.logical_name)
        # Filter global choices to only include those relevant to our prefix
        all_choices = self.dataverse.global_choices
        prefix_filter = self.table_prefix.rstrip("_")
        self.choices = {
            name: options for name, options in all_choices.items() if prefix_filter in name
        }
        self.relationships = self.get_relationships()

        self.guid = None
        self.data = {}  # Dictionary to store record fields

        # Auto-generate properties based on metadata
        self._generate_properties()

    def _generate_properties(self):
        """Automatically generates properties for all valid columns in the table"""
        logger.info(f"Generating properties for {self.logical_name}")
        for column_logical_name, metadata in self.col_metadata.items():
            # Skip system fields and non-user fields
            if not column_logical_name.startswith(self.table_prefix):
                continue

            # File and Virtual columns often have IsValidForCreate/Update = False, so allow them through
            field_type = metadata.get("AttributeType")
            if (
                field_type not in ["File", "Virtual"]
                and not metadata.get("IsValidForCreate")
                and not metadata.get("IsValidForUpdate")
            ):
                continue

            # Generate property name by removing prefix
            if column_logical_name.startswith(self.table_prefix):
                property_name = column_logical_name.replace(
                    self.table_prefix, "", 1
                )  # Remove prefix
            else:
                property_name = column_logical_name

            # Determine property type based on field metadata
            field_type = metadata.get("AttributeType")

            if field_type == "File" or (
                field_type == "Virtual" and "json" in column_logical_name.lower()
            ):
                # This is a file field or virtual file field - check this FIRST
                logger.info(f"Setting {property_name} as file property")
                setattr(self.__class__, property_name, self.file_property(column_logical_name))
            elif column_logical_name in self.relationships:
                # This is a lookup field
                logger.info(f"Setting {property_name} as lookup property")
                setattr(self.__class__, property_name, self.lookup_property(column_logical_name))
            elif column_logical_name in self.choices:
                # This is a choice field
                logger.info(f"Setting {property_name} as choice property")
                setattr(self.__class__, property_name, self.choice_property(column_logical_name))
            else:
                # This is a regular data field
                logger.info(f"Setting {property_name} as data property (fallback)")
                setattr(self.__class__, property_name, self.data_property(column_logical_name))

    # === Init values ===
    def get_relationships(self):
        """Fetches all possible lookups (relationships) for this entity."""
        result = self.dataverse.relationships

        _relationships = {}
        for rel in result.get("value", []):
            if rel.get("ReferencingEntity") == self.logical_name:
                # Store lookup column name -> related entity table
                if "ReferencingAttribute" in rel and "ReferencedEntity" in rel:
                    _relationships[rel["ReferencingAttribute"]] = rel["ReferencedEntity"]
        return _relationships

    # === FREE TEXT COLUMNS ===
    def set_data(self, column, value):
        """Adds a simple column value"""
        self.data[column] = value

    def get_data(self, column):
        value = self.data.get(column, "")

        # If value is empty but we have a GUID, try to fetch from Dataverse
        if not value and self.guid:
            try:
                entity_set_name = self.dataverse.get_table_entity_set_name(
                    logical_name=self.logical_name
                )
                record = self.dataverse.get_record(entity_set_name, self.guid)

                # Update our data with the fresh record
                for field, fresh_value in record.items():
                    if field.startswith(self.table_prefix) or field.endswith("id"):
                        self.data[field] = fresh_value

                # Return the requested value
                value = self.data.get(column, "")

            except Exception as e:
                logger.warning(f"Could not auto-fetch data for {column}: {e}")

        return value

    def refresh(self):
        """
        Refreshes the instance data by fetching the latest values from Dataverse.
        Requires self.guid to be set.

        Returns:
            bool: True if refresh was successful, False otherwise
        """
        if not self.guid:
            logger.warning("Cannot refresh: no GUID available")
            return False

        try:
            entity_set_name = self.dataverse.get_table_entity_set_name(
                logical_name=self.logical_name
            )
            record = self.dataverse.get_record(entity_set_name, self.guid)

            # Update our data with the fresh record
            for field, fresh_value in record.items():
                if field.startswith(self.table_prefix) or field.endswith("id"):
                    self.data[field] = fresh_value

            logger.info(f"Refreshed data for {self.logical_name} GUID: {self.guid}")
            return True

        except Exception as e:
            logger.error(f"Failed to refresh data for {self.logical_name} GUID {self.guid}: {e}")
            return False

    @staticmethod
    def data_property(column):
        def getter(self):
            return self.get_data(column)

        def setter(self, value):
            self.set_data(column, value)

        return property(getter, setter)

    # === LOOKUP
    def set_lookup(self, lookup_column, value: str):
        """Adds a lookup reference using @odata.bind"""
        lookup_column_schema_name = self.col_metadata[lookup_column]["SchemaName"]

        target_entity = self.relationships.get(lookup_column)  # Get table of lookup column
        target_entity_set_name = self.dataverse.get_table_entity_set_name(
            logical_name=target_entity
        )

        if not is_valid_guid(value):
            value = self.dataverse.name_to_guid(target_entity, value)

        self.data[f"{lookup_column_schema_name}@odata.bind"] = f"/{target_entity_set_name}({value})"

    def get_lookup(self, lookup_column):
        """Retrieves the lookup GUID (if stored)"""
        return (
            self.data.get(f"{lookup_column}@odata.bind", "")
            .replace("/", "")
            .split("(")[-1]
            .strip(")")
        )

    @staticmethod
    def lookup_property(lookup_column):
        """Creates dynamic properties for lookup fields"""
        return property(
            lambda self: self.get_lookup(lookup_column),  # Getter: Retrieve lookup GUID
            lambda self, guid: self.set_lookup(lookup_column, guid),  # Setter: Set lookup
        )

    # === CHOICE
    def set_choice(self, column, value):
        """Adds a choice field by looking up its numeric value"""
        choice_value = self.choices[column].get(value)
        if choice_value is not None:
            self.data[column] = choice_value
        else:
            from .exceptions import ValidationError

            raise ValidationError(f"Invalid choice '{value}' for column '{column}'")

    def get_choice(self, column):
        """Retrieves the readable choice name from its stored numeric value (Int → String)"""
        return self.choices.get(column, {}).get(self.data.get(column), None)

    @staticmethod
    def choice_property(lookup_column):
        """Creates dynamic properties for lookup fields"""
        return property(
            lambda self: self.get_choice(lookup_column),  # Getter: Retrieve GUID
            lambda self, guid: self.set_choice(lookup_column, guid),  # Setter: Setter
        )

    # === FILE
    def upload_file(self, column, file_content, filename):
        if not self.guid:
            raise EntityError("Record must be created first (GUID required)")

        entity_set_name = self.dataverse.get_table_entity_set_name(logical_name=self.logical_name)
        base_url = f"{self.dataverse.environment_uri}api/data/v9.2/{entity_set_name}({self.guid})"

        # Step 1: PATCH metadata
        meta_headers = self.dataverse.session.headers.copy()
        meta_headers["Content-Type"] = "application/json"

        metadata_payload = {
            f"{column}@odata.type": "#Microsoft.Dynamics.CRM.File",
            f"{column}@odata.mediaName": filename,
        }

        response_meta = requests.patch(base_url, json=metadata_payload, headers=meta_headers)
        if response_meta.status_code not in [204, 200]:
            raise Exception(f"Metadata update failed: {response_meta.text}")

        # Step 2: Convert file content to bytes
        if isinstance(file_content, io.BytesIO):
            file_bytes = file_content.read()
        else:
            raise TypeError(
                f"Unsupported file content type: {type(file_content)}. Expected io.BytesIO."
            )

        # Dataverse requires application/octet-stream and x-ms-file-name header
        put_headers = {
            "Authorization": meta_headers["Authorization"],
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Content-Type": "application/octet-stream",
            "Content-Length": str(len(file_bytes)),
            "x-ms-file-name": filename,
        }

        file_upload_url = f"{base_url}/{column}"

        response = requests.patch(file_upload_url, headers=put_headers, data=file_bytes)

        if response.status_code in [200, 204]:
            logger.info(f"✅ File uploaded to {column} successfully!")
            return True
        else:
            raise DataverseAPIError(
                f"Error uploading file: {response.text}", response.status_code, response.text
            )

    def set_file(self, column, value):
        """Handles file upload for file columns"""
        logger.info(f"Setting file for column {column} with value type {type(value)}")

        if isinstance(value, (dict, list)):
            # JSON data - validate serialization before proceeding
            try:
                json_content = json.dumps(value, indent=2, cls=DecimalEncoder)
            except (TypeError, ValueError) as e:
                raise ValueError(f"Value is not JSON serializable: {e}")

            file_content = io.BytesIO(json_content.encode("utf-8"))
            filename = f"{column}_data.json"
            # logger.info(f"Uploading JSON content as file: {filename} of type {type(json_content)}")
            return self.upload_file(column, file_content, filename)
        else:
            raise ValueError(
                f"Unsupported file value type: {type(value)}. Expected dict or list for JSON data."
            )

    def get_file_url(self, column):
        """Retrieves file download URL for file columns"""
        if not self.guid:
            return None

        entity_set_name = self.dataverse.get_table_entity_set_name(logical_name=self.logical_name)
        return f"{self.dataverse.environment_uri}api/data/v9.2/{entity_set_name}({self.guid})/{column}/$value"

    def get_file(self, column):
        """Downloads and returns file content from file columns"""
        if not self.guid:
            return None

        entity_set_name = self.dataverse.get_table_entity_set_name(logical_name=self.logical_name)
        file_url = f"{self.dataverse.environment_uri}api/data/v9.2/{entity_set_name}({self.guid})/{column}/$value"

        response = self.dataverse.session.get(file_url)

        if response.status_code == 200:
            # For JSON files, try to parse and return as dict
            content_type = response.headers.get("Content-Type", "")
            if "json" in content_type.lower() or column.endswith("json"):
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return response.content
            else:
                return response.content
        else:
            logger.error(f"Error downloading file from {column}: {response.text}")
            raise DataverseAPIError(
                f"Error downloading file: {response.text}", response.status_code, response.text
            )

    @staticmethod
    def file_property(file_column):
        """Creates dynamic properties for file fields"""
        return property(
            lambda self: self.get_file(file_column),  # Getter: Download file content
            lambda self, value: self.set_file(file_column, value),  # Setter: Upload file
        )

    # === DATA VALIDATION
    def _validate_and_convert_data(self, data):
        """Validates and converts data types according to Dataverse field metadata"""
        validated_data = {}

        for field, value in data.items():
            # Skip odata.bind fields (lookup references)
            if "@odata.bind" in field:
                validated_data[field] = value
                continue

            if field not in self.col_metadata:
                # Field not in metadata, pass through as-is
                validated_data[field] = value
                continue

            field_type = self.col_metadata[field].get("AttributeType")

            if field_type == "Decimal" and isinstance(value, (int, float, str)):
                # Convert to proper decimal format for Dataverse
                validated_data[field] = Decimal(str(value))
                logger.info(f"Converted {field} from {type(value).__name__} to Decimal: {value}")
            elif field_type == "Money" and isinstance(value, (int, float, str)):
                # Money fields also need decimal conversion
                validated_data[field] = Decimal(str(value))
                logger.info(
                    f"Converted {field} from {type(value).__name__} to Decimal for Money field: {value}"
                )
            elif field_type == "Integer" and isinstance(value, (float, str)):
                # Convert float/string to int for integer fields
                validated_data[field] = int(float(value))
                logger.info(f"Converted {field} from {type(value).__name__} to int: {value}")

            else:
                # Pass through other types as-is
                validated_data[field] = value

        return validated_data

    # === WRITE
    def write_to_dataverse(self):
        """Writes the record to Dataverse (CREATE if new, UPDATE if exists)"""

        # If we already have a GUID, this is an UPDATE operation
        if self.guid:
            return self._update_record()

        # === CHECK IF ROW EXISTS (for certain table types there is a casual name identifier) ===
        if self.logical_name in [f"{self.table_prefix}article", f"{self.table_prefix}recipe"]:
            # Check if name exists
            guid = self.dataverse.get_guid_by_casual_name(self.logical_name, self.data)
            if guid:
                self.guid = guid
                logger.warning(
                    f"✅ This {self.logical_name} already exists. GUID {guid} fetched and stored, no data written."
                )
                return guid

        # This is a CREATE operation
        return self._create_record()

    def _create_record(self):
        """Creates a new record in Dataverse"""
        entity_set_name = self.dataverse.get_table_entity_set_name(logical_name=self.logical_name)
        request_uri = f"{self.dataverse.environment_uri}api/data/v9.2/{entity_set_name}"

        # Validate and convert data types before sending
        validated_data = self._validate_and_convert_data(self.data)

        # Prepare record data
        record = validated_data if validated_data else {}

        # Send record to Dataverse (convert Decimals to floats)
        record_json = json.dumps(record, cls=DecimalEncoder)
        req = requests.Request(
            "POST",
            request_uri,
            data=record_json,
            headers={**self.dataverse.session.headers, "Content-Type": "application/json"},
        ).prepare()
        response = self.dataverse.session.send(req)

        if response.status_code == 204:
            logger.info(f"✅ Record created in {self.logical_name} successfully!")

            # Extract GUID from OData-EntityId header
            created_record_url = response.headers.get("OData-EntityId")
            if created_record_url:
                self.guid = created_record_url.split("(")[-1].strip(")")
                logger.info(f"🆔 Assigned GUID: {self.guid}")

                # Update guid mapping
                self.dataverse.name_to_guid(self.logical_name)
                return self.guid
        else:
            # Enhanced error message with field information
            error_details = []
            error_details.append(f"Table: {entity_set_name}")
            error_details.append(f"Record data sent: {json.dumps(record, indent=2)}")

            # Analyze data types for decimal conversion issues
            decimal_fields = []
            for field, value in record.items():
                if isinstance(value, (int, float)) and field in self.col_metadata:
                    field_type = self.col_metadata[field].get("AttributeType")
                    if field_type == "Decimal":
                        decimal_fields.append(
                            f"  {field}: {value} (type: {type(value).__name__}, expected: Decimal)"
                        )

            if decimal_fields:
                error_details.append("Potential decimal conversion issues:")
                error_details.extend(decimal_fields)

            enhanced_error = (
                "\n".join(error_details) + f"\n\nOriginal Dataverse error: {response.text}"
            )
            error_msg = f"Error while writing to {entity_set_name}: {enhanced_error}"
            logger.error(error_msg)
            raise DataverseAPIError(error_msg, response.status_code, response.text)

    def _update_record(self):
        """Updates an existing record in Dataverse"""
        entity_set_name = self.dataverse.get_table_entity_set_name(logical_name=self.logical_name)
        request_uri = (
            f"{self.dataverse.environment_uri}api/data/v9.2/{entity_set_name}({self.guid})"
        )

        # Validate and convert data types before sending
        validated_data = self._validate_and_convert_data(self.data)

        # Filter out fields that shouldn't be updated (odata.bind lookups and empty values)
        update_data = {}
        for field, value in validated_data.items():
            # Skip odata.bind fields in updates (they require special handling)
            if "@odata.bind" in field:
                continue
            # Skip empty values unless explicitly needed
            if value is not None and value != "":
                update_data[field] = value

        if not update_data:
            logger.info(f"No data to update for {self.logical_name} GUID: {self.guid}")
            return self.guid

        # Send update to Dataverse (convert Decimals to floats)
        update_json = json.dumps(update_data, cls=DecimalEncoder)
        req = requests.Request(
            "PATCH",
            request_uri,
            data=update_json,
            headers={**self.dataverse.session.headers, "Content-Type": "application/json"},
        ).prepare()
        response = self.dataverse.session.send(req)

        if response.status_code == 204:
            logger.info(f"✅ Record updated in {self.logical_name} successfully!")
            return self.guid
        else:
            error_msg = f"Error updating record in {entity_set_name}: {response.text}"
            logger.error(error_msg)
            raise DataverseAPIError(error_msg, response.status_code, response.text)
