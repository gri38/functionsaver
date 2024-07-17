# function saver

**⚠ ⚠ ⚠ ⚠ WORK IN PROGRESS ⚠ ⚠ ⚠ ⚠**

This package provides a decorator to **save the function inputs, output and intermediate values** to a file.  
It also provides a function to **replay the function** with the same inputs and compare the output with the saved one.

That's useful to:
- debug a function
- easily generate tests data
- easily code non-regression tests
- get data to analyze the function behavior

## Please: feedbacks, issues, MRs are welcome

Today the package supports:
- sync / async functions
- mutlithreaded / multitasking
- numpy arrays serialization
- jsons serialization for common types
- args, kwargs, default args:
  ```python
  # with:
  @function_saver
  def my_function(a, b, c=1):
      ...
  
  # all those syntaxes work:
  my_fonction(1, 2, c=3)
  my_function(1, 2, 3)
  my_function(1, 2)
  ````
- function save and replay from classes' methods

It has not been used intensively yet, so we are looking for feedbacks, issues, side-effects, MRs, etc...

## Installation

### pip

```shell
pip install functionsaver
```

### In your Pipfile

```toml
[packages]
functionsaver = "==x.y.*"
```

## How to... for hurry developers

### Note to hurry developers:

Dear hurry developers, please note the following requirement:  
👉 **for the saved data to be replayable (function inputs and outputs), if these data are classes, 
all serialized members must be present in the constructor.**  
Otherwise, a ReplayException will be raised. A good practice is to use [dataclass](https://docs.python.org/3/library/dataclasses.html).

```python
from functionsaver import function_saver

@function_saver  # <====== This is the magic line
def my_function(a, b):
    my_function.save_internals(a - b, "substraction")
    return a + b
```
**THAT'S ALL** ! The magic is done... or almost (see below to enable the magic with environment variables).

```python
my_function(1, 2)
```
That will produce:
![image](./readme_ressources/01.png)

## Another example with class

👉 **Limitation: the object itslef is not saved, only its members.  
So you can replay 'static' methods only (or you need to recreate an object with same attributes).  
If you need better: ask**

````python
from functionsaver import function_saver, replay_and_check_function

class MyClass:

    @function_saver  # ⚠ self is not saved, only a, b and the output
    def my_method(self, a, b):
        return a + b
    
    @function_saver(save_in=False, save_out=False)
    def another_method(self, a, b):
        # ... instructions with self...
        self.another_method.save_internals(something, "something")
        # ...
        
my_instance = MyClass()
my_instance.my_method(1, 2)
my_instance.another_method(3, 4)

another_instance_to_replay = MyClass()
replay_and_check_function(another_instance_to_replay.my_method, "path_to_saved_data")
````

## An async example

```python
from functionsaver import function_saver
from functionsaver.function_saver import replay_and_check_function_async
import asyncio

@function_saver
async def my_async_function(a, b):
    await my_async_function.save_internal_async(a - b, "substraction")
    return a + b


async def main():
    await my_async_function(1, 2)
    ...
    function_saver_path = "path_to_saved_data"
    await replay_and_check_function_async(my_async_function, function_saver_path)

    
if __name__ == "__main__":
    asyncio.run(main())
```

## Another example for our friends from Algo team (they like np.array 😖)

```python
import numpy as np
from functionsaver import function_saver

@function_saver
def mirror_image(image):
    return np.flip(image, axis=1)

url = "https://upload.wikimedia.org/wikipedia/en/7/7d/Lenna_%28test_image%29.png"
response = requests.get(url)
img = Image.open(BytesIO(response.content))
lena = np.array(img)

mirror_image(lena)
```
That will produce:  
![image](./readme_ressources/02.png)

## Decorator parameters

function_save decorator can be used with or without parameters:
* save_in: save the inputs (default is True)
* save_out: save the output (default is True)
* save_internals: save the internals (default is False)

Here is an example with parameters:
```python
@function_saver(save_in=False, save_out=False)  # <====== Only save the internals
def my_function(a, b):
    ...
```

Here is an axemple without parameters:
```python
@function_saver  # <====== Save the inputs, output and internals
def my_function(a, b):
    ...
```

👉 **Use is_save_internal_enabled to save time**  
If save_internals is not enabled, you don't want to spend time to generate the internals.  
save_internal is optimized: it immediately returns if save_internals is not enabled.  
But you can use is_save_internal_enabled to avoid generating the internals at all.
```python
@function_saver
def my_function(a, b):
    if my_function.is_save_internal_enabled():
        data = long_computation_function(a, b)
        my_function.save_internals(data, "data")
```

## Enable the magic with environment variables

Saving the function calls can be enabled/disabled with environment variables.

### Global impact (all the decorated functions)

* FUNCTION_SAVER_ALL = 1: enable the saving of inputs output all the decorated functions
* FUNCTION_SAVER_INTERNALS_ALL = 1: enable the saving of internals all the decorated functions
* FUNCTION_SAVER_LOG = 1: verbose logging of the function saver
* FUNCTION_SAVER_ROOT_PATH = "path": set the root path where the function calls will be saved
  * default is: OS temp folder / function_saver

### Per function impact

For a function named
```python
def my_function(...):
    ...
```
* FUNCTION_SAVER_MY_FUNCTION = 1: enable the saving of inputs output for this function
* FUNCTION_SAVER_INTERNALS_MY_FUNCTION = 1: enable the saving of internals for this function

## The serializers

The default serializer is [jsons](https://github.com/ramonhagenaars/jsons), and np.save/load for numpy arrays.  
Another serializer is provider for numpy arrays, to save them as png files.

👉 **You control how the args or output are serialized by typing them.**  
Example:
```python
from functionsaver import function_saver, SerializeAsArrayPng
import numpy as np


@function_saver
def mirror_image(image: np.ndarray | SerializeAsArrayPng) -> np.ndarray | SerializeAsArrayPng:
    return np.flip(image, axis=1)
```
That will produce:  
![image](./readme_ressources/03.png)

### The serializers are "by type and extension"

As implemented today we have those links:
* one type => one serializer + one extension
* one extension => one deserializer + one type

### Write and register your own serializer

You can write your own serializer and register it.  
Do it by following the example of functionsaver/serializers.py
* Define a serialization and deserialization function
* Create a type starting with SerializeAs...
* call register_serializer

If your newly created serializer manages a widely used type, we encourage you to submit a merge request to incorporate it into the package.

## Replay and check

Once you have saved some function calls, you can replay them and check the output.  
```python
from functionsaver import function_saver, replay_function, replay_and_check_function

@function_saver
def my_function(a, b):
    return a + b + 1  #  <===== let's introduce a change

replay_folder = Path(r"c:\...\my_function_reference")
res = replay_function(my_function, replay_folder)  # <===== This will replay the function from the saved inputs: res == 4
replay_and_check_function(my_function, replay_folder)  # <===== This will replay the function and check the output, here saved output is 3, so it will raise an exception:
# "AssertionError: Output does not match the expected output: 4 != 3"
```


* 👉  **When replaying a function, the "function_save" saves internal|output in internal|output_replay folder, only if internal|output were saved.****
* 👉 **Only one replay folder: replaying again will erase the previous replayed data.**

## Conclusion

This package is a powerful tool for developers, providing the ability to save, replay, and check function calls.   
It's particularly useful for
* debugging
* generating test data
* coding non-regression tests
* analyzing function behavior.

With its easy-to-use decorators and flexible serializer system, it can be seamlessly integrated into your unit tests. We hope you find it as useful as we do.

Happy coding! 🤩 🥳
