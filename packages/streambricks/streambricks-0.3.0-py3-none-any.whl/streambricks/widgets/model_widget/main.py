"""Primitive type handlers for Pydantic form fields."""

from __future__ import annotations

from collections.abc import Callable
from datetime import date, datetime, time
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING, Any, Literal, TypeVar, get_args, get_origin, overload

import fieldz
from pydantic import BaseModel, SecretStr
import streamlit as st

from streambricks.widgets.model_widget.field_metadata_renderers import (
    render_model_id_field,
)
from streambricks.widgets.model_widget.type_renderers import (
    render_bool_field,
    render_date_field,
    render_datetime_field,
    render_enum_field,
    render_float_field,
    render_int_field,
    render_literal_field,
    render_secret_str_field,
    render_str_field,
    render_time_field,
)
from streambricks.widgets.type_helpers import (
    add_new_item,
    create_default_instance,
    get_description,
    get_field,
    get_inner_type,
    get_union_type_options,
    get_with_default,
    is_dataclass_like,
    is_literal_type,
    is_sequence_type,
    is_set_type,
    is_union_type,
    unpack_annotated,
)


if TYPE_CHECKING:
    from collections.abc import Sequence


T = TypeVar("T")
WidgetFunc = Callable[..., T]
TForm = TypeVar("TForm", bound=BaseModel)


FIELD_METADATA_RENDERERS: dict[str, WidgetFunc[Any]] = {
    "model_identifier": render_model_id_field
}


PRIMITIVE_RENDERERS = {
    str: render_str_field,
    bool: render_bool_field,
    int: render_int_field,
    float: render_float_field,
    Decimal: render_float_field,
    date: render_date_field,
    time: render_time_field,
    datetime: render_datetime_field,
    Enum: render_enum_field,
    Literal: render_literal_field,
    SecretStr: render_secret_str_field,
}


