import datetime
import operator

import pytest

from pyairtable.orm import fields as f
from pyairtable.orm.model import Model
from pyairtable.testing import fake_attachment, fake_meta, fake_record, fake_user

DATE_S = "2023-01-01"
DATE_V = datetime.date(2023, 1, 1)
DATETIME_S = "2023-04-12T09:30:00.000Z"
DATETIME_V = datetime.datetime(2023, 4, 12, 9, 30, 0)


def test_field():
    class T:
        name = f.Field("Name")

    t = T()
    t.name = "x"
    assert t.name == "x"
    assert t.__dict__["_fields"]["Name"] == "x"

    with pytest.raises(AttributeError):
        del t.name


@pytest.mark.parametrize(
    "instance,expected",
    [
        (
            f.Field("Name"),
            "Field('Name', readonly=False, validate_type=True)",
        ),
        (
            f.Field("Name", readonly=True, validate_type=False),
            "Field('Name', readonly=True, validate_type=False)",
        ),
        (
            f.CollaboratorField("Collaborator"),
            "CollaboratorField('Collaborator', readonly=False, validate_type=True)",
        ),
        (
            f.LastModifiedByField("User"),
            "LastModifiedByField('User', readonly=True, validate_type=True)",
        ),
        (
            f.ListField("Items", dict, validate_type=False),
            "ListField('Items', model=<class 'dict'>, readonly=False, validate_type=False)",
        ),
        (
            f.LinkField("Records", type("TestModel", (Model,), {"Meta": fake_meta()})),
            "LinkField('Records', model=<class 'abc.TestModel'>, lazy=True)",
        ),
    ],
)
def test_repr(instance, expected):
    assert repr(instance) == expected


@pytest.mark.parametrize(
    argnames=("field_type", "default_value"),
    argvalues=[
        (f.Field, None),
        (f.CheckboxField, False),
        (f.ListField, []),
        (f.LookupField, []),
        (f.MultipleCollaboratorsField, []),
        (f.MultipleSelectField, []),
    ],
)
def test_orm_missing_values(field_type, default_value):
    """
    Test that certain field types produce the correct default value
    when there is no field value provided from Airtable.
    """

    class T:
        the_field = field_type("Field Name")

    t = T()
    assert t.the_field == default_value


# Mapping from types to a test value for that type.
TYPE_VALIDATION_TEST_VALUES = {
    **{t: t() for t in (str, bool, list, dict)},
    int: 1,  # cannot use int() because RatingField requires value >= 1
    float: 1.0,  # cannot use float() because RatingField requires value >= 1
    datetime.date: datetime.date.today(),
    datetime.datetime: datetime.datetime.now(),
    datetime.timedelta: datetime.timedelta(seconds=1),
}


@pytest.mark.parametrize(
    "test_case",
    [
        (f.TextField, str),
        (f.IntegerField, int),
        (f.RichTextField, str),
        (f.DatetimeField, datetime.datetime),
        (f.TextField, str),
        (f.CheckboxField, bool),
        (f.BarcodeField, dict),
        (f.NumberField, (int, float)),
        (f.PhoneNumberField, str),
        (f.DurationField, datetime.timedelta),
        (f.RatingField, int),
        (f.ListField, list),
        (f.UrlField, str),
        (f.LookupField, list),
        (f.MultipleSelectField, list),
        (f.PercentField, (int, float)),
        (f.DateField, (datetime.date, datetime.datetime)),
        (f.FloatField, float),
        (f.CollaboratorField, dict),
        (f.SelectField, str),
        (f.EmailField, str),
        (f.MultipleCollaboratorsField, list),
        (f.CurrencyField, (int, float)),
    ],
    ids=operator.itemgetter(0),
)
def test_type_validation(test_case):
    """
    Test that attempting to assign the wrong type of value to a field
    will throw TypeError, but the right kind of value will work.
    """
    field_type, accepted_types = test_case
    if isinstance(accepted_types, type):
        accepted_types = [accepted_types]

    class T:
        the_field = field_type("Field Name")
        unvalidated_field = field_type("Unvalidated", validate_type=False)

    t = T()

    for testing_type, test_value in TYPE_VALIDATION_TEST_VALUES.items():
        # This statement should not raise an exception, no matter what. Caveat emptor.
        t.unvalidated_field = test_value

        if testing_type in accepted_types:
            t.the_field = test_value
        else:
            with pytest.raises(TypeError):
                t.the_field = test_value
                pytest.fail(
                    f"{field_type.__name__} = {test_value!r} {testing_type} did not raise TypeError"
                )


