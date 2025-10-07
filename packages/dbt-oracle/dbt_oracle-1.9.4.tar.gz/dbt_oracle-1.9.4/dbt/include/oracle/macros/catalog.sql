{#
 Copyright (c) 2022, Oracle and/or its affiliates.
 Copyright (c) 2020, Vitor Avancini

  Licensed under the Apache License, Version 2.0 (the "License");
  you may not use this file except in compliance with the License.
  You may obtain a copy of the License at

     https://www.apache.org/licenses/LICENSE-2.0

  Unless required by applicable law or agreed to in writing, software
  distributed under the License is distributed on an "AS IS" BASIS,
  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  See the License for the specific language governing permissions and
  limitations under the License.
#}

{% macro oracle__get_catalog_tables_sql(information_schema) -%}
    select SYS_CONTEXT('userenv', 'DB_NAME') table_catalog,
                   owner table_schema,
                   table_name,
                   case
                     when iot_type = 'Y'
                     then 'IOT'
                     when temporary = 'Y'
                     then 'TEMP'
                     else 'BASE TABLE'
                   end table_type
                 from sys.all_tables
                 where upper(table_name) not in (
                 select upper(mview_name)
                 from sys.all_mviews)
                 union all
                 select SYS_CONTEXT('userenv', 'DB_NAME'),
                   owner,
                   view_name,
                   'VIEW'
                 from sys.all_views
                 union all
                 select SYS_CONTEXT('userenv', 'DB_NAME'),
                   owner,
                   mview_name,
                   'MATERIALIZED VIEW'
                 from sys.all_mviews
{%- endmacro %}

{% macro oracle__get_catalog_columns_sql(information_schema) -%}
    select
        SYS_CONTEXT('userenv', 'DB_NAME') table_catalog,
        owner table_schema,
        table_name,
        column_name,
        data_type,
        data_type_mod,
        decode(data_type_owner, null, TO_CHAR(null), SYS_CONTEXT('userenv', 'DB_NAME')) domain_catalog,
        data_type_owner domain_schema,
        data_length character_maximum_length,
        data_length character_octet_length,
        data_length,
        data_precision numeric_precision,
        data_scale numeric_scale,
        nullable is_nullable,
        coalesce(column_id, 0) ordinal_position,
        default_length,
        data_default column_default,
        num_distinct,
        low_value,
        high_value,
        density,
        num_nulls,
        num_buckets,
        last_analyzed,
        sample_size,
        SYS_CONTEXT('userenv', 'DB_NAME') character_set_catalog,
        'SYS' character_set_schema,
        SYS_CONTEXT('userenv', 'DB_NAME') collation_catalog,
        'SYS' collation_schema,
        character_set_name,
        char_col_decl_length,
        global_stats,
        user_stats,
        avg_col_len,
        char_length,
        char_used,
        v80_fmt_image,
        data_upgraded,
        histogram
      from sys.all_tab_columns
{%- endmacro %}

{% macro oracle__get_catalog_results_sql() -%}
    select
      tables.table_catalog as "table_database",
      tables.table_schema as "table_schema",
      tables.table_name as "table_name",
      tables.table_type as "table_type",
      all_tab_comments.comments as "table_comment",
      columns.column_name as "column_name",
      ordinal_position as "column_index",
      case
        when data_type like '%CHAR%' then
            CASE
                WHEN char_used = 'C' THEN
                    data_type || '(' || cast(char_length as varchar(10)) || ' CHAR )'
                ELSE
                    data_type || '(' || cast(char_length as varchar(10)) || ')'
            END
        else data_type
      end as "column_type",
      all_col_comments.comments as "column_comment",
      tables.table_schema as "table_owner"
  from tables
  inner join columns on upper(columns.table_catalog) = upper(tables.table_catalog)
    and upper(columns.table_schema) = upper(tables.table_schema)
    and upper(columns.table_name) = upper(tables.table_name)
  left join all_tab_comments
    on upper(all_tab_comments.owner) = upper(tables.table_schema)
      and upper(all_tab_comments.table_name) = upper(tables.table_name)
  left join all_col_comments
    on upper(all_col_comments.owner) = upper(columns.table_schema)
      and upper(all_col_comments.table_name) = upper(columns.table_name)
      and upper(all_col_comments.column_name) = upper(columns.column_name)
{%- endmacro %}

{% macro oracle__get_catalog_schemas_where_clause_sql(schemas) -%}
     where (
      {%- for schema in schemas -%}
        upper(tables.table_schema) = upper('{{ schema }}'){%- if not loop.last %} or {% endif -%}
      {%- endfor -%}
        )
{%- endmacro %}

{% macro oracle__get_catalog_relations_where_clause_sql(relations) -%}
    where (
        {%- for relation in relations -%}
            {% if relation.schema and relation.identifier %}
                (
                    upper(tables.table_schema) = upper('{{ relation.schema }}')
                    and upper(tables.table_name) = upper('{{ relation.identifier }}')
                )
            {% elif relation.schema %}
                (
                    upper(tables.table_schema) = upper('{{ relation.schema }}')
                )
            {% else %}
                {% do exceptions.raise_compiler_error(
                    '`get_catalog_relations` requires a list of relations, each with a schema'
                ) %}
            {% endif %}

            {%- if not loop.last %} or {% endif -%}
        {%- endfor -%}
    )
{%- endmacro %}

{% macro oracle__get_catalog(information_schema, schemas) -%}
    {% set query %}
        with tables as (
            {{ oracle__get_catalog_tables_sql(information_schema) }}
        ),
        columns as (
            {{ oracle__get_catalog_columns_sql(information_schema) }}
        )
        {{ oracle__get_catalog_results_sql() }}
        {{ oracle__get_catalog_schemas_where_clause_sql(schemas) }}
        order by
        tables.table_schema,
        tables.table_name,
        ordinal_position
    {%- endset -%}
    {{ return(run_query(query)) }}
{%- endmacro %}

{% macro oracle__get_catalog_relations(information_schema, relations) -%}
    {% set query %}
        with tables as (
            {{ oracle__get_catalog_tables_sql(information_schema) }}
        ),
        columns as (
            {{ oracle__get_catalog_columns_sql(information_schema) }}
        )
        {{ oracle__get_catalog_results_sql() }}
        {{ oracle__get_catalog_relations_where_clause_sql(relations) }}
        order by
        tables.table_schema,
        tables.table_name,
        ordinal_position
    {%- endset -%}

    {{ return(run_query(query)) }}

{%- endmacro %}