def render_union_field(
    *,
    key: str,
    value: Any = None,
    label: str | None = None,
    disabled: bool = False,
    help: str | None = None,  # noqa: A002
    **field_info: Any,
) -> Any:
    """Render a field that can accept multiple types."""
    annotation = field_info.get("type") or field_info.get("annotation")

    type_options = get_union_type_options(annotation)  # list of (type, description)

    # Check if None is one of the options
    none_type_index = None
    for i, (t, _) in enumerate(type_options):
        if t is type(None):
            none_type_index = i
            break

    # Handle optional fields (union with None)
    if none_type_index is not None:
        # Remove None from type options
        type_options.pop(none_type_index)

        # Add checkbox to toggle between None and non-None
        enable_key = f"{key}_not_none"

        # Initialize the session state for this checkbox if it doesn't exist
        if enable_key not in st.session_state:
            st.session_state[enable_key] = value is not None

        # Render checkbox using session state
        is_enabled = st.checkbox(
            f"Enable {label or key}",
            key=enable_key,
            disabled=disabled,
            help=help,
        )

        if not is_enabled:
            # If checkbox is unchecked, return None
            st.text("None")
            return None

        # Continue with the regular union handling for non-None types
        # If there's only one non-None type left, we can skip the type selector
        if len(type_options) == 1:
            selected_type, selected_type_name = type_options[0]
            field_key = f"{key}_value"

            # Special case for literal types
            if is_literal_type(selected_type):
                literal_values = get_args(selected_type)
                value_index = 0
                if value in literal_values:
                    value_index = literal_values.index(value)

                return st.selectbox(
                    label or key,
                    options=literal_values,
                    index=value_index,
                    key=field_key,
                    disabled=disabled,
                    help=None,  # Help already shown with checkbox
                )

            # For regular type, use standard field renderer
            modified_field_info = field_info.copy()
            modified_field_info["type"] = selected_type

            typed_val: Any = None
            if value is not None:
                try:
                    if selected_type is int and isinstance(value, int | float):
                        typed_val = int(value)
                    elif selected_type is float and isinstance(value, int | float):
                        typed_val = float(value)
                    elif selected_type is str:
                        typed_val = str(value)
                    elif selected_type is bool:
                        typed_val = bool(value)
                    elif isinstance(value, selected_type):
                        typed_val = value
                except (ValueError, TypeError):
                    # If conversion fails, start with a blank/default value
                    pass

            renderer = get_field_renderer(modified_field_info)
            result = renderer(
                key=field_key,
                value=typed_val,
                label=label or key,
                disabled=disabled,
                help=None,  # Help already shown with checkbox
                **modified_field_info,
            )

            return convert_result_type(result, selected_type)

    # Original code for handling standard unions (no None or None already handled)
    default_index = 0
    if value is not None:
        for i, (t, _) in enumerate(type_options):
            if (is_literal_type(t) and value in get_args(t)) or isinstance(value, t):
                default_index = i
                break

    type_descriptions = [desc for _, desc in type_options]

    # Skip type selector if there's only one option left
    if len(type_options) == 1:
        selected_type, selected_type_name = type_options[0]
    else:
        type_key = f"{key}_type"
        selected_type_name = st.selectbox(
            f"Type for {label or key}",
            options=type_descriptions,
            index=default_index,
            key=type_key,
            disabled=disabled,
            help=help,
        )
        selected_type_index = type_descriptions.index(selected_type_name)
        selected_type, selected_type_name = type_options[selected_type_index]

    field_key = f"{key}_value"

    # Special case for literal types
    if is_literal_type(selected_type):
        literal_values = get_args(selected_type)
        value_index = 0
        if value in literal_values:
            value_index = literal_values.index(value)

        return st.selectbox(
            f"Value ({selected_type_name if len(type_options) > 1 else label or key})",
            options=literal_values,
            index=value_index,
            key=field_key,
            disabled=disabled,
            help=help if len(type_options) == 1 else None,
        )

    # For other types, use standard field renderer
    modified_field_info = field_info.copy()
    modified_field_info["type"] = selected_type

    typed_value: Any = None
    if value is not None:
        try:
            if selected_type is int and isinstance(value, int | float):
                typed_value = int(value)
            elif selected_type is float and isinstance(value, int | float):
                typed_value = float(value)
            elif selected_type is str:
                typed_value = str(value)
            elif selected_type is bool:
                typed_value = bool(value)
            elif isinstance(value, selected_type):
                typed_value = value
        except (ValueError, TypeError):
            # If conversion fails, start with a blank/default value
            pass

    renderer = get_field_renderer(modified_field_info)
    result = renderer(
        key=field_key,
        value=typed_value,
        label=f"Value ({selected_type_name})" if len(type_options) > 1 else label or key,
        disabled=disabled,
        help=help if len(type_options) == 1 else None,
        **modified_field_info,
    )

    return convert_result_type(result, selected_type)


def convert_result_type(result: Any, target_type: Any) -> Any:  # noqa: PLR0911
    """Convert result to the target type, with error handling."""
    try:
        if target_type is int and not isinstance(result, int):
            return int(result)
        if target_type is float and not isinstance(result, float):
            return float(result)
        if target_type is str and not isinstance(result, str):
            return str(result)
        if target_type is bool and not isinstance(result, bool):
            return bool(result)
    except (ValueError, TypeError) as e:
        error_msg = f"Cannot convert {result} to {target_type.__name__}: {e!s}"
        st.error(error_msg)
        if target_type is int:
            return 0
        if target_type is float:
            return 0.0
        if target_type is str:
            return ""
        if target_type is bool:
            return False
        return None
    else:
        return result


def try_create_default_instance(model_class: type) -> Any:
    """Create a default instance of a model with default values for required fields."""
    try:
        return create_default_instance(model_class)
    except Exception as e:  # noqa: BLE001
        error_msg = f"Error creating default instance: {e}"
        st.error(error_msg)
        return None


