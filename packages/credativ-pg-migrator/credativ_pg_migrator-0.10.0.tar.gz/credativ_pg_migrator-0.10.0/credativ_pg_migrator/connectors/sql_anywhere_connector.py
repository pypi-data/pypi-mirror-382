# credativ-pg-migrator
# Copyright (C) 2025 credativ GmbH
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from credativ_pg_migrator.database_connector import DatabaseConnector
from credativ_pg_migrator.migrator_logging import MigratorLogger
import sqlanydb
import pyodbc
import traceback
from tabulate import tabulate
import time
import datetime

class SQLAnywhereConnector(DatabaseConnector):
    def __init__(self, config_parser, source_or_target):
        if source_or_target != 'source':
            raise ValueError("SQL Anywhere is only supported as a source database")

        self.connection = None
        self.config_parser = config_parser
        self.source_or_target = source_or_target
        self.on_error_action = self.config_parser.get_on_error_action()
        self.logger = MigratorLogger(self.config_parser.get_log_file()).logger

    def connect(self):
        if self.config_parser.get_connectivity(self.source_or_target) == 'native':
            config = self.config_parser.get_db_config(self.source_or_target)
            self.connection = sqlanydb.connect(
                    userid=config['username'],
                    pwd=config['password'],
                    host=f"{config['host']}:{config['port']}",
                    dbn=config['database'])
            # self.connection = sqlanydb.connect(connection_string)
        elif self.config_parser.get_connectivity(self.source_or_target) == 'odbc':
            connection_string = self.config_parser.get_connect_string(self.source_or_target)
            self.config_parser.print_log_message('DEBUG', f"SQL Anywhere ODBC connection string: {connection_string}")
            self.connection = pyodbc.connect(connection_string)

    def disconnect(self):
        try:
            if self.connection:
                self.connection.close()
        except Exception as e:
            pass

    def get_sql_functions_mapping(self, settings):
        """ Returns a dictionary of SQL functions mapping for the target database """
        target_db_type = settings['target_db_type']
        if target_db_type == 'postgresql':
            return {}
        else:
            self.config_parser.print_log_message('ERROR', f"Unsupported target database type: {target_db_type}")

    def fetch_table_names(self, table_schema: str):
        query = f"""
            SELECT table_id, table_name
            FROM sys.systable
            WHERE creator in (SELECT DISTINCT user_id
            FROM sys.SYSUSERPERM where user_name = '{table_schema}')
            AND table_type = 'BASE'
            ORDER BY table_name
        """
        try:
            tables = {}
            order_num = 1
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                tables[order_num] = {
                    'id': row[0],
                    'schema_name': table_schema,
                    'table_name': row[1],
                    'comment': ''
                }
                order_num += 1
            cursor.close()
            self.disconnect()
            return tables
        except Exception as e:
            self.config_parser.print_log_message('ERROR', f"Error executing query: {query}")
            self.config_parser.print_log_message('ERROR', e)
            raise

    def fetch_table_columns(self, settings) -> dict:
        table_schema = settings['table_schema']
        table_name = settings['table_name']
        query = f"""
            SELECT
                c.column_id,
                c.column_name,
                d.domain_name,
                c.width,
                c.scale,
                c."nulls",
                c."default"
            FROM sys.syscolumn c
            LEFT JOIN SYS.SYSDOMAIN d ON d.domain_id = c.domain_id
            WHERE c.table_id = (
                SELECT t.table_id FROM sys.systable t
                WHERE t.creator in (
                    SELECT DISTINCT user_id
                    FROM sys.SYSUSERPERM where user_name = '{table_schema}'
                    )
                AND table_name = '{table_name}'
                )
            ORDER BY column_id
        """
        try:
            result = {}
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                column_id = row[0]
                column_name = row[1]
                domain_name = row[2]
                width = row[3]
                scale = row[4]
                nulls = row[5]
                default_value = row[6]
                column_type = domain_name
                if self.is_string_type(column_type) and width is not None and width > 0:
                    column_type += f"({width})"
                elif self.is_numeric_type(column_type) and width is not None and scale is not None:
                    column_type += f"({width}, {scale})"
                elif self.is_numeric_type(column_type) and width is not None:
                    column_type += f"({width})"
                result[column_id] = {
                    'column_name': column_name,
                    'data_type': domain_name,
                    'column_type': column_type,
                    'character_maximum_length': width if self.is_string_type(row[2]) else None,
                    'numeric_precision': width if self.is_numeric_type(row[2]) else None,
                    'numeric_scale': scale,
                    'is_nullable': 'NO' if nulls == 'N' else 'YES',
                    'is_identity': 'YES' if default_value is not None and default_value.upper() == 'AUTOINCREMENT' else 'NO',
                    'column_default_value': default_value if default_value is not None and default_value.upper() != 'AUTOINCREMENT' else None,
                    'column_comment': '',
                }
            cursor.close()
            self.disconnect()
            return result
        except Exception as e:
            self.config_parser.print_log_message('ERROR', f"Error executing query: {query}")
            self.config_parser.print_log_message('ERROR', e)
            raise

    def get_types_mapping(self, settings):
        target_db_type = settings['target_db_type']
        types_mapping = {}
        if target_db_type == 'postgresql':
            types_mapping = {
                'INTEGER': 'INTEGER',
                'VARCHAR': 'VARCHAR',
                'CHAR': 'CHAR',
                'DATE': 'DATE',
                'TIMESTAMP': 'TIMESTAMP',
                'DECIMAL': 'DECIMAL',
                'BINARY': 'BYTEA',
                'LONG VARBINARY': 'BYTEA',
                'LONG BINARY': 'BYTEA',
                'BOOLEAN': 'BOOLEAN',
                'FLOAT': 'REAL',
                'DOUBLE PRECISION': 'DOUBLE PRECISION',
                'SMALLINT': 'SMALLINT',
                'BIGINT': 'BIGINT',
                'TINYINT': 'SMALLINT',
                'NUMERIC': 'NUMERIC',
                'TEXT': 'TEXT',
                'LONG VARCHAR': 'TEXT',
                'LONG NVARCHAR': 'TEXT',
                'UNICHAR': 'CHAR',
                'UNIVARCHAR': 'VARCHAR',
                'CLOB': 'TEXT',
                'BLOB': 'BYTEA',
                'XML': 'XML',
                'JSON': 'JSON',
                'UUID': 'UUID',
            }
        else:
            raise ValueError(f"Unsupported target database type: {target_db_type}")
        return types_mapping

    def get_create_table_sql(self, settings):
        return ""

    def is_string_type(self, column_type: str) -> bool:
        string_types = ['CHAR', 'VARCHAR', 'NCHAR', 'NVARCHAR', 'TEXT', 'LONG VARCHAR', 'LONG NVARCHAR', 'UNICHAR', 'UNIVARCHAR']
        return column_type.upper() in string_types

    def is_numeric_type(self, column_type: str) -> bool:
        numeric_types = ['BIGINT', 'INTEGER', 'INT', 'TINYINT', 'SMALLINT', 'FLOAT', 'DOUBLE PRECISION', 'DECIMAL', 'NUMERIC']
        return column_type.upper() in numeric_types

    def migrate_table(self, migrate_target_connection, settings):
        part_name = 'initialize'
        source_table_rows = 0
        target_table_rows = 0
        total_inserted_rows = 0
        migration_stats = {}
        batch_number = 0
        shortest_batch_seconds = 0
        longest_batch_seconds = 0
        average_batch_seconds = 0
        chunk_start_row_number = 0
        chunk_end_row_number = 0
        processing_start_time = time.time()
        order_by_clause = ''
        try:
            worker_id = settings['worker_id']
            source_schema = settings['source_schema']
            source_table = settings['source_table']
            source_table_id = settings['source_table_id']
            source_columns = settings['source_columns']
            target_schema = self.config_parser.convert_names_case(settings['target_schema'])
            target_table = self.config_parser.convert_names_case(settings['target_table'])
            target_columns = settings['target_columns']
            batch_size = settings['batch_size']
            migrator_tables = settings['migrator_tables']
            source_table_rows = self.get_rows_count(source_schema, source_table)
            target_table_rows = 0
            migration_limitation = settings['migration_limitation']
            chunk_size = settings['chunk_size']
            chunk_number = settings['chunk_number']
            resume_after_crash = settings['resume_after_crash']
            drop_unfinished_tables = settings['drop_unfinished_tables']

            source_table_rows = self.get_rows_count(source_schema, source_table, migration_limitation)
            target_table_rows = migrate_target_connection.get_rows_count(target_schema, target_table)

            total_chunks = self.config_parser.get_total_chunks(source_table_rows, chunk_size)
            if chunk_size == -1:
                chunk_size = source_table_rows + 1

            migration_stats = {
                'rows_migrated': target_table_rows,
                'chunk_number': chunk_number,
                'total_chunks': total_chunks,
                'source_table_rows': source_table_rows,
                'target_table_rows': target_table_rows,
                'finished': True if source_table_rows == 0 else False,
            }

            protocol_id = migrator_tables.insert_data_migration({
                'worker_id': worker_id,
                'source_table_id': source_table_id,
                'source_schema': source_schema,
                'source_table': source_table,
                'target_schema': target_schema,
                'target_table': target_table,
                'source_table_rows': source_table_rows,
                'target_table_rows': target_table_rows,
            })

            if source_table_rows == 0:
                self.config_parser.print_log_message('INFO', f"Worker {worker_id}: Table {source_table} is empty - skipping data migration.")
                migrator_tables.update_data_migration_status({
                        'row_id': protocol_id,
                        'success': True,
                        'message': 'Skipped',
                        'target_table_rows': 0,
                        'batch_count': 0,
                        'shortest_batch_seconds': 0,
                        'longest_batch_seconds': 0,
                        'average_batch_seconds': 0,
                    })

                return migration_stats

            else:
                if source_table_rows > target_table_rows:

                    self.config_parser.print_log_message('INFO', f"Worker {worker_id}: Source table {source_table}: {source_table_rows} rows / Target table {target_table}: {target_table_rows} rows - starting data migration.")

                    select_columns_list = []
                    orderby_columns_list = []
                    insert_columns_list = []
                    for order_num, col in source_columns.items():
                        self.config_parser.print_log_message('DEBUG2',
                                                            f"Worker {worker_id}: Table {source_schema}.{source_table}: Processing column {col['column_name']} ({order_num}) with data type {col['data_type']}")
                        insert_columns_list.append(f'''"{self.config_parser.convert_names_case(col['column_name'])}"''')
                        orderby_columns_list.append(f'''"{col['column_name']}"''')

                        # if col['data_type'].lower() == 'datetime':
                        #     select_columns_list.append(f"TO_CHAR({col['column_name']}, '%Y-%m-%d %H:%M:%S') as {col['column_name']}")
                        #     select_columns_list.append(f"ST_asText(`{col['column_name']}`) as `{col['column_name']}`")
                        # elif col['data_type'].lower() == 'set':
                        #     select_columns_list.append(f"cast(`{col['column_name']}` as char(4000)) as `{col['column_name']}`")
                        # else:
                        select_columns_list.append(f'''"{col['column_name']}"''')

                    select_columns = ', '.join(select_columns_list)
                    orderby_columns = ', '.join(orderby_columns_list)
                    insert_columns = ', '.join(insert_columns_list)

                    if resume_after_crash and not drop_unfinished_tables:
                        chunk_number = self.config_parser.get_total_chunks(target_table_rows, chunk_size)
                        self.config_parser.print_log_message('DEBUG', f"Worker {worker_id}: Resuming migration for table {source_schema}.{source_table} from chunk {chunk_number} with data chunk size {chunk_size}.")
                        chunk_offset = target_table_rows
                    else:
                        chunk_offset = (chunk_number - 1) * chunk_size

                    chunk_start_row_number = chunk_offset + 1
                    chunk_end_row_number = chunk_offset + chunk_size

                    self.config_parser.print_log_message('DEBUG', f"Worker {worker_id}: Migrating table {source_schema}.{source_table}: chunk {chunk_number}, data chunk size {chunk_size}, batch size {batch_size}, chunk offset {chunk_offset}, chunk end row number {chunk_end_row_number}, source table rows {source_table_rows}")
                    order_by_clause = ''

                    part_name = 'fetch_data'
                    query = f"SELECT TOP {chunk_size} START AT {chunk_start_row_number} {select_columns} FROM {source_schema}.{source_table}"
                    if migration_limitation:
                        query += f" WHERE {migration_limitation}"
                    primary_key_columns = migrator_tables.select_primary_key(source_schema, source_table)
                    self.config_parser.print_log_message('DEBUG2', f"Worker {worker_id}: Primary key columns for {source_schema}.{source_table}: {primary_key_columns}")
                    if primary_key_columns:
                        orderby_columns = primary_key_columns
                    order_by_clause = f""" ORDER BY {orderby_columns}"""

                    self.config_parser.print_log_message('DEBUG', f"Worker {worker_id}: Fetching data with cursor using query: {query}")

                    part_name = 'execute query'
                    cursor = self.connection.cursor()
                    cursor.arraysize = batch_size

                    batch_start_time = time.time()
                    reading_start_time = batch_start_time
                    processing_start_time = batch_start_time
                    batch_end_time = None
                    batch_number = 0
                    batch_durations = []

                    cursor.execute(query)
                    total_inserted_rows = 0
                    while True:
                        part_name = 'fetch_data_batch'
                        records = cursor.fetchmany(batch_size)
                        if not records:
                            break
                        batch_number += 1
                        reading_end_time = time.time()
                        reading_duration = reading_end_time - reading_start_time
                        self.config_parser.print_log_message('DEBUG', f"Worker {worker_id}: Fetched {len(records)} rows (batch {batch_number}) from source table '{source_table}' using cursor")

                        transforming_start_time = time.time()
                        records = [
                            {column['column_name']: value for column, value in zip(source_columns.values(), record)}
                            for record in records
                        ]
                        for record in records:
                            for order_num, column in source_columns.items():
                                column_name = column['column_name']
                                column_type = column['data_type']
                                target_column_type = target_columns[order_num]['data_type']
                                # if column_type.lower() in ['binary', 'bytea']:
                                if column_type.lower() in ['blob']:
                                    record[column_name] = bytes(record[column_name].getBytes(1, int(record[column_name].length())))  # Convert 'com.informix.jdbc.IfxCblob' to bytes
                                elif column_type.lower() in ['clob']:
                                    # elif isinstance(record[column_name], IfxCblob):
                                    record[column_name] = record[column_name].getSubString(1, int(record[column_name].length()))  # Convert IfxCblob to string
                                    # record[column_name] = bytes(record[column_name].getBytes(1, int(record[column_name].length())))  # Convert IfxBblob to bytes
                                    # record[column_name] = record[column_name].read()  # Convert IfxBblob to bytes
                                elif column_type.lower() in ['integer', 'smallint', 'tinyint', 'bit', 'boolean'] and target_column_type.lower() in ['boolean']:
                                    # Convert integer to boolean
                                    record[column_name] = bool(record[column_name])

                        self.config_parser.print_log_message('DEBUG', f"Worker {worker_id}: Starting insert of {len(records)} rows from source table {source_table}")
                        transforming_end_time = time.time()
                        transforming_duration = transforming_end_time - transforming_start_time
                        inserting_start_time = time.time()
                        inserted_rows = migrate_target_connection.insert_batch({
                            'target_schema': target_schema,
                            'target_table': target_table,
                            'target_columns': target_columns,
                            'data': records,
                            'worker_id': worker_id,
                            'migrator_tables': migrator_tables,
                            'insert_columns': insert_columns,
                        })
                        total_inserted_rows += inserted_rows
                        inserting_end_time = time.time()
                        inserting_duration = inserting_end_time - inserting_start_time

                        batch_end_time = time.time()
                        batch_duration = batch_end_time - batch_start_time
                        batch_durations.append(batch_duration)
                        percent_done = round(total_inserted_rows / source_table_rows * 100, 2)

                        batch_start_dt = datetime.datetime.fromtimestamp(batch_start_time)
                        batch_end_dt = datetime.datetime.fromtimestamp(batch_end_time)
                        batch_start_str = batch_start_dt.strftime('%Y-%m-%d %H:%M:%S.%f')
                        batch_end_str = batch_end_dt.strftime('%Y-%m-%d %H:%M:%S.%f')
                        migrator_tables.insert_batches_stats({
                            'source_schema': source_schema,
                            'source_table': source_table,
                            'source_table_id': source_table_id,
                                'chunk_number': chunk_number,
                            'batch_number': batch_number,
                            'batch_start': batch_start_str,
                            'batch_end': batch_end_str,
                            'batch_rows': inserted_rows,
                            'batch_seconds': batch_duration,
                            'worker_id': worker_id,
                            'reading_seconds': reading_duration,
                            'transforming_seconds': transforming_duration,
                            'writing_seconds': inserting_duration,
                        })

                        msg = (
                            f"Worker {worker_id}: Inserted {inserted_rows} "
                            f"(total: {total_inserted_rows} from: {source_table_rows} "
                            f"({percent_done}%)) rows into target table '{target_table}': "
                            f"Batch {batch_number} duration: {batch_duration:.2f} seconds "
                            f"(r: {reading_duration:.2f}, t: {transforming_duration:.2f}, w: {inserting_duration:.2f})"
                        )
                        self.config_parser.print_log_message('INFO', msg)

                        batch_start_time = time.time()
                        reading_start_time = batch_start_time

                    target_table_rows = migrate_target_connection.get_rows_count(target_schema, target_table)
                    self.config_parser.print_log_message('INFO', f"Worker {worker_id}: Target table {target_schema}.{target_table} has {target_table_rows} rows")

                    shortest_batch_seconds = min(batch_durations) if batch_durations else 0
                    longest_batch_seconds = max(batch_durations) if batch_durations else 0
                    average_batch_seconds = sum(batch_durations) / len(batch_durations) if batch_durations else 0
                    self.config_parser.print_log_message('INFO', f"Worker {worker_id}: Migrated {total_inserted_rows} rows from {source_table} to {target_schema}.{target_table} in {batch_number} batches: "
                                                            f"Shortest batch: {shortest_batch_seconds:.2f} seconds, "
                                                            f"Longest batch: {longest_batch_seconds:.2f} seconds, "
                                                            f"Average batch: {average_batch_seconds:.2f} seconds")

                    cursor.close()

                elif source_table_rows <= target_table_rows:
                    self.config_parser.print_log_message('INFO', f"Worker {worker_id}: Source table {source_table} has {source_table_rows} rows, which is less than or equal to target table {target_table} with {target_table_rows} rows. No data migration needed.")

                migration_stats = {
                    'rows_migrated': total_inserted_rows,
                    'chunk_number': chunk_number,
                    'total_chunks': total_chunks,
                    'source_table_rows': source_table_rows,
                    'target_table_rows': target_table_rows,
                    'finished': False,
                }

                self.config_parser.print_log_message('DEBUG', f"Worker {worker_id}: Migration stats: {migration_stats}")
                if source_table_rows <= target_table_rows or chunk_number >= total_chunks:
                    self.config_parser.print_log_message('DEBUG3', f"Worker {worker_id}: Setting migration status to finished for table {source_table} (chunk {chunk_number}/{total_chunks})")
                    migration_stats['finished'] = True
                    migrator_tables.update_data_migration_status({
                        'row_id': protocol_id,
                        'success': True,
                        'message': 'OK',
                        'target_table_rows': target_table_rows,
                        'batch_count': batch_number,
                        'shortest_batch_seconds': shortest_batch_seconds,
                        'longest_batch_seconds': longest_batch_seconds,
                        'average_batch_seconds': average_batch_seconds,
                    })

                migrator_tables.insert_data_chunk({
                    'worker_id': worker_id,
                    'source_table_id': source_table_id,
                    'source_schema': source_schema,
                    'source_table': source_table,
                    'target_schema': target_schema,
                    'target_table': target_table,
                    'source_table_rows': source_table_rows,
                    'target_table_rows': target_table_rows,
                    'chunk_number': chunk_number,
                    'chunk_size': chunk_size,
                    'migration_limitation': migration_limitation,
                    'chunk_start': chunk_start_row_number,
                    'chunk_end': chunk_end_row_number,
                    'inserted_rows': total_inserted_rows,
                    'batch_size': batch_size,
                    'total_batches': batch_number,
                    'task_started': datetime.datetime.fromtimestamp(processing_start_time).strftime('%Y-%m-%d %H:%M:%S.%f'),
                    'task_completed': datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S.%f'),
                    'order_by_clause': order_by_clause,
                })

                return migration_stats

        except Exception as e:
            self.config_parser.print_log_message('ERROR', f"Worker {worker_id}: Error during {part_name} -> {e}")
            self.config_parser.print_log_message('ERROR', f"Worker {worker_id}: Full stack trace: {traceback.format_exc()}")
            raise e


    def fetch_indexes(self, settings):
        source_table_id = settings['source_table_id']
        source_table_schema = settings['source_table_schema']
        source_table_name = settings['source_table_name']

        table_indexes = {}
        order_num = 1
        query = f"""
            SELECT
                iname,
                indextype,
                colnames
            FROM SYS.SYSINDEXES
            WHERE creator = '{source_table_schema}'
            AND tname = '{source_table_name}'
            ORDER BY iname
        """
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                index_name = row[0]
                index_type = row[1].upper()
                index_columns = row[2]

                if index_type == 'NON-UNIQUE':
                    index_type = 'INDEX'

                if index_type == 'PRIMARY KEY':
                    index_columns = index_columns.replace(" ASC", "").replace(" DESC", "")

                columns = []
                for col in index_columns.split(","):
                    col = col.strip()
                    if col.upper().endswith(" ASC"):
                        col_name = col[:-4].strip()
                        columns.append(f'"{col_name}" ASC')
                    elif col.upper().endswith(" DESC"):
                        col_name = col[:-5].strip()
                        columns.append(f'"{col_name}" DESC')
                    else:
                        columns.append(f'"{col}"')
                index_columns = ', '.join(columns)
                if index_type != 'FOREIGN KEY':
                    table_indexes[order_num] = {
                        'index_name': index_name,
                        'index_owner': source_table_schema,
                        'index_type': index_type,
                        'index_columns': index_columns,
                        'index_comment': '',
                    }
                    order_num += 1
            cursor.close()
            self.disconnect()

            return table_indexes
        except Exception as e:
            self.config_parser.print_log_message('ERROR', f"Error executing query: {query}")
            self.config_parser.print_log_message('ERROR', e)
            raise

    def get_create_index_sql(self, settings):
        return ""

    def fetch_constraints(self, settings):
        source_table_id = settings['source_table_id']
        source_table_schema = settings['source_table_schema']
        source_table_name = settings['source_table_name']

        order_num = 1
        table_constraints = {}
        query = f"""
            SELECT
                "role" as fk_name,
                primary_creator,
                primary_tname,
                foreign_creator,
                foreign_tname,
                columns,
                count(*) over (partition by "role") fk_name_uniqueness,
                row_number() over (partition by "role" order by s.foreign_tname) as fk_name_ordinal_number
            FROM SYS.SYSFOREIGNKEYS s
            WHERE (primary_creator = '{source_table_schema}' or foreign_creator = '{source_table_schema}')
            AND primary_tname = '{source_table_name}'
            ORDER BY "role"
        """
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                constraint_name = f"{row[0]}_fk"
                constraint_type = 'FOREIGN KEY'
                primary_table_name = row[2]
                foreign_table_name = row[4]
                sa_columns = row[5]
                pk_columns, ref_columns = sa_columns.split(" IS ")

                fk_name_uniqueness = row[6]
                fk_name_ordinal_number = row[7]
                if fk_name_uniqueness > 1:
                    constraint_name = f"{constraint_name}{fk_name_ordinal_number}"

                columns = []
                for col in ref_columns.split(","):
                    col = col.strip().replace(" ASC", "").replace(" DESC", "")
                    if col not in columns:
                        columns.append('"'+col+'"')
                ref_columns = ','.join(columns)

                columns = []
                for col in pk_columns.split(","):
                    col = col.strip().replace(" ASC", "").replace(" DESC", "")
                    if col not in columns:
                        columns.append('"'+col+'"')
                pk_columns = ','.join(columns)

                table_constraints[order_num] = {
                    'constraint_name': constraint_name,
                    'constraint_type': constraint_type,
                    'constraint_owner': source_table_schema,
                    'constraint_columns': ref_columns,
                    'referenced_table_name': foreign_table_name,
                    'referenced_columns': pk_columns,
                    'constraint_sql': '',
                    'constraint_comment': '',
                }
                order_num += 1
            cursor.close()
            self.disconnect()

            return table_constraints
        except Exception as e:
            self.config_parser.print_log_message('ERROR', f"Error executing query: {query}")
            self.config_parser.print_log_message('ERROR', e)
            raise

    def get_create_constraint_sql(self, settings):
        return ""

    def fetch_triggers(self, table_id: int, table_schema: str, table_name: str):
        pass

    def convert_trigger(self, trig: str, settings: dict):
        pass

    def fetch_funcproc_names(self, schema: str):
        pass

    def fetch_funcproc_code(self, funcproc_id: int):
        pass

    def convert_funcproc_code(self, settings):
        funcproc_code = settings['funcproc_code']
        target_db_type = settings['target_db_type']
        source_schema = settings['source_schema']
        target_schema = settings['target_schema']
        table_list = settings['table_list']
        view_list = settings['view_list']
        converted_code = ''
        # placeholder for actual conversion logic
        return converted_code

    def fetch_sequences(self, table_schema: str, table_name: str):
        pass

    def get_sequence_details(self, sequence_owner, sequence_name):
        # Placeholder for fetching sequence details
        return {}

    def fetch_views_names(self, source_schema: str):
        views = {}
        order_num = 1
        query = f"""SELECT viewname FROM sys.sysviews WHERE vcreator = '{source_schema}'"""
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query)
            for row in cursor.fetchall():
                views[order_num] = {
                    'id': None,
                    'schema_name': source_schema,
                    'view_name': row[0],
                    'comment': ''
                }
                order_num += 1
            cursor.close()
            self.disconnect()
            return views
        except Exception as e:
            self.config_parser.print_log_message('ERROR', f"Error executing query: {query}")
            self.config_parser.print_log_message('ERROR', e)
            raise

    def fetch_view_code(self, settings):
        view_id = settings['view_id']
        source_schema = settings['source_schema']
        source_view_name = settings['source_view_name']
        target_schema = settings['target_schema']
        target_view_name = settings['target_view_name']
        query = f"""
            SELECT viewtext
            FROM sys.sysviews
            WHERE vcreator = '{source_schema}'
            AND viewname = '{source_view_name}'
        """
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query)
            view_code = cursor.fetchone()[0]
            cursor.close()
            self.disconnect()
            return view_code
        except Exception as e:
            self.config_parser.print_log_message('ERROR', f"Error executing query: {query}")
            self.config_parser.print_log_message('ERROR', e)
            raise

    def convert_view_code(self, settings: dict):
        view_code = settings['view_code']
        return view_code

    def get_sequence_current_value(self, sequence_id: int):
        pass

    def execute_query(self, query: str, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        cursor.close()

    def execute_sql_script(self, script_path: str):
        with open(script_path, 'r') as file:
            script = file.read()
        cursor = self.connection.cursor()
        cursor.execute(script)
        cursor.close()

    def begin_transaction(self):
        self.connection.autocommit = False

    def commit_transaction(self):
        self.connection.commit()
        self.connection.autocommit = True

    def rollback_transaction(self):
        self.connection.rollback()

    def get_rows_count(self, table_schema: str, table_name: str, migration_limitation: str = None):
        query = f"SELECT COUNT(*) FROM \"{table_schema}\".\"{table_name}\""
        if migration_limitation:
            query += f" WHERE {migration_limitation}"
        cursor = self.connection.cursor()
        cursor.execute(query)
        count = cursor.fetchone()[0]
        cursor.close()
        return count

    def get_table_size(self, table_schema: str, table_name: str):
        raise NotImplementedError("Fetching table size is not yet implemented for SQL Anywhere")

    def fetch_user_defined_types(self, schema: str):
        pass

    def fetch_domains(self, schema: str):
        # Placeholder for fetching domains
        return {}

    def get_create_domain_sql(self, settings):
        # Placeholder for generating CREATE DOMAIN SQL
        return ""

    def fetch_default_values(self, settings) -> dict:
        # Placeholder for fetching default values
        return {}

    def get_table_description(self, settings) -> dict:
        table_schema = settings['table_schema']
        table_name = settings['table_name']
        output = ""
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(f"SELECT sa_get_table_definition('{table_schema}', '{table_name}')")

            set_num = 1
            if cursor.description is not None:
                rows = cursor.fetchall()
                if rows:
                    output += f"Result set {set_num}:\n"
                    columns = [column[0] for column in cursor.description]
                    table = tabulate(rows, headers=columns, tablefmt="github")
                    output += table + "\n\n"
                    set_num += 1

            cursor.close()
            self.disconnect()
        except Exception as e:
            self.config_parser.print_log_message('ERROR', f"Error fetching table description for {table_schema}.{table_name}: {e}")
            raise

        return { 'table_description': output.strip() }

    def testing_select(self):
        return "SELECT 1"

    def get_database_version(self):
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute("select top 1 version, platform, first_time from SYSHISTORY order by first_time desc")
            version = cursor.fetchone()
            cursor.close()
            self.disconnect()
            return version
        except Exception as e:
            self.config_parser.print_log_message('ERROR', f"Error fetching database version: {e}")
            raise

    def get_database_size(self):
        query = "select round(db_property('FileSize') * db_property('PageSize') / 1024 / 1024,2) as db_size_mb"
        self.connect()
        cursor = self.connection.cursor()
        cursor.execute(query)
        size = cursor.fetchone()[0]
        cursor.close()
        self.disconnect()
        return size

    def get_top_n_tables(self, settings):
        top_tables = {}
        top_tables['by_rows'] = {}
        top_tables['by_size'] = {}
        top_tables['by_columns'] = {}
        top_tables['by_indexes'] = {}
        top_tables['by_constraints'] = {}

        source_schema = settings.get('source_schema', 'public')
        try:
            order_num = 1
            top_n = self.config_parser.get_top_n_tables_by_rows()
            if top_n > 0:
                query = f"""
                    SELECT TOP {top_n}
                        t.table_name,
                        table_page_count
                    FROM sys.systable t
                    WHERE creator in (SELECT DISTINCT user_id
                    FROM sys.SYSUSERPERM where user_name = '{source_schema}')
                    ORDER BY table_page_count DESC
                """
                self.config_parser.print_log_message('DEBUG3', f"Fetching top {top_n} tables by rows for schema {source_schema} with query: {query}")
                self.connect()
                cursor = self.connection.cursor()
                cursor.execute(query)
                order_num = 1
                for row in cursor.fetchall():
                    top_tables['by_rows'][order_num] = {
                        'owner': source_schema,
                        'table_name': row[0].strip(),
                        'table_size': row[1]
                    }
                    order_num += 1
                cursor.close()
                self.disconnect()
                self.config_parser.print_log_message('DEBUG3', f"Top {top_n} tables by rows fetched successfully {top_tables['by_rows']}")
            else:
                self.config_parser.print_log_message('DEBUG', "Top N tables by rows is not configured or set to 0")
        except Exception as e:
            self.config_parser.print_log_message('ERROR', f"Error fetching top tables by rows: {e}")

        return top_tables

    def get_top_fk_dependencies(self, settings):
        top_fk_dependencies = {}
        return top_fk_dependencies

    def target_table_exists(self, target_schema, target_table):
        query = f"""
            SELECT COUNT(*)
            FROM sys.systable
            WHERE creator in (SELECT DISTINCT user_id
            FROM sys.SYSUSERPERM where user_name = '{target_schema}')
            AND table_name = '{target_table}'
        """
        try:
            self.connect()
            cursor = self.connection.cursor()
            cursor.execute(query)
            exists = cursor.fetchone()[0] > 0
            cursor.close()
            self.disconnect()
            return exists
        except Exception as e:
            self.config_parser.print_log_message('ERROR', f"Error checking if target table exists: {e}")
            raise

    def fetch_all_rows(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        cursor.close()
        return rows

if __name__ == "__main__":
    print("This script is not meant to be run directly")
