import os
import uuid
from dataclasses import dataclass
from typing import Any, List, Dict
from unittest.mock import patch

import pytest

from detective import snapshot

from .fixtures_data import (
    BoboCat,
    BoboProto,
    Cat,
    CatData_dict,
    CocoCat,
    CocoDataclass,
    CocoProto,
    JaggerCat,
    JaggerDataclass,
    JaggerProto,
)
from .utils import are_snapshots_equal, get_debug_file, get_test_hash, setup_debug_dir

# Split the test cases into arrays based on input patterns
SINGLE_INPUT_TEST_CASES = [
    {
        "name": "wildcard_single_field",
        "input_fields": ["cats.*.color"],
        "expected_input": {
            "cats": {
                "Coco": {"color": "calico"},
                "Bobo": {"color": "tuxedo"},
                "Jagger": {"color": "void"},
            }
        },
    },
    {
        "name": "wildcard_single_field_args_syntax",
        "input_fields": ["args[0].*.color"],
        "expected_input": {
            "cats": {  # Note: still using "cats" as the key, not "args[0]"
                "Coco": {"color": "calico"},
                "Bobo": {"color": "tuxedo"},
                "Jagger": {"color": "void"},
            }
        },
    },
    {
        "name": "nested_array_fields",
        "input_fields": [
            "cats.*.activities[*].name",
            "cats.*.activities[*].adorableness",
        ],
        "expected_input": {
            "cats": {
                "Coco": {
                    "activities": [
                        {"name": "sunbathing"},
                        {"name": "brushing", "adorableness": "melts_like_butter"},
                    ]
                },
                "Bobo": {"activities": [{"name": "belly rubs"}]},
                "Jagger": {
                    "activities": [
                        {"name": "shadow prowling"},
                        {"name": "shoulder rides"},
                    ]
                },
            }
        },
    },
    {
        "name": "specific_array_index",
        "input_fields": ["cats.*.activities[0].name"],
        "expected_input": {
            "cats": {
                "Coco": {"activities": [{"name": "sunbathing"}]},
                "Bobo": {"activities": [{"name": "belly rubs"}]},
                "Jagger": {"activities": [{"name": "shadow prowling"}]},
            }
        },
    },
    {
        "name": "multiple_field_selection",
        "input_fields": ["cats.Coco.(color, name)"],
        "expected_input": {"cats": {"Coco": {"name": "Coco", "color": "calico"}}},
    },
    {
        "name": "multiple_cats_specific_fields",
        "input_fields": ["cats.(Coco, Bobo).color"],
        "expected_input": {
            "cats": {"Coco": {"color": "calico"}, "Bobo": {"color": "tuxedo"}}
        },
    },
    {
        "name": "nested_multiple_selection",
        "input_fields": ["cats.*.activities[*].(name, cuteness)"],
        "expected_input": {
            "cats": {
                "Coco": {
                    "activities": [
                        {"name": "sunbathing", "cuteness": "purrfectly_toasty"},
                        {"name": "brushing"},
                    ]
                },
                "Bobo": {"activities": [{"name": "belly rubs"}]},
                "Jagger": {
                    "activities": [
                        {"name": "shadow prowling"},
                        {"name": "shoulder rides"},
                    ]
                },
            }
        },
    },
    {
        "name": "overlapping_fields_specific_and_wildcard",
        "input_fields": [
            "cats.Coco.activities[*].name",  # Specific cat
            "cats.*.activities[*].name",  # All cats
        ],
        "expected_input": {
            "cats": {
                "Coco": {
                    "activities": [
                        {"name": "sunbathing"},
                        {"name": "brushing"},
                    ]
                },
                "Bobo": {"activities": [{"name": "belly rubs"}]},
                "Jagger": {
                    "activities": [
                        {"name": "shadow prowling"},
                        {"name": "shoulder rides"},
                    ]
                },
            }
        },
    },
    {
        "name": "duplicate_fields",
        "input_fields": ["cats.*.color", "cats.*.color"],  # Same field twice
        "expected_input": {
            "cats": {
                "Coco": {"color": "calico"},
                "Bobo": {"color": "tuxedo"},
                "Jagger": {"color": "void"},
            }
        },
    },
    {
        "name": "overlapping_nested_fields",
        "input_fields": [
            "cats.*.activities[0]",  # First activity of each cat
            "cats.*.activities[*].name",  # All activity names
        ],
        "expected_input": {
            "cats": {
                "Coco": {
                    "activities": [
                        {"name": "sunbathing", "cuteness": "purrfectly_toasty"},
                        {"name": "brushing"},
                    ]
                },
                "Bobo": {
                    "activities": [
                        {"name": "belly rubs", "goofiness": "rolls_around_happily"}
                    ]
                },
                "Jagger": {
                    "activities": [
                        {"name": "shadow prowling", "stealth": "ninja_level"},
                        {"name": "shoulder rides"},
                    ]
                },
            }
        },
    },
    {
        "name": "overlapping_array_indices",
        "input_fields": [
            "cats.*.activities[0].name",  # First activity name
            "cats.*.activities[*].name",  # All activity names
        ],
        "expected_input": {
            "cats": {
                "Coco": {"activities": [{"name": "sunbathing"}, {"name": "brushing"}]},
                "Bobo": {"activities": [{"name": "belly rubs"}]},
                "Jagger": {
                    "activities": [
                        {"name": "shadow prowling"},
                        {"name": "shoulder rides"},
                    ]
                },
            }
        },
    },
    {
        "name": "overlapping_args_and_direct_syntax",
        "input_fields": [
            "args[0].Coco.activities[*].name",  # Using args[0] syntax
            "cats.*.activities[*].name",  # Using parameter name directly
        ],
        "expected_input": {
            "cats": {
                "Coco": {
                    "activities": [
                        {"name": "sunbathing"},
                        {"name": "brushing"},
                    ]
                },
                "Bobo": {"activities": [{"name": "belly rubs"}]},
                "Jagger": {
                    "activities": [
                        {"name": "shadow prowling"},
                        {"name": "shoulder rides"},
                    ]
                },
            }
        },
    },
    {
        "name": "args_nested_wildcard_fields",
        "input_fields": [
            "args[0].*.color",
            "cats.*.name",
        ],
        "expected_input": {
            "cats": {  # Note: still using "cats" as the key
                "Coco": {"color": "calico", "name": "Coco"},
                "Bobo": {"color": "tuxedo", "name": "Bobo"},
                "Jagger": {"color": "void", "name": "Jagger"},
            }
        },
    },
]

