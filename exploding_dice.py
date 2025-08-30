import random

def roll(dicestring="1d6") -> (int,str):
    """
    get a dicestring and returns result (int) and details (text)
    d.... normal die
    D.....exploding die

    examples:
    1d6 ..... roll one six-sided die
    2d6 ..... roll two six-sided dice (and add the results)
    1d20 .... roll one 20-sided die

    1D6 ..... roll one six sided "exploding" die. If you roll a 6,
              add 5 to the result and roll again.
              If you roll another 6, add 5 to the result and
              roll again and so on ...

    1d6+4 ... roll one six-sided die and add 4 to the result
    1d20-2 .. roll one 20-sided die and subtract 2 from the result
    1D6+8 ..... roll one six-sided "exploding" die,
                add 8 to the final result

    1d6+2 ... roll one six-sided die and add 2 to the result
    2D6-10 .. roll two six-sided exploding dice and subtract 10 from
              the final result
    """

    # guardians, checking if dicestring is valid
    if "d" not in dicestring.lower():
        raise ValueError("neither 'd' nor 'D' found in dicestring", dicestring)
    if dicestring.lower().count("d") > 1:
        raise ValueError("more than one 'd'(or 'D') found inside dicestring", dicestring)
    # fix part?
    if ("+" in dicestring) or ("-" in dicestring):
        if dicestring.count("+") > 1:
            raise ValueError("more than one + sign found inside dicestring", dicestring)
        if dicestring.count("-") > 1:
            raise ValueError("more than one - sign found inside dicestring", dicestring)
        if "+" in dicestring:
            sign = "+"
            first, second = dicestring.split("+")
        else:
            sign = "-"
            first, second = dicestring.split("-")
        if not second.isnumeric():
            raise ValueError("non-numeric char found after +/- sign", dicestring)
        dice, sides = first.lower().split("d")
        fix_part = int(second)
    else:
        dice, sides = dicestring.lower().split("d")
        fix_part = 0
    if not (dice.isnumeric() and sides.isnumeric()):
        raise ValueError("non-numeric char (except 'd'/'D') found in dicestring", dicestring)

    # repeat (exploding dice) ?
    #if "d" in dicestring:
    repeat = False
    if "D" in dicestring:
        repeat = True
    dice = int(dice)
    sides = int(sides)
    resultstring = ""
    result = 0
    for i in range(dice):
        x = random.randint(1, sides)
        while repeat and (x == sides):
            result += (x - 1)
            resultstring += f"({x}-1)+"
            x = random.randint(1, sides)
        resultstring += f"{x}"
        if i < dice - 1:
            resultstring += "+ "
        result += x
    resultstring += f"= {result}"
    if fix_part != 0:
        if sign == "+":
            resultstring += sign + second + "=" + str(result + fix_part)
            result += fix_part
        else:
            resultstring += sign + second + "=" + str(result - fix_part)
            result -= fix_part
    return result, resultstring

if __name__ == "__main__":
    # testing
    for _ in range(20):
        dice = random.randint(1,6)
        sides = random.choice((4,6,6,6,8,20,20))
        char = random.choice(("d","d","d","D","D"))
        sign = random.choice(("+","-",None,None,None,None))
        extra = random.randint(1,20)
        text = f"{dice}{char}{sides}"
        if sign is not None:
            text += f"{sign}{extra}"
        print(f"{text}: {roll(text)}")