def render_sequence_field(
    *,
    key: str,
    value: Sequence[Any] | None = None,
    label: str | None = None,
    disabled: bool = False,
    help: str | None = None,  # noqa: A002
    **field_info: Any,
) -> list[Any] | tuple[Any, ...]:
    """Render a field for sequence types (list, tuple, set)."""
    from streambricks.widgets.sequence import sequence_widget

    item_type = get_inner_type(field_info)
    result = sequence_widget(
        label=label or key,
        item_type=item_type,
        value=value,  # type: ignore
        key=key,
        disabled=disabled,
        help=help,
        **field_info,
    )

    # Cast back to original sequence type if needed
    annotation = field_info.get("type")
    if annotation is tuple or (get_origin(annotation) is tuple):
        return tuple(result)

    return result


def render_set_field(
    *,
    key: str,
    value: set[Any] | None = None,
    label: str | None = None,
    disabled: bool = False,
    help: str | None = None,  # noqa: A002
    **field_info: Any,
) -> set[Any]:
    """Render a field for set types with a multi-select interface when possible."""
    if value is None:
        value = set()
    item_type = get_inner_type(field_info)
    if (isinstance(item_type, type) and issubclass(item_type, Enum)) or is_literal_type(  # pyright: ignore
        item_type
    ):
        return render_set_with_known_domain(
            key=key,
            value=value,
            item_type=item_type,
            label=label,
            disabled=disabled,
            help=help,
        )

    return render_open_set_field(
        key=key,
        value=value,
        item_type=item_type,
        label=label,
        disabled=disabled,
        help=help,
        **field_info,
    )


def render_set_with_known_domain(
    *,
    key: str,
    value: set[Any],
    item_type: Any,
    label: str | None = None,
    disabled: bool = False,
    help: str | None = None,  # noqa: A002
) -> set[Any]:
    """Render a set field using a multiselect when domain is known (enum or literal)."""
    if isinstance(item_type, type) and issubclass(item_type, Enum):
        all_options = list(item_type.__members__.values())
        format_func = lambda x: x.name  # noqa: E731
    else:  # Literal type
        all_options = list(get_args(item_type))
        format_func = str
    selected = st.multiselect(
        label=label or key,
        options=all_options,
        default=list(value),
        format_func=format_func,
        disabled=disabled,
        key=key,
        help=help,
    )
    return set(selected)


def render_open_set_field(
    *,
    key: str,
    value: set[Any],
    item_type: Any,
    label: str | None = None,
    disabled: bool = False,
    help: str | None = None,  # noqa: A002
    **field_info: Any,
) -> set[Any]:
    """Render an open-ended set field with uniqueness enforcement."""
    add_item_key = f"{key}_add_item"
    items_key = f"{key}_items"
    if items_key not in st.session_state:
        st.session_state[items_key] = list(value)
    st.markdown(f"**{label or key}**")
    if help:
        st.caption(help)
    with st.container():
        if st.button("Add Item", key=add_item_key, disabled=disabled):
            temp_list: list[Any] = []
            add_new_item(temp_list, item_type)
            # If the temp_list has an item and it's not a duplicate, add it to our items
            if temp_list and str(temp_list[0]) not in {
                str(i) for i in st.session_state[items_key]
            }:
                st.session_state[items_key].append(temp_list[0])
            elif temp_list:  # Item was created but was a duplicate
                st.warning("Item already exists in the set.")

        render_set_items(
            st.session_state[items_key],
            item_type,
            key,
            items_key,
            disabled,
            field_info,
        )

    # Return the current items as a set
    return set(st.session_state[items_key])


