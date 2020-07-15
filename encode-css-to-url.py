#!/usr/bin/python3

from urllib.parse import quote


file = open(input("Enter name of css file: "), "r")
css = file.read()
file.close()
print(quote(css))