ARGS_TEST_CASES = [
    {
        "name": "multiple_args_selection",
        "input_fields": ["args[0].name", "args[1].color"],
        "args": [CocoCat, BoboCat],
        "expected_input": {"args": [{"name": "Coco"}, {"color": "tuxedo"}]},
    },
    {
        "name": "args_and_kwargs_mixed",
        "input_fields": ["args[0].name", "other_cat.color"],
        "args": [CocoCat],
        "kwargs": {"other_cat": BoboCat},
        "expected_input": {
            "args": [{"name": "Coco"}],
            "kwargs": {"other_cat": {"color": "tuxedo"}},
        },
    },
]

# Add after ARGS_TEST_CASES
ARRAY_TEST_CASES = [
    {
        "name": "array_of_dicts",
        "input_fields": ["cats[*].color", "cats[*].name"],
        "input_data": [
            {"name": "Coco", "color": "calico"},
            {"name": "Bobo", "color": "tuxedo"},
            {"name": "Jagger", "color": "void"},
        ],
        "expected_input": {
            "cats": [
                {"name": "Coco", "color": "calico"},
                {"name": "Bobo", "color": "tuxedo"},
                {"name": "Jagger", "color": "void"},
            ]
        },
    },
    {
        "name": "array_of_objects",
        "input_fields": ["cats[*].(name, color)"],
        "input_data": [CocoCat, BoboCat, JaggerCat],
        "expected_input": {
            "cats": [
                {"name": "Coco", "color": "calico"},
                {"name": "Bobo", "color": "tuxedo"},
                {"name": "Jagger", "color": "void"},
            ]
        },
    },
    {
        "name": "array_nested_fields",
        "input_fields": ["cats[*].activities[*].name"],
        "input_data": [CocoCat, BoboCat, JaggerCat],
        "expected_input": {
            "cats": [
                {"activities": [{"name": "sunbathing"}, {"name": "brushing"}]},
                {"activities": [{"name": "belly rubs"}]},
                {
                    "activities": [
                        {"name": "shadow prowling"},
                        {"name": "shoulder rides"},
                    ]
                },
            ]
        },
    },
    {
        "name": "array_specific_indices",
        "input_fields": ["cats[0].activities[1].name", "cats[2].activities[0].name"],
        "input_data": [CocoCat, BoboCat, JaggerCat],
        "expected_input": {
            "cats": [
                {"activities": [{"name": "brushing"}]},
                # Middle element omitted entirely since it's not selected
                {"activities": [{"name": "shadow prowling"}]},
            ]
        },
    },
]

