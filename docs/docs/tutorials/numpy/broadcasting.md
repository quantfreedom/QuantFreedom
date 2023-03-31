# Broadcasting
I will be going over all things broadcasting in this section

## np.broadcast_to
### Youtube Tutorial
https://youtu.be/2rZnShOh9as
### Offical numpy doc link
Check offical doc link for proper syntax:
https://numpy.org/doc/stable/reference/generated/numpy.broadcast_to.html

### Example 1
```pycon
>>> import numpy as np
>>> a = np.array([2,3,4])
>>> np.broadcast_to(a, (3, 3))
array([[2, 3, 4],
       [2, 3, 4],
       [2, 3, 4]])
```
In the above code, an array 'a' is created with the values [2, 3, 4]. The numpy.broadcast_to() function is then used to create a new array with shape (3, 3) by repeating the values of 'a'. The resulting array has the values [[2, 3, 4], [2, 3, 4], [2, 3, 4]].

![yes](np_assets/numpy-manipulation-broadcast-to-function-image-1.png)

### Example 2
another example is if we wanted to take a scaler aka just a number and broadcast it to an array of a specific shape.
```pycon
>>> np.broadcast_to(5, (2,5))     
array([[5, 5, 5, 5, 5],
       [5, 5, 5, 5, 5]])
```
here you can see we took the number 5 and broadcast it to 2 rows and 5 columns

also you have to make sure that you are broadcasting to a shape that works mathematically as in you can't take a shape that has 1 rows and 2 columns and broadcast it to (3,3) that math just doesn't work out