def render_set_items(
    items: list,
    item_type: Any,
    key: str,
    items_key: str,
    disabled: bool,
    field_info: dict,
) -> None:
    """Render items in a set with delete buttons and uniqueness enforcement."""
    item_info = field_info.copy()
    item_info["type"] = item_type
    item_info["inside_expander"] = True
    try:
        renderer = get_field_renderer(item_info)
        items_to_delete = []
        for i, item in enumerate(items):
            st.divider()
            st.markdown(f"**Item {i + 1}**")
            updated_item = renderer(
                key=f"{key}_item_{i}",
                value=item,
                label=f"Item {i + 1}",
                disabled=disabled,
                **item_info,
            )
            duplicate = False
            for j, other_item in enumerate(items):
                if i != j and str(updated_item) == str(other_item):
                    duplicate = True
                    break
            if duplicate:
                st.error("This value would create a duplicate in the set.")
            else:
                items[i] = updated_item
            delete_key = f"{key}_delete_{i}"
            if st.button("Delete Item", key=delete_key, disabled=disabled):
                items_to_delete.append(i)
        if items_to_delete:
            for idx in sorted(items_to_delete, reverse=True):
                if 0 <= idx < len(items):
                    items.pop(idx)
            st.rerun()

    except Exception as e:  # noqa: BLE001
        st.error(f"Error rendering set items: {e!s}")


def display_set_readonly(value, field_type, key=None):
    """Display a set in read-only mode."""
    if not value:
        st.text("No items")
        return

    item_type = get_inner_type(field_type)
    # For known domain sets (enum or literal), show as comma-separated list
    if (isinstance(item_type, type) and issubclass(item_type, Enum)) or is_literal_type(  # pyright: ignore
        item_type
    ):
        if isinstance(item_type, type) and issubclass(item_type, Enum):  # pyright: ignore
            display_text = ", ".join(item.name for item in value)
        else:
            display_text = ", ".join(str(item) for item in value)
        st.text(display_text)
    # For other sets, use the same expander approach as sequences
    else:
        for i, item in enumerate(value):
            with st.expander(f"Item {i + 1}", expanded=False):
                display_value_readonly(item, item_type, key=f"{key}_{i}" if key else None)


def wrap_as_optional_field(renderer: WidgetFunc) -> WidgetFunc:
    """Wrap a field renderer with None toggle functionality.

    Args:
        renderer: The inner renderer function

    Returns:
        A new renderer that handles None values with a toggle
    """

    def optional_wrapper(
        *,
        key: str,
        value: Any = None,
        label: str | None = None,
        disabled: bool = False,
        help: str | None = None,  # noqa: A002
        **field_info: Any,
    ) -> Any:
        enable_key = f"{key}_enable"
        cols = st.columns([0.1, 0.9])
        with cols[0]:
            is_enabled = st.checkbox(
                "Enable",
                value=value is not None,
                key=enable_key,
                disabled=disabled,
                label_visibility="collapsed",
            )
        with cols[1]:
            # Show field label
            st.markdown(f"**{label or key}**")
            if help:
                st.caption(help)
            if is_enabled:
                return renderer(
                    key=key,
                    value=value,
                    label="",  # We've already shown the label
                    disabled=disabled,
                    **field_info,
                )
            st.text("None")
            return None

    return optional_wrapper


