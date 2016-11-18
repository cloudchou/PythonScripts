# -*- coding: utf-8 -*-
import demjson


def main():
    data = [{'a': 'A', 'b': (2, 4), 'c': 3.0}]
    print(demjson.encode(data, encoding='utf-8', indent_amount=2, compactly=False))


if __name__ == '__main__':
    main()
