from typing import Type, TypeVar, Any
from shua.struct.field import FieldProtocol

class BinaryMeta(type):
    def __new__(cls, name, bases, namespace):
        fields = {}
        annotations = namespace.get('__annotations__', {})
        
        for field_name, field_type in annotations.items():
            default = namespace.get(field_name, None)
            fields[field_name] = (field_type, default)
        
        namespace['_fields_info'] = fields
        return super().__new__(cls, name, bases, namespace)

T = TypeVar('T', bound='BinaryStruct')

class BinaryStruct(metaclass=BinaryMeta):
    def __init__(self, **kwargs):
        for field_name, (field_type, default) in self._fields_info.items():
            value = kwargs.get(field_name, default)
            
            if value is default and value is None:
                if isinstance(field_type, FieldProtocol):
                    value = field_type()
                elif issubclass(field_type, BinaryStruct):
                    value = field_type()
            elif value is default and default is not None:
                value = default
            else:
                if isinstance(field_type, FieldProtocol):
                    if not isinstance(value, field_type):
                        value = field_type(value)
                elif issubclass(field_type, BinaryStruct):
                    if isinstance(value, dict):
                        value = field_type(**value)
                    elif not isinstance(value, field_type):
                        raise TypeError("Type mismatch")
                    elif isinstance(value, field_type):
                        pass
                    else:
                        raise RuntimeError("Unhandled value")
            setattr(self, field_name, value)

    @classmethod
    def parse(cls: Type[T], data: bytes, context: dict | None = None) -> T:
        if context is None:
            context = {}
        ctx = context.copy()
        offset = 0
        obj_kwargs = {}
        
        for name, (field_type, default) in cls._fields_info.items():
            field_length = cls._get_field_length(name, field_type, default, ctx, data, offset)
            field_data = data[offset:offset + field_length]
            
            value = cls._parse_field_value(name, field_type, default, field_data, ctx)
            
            offset += field_length
            ctx[name] = value
            obj_kwargs[name] = value
        
        return cls(**obj_kwargs)

    @classmethod
    def _get_field_length(cls, name: str, field_type: Any, default: Any, 
                         context: dict, data: bytes, offset: int) -> int:
        if default is not None and hasattr(default, 'get_length'):
            return default.get_length(context)
        elif hasattr(field_type, 'size'):
            return field_type.size
        elif issubclass(field_type, BinaryStruct):
            temp_obj = field_type.parse(data[offset:], context)
            built_data = temp_obj.build(context)
            return len(built_data)
        else:
            return len(data) - offset

    @classmethod
    def _parse_field_value(cls, name: str, field_type: Any, default: Any, 
                          data: bytes, context: dict) -> Any:

        if default is not None and hasattr(default, 'parse'):
            return default.parse(data, context)
        elif isinstance(field_type, FieldProtocol):
            return field_type.parse(data, context)
        elif issubclass(field_type, BinaryStruct):
            return field_type.parse(data, context)
        else:
            return data

    def build(self, context: dict | None = None) -> bytes:
        if context is None:
            context = {}
        result = []
        ctx = context.copy()
        
        for name, (field_type, default) in self._fields_info.items():
            value = getattr(self, name)
            built_data = self._build_field_value(name, value, field_type, ctx)
            result.append(built_data)
        
        return b''.join(result)

    def _build_field_value(self, name: str, value: Any, field_type: Any, context: dict) -> bytes:
        if hasattr(value, 'build'):
            return value.build(context)
        elif isinstance(value, bytes):
            return value
        else:
            raise TypeError(f"Cannot build field {name}: {value}")

    def __repr__(self):
        fields = []
        for name, (field_type, default) in self._fields_info.items():
            value = getattr(self, name)
            fields.append(f"{name}={value!r}")
        return f"{self.__class__.__name__}({', '.join(fields)})"

    def __getitem__(self, key):
        return getattr(self, key)

__all__ = ["BinaryStruct"]