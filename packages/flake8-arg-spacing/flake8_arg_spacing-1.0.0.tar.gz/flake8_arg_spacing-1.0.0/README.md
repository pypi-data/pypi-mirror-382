flake8-arg-spacing
==================

[![pypi](https://img.shields.io/pypi/v/flake8-arg-spacing.svg)](https://pypi.org/project/flake8-arg-spacing/)

When applying the standard formatting rules of Python, it's easy to end up with code like below,
where spacing obscures the actual operator precedence:

```py
foo(bar=a + b)
# or
Order.objects.filter(timestamp__gt=timezone.now() - timedelta(minutes=30))
```

This plugin reports such patterns in function calls and definitions. You may want to:

* remove spaces around the binary operator:
```py
foo(bar=a+b)
```

* add parentheses around the expression:
```py
foo(bar=(a + b))
```

* create a separate variable for the expression:
```py
c = a + b
foo(bar=c)
```

* or add spaces around the equals sign:
```py
foo(bar = a + b)  # incompatible with PEP 8
```

Included rules
--------------

* `ARG101` - confusing spacing around keyword argument
* `ARG102` - confusing spacing around parameter default
