#!/usr/bin/env python
import openapi_tools

OZ_SPEC = "assets/oz-zaken.yaml"
VNG_SPEC = "assets/vng-zaken.yaml"

TEST_SPEC1 = "assets/test.yaml"
TEST_SPEC2 = "assets/test2.yaml"


def main():
    openapi_tools.compare(TEST_SPEC1, TEST_SPEC2)


if __name__ == "__main__":
    main()
