import math
from pathlib import Path
from gnps import GnpsSystem
from gnps.parser.ast.value import FloatValue
from gnps.parser.ast.expression import ConstantExpression
from gnps.rule import Rule
from gnps.parser.ast.variable import Variable

def test_math_functions():
    p = Path(__file__).resolve().parent
    gnps = GnpsSystem.from_yaml(f"{p}/test_math_functions.yaml")

    # Verify the system was loaded correctly
    assert len(gnps.cells) == 1
    assert len(gnps.rules) == 6

    # Get all variables
    x = gnps.get_variable("x")
    y = gnps.get_variable("y")
    z = gnps.get_variable("z")
    a = gnps.get_variable("a")
    b = gnps.get_variable("b")
    c = gnps.get_variable("c")
    trigResult = gnps.get_variable("trigResult")
    powerResult = gnps.get_variable("powerResult")
    nestedResult = gnps.get_variable("nestedResult")
    standardFuncResult = gnps.get_variable("standardFuncResult")
    complexResult = gnps.get_variable("complexResult")
    step = gnps.get_variable("step")

    # Verify initial values
    assert x.value.value == 2.0
    assert y.value.value == 3.0
    assert z.value.value == 4.0

    # Check dependencies were properly initialized
    assert abs(a.value.value - math.sin(2.0)) < 1e-10, f"Expected a = sin(x) = {math.sin(2.0)}, got {a.value.value}"
    assert abs(b.value.value - math.pow(3.0, 2)) < 1e-10, f"Expected b = pow(y,2) = {math.pow(3.0, 2)}, got {b.value.value}"
    assert abs(c.value.value - (math.sin(2.0) + math.pow(3.0, 2))) < 1e-10, f"Expected c = a + b = {math.sin(2.0) + math.pow(3.0, 2)}, got {c.value.value}"

    # Verify result variables are initialized to zero
    assert trigResult.value.value == 0.0
    assert powerResult.value.value == 0.0
    assert nestedResult.value.value == 0.0
    assert standardFuncResult.value.value == 0.0
    assert complexResult.value.value == 0.0
    assert step.value.value == 0.0

    # Store original values for validation
    x_orig = x.value.value  # 2.0
    y_orig = y.value.value  # 3.0
    z_orig = z.value.value  # 4.0
    a_orig = a.value.value  # sin(2.0)
    b_orig = b.value.value  # pow(3.0, 2) = 9.0
    c_orig = c.value.value  # sin(2.0) + 9.0

    # Calculate expected results for the first step
    expected_trig = math.sin(x_orig) * math.cos(y_orig)
    expected_power = math.pow(a_orig, b_orig)
    expected_nested = math.sqrt(math.pow(math.sin(x_orig), 2) + math.pow(math.cos(y_orig), 2))
    expected_standard = max(x_orig, y_orig, z_orig) - min(x_orig, y_orig, z_orig)
    expected_complex = math.sqrt(c_orig*c_orig + z_orig*z_orig) + round(math.pi)
    expected_step = 1.0  # This is an increment from 0

    # Run the first step
    gnps.step()

    # Check that variables used in rules were reset to zero
    assert x.value.value == 0.0, f"x should be reset to 0, got {x.value.value}"
    assert y.value.value == 0.0, f"y should be reset to 0, got {y.value.value}"
    assert z.value.value == 0.0, f"z should be reset to 0, got {z.value.value}"
    assert a.value.value == 0.0, f"a should be reset to 0, got {a.value.value}"
    assert b.value.value == 0.0, f"b should be reset to 0, got {b.value.value}"
    assert c.value.value == 0.0, f"c should be reset to 0, got {c.value.value}"

    # Step is a special case - it's used in a rule but then incremented to 1.0
    assert step.value.value == 1.0, f"step should be 1.0 after first step, got {step.value.value}"

    # Check that result variables received the correct values
    # Result variables (consumers) get the computed values added to their existing values (which were 0)
    assert abs(trigResult.value.value - expected_trig) < 1e-10, f"Expected trigResult = {expected_trig}, got {trigResult.value.value}"
    assert abs(powerResult.value.value - expected_power) < 1e-10, f"Expected powerResult = {expected_power}, got {powerResult.value.value}"
    assert abs(nestedResult.value.value - expected_nested) < 1e-10, f"Expected nestedResult = {expected_nested}, got {nestedResult.value.value}"
    assert abs(standardFuncResult.value.value - expected_standard) < 1e-10, f"Expected standardFuncResult = {expected_standard}, got {standardFuncResult.value.value}"
    assert abs(complexResult.value.value - expected_complex) < 1e-10, f"Expected complexResult = {expected_complex}, got {complexResult.value.value}"

    # For the second step, all input variables are now zero:
    expected_trig_step2 = math.sin(0.0) * math.cos(0.0)  # 0.0
    expected_power_step2 = math.pow(0.0, 0.0)  # 1.0 (special case in math)
    expected_nested_step2 = math.sqrt(math.pow(math.sin(0.0), 2) + math.pow(math.cos(0.0), 2))  # 1.0
    expected_standard_step2 = max(0.0, 0.0, 0.0) - min(0.0, 0.0, 0.0)  # 0.0
    expected_complex_step2 = math.sqrt(0.0*0.0 + 0.0*0.0) + round(math.pi)  # 3.0
    expected_step_step2 = 2.0  # Step should be incremented to 2.0 in the second step

    # Store current result values before second step
    trigResult_after_step1 = trigResult.value.value
    powerResult_after_step1 = powerResult.value.value
    nestedResult_after_step1 = nestedResult.value.value
    standardFuncResult_after_step1 = standardFuncResult.value.value
    complexResult_after_step1 = complexResult.value.value

    # Run the second step
    gnps.step()

    # Check that step incremented to 2.0
    assert step.value.value == 2.0, f"step should be 2.0 after second step, got {step.value.value}"

    # For the second step, the consumer variables should have the new values ADDED to their previous values
    assert abs(trigResult.value.value - (trigResult_after_step1 + expected_trig_step2)) < 1e-10
    assert abs(powerResult.value.value - (powerResult_after_step1 + expected_power_step2)) < 1e-10
    assert abs(nestedResult.value.value - (nestedResult_after_step1 + expected_nested_step2)) < 1e-10
    assert abs(standardFuncResult.value.value - (standardFuncResult_after_step1 + expected_standard_step2)) < 1e-10
    assert abs(complexResult.value.value - (complexResult_after_step1 + expected_complex_step2)) < 1e-10

    # Let's demonstrate the summing behavior with a new test
    # Create a new variable that we won't use in any rules (it should keep its value)
    unused_var = Variable("unused", FloatValue(42.0))
    gnps.variables[unused_var.name] = unused_var

    # Add a new rule that targets an existing consumer (trigResult)
    # This will demonstrate the summing behavior for consumers
    new_rule = Rule(
        consumer=trigResult,
        producer=ConstantExpression(FloatValue(5.0)),
        guard=gnps.rules[0].guard
    )
    gnps.add_rule(new_rule)

    # Store the current value of trigResult
    trigResult_before_step3 = trigResult.value.value

    # Run another step
    gnps.step()

    # The unused_var should keep its value (it's not used in any rules)
    assert unused_var.value.value == 42.0, f"Unused variable should keep its value, got {unused_var.value.value}"

    # The trigResult should have both rule results summed to its previous value
    # Expected: previous_value + sin(0)*cos(0) + 5.0 = previous_value + 0.0 + 5.0
    expected_trigResult_summed = trigResult_before_step3 + 0.0 + 5.0
    assert abs(trigResult.value.value - expected_trigResult_summed) < 1e-10, f"Expected summed trigResult = {expected_trigResult_summed}, got {trigResult.value.value}"
