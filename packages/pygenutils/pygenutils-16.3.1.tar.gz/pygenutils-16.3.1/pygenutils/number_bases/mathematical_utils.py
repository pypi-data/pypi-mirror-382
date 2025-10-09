# Import modules #
#----------------#

from math import factorial

# Define functions #
#------------------#

def adapted_factorial(num, significant_digits):
    """
    Calculate the factorial of a number with precise formatting control.
    
    For standard-sized results, formats the output using the specified precision.
    For extremely large factorials that would cause an OverflowError during formatting,
    converts the result to scientific notation with appropriate rounding.
    
    Parameters
    ----------
    num : int | float
        The number for which to calculate the factorial
    significant_digits : int
        The number of significant digits to include in the result
    
    Returns
    -------
    result_adapted : str
        The formatted factorial result as a string, either in standard or
        scientific notation depending on the magnitude
             
    Raises
    ------
    TypeError
        If the input is not an integer or float
    """
    # Validate input
    if not isinstance(num, (int, float)):
        raise TypeError("Input must either be an integer or a float")
    
    # Calculate factorial
    result = factorial(num)

    try:
        result = f"{result:.{significant_digits}g}"
    except OverflowError:
        # Convert to string and round to the desired significant digits
        result_str = str(result)
        # Take into account the number next to the significant digits position
        if int(result_str[significant_digits]) >= 5:
            prev_num = int(result_str[significant_digits-1]) + 1
        else:
            prev_num = int(result_str[significant_digits-1])
        # Convert to float
        result_adapted = f"{result_str[0]}.{result_str[1:significant_digits-1]}{prev_num}e+{len(result_str)-1}"
    else:
        result_adapted = result
    
    # Return result
    return result_adapted