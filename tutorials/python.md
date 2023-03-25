tuple
    Test type of elements python tuple/list https://stackoverflow.com/questions/8964191/test-type-of-elements-python-tuple-list
    add to a tuple    hey = ()    hey + (9,) + (5,)

    turn a tuple into a list turn a list into a tuple

dictionary
    How to check if a dictionary is empty? https://stackoverflow.com/questions/23177439/how-to-check-if-a-dictionary-is-empty

    turn a dictionary into a list
    https://stackoverflow.com/questions/1679384/converting-dictionary-to-list
    for key, value in dict.iteritems():
        temp = [key,value]
        dictlist.append(temp)

list
    append to beginning of list
        https://stackoverflow.com/questions/17911091/append-integer-to-beginning-of-list-in-python

    turn a list into a dictionary https://builtin.com/software-engineering-perspectives/convert-list-to-dictionary-python

    append to list without chaning the original list
    https://stackoverflow.com/questions/35608790/how-to-add-new-value-to-a-list-without-using-append-and-then-store-the-value
    ['yo'] + param_keys + ['hey']

    get specific part of a string python
    https://stackoverflow.com/questions/27387415/how-would-i-get-everything-before-a-in-a-string-python
    param_keys[0].split('_')[0] returns rsi

How to open a URL in python
https://stackoverflow.com/questions/4302027/how-to-open-a-url-in-python

itertools cart product
        final_user_args = np.array(list(product(*users_args_list))).T

if statement one line
'Yes' if fruit == 'Apple' else 'No'
https://stackoverflow.com/questions/2802726/putting-a-simple-if-then-else-statement-on-one-line

How to test multiple variables for equality against a single value?
and test one variable against multiple values
https://stackoverflow.com/questions/15112125/how-to-test-multiple-variables-for-equality-against-a-single-value
if tester.lower() in ('open', 'high', 'low', 'close'):
if tester.lower() not in ('open', 'high', 'low', 'close'):

capitalize upper lowercase str or list
.upper .lower .capitialize

list comprehension for loop 
param_keys = [ind_name + '_' + x for x in param_keys] 