def render_model_instance_field(  # noqa: PLR0911
    *,
    key: str,
    value: Any = None,
    label: str | None = None,
    disabled: bool = False,
    help: str | None = None,  # noqa: A002
    **field_info: Any,
) -> Any:
    """Render a nested model instance field."""
    model_class = field_info.get("type")
    if model_class is None:
        error_msg = f"Model class not provided for field {key}"
        raise ValueError(error_msg)
    if is_union_type(model_class):
        if value is None:
            # For Union types, try each possible model type
            possible_types = get_args(model_class)
            for possible_type in possible_types:
                if is_dataclass_like(possible_type):
                    try:
                        # Try to create a minimal valid instance
                        value = create_default_instance(possible_type)
                        break
                    except Exception as e:  # noqa: BLE001
                        st.warning(f"Could not create {possible_type.__name__}: {e}")
                        continue

            if value is None:
                for possible_type in possible_types:
                    if not is_dataclass_like(possible_type):
                        if possible_type is type(None):
                            return None
                        if is_literal_type(possible_type):
                            return get_args(possible_type)[
                                0
                            ]  # Return first literal value

                st.error(
                    f"Could not create instance of any type in {model_class.__name__}"
                )
                return None
    # Initialize value if none for non-union types
    elif value is None:
        try:
            # Try to create a minimal valid instance
            value = create_default_instance(model_class)
        except Exception as e:  # noqa: BLE001
            st.error(f"Failed to create {model_class.__name__}: {e}")
            return None

    st.markdown(f"**{label or key}**")
    if help:
        st.caption(help)

    with st.expander("Edit", expanded=True):
        if value is None:
            st.error("Cannot render model: creation failed")
            return None

        updated_value = {}
        try:
            # Use the actual class of the value instance, not the field type
            actual_class = value.__class__
            for field in fieldz.fields(actual_class, parse_annotated=True):
                field_name = field.name
                field_value = get_with_default(value, field_name, field)
                field_help = get_description(field)
                nested_field_info = {"name": field_name, "type": field.type}
                if field_help:
                    nested_field_info["help"] = field_help
                if hasattr(field.native_field, "json_schema_extra"):
                    nested_field_info.update(field.native_field.json_schema_extra or {})  # type: ignore
                renderer = get_field_renderer(nested_field_info)
                updated_value[field_name] = renderer(
                    key=f"{key}_{field_name}",
                    value=field_value,
                    label=field_name.replace("_", " ").title(),
                    disabled=disabled,
                    **nested_field_info,
                )

            return fieldz.replace(value, **updated_value)
        except Exception as e:  # noqa: BLE001
            st.error(f"Error rendering nested model fields: {e!s}")
            return value


def get_field_renderer(field_info: dict[str, Any]) -> WidgetFunc[Any]:  # noqa: PLR0911
    """Get the appropriate renderer for a field based on its type and constraints."""
    annotation = field_info.get("type") or field_info.get("annotation")
    if (ann := unpack_annotated(annotation)) != annotation:
        annotation = ann
        field_info["type"] = annotation

    json_schema_extra = field_info.get("json_schema_extra", {})
    if (
        json_schema_extra
        and (field_type := json_schema_extra.get("field_type"))
        in FIELD_METADATA_RENDERERS
    ):
        return FIELD_METADATA_RENDERERS[field_type]
    if annotation is SecretStr or (
        isinstance(annotation, type) and issubclass(annotation, SecretStr)
    ):
        return render_secret_str_field
    if is_literal_type(annotation):
        return render_literal_field
    if is_union_type(annotation):
        return render_union_field
    if is_set_type(annotation):
        return render_set_field
    if is_sequence_type(annotation):
        return render_sequence_field
    origin = get_origin(annotation)
    if origin is not None:
        args = get_args(annotation)
        if len(args) > 0:
            annotation = args[0]

    if is_dataclass_like(annotation):
        return render_model_instance_field

    if isinstance(annotation, type):
        try:
            if issubclass(annotation, Enum):
                field_info["enum_class"] = annotation
                return render_enum_field
        except TypeError:
            pass

    for base_type, renderer in PRIMITIVE_RENDERERS.items():
        if isinstance(annotation, type):
            try:
                if issubclass(annotation, base_type):  # type: ignore
                    return renderer  # type: ignore
            except TypeError:
                # Skip if we get a TypeError (for special typing constructs)
                continue

    if getattr(annotation, "__origin__", None) is Literal:
        return render_literal_field

    error_msg = f"No renderer found for type: {annotation}"
    raise ValueError(error_msg)


def render_model_readonly[T](
    model_class: type[T],
    instance: T | None = None,
    exclude: set[str] | None = None,
):
    """Render a model in read-only mode using a clean label-based layout."""
    excluded_fields = exclude or set()
    if instance is None:
        st.info("No data available")
        return

    with st.container():
        # Get all fields from the model
        for field in fieldz.fields(model_class, parse_annotated=True):
            field_name = field.name
            if field_name in excluded_fields:
                continue
            field_value = getattr(instance, field_name, None)
            field_type = field.type
            label = field_name.replace("_", " ").title()
            render_field_readonly(
                label=label,
                value=field_value,
                field_type=field_type,
                description=get_description(field),
                key=f"ro_{field_name}",
            )


