import setuptools

setuptools.setup(
    packages=setuptools.find_packages(exclude=["tests", "tests.*"]),
    test_suite="tests",
    zip_safe=False,
)