# If you have protobuf test cases, add them here:
PROTO_ARRAY_TEST_CASES = [
    # Add when proto fixtures are available
]


# Add these dataclass definitions at the top
@dataclass
class Activity:
    name: str
    fun_level: int


MIXED_OBJECTS_TEST_CASES = [
    {
        "name": "dict_of_protos",
        "input_fields": ["data.cats.*.name", "data.cats.*.color"],
        "input_data": {
            "cats": {
                "cat1": CocoProto,
                "cat2": BoboProto,
            }
        },
        "expected_input": {
            "data": {
                "cats": {
                    "cat1": {"name": "Coco", "color": "calico"},
                    "cat2": {"name": "Bobo", "color": "tuxedo"},
                }
            }
        },
    },
    {
        "name": "array_of_protos",
        "input_fields": ["data.cats[*].(name, color)"],
        "input_data": {
            "cats": [
                CocoProto,
                BoboProto,
                JaggerProto,
            ]
        },
        "expected_input": {
            "data": {
                "cats": [
                    {"name": "Coco", "color": "calico"},
                    {"name": "Bobo", "color": "tuxedo"},
                    {"name": "Jagger", "color": "void"},
                ]
            }
        },
    },
    {
        "name": "mixed_dataclass_with_proto",
        "input_fields": [
            "data.*.name",
            "data.*.color",
            "data.*.activities[*].name",
        ],
        "input_data": {"cat1": CocoCat, "cat2": BoboProto, "cat3": JaggerDataclass},
        "expected_input": {
            "data": {
                "cat1": {
                    "name": "Coco",
                    "color": "calico",
                    "activities": [{"name": "sunbathing"}, {"name": "brushing"}],
                },
                "cat2": {
                    "name": "Bobo",
                    "color": "tuxedo",
                    "activities": [{"name": "belly rubs"}],
                },
                "cat3": {
                    "name": "Jagger",
                    "color": "void",
                    "activities": [
                        {"name": "shadow prowling"},
                        {"name": "shoulder rides"},
                    ],
                },
            }
        },
    },
    {
        "name": "array_of_mixed_objects",
        "input_fields": [
            "data.cats[*].(name, color)",
            "data.cats[*].activities",
        ],
        "input_data": {
            "cats": [
                {
                    "name": "Coco",
                    "color": "calico",
                    "activities": CocoProto.activities,
                },
                BoboProto,
            ]
        },
        "expected_input": {
            "data": {
                "cats": [
                    {
                        "name": "Coco",
                        "color": "calico",
                        "activities": (
                            '[name: "sunbathing"\ncuteness: "purrfectly_toasty"\n, '
                            'name: "brushing"\nadorableness: "melts_like_butter"\n]'
                        ),
                    },
                    {
                        "name": "Bobo",
                        "color": "tuxedo",
                        "activities": [
                            {"name": "belly rubs", "goofiness": "rolls_around_happily"}
                        ],
                    },
                ]
            }
        },
    },
    {
        "name": "explicit_nesting_levels",
        "input_fields": ["data.cat.*.name", "data.cat.*.color"],
        "input_data": {
            "cat": {
                "cat1": CocoProto,
                "cat2": BoboProto,
            }
        },
        "expected_input": {
            "data": {
                "cat": {
                    "cat1": {"name": "Coco", "color": "calico"},
                    "cat2": {"name": "Bobo", "color": "tuxedo"},
                }
            }
        },
    },
]