def render_field_readonly(label, value, field_type, description=None, key=None):
    """Render a single field in read-only mode."""
    cols = st.columns([0.3, 0.7])
    with cols[0]:
        st.markdown(f"**{label}:**")
        if description:
            st.caption(description)

    with cols[1]:
        display_value_readonly(value, field_type, key)


def display_value_readonly(value, field_type, key=None):
    """Display a value in read-only mode based on its type."""
    # Handle None values
    if value is None:
        st.text("—")  # Em dash to indicate empty value
        return

    if is_set_type(field_type):
        display_set_readonly(value, field_type, key)
        return

    if is_sequence_type(field_type):
        display_sequence_readonly(value, field_type, key)
        return

    if is_dataclass_like(field_type):
        display_model_readonly(value, key)
        return

    if isinstance(value, Enum):
        st.text(str(value.name))
        return

    match value:
        case Enum() as enum_value:
            st.text(str(enum_value.name))
        case bool() as bool_value:
            st.checkbox("", value=bool_value, disabled=True, key=key)
        case datetime():
            st.text(value.strftime("%Y-%m-%d %H:%M:%S"))
        case int() | float() | Decimal() | date() | time() | datetime():
            st.text(str(value))
        case str() as str_value:
            if len(str_value) > 100:  # noqa: PLR2004
                st.text_area("", value=str_value, disabled=True, height=100, key=key)
            else:
                st.text(str_value)
        case SecretStr():
            st.text("********")
        case _:
            st.text(str(value))


def display_sequence_readonly(value, field_type, key=None):
    """Display a sequence (list, set, tuple) in read-only mode."""
    if not value:  # Empty sequence
        st.text("No items")
        return
    item_type = get_inner_type(field_type)
    for i, item in enumerate(value):
        with st.expander(f"Item {i + 1}", expanded=False):
            display_value_readonly(item, item_type, key=f"{key}_{i}" if key else None)


def display_model_readonly(value, key=None):
    """Display a nested model in read-only mode."""
    model_class = value.__class__
    for field in fieldz.fields(model_class):
        field_name = field.name
        field_value = getattr(value, field_name, None)
        if field_value == fieldz.Field.MISSING:
            field_value = get_with_default(value, field_name, field)
        sub_key = f"{key}_{field_name}" if key else field_name
        cols = st.columns([0.3, 0.7])
        with cols[0]:
            st.markdown(f"**{field_name.replace('_', ' ').title()}:**")
        with cols[1]:
            display_value_readonly(field_value, field.type, key=sub_key)


def render_model_field(model_class, field_name, value=None, container=st):
    """Render a field from a model using a compact layout."""
    field = get_field(model_class, field_name)
    field_info = {"name": field.name, "type": field.type, "default": field.default}
    if hasattr(field.native_field, "json_schema_extra"):
        dct = field.native_field.json_schema_extra or {}  # type: ignore
        field_info.update(dct)
        field_info["json_schema_extra"] = dct
    label = field_name.replace("_", " ").title()
    help_text = get_description(field)
    if help_text:
        field_info["help"] = help_text
    renderer = get_field_renderer(field_info)
    return renderer(key=field_name, value=value, label=label, **field_info)


@overload
def render_model_form[TForm: BaseModel](
    model_or_instance: type[TForm],
    *,
    readonly: bool = False,
    exclude: set[str] | None = None,
) -> TForm: ...


@overload
def render_model_form[TForm: BaseModel](
    model_or_instance: TForm,
    *,
    readonly: bool = False,
    exclude: set[str] | None = None,
) -> TForm: ...


