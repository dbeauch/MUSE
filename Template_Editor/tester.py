from mendeleev import element


def zaid_to_isotope(zaid):
    zaid_str = str(zaid)

    if len(zaid_str) != 5:
        return 'Invalid ZAID'

    element_number = int(zaid_str[:2])
    isotope_number = int(zaid_str[2:])

    element_name = element(element_number).symbol
    return f'{element_name}-{isotope_number}'
