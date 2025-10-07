__all__ = ['Uuid']

from uuid import UUID

from nuql import resources


class Uuid(resources.FieldBase):
    type = 'uuid'

    def serialise(self, value: UUID | str | None) -> str | None:
        """
        Serialises a UUID value.

        :arg value: UUID, str or None.
        :return: str or None.
        """
        try:
            if not value:
                return None
            if isinstance(value, str):
                value = UUID(value)
            return str(value)
        except (AttributeError, ValueError, TypeError) as e:
            return None

    def deserialise(self, value: str | None) -> str | None:
        """
        Deserialises a UUID value (only to string).

        :arg value: str or None.
        :return: str or None.
        """
        if isinstance(value, str):
            try:
                return str(UUID(value))
            except (AttributeError, ValueError, TypeError):
                return None
        return None