# Test cases for non-serializable objects
NON_SERIALIZABLE_TEST_CASES = [
    {
        "name": "non_serializable_excluded_by_input_fields",
        "description": "Non-serializable parameter excluded via input_fields",
        "input_fields": ["value"],
        "args_data": {"non_serializable": object(), "value": 42},
        "expected_input": {"value": 42},
        "expected_output": 84,
    },
    {
        "name": "multiple_params_one_non_serializable",
        "description": "Multiple parameters, only serializable ones in input_fields",
        "input_fields": ["name", "count"],
        "args_data": {"scene": object(), "name": "test", "count": 5},
        "expected_input": {"name": "test", "count": 5},
        "expected_output": "test-5",
    },
    {
        "name": "nested_field_from_non_serializable_excluded",
        "description": "Nested field access with non-serializable param excluded",
        "input_fields": ["config.value"],
        "args_data": {
            "non_serializable": object(),
            "config": {"value": 100, "extra": "data"}
        },
        "expected_input": {"config": {"value": 100}},
        "expected_output": 100,
    },
]

# Add to existing test cases section
OUTPUT_FIELDS_TEST_CASES = [
    {
        "name": "dict_output_direct_field",
        "output_fields": ["name", "color"],  # Using dot to reference from root
        "return_value": {"name": "Coco", "color": "calico", "extra": "ignored"},
        "expected_output": {
            "name": "Coco",
            "color": "calico",
        },
    },
    {
        "name": "list_output_array_access",
        "output_fields": ["[*].name"],  # Array access from root
        "return_value": [
            {"name": "Coco", "extra": "ignored"},
            {"name": "Bobo", "extra": "ignored"},
        ],
        "expected_output": [
            {"name": "Coco"},
            {"name": "Bobo"},
        ],
    },
    {
        "name": "protobuf_output_direct_field",
        "output_fields": ["name", "color"],  # Direct field access from root
        "return_value": CocoProto,
        "expected_output": {
            "name": "Coco",
            "color": "calico",
        },
    },
    {
        "name": "dataclass_output_nested_field",
        "output_fields": ["activities[*].name"],  # Nested field from root
        "return_value": CocoDataclass,
        "expected_output": {
            "activities": [
                {"name": "sunbathing"},
                {"name": "brushing"},
            ]
        },
    },
    {
        "name": "direct_field_access",
        "output_fields": ["name"],  # Direct field access
        "return_value": {"name": "Coco", "extra": "ignored"},
        "expected_output": {"name": "Coco"},
    },
]


