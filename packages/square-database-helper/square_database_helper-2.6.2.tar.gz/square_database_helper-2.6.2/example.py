from square_database_helper import SquareDatabaseHelper
from square_database_helper.pydantic_models import FiltersV0, FilterConditionsV0

square_database_helper = SquareDatabaseHelper()

# Example: Insert Rows
insert_data = [
    {"test_text": "example"},
]
insert_output = square_database_helper.insert_rows_v0(
    database_name="square",
    schema_name="public",
    table_name="test",
    data=insert_data,
)
print(insert_output)

# Example: Get Rows
get_filters = FiltersV0(root={"test_text": FilterConditionsV0(like="exam%")})
get_output = square_database_helper.get_rows_v0(
    database_name="square",
    schema_name="public",
    table_name="test",
    filters=get_filters,
)
print(get_output)

# Example: Edit Rows
edit_filters = FiltersV0(root={"test_text": FilterConditionsV0(eq="example")})
edit_data = {"test_text": "edited"}
edit_output = square_database_helper.edit_rows_v0(
    database_name="square",
    schema_name="public",
    table_name="test",
    filters=edit_filters,
    data=edit_data,
)
print(edit_output)

# Example: Delete Rows
delete_filters = FiltersV0(root={"test_text": FilterConditionsV0(eq="edited")})
delete_output = square_database_helper.delete_rows_v0(
    database_name="square",
    schema_name="public",
    table_name="test",
    filters=delete_filters,
)
print(delete_output)