@pytest.mark.parametrize(
    argnames="test_case",
    argvalues=[
        # If a 2-tuple, the API and ORM values should be identical.
        (f.AutoNumberField, 1),
        (f.CountField, 1),
        (f.ExternalSyncSourceField, "Source"),
        (f.ButtonField, {"label": "Click me!"}),
        # If a 3-tuple, we should be able to convert API -> ORM values.
        (f.CreatedByField, fake_user()),
        (f.CreatedTimeField, DATETIME_S, DATETIME_V),
        (f.LastModifiedByField, fake_user()),
        (f.LastModifiedTimeField, DATETIME_S, DATETIME_V),
    ],
    ids=operator.itemgetter(0),
)
def test_readonly_fields(test_case):
    """
    Test that a readonly field cannot be overwritten.
    """
    if len(test_case) == 2:
        field_type, api_value = test_case
        orm_value = api_value
    else:
        field_type, api_value, orm_value = test_case

    class T(Model):
        Meta = fake_meta()
        the_field = field_type("Field Name")

    assert orm_value == T.the_field.to_internal_value(api_value)
    assert api_value == T.the_field.to_record_value(orm_value)

    t = T.from_record(fake_record({"Field Name": api_value}))
    assert t.the_field == orm_value
    with pytest.raises(AttributeError):
        t.the_field = orm_value


@pytest.mark.parametrize(
    argnames="test_case",
    argvalues=[
        # If a 2-tuple, the API and ORM values should be identical.
        (f.Field, object()),  # accepts any value, but Airtable API *will* complain
        (f.TextField, "name"),
        (f.EmailField, "x@y.com"),
        (f.NumberField, 1),
        (f.NumberField, 1.5),
        (f.IntegerField, 1),
        (f.FloatField, 1.5),
        (f.RatingField, 1),
        (f.CurrencyField, 1.05),
        (f.CheckboxField, True),
        (f.CollaboratorField, {"id": "usrFakeUserId", "email": "x@y.com"}),
        (f.ListField, ["any", "values"]),
        (f.LookupField, ["any", "values"]),
        (f.MultipleAttachmentsField, [fake_attachment(), fake_attachment()]),
        (f.MultipleSelectField, ["any", "values"]),
        (f.MultipleCollaboratorsField, [fake_user(), fake_user()]),
        (f.BarcodeField, {"type": "upce", "text": "084114125538"}),
        (f.PercentField, 0.5),
        (f.PhoneNumberField, "+49 40-349180"),
        (f.RichTextField, "Check out [Airtable](www.airtable.com)"),
        (f.SelectField, "any value"),
        (f.UrlField, "www.airtable.com"),
        # If a 3-tuple, we should be able to convert API -> ORM values.
        (f.DateField, DATE_S, DATE_V),
        (f.DurationField, 100.5, datetime.timedelta(seconds=100, microseconds=500000)),
        (f.DatetimeField, DATETIME_S, DATETIME_V),
    ],
    ids=operator.itemgetter(0),
)
def test_writable_fields(test_case):
    """
    Test that the ORM does not modify values that can be persisted as-is.
    """
    if len(test_case) == 2:
        field_type, api_value = test_case
        orm_value = api_value
    else:
        field_type, api_value, orm_value = test_case

    class T(Model):
        Meta = fake_meta()
        the_field = field_type("Field Name")

    assert orm_value == T.the_field.to_internal_value(api_value)
    assert api_value == T.the_field.to_record_value(orm_value)

    new_obj = T()
    new_obj.the_field = orm_value
    assert new_obj.to_record()["fields"] == {"Field Name": api_value}

    from_init = T(the_field=orm_value)
    assert from_init.the_field == orm_value

    existing_obj = T.from_record(fake_record({"Field Name": api_value}))
    assert existing_obj.the_field == orm_value


def test_completeness():
    """
    Ensure that we test conversion of all readonly and writable fields.
    """
    assert_all_fields_tested_by(test_writable_fields, test_readonly_fields)


