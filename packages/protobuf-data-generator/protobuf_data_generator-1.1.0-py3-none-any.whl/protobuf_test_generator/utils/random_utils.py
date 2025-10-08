from random import randint, choice, random
import string


def random_int(min_value, max_value):
    return randint(min_value, max_value)


def random_float(min_value, max_value):
    return min_value + (max_value - min_value) * random()


def random_string(length):
    letters = string.ascii_letters
    return "".join(choice(letters) for _ in range(length))


def random_boolean():
    return choice([True, False])


def random_list(element_generator, min_items, max_items):
    size = randint(min_items, max_items)
    return [element_generator() for _ in range(size)]
