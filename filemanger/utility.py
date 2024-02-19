import re


def get_class_collection_name(qualified_class_name):
    # Remove the specific prefix and replace periods with dashes
    temp_name = qualified_class_name.replace("com.intesasanpaolo.bear.sxdr0.metaconto", "").replace(".", "-")

    # Ensure the name starts with a lowercase letter or digit
    if not re.match("^[a-z0-9]", temp_name):
        temp_name = "a" + temp_name  # Prefix with 'a' to ensure it starts correctly

    # Ensure the name ends with a lowercase letter or digit
    if not re.match("[a-z0-9]$", temp_name):
        temp_name += "1"  # Suffix with '1' to ensure it ends correctly

    # Adjust the length to be between 3 and 63 characters
    if len(temp_name) > 63:
        temp_name = temp_name[:63]  # Trim to the max length if necessary
    elif len(temp_name) < 3:
        temp_name += "a1"  # Add characters to meet the min length if necessary

    return temp_name