class TestSnapshotFieldSelection:
    def setup_method(self):
        """Setup before each test."""
        setup_debug_dir()
        os.environ["DEBUG"] = "true"

    @pytest.mark.parametrize(
        "test_case",
        SINGLE_INPUT_TEST_CASES,
        ids=[case["name"] for case in SINGLE_INPUT_TEST_CASES],
    )
    @patch("detective.snapshot._generate_short_hash")
    def test_field_selection_dict(self, mock_hash, test_case):
        """Test field selection patterns with dictionary input."""
        mock_hash.return_value = get_test_hash()

        @snapshot(input_fields=test_case["input_fields"])
        def func(cats: dict) -> bool:
            return True

        # Run the function with CatData_dict
        assert func(CatData_dict)

        _, actual_data = get_debug_file(get_test_hash())
        expected_data = {
            "FUNCTION": "func",
            "INPUTS": test_case["expected_input"],
            "OUTPUT": True,
        }
        assert are_snapshots_equal(actual_data, expected_data)

    @pytest.mark.parametrize(
        "test_case",
        ARGS_TEST_CASES,
        ids=[case["name"] for case in ARGS_TEST_CASES],
    )
    @patch("detective.snapshot._generate_short_hash")
    def test_field_selection_args(self, mock_hash, test_case):
        """Test field selection patterns with args/kwargs."""
        mock_hash.return_value = get_test_hash()

        @snapshot(input_fields=test_case["input_fields"])
        def func(*args, **kwargs) -> bool:
            return True

        args = test_case.get("args", [])
        kwargs = test_case.get("kwargs", {})
        assert func(*args, **kwargs)

        _, actual_data = get_debug_file(get_test_hash())
        expected_data = {
            "FUNCTION": "func",
            "INPUTS": test_case["expected_input"],
            "OUTPUT": True,
        }
        assert are_snapshots_equal(actual_data, expected_data)

    # Add new test method for array cases
    @pytest.mark.parametrize(
        "test_case",
        ARRAY_TEST_CASES,
        ids=[case["name"] for case in ARRAY_TEST_CASES],
    )
    @patch("detective.snapshot._generate_short_hash")
    def test_field_selection_arrays(self, mock_hash, test_case):
        """Test field selection patterns with array inputs."""
        mock_hash.return_value = get_test_hash()

        @snapshot(input_fields=test_case["input_fields"])
        def func(cats: List[Any]) -> bool:
            return True

        # Run the function with the test input data
        assert func(test_case["input_data"])

        _, actual_data = get_debug_file(get_test_hash())
        expected_data = {
            "FUNCTION": "func",
            "INPUTS": test_case["expected_input"],
            "OUTPUT": True,
        }
        assert are_snapshots_equal(actual_data, expected_data)

    @pytest.mark.parametrize(
        "test_case",
        MIXED_OBJECTS_TEST_CASES,
        ids=[case["name"] for case in MIXED_OBJECTS_TEST_CASES],
    )
    @patch("detective.snapshot._generate_short_hash")
    def test_field_selection_mixed_objects(self, mock_hash, test_case):
        """Test field selection patterns with mixed object types."""
        mock_hash.return_value = get_test_hash()

        @snapshot(input_fields=test_case["input_fields"])
        def func(data: Any) -> bool:
            return True

        # Run the function with the test input data
        assert func(test_case["input_data"])

        _, actual_data = get_debug_file(get_test_hash())
        expected_data = {
            "FUNCTION": "func",
            "INPUTS": test_case["expected_input"],
            "OUTPUT": True,
        }
        assert are_snapshots_equal(actual_data, expected_data)

    @pytest.mark.parametrize(
        "test_case",
        OUTPUT_FIELDS_TEST_CASES,
        ids=[case["name"] for case in OUTPUT_FIELDS_TEST_CASES],
    )
    @patch("detective.snapshot._generate_short_hash")
    def test_field_selection_outputs(self, mock_hash, test_case):
        """Test field selection patterns for function outputs."""
        mock_hash.return_value = get_test_hash()

        @snapshot(output_fields=test_case["output_fields"])
        def func() -> Any:
            return test_case["return_value"]

        # Run the function with the test input data
        result = func()
        assert result == test_case["return_value"]  # Original function output unchanged

        _, actual_data = get_debug_file(get_test_hash())
        expected_data = {
            "FUNCTION": "func",
            "INPUTS": {},
            "OUTPUT": test_case["expected_output"],
        }
        assert are_snapshots_equal(actual_data, expected_data)

    @patch("detective.snapshot._generate_short_hash")
    def test_instance_method_without_self(self, mock_hash):
        """Test that 'self' is not included when not in input_fields."""
        mock_hash.return_value = get_test_hash()

        class MyClass:
            def __init__(self, a):
                self.a = a

            def instance_method(self, x, y):
                return x + y + self.a

        instance = MyClass(5)

        @snapshot(input_fields=["x"])
        def func(instance, x, y):
            return instance.instance_method(x, y)

        assert func(instance, 10, 20) == 35

        _, actual_data = get_debug_file(get_test_hash())
        expected_data = {
            "FUNCTION": "func",
            "INPUTS": {"x": 10},
            "OUTPUT": 35,
        }
        assert are_snapshots_equal(actual_data, expected_data)

    @patch("detective.snapshot._generate_short_hash")
    def test_class_method_without_cls(self, mock_hash):
        """Test that 'cls' is not included when not in input_fields."""
        mock_hash.return_value = get_test_hash()

        class MyClass:
            class_variable = 10

            @classmethod
            def class_method(cls, x, y):
                return x + y + cls.class_variable

        @snapshot(input_fields=["y"])
        def func(x, y):
            return MyClass.class_method(x, y)

        assert func(5, 15) == 30

        _, actual_data = get_debug_file(get_test_hash())
        expected_data = {
            "FUNCTION": "func",
            "INPUTS": {"y": 15},
            "OUTPUT": 30,
        }
        assert are_snapshots_equal(actual_data, expected_data)

    @patch("detective.snapshot._generate_short_hash")
    def test_omit_self_cls_parameter(self, mock_hash):
        """Test that 'self' and 'cls' can be omitted using include_implicit=False."""
        mock_hash.return_value = get_test_hash()

        class TestClass:
            value = 100

            def __init__(self, x):
                self.x = x

            @snapshot(include_implicit=False)  # Explicitly omit self
            def instance_method(self, y, z):
                return self.x + y + z

            @classmethod
            @snapshot(include_implicit=False)  # Explicitly omit cls
            def class_method(cls, a, b):
                return cls.value + a + b

            @staticmethod
            @snapshot()  # No change for static methods
            def static_method(p, q):
                return p * q

        # Create instance and call methods
        instance = TestClass(10)

        # Test instance method
        result1 = instance.instance_method(20, 30)
        assert result1 == 60  # 10 + 20 + 30

        # Get debug file and check contents
        _, actual_data1 = get_debug_file(get_test_hash())
        expected_data1 = {
            "FUNCTION": "instance_method",
            "INPUTS": {
                # 'self' should be omitted
                "y": 20,
                "z": 30,
            },
            "OUTPUT": 60,
        }
        assert are_snapshots_equal(actual_data1, expected_data1)

        # Reset hash for next test
        mock_hash.return_value = get_test_hash("second")

        # Test class method
        result2 = TestClass.class_method(50, 60)
        assert result2 == 210  # 100 + 50 + 60

        # Get debug file and check contents
        _, actual_data2 = get_debug_file(get_test_hash("second"))
        expected_data2 = {
            "FUNCTION": "class_method",
            "INPUTS": {
                # 'cls' should be omitted
                "a": 50,
                "b": 60,
            },
            "OUTPUT": 210,
        }
        assert are_snapshots_equal(actual_data2, expected_data2)

        # Reset hash for next test
        mock_hash.return_value = get_test_hash("third")

        # Test static method
        result3 = TestClass.static_method(7, 8)
        assert result3 == 56  # 7 * 8

        # Get debug file and check contents
        _, actual_data3 = get_debug_file(get_test_hash("third"))
        expected_data3 = {
            "FUNCTION": "static_method",
            "INPUTS": {"p": 7, "q": 8},
            "OUTPUT": 56,
        }
        assert are_snapshots_equal(actual_data3, expected_data3)

    @patch("detective.snapshot._generate_short_hash")
    def test_explicit_self_with_implicit_false(self, mock_hash):
        """Test that self is included when explicitly requested, even with include_implicit=False."""
        mock_hash.return_value = get_test_hash()

        class CatHandler:
            def __init__(self, cat: Cat):
                self.cat = cat
                self.id = "handler123"

            @snapshot(
                input_fields=["self.id", "name"],  # Explicitly request self.id
                include_implicit=False  # But don't include implicit self
            )
            def rename_cat(self, name: str) -> Dict[str, str]:
                return {"handler": self.id, "old_name": self.cat.name, "new_name": name}

        handler = CatHandler(CocoDataclass)
        result = handler.rename_cat("Luna")

        assert result == {"handler": "handler123", "old_name": "Coco", "new_name": "Luna"}

        _, actual_data = get_debug_file(get_test_hash())
        expected_data = {
            "FUNCTION": "rename_cat",
            "INPUTS": {
                "self": {"id": "handler123"},  # self.id is included because it was requested
                "name": "Luna"  # Other args are included normally
            },
            "OUTPUT": {
                "handler": "handler123",
                "old_name": "Coco",
                "new_name": "Luna"
            }
        }
        assert are_snapshots_equal(actual_data, expected_data)

    @patch("detective.snapshot._generate_short_hash")
    def test_implicit_self_included(self, mock_hash):
        """Test that self is included when include_implicit=True, even if not in input_fields."""
        mock_hash.return_value = get_test_hash()

        class CatHandler:
            def __init__(self, cat: Cat):
                self.cat = cat
                self.id = "handler123"
                self.prefix = "CAT-"

            @snapshot(
                input_fields=["name"],  # Don't explicitly request any self fields
                include_implicit=True  # But include implicit self
            )
            def generate_id(self, name: str) -> str:
                return f"{self.prefix}{name}-{self.id}"

        handler = CatHandler(CocoDataclass)
        result = handler.generate_id("Luna")

        assert result == "CAT-Luna-handler123"

        _, actual_data = get_debug_file(get_test_hash())
        expected_data = {
            "FUNCTION": "generate_id",
            "INPUTS": {
                "self": {  # All of self should be included
                    "cat": CocoDataclass.to_dict(),
                    "id": "handler123",
                    "prefix": "CAT-"
                },
                "name": "Luna"
            },
            "OUTPUT": "CAT-Luna-handler123"
        }
        assert are_snapshots_equal(actual_data, expected_data)

    @pytest.mark.parametrize(
        "test_case",
        NON_SERIALIZABLE_TEST_CASES,
        ids=[case["name"] for case in NON_SERIALIZABLE_TEST_CASES],
    )
    @patch("detective.snapshot._generate_short_hash")
    def test_non_serializable_objects(self, mock_hash, test_case):
        """Test that non-serializable parameters are handled when excluded via input_fields."""
        mock_hash.return_value = get_test_hash()

        # Create test functions based on the test case
        if test_case["name"] == "non_serializable_excluded_by_input_fields":
            @snapshot(input_fields=test_case["input_fields"])
            def func(non_serializable, value):
                return value * 2

            result = func(**test_case["args_data"])

        elif test_case["name"] == "multiple_params_one_non_serializable":
            @snapshot(input_fields=test_case["input_fields"])
            def func(scene, name, count):
                return f"{name}-{count}"

            result = func(**test_case["args_data"])

        elif test_case["name"] == "nested_field_from_non_serializable_excluded":
            @snapshot(input_fields=test_case["input_fields"])
            def func(non_serializable, config):
                return config["value"]

            result = func(**test_case["args_data"])

        # Verify the function returned the expected result
        assert result == test_case["expected_output"]

        # Verify snapshot was created with correct data
        _, actual_data = get_debug_file(get_test_hash())
        expected_data = {
            "FUNCTION": "func",
            "INPUTS": test_case["expected_input"],
            "OUTPUT": test_case["expected_output"],
        }
        assert are_snapshots_equal(actual_data, expected_data)