def render_model_form(
    model_or_instance,
    *,
    readonly: bool = False,
    exclude: set[str] | None = None,
) -> Any:
    """Render a complete form for a model class or instance using compact layout."""
    excluded_fields = exclude or set()
    if isinstance(model_or_instance, type):
        model_class = model_or_instance
        instance = model_class()  # Create a default instance
    else:
        instance = model_or_instance
        model_class = instance.__class__

    if readonly:
        render_model_readonly(model_class, instance, exclude=excluded_fields)
        return instance  # No changes in read-only mode

    result = {}
    field_groups: dict[str, Any] = {}
    for field in fieldz.fields(model_class):
        category = "General"
        if "category" in field.metadata:
            category = field.metadata["category"]

        if category not in field_groups:
            field_groups[category] = []

        field_groups[category].append(field)

    # If we have multiple categories, use tabs
    if len(field_groups) > 1:
        tabs = st.tabs(list(field_groups.keys()))

        for i, (_group_name, fields) in enumerate(field_groups.items()):
            with tabs[i]:
                for field in fields:
                    if field.name in excluded_fields:
                        continue
                    current_value = get_with_default(instance, field.name, field)
                    result[field.name] = render_model_field(
                        model_class, field.name, current_value
                    )
    else:
        # Single category, render fields directly
        for field in fieldz.fields(model_class, parse_annotated=True):
            if field.name in excluded_fields:
                continue
            current_value = get_with_default(instance, field.name, field)
            result[field.name] = render_model_field(
                model_class, field.name, current_value
            )

    return fieldz.replace(instance, **result)


if __name__ == "__main__":
    from typing import Annotated, Literal

    import pydantic

    from streambricks.helpers import run

    # Example models to simulate chunker configs
    class LlamaIndexChunkerConfig(BaseModel):
        """LlamaIndex chunker configuration."""

        type: Literal["llamaindex"] = "llamaindex"
        chunk_size: int = 1024
        chunk_overlap: int = 20

    class MarkdownChunkerConfig(BaseModel):
        """Markdown chunker configuration."""

        type: Literal["markdown"] = "markdown"
        split_level: int = 1

    class AiChunkerConfig(BaseModel):
        """AI-based chunker configuration."""

        type: Literal["ai"] = "ai"
        max_chunk_size: int = 2000

    # Create an Annotated union type similar to ChunkerConfig
    ChunkerConfig = Annotated[
        LlamaIndexChunkerConfig | MarkdownChunkerConfig | AiChunkerConfig,
        pydantic.Field(discriminator="type"),
    ]

    # Create a literal type similar to ChunkerShorthand
    ChunkerShorthand = Literal["markdown", "llamaindex", "ai"]

    class SubModel(BaseModel):
        """Test submodel."""

        name: str
        value: int | float
        active: bool = True

    class TestModel(BaseModel):
        """Test model with complex union types."""

        # This field simulates the problematic chunker field
        chunker: ChunkerConfig | ChunkerShorthand | None = None
        """Optional chunker configuration. If None, processes entire document at once."""

        status: int | str | bool = 2
        """A field that can be either int, str, or bool."""

        boolean: bool = True
        """Optional text field."""

        long_text: str = "test " * 40
        """Long text."""

        optional_int: int | None = None
        """An optional integer that can be None."""

        optional_string: str | None = None
        """An optional string that can be None."""

        optional_model: SubModel | None = None
        """An optional nested model that can be None."""

        tags: list[str] = pydantic.Field(default_factory=list)
        """A list of string tags."""

        numbers: list[int | float] = pydantic.Field(default_factory=list)
        """A list of numbers (int or float)"""

        settings: list[SubModel] = pydantic.Field(default_factory=list)
        """A list of nested models"""

        priorities: list[Literal["Low", "Medium", "High"]] = pydantic.Field(
            default_factory=list
        )
        """A list of priority levels."""

    def demo():
        st.title("Pydantic Form Demo")
        if "model" not in st.session_state:
            st.session_state.model = TestModel(status=2)

        st.session_state.model = render_model_form(st.session_state.model)

        with st.expander("Current Model State", expanded=True):
            st.json(st.session_state.model.model_dump_json(indent=2))

    run(demo)