def assert_all_fields_tested_by(*test_fns, exclude=(f.Field, f.LinkField)):
    """
    Allows meta-tests that fail if any new Field classes appear in pyairtable.orm.fields
    which are not covered by one of a few basic tests. This is intended to help remind
    us as contributors to test our edge cases :)
    """

    def extract_fields(obj):
        if isinstance(obj, pytest.Mark):
            yield from [*extract_fields(obj.args), *extract_fields(obj.kwargs)]
        elif isinstance(obj, str):
            pass
        elif isinstance(obj, dict):
            yield from extract_fields(list(obj.values()))
        elif hasattr(obj, "__iter__"):
            for item in obj:
                yield from extract_fields(item)
        elif isinstance(obj, type) and issubclass(obj, f.Field):
            yield obj

    tested_field_classes = {
        field_class
        for test_function in test_fns
        for pytestmark in getattr(test_function, "pytestmark", [])
        if isinstance(pytestmark, pytest.Mark) and pytestmark.name == "parametrize"
        for field_class in extract_fields(pytestmark)
        if field_class not in exclude
    }

    missing = [
        field_class_name
        for field_class_name, field_class in vars(f).items()
        if field_class_name.endswith("Field")
        and isinstance(field_class, type)
        and field_class not in tested_field_classes
        and field_class not in exclude
        and not field_class.__name__.startswith("_")
    ]

    if missing:
        test_names = sorted(fn.__name__ for fn in test_fns)
        fail_names = "\n".join(f"- {name}" for name in missing)
        pytest.fail(f"Some fields were not tested by {test_names}:\n{fail_names}")


def test_invalid_kwarg():
    """
    Ensure we raise AttributeError if an invalid kwarg is passed to the constructor.
    """

    class T(Model):
        Meta = fake_meta()
        the_field = f.TextField("Field Name")

    assert T(the_field="whatever").the_field == "whatever"
    with pytest.raises(AttributeError):
        T(foo="bar")


def test_list_field_with_none():
    """
    Ensure that a ListField represents a null value as an empty list.
    """

    class T(Model):
        Meta = fake_meta()
        the_field = f.ListField("Fld")

    assert T.from_record(fake_record()).the_field == []
    assert T.from_record(fake_record(Fld=None)).the_field == []


def test_list_field_with_invalid_type():
    """
    Ensure that a ListField represents a null value as an empty list.
    """

    class T(Model):
        Meta = fake_meta()
        the_field = f.ListField("Field Name")

    obj = T.from_record(fake_record())
    with pytest.raises(TypeError):
        obj.the_field = object()


def test_list_field_with_string():
    """
    If we pass a string to a list field, it should not be turned
    into a list of single-character strings; it should be an error.
    """

    class T:
        items = f.ListField("Items")

    t = T()
    with pytest.raises(TypeError):
        t.items = "hello!"


def test_linked_field_must_link_to_model():
    """
    Tests that a LinkField cannot link to an arbitrary type.
    """
    with pytest.raises(TypeError):
        f.LinkField("Field Name", model=dict)


def test_linked_field():
    class T(Model):
        Meta = fake_meta()

    class X(Model):
        Meta = fake_meta()
        t = f.LinkField("Field Name", model=T)

    x = X(t=[])
    x.t = [T(), T(), T()]

    with pytest.raises(TypeError):
        x.t = [1, 2, 3]

    with pytest.raises(TypeError):
        x.t = -1


def test_lookup_field():
    class T:
        items = f.LookupField("Items")

    lookup_from_airtable = ["Item 1", "Item 2", "Item 3"]
    rv_list = T.items.to_internal_value(lookup_from_airtable)
    rv_json = T.items.to_record_value(rv_list)
    assert rv_json == lookup_from_airtable
    assert isinstance(rv_list, list)
    assert rv_list[0] == "Item 1" and rv_list[1] == "Item 2" and rv_list[2] == "Item 3"

    class T:
        events = f.LookupField("Event times", model=f.DatetimeField)

    lookup_from_airtable = [
        "2000-01-02T03:04:05.000Z",
        "2000-02-02T03:04:05.000Z",
        "2000-03-02T03:04:05.000Z",
    ]
    rv_to_internal = T.events.to_internal_value(lookup_from_airtable)
    rv_to_record = T.events.to_record_value(rv_to_internal)
    assert rv_to_record == lookup_from_airtable
    assert isinstance(rv_to_internal, list)
    assert (
        rv_to_internal[0] == "2000-01-02T03:04:05.000Z"
        and rv_to_internal[1] == "2000-02-02T03:04:05.000Z"
        and rv_to_internal[2] == "2000-03-02T03:04:05.000Z"
    )


def test_rating_field():
    """
    Test that a RatingField does not accept floats or values below 1.
    """

    class T:
        rating = f.RatingField("Rating")

    T().rating = 1

    with pytest.raises(TypeError):
        T().rating = 0.5

    with pytest.raises(ValueError):
        T().rating = 0
