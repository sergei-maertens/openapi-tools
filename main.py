#!/usr/bin/env python
import openapi_tools

OZ_SPEC = "assets/oz-zaken.yaml"
VNG_SPEC = "assets/vng-zaken.yaml"


def main():
    openapi_tools.compare(OZ_SPEC, VNG_SPEC)


if __name__ == "__main__":
    main()
