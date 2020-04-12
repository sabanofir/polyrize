from dataclasses import dataclass


class MagicList(list):
    def __init__(self, cls_type, *args, **kwargs):
        super(MagicList, self).__init__(*args, **kwargs)
        self._cls_type = cls_type

    def __getitem__(self, item):
        # Check that the item indicated is index exist and index is available.
        if isinstance(item, int) and len(self) == item:
            # Initialize the object
            self.append(self._cls_type())
            return super(MagicList, self).__getitem__(item)
        return super(MagicList, self).__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(value, self._cls_type) and len(self) == key:
            self.append(value)
        else:
            super(MagicList, self).__setitem__(key, value)


@dataclass
class Person:
    age: int = 1


def main():
    a = MagicList(cls_type=Person)
    a[0].age = 6
    print(a[0])


if __name__ == '__main__':
    main()
