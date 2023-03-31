# Logical
Here we will be going over different functions that test if something is true or false

## np.where
### Youtube video
https://youtu.be/-oMjyoQhvCY
### Offical Doc Link
Check offical doc link for proper syntax:
https://numpy.org/doc/stable/reference/generated/numpy.where.html

### Import and Create
```pycon
>>> import numpy as np
>>> rand = np.random.randint(1,11,5)
>>> x = np.arange(1,6,1)
>>> y = np.arange(6,11,1)
>>> rand, x
(array([4, 1, 5, 3, 7]), array([1, 2, 3, 4, 5]))
```
### Example 1
```pycon
>>> np.where(rand>5, True, False)
array([False, False, False, False,  True])
```
Here we are checking to see where our rand array is greater than 5 and if it is put true if it isn't put false
### Example 2
```pycon
>>> np.where(rand>x, True, False)
array([ True, False,  True, False,  True])
>>> np.where(rand>x, 600, False)
array([600,   0, 600,   0, 600])
>>> np.where(rand>x, 600, rand)
array([600,   1, 600,   3, 600])
```
In this situation we are checking the random array against the x array and seeing where the rand array is greater than the x array put true else put false.

Numpy goes element by element here ... so it will check to see if rand[0] > x[0] then the next then the next and spit out an array of results.

We can also put numbers in the place of the true result as you can see we put 600 instead or true so where true we put 600. So you can think of it literally as if rand>x do the first thing else do the second thing.

Also we can set the result to be an array of the same shape so we can say where rand greater than x put 600 else keep the rand value 
### Example 3
```pycon
>>> np.where((rand > x) & (rand < y), True, False)
array([ True, False,  True, False,  True])
```
You can do a comparison where you have one check and / or another check and then the where will check the true and false values of those.

This is no different than saying if x==3 and y==5 so just think of applying that to this where function. You take the truth values of the first part and the truth value of the second part and see where both of those are true and both of those are false.

Again remember numpy goes element by element any time you compare an array
### Example 4
```pycon
>>> ema_above = np.random.randint(0,2, 10, dtype=np.bool_)
>>> rsi_below = np.random.randint(0,2, 10, dtype=np.bool_)
>>> np.where((ema_above == True) & (rsi_below == True), True, False)
array([False,  True, False, False, False, False, False, False, False,
       False])
```
Here is a real world example of how we use it in trading by comparing something like an ema above and rsi below