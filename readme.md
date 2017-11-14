# portal

## useful articles

- [React Component Patterns](https://medium.com/gitconnected/react-component-patterns-ab1f09be2c82)
- [Django Channels (live webpages with WebSockets)](https://www.ploggingdev.com/2017/11/building-a-chat-room-using-django-channels/)
- [Front end checklist](https://github.com/thedaviddias/Front-End-Checklist)


## Apis:

- BikeRegister
- Police
- Google maps
- Twitter RSS
- Postcodes

## Key tech:

### Requests
- html for humans
- used to (easily) make web requests
- has a .json() function that parses the request (if we know it's json)

### Flask
- used to handle web requests
- allows you to define routes (with the @app.route decorator)

### Jinja2
- allows you to define templates and inject veriables into them on the server side
- comes packaged with flask by default

### Peewee
- an object-relational-mapper
- allows you do define classes and save and fetch them easily
- NO MORE SQL QUERIES <3<3

### React
- allows you to create complex uis with javascript

### Webpack
- a build tool for the web
- allows you to compile "future" js into browser compatible code
- also supports other formats: images, css, svg, etc.

### Typescript (?)
- brings optional typing to javascript
- provides better type inference and code completion
- entirely optional
- typescript and javascript can live side-by-side

## To install

- Make sure you have node and npm installed
- make sure you have python3 installed
- run these commands:


    pip3 install -r requirements.txt
    npm install
    npm run build
    python3 back/app.py
      
## some useful rambling:

### Typescript and anonymous functions

An anonymous function is defined similarly to ML:

    ML - fn x => x+1
    JS - x => x+1
    Py - lambda x: x+1

You may optionally define types for your functions.
This is because of typescript, which provides some
cool features.

    ML - fn (x:int):int => x+1
    JS - (x: number):number => x+1

Notice how js doesnt have a distinction between `int`
and `floats`. All numbers (including what you might
think is an int) are floats. You can do more complex stuff
that ml doesn't allow like returning x / 2 if disible
by two otherwise false since javascript is so relaxed.
The important part here is the `|` symbol which allows
you to define multiple return types (in this case a 
number or false). The IDE and compiler, when presented
with conflicting types, will not allow you to for
example pass a string into a function that specifically
only takes a number. This allows us to catch what is
typically a runtime error in JS at compile time instead.

    (x: number): number | false => x % 2 == 0 ? x / 2 : false
    
This uses the [ternary operator](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Conditional_Operator) 
`condition ? ifTrue : ifFalse` as a way of getting rid of
if statements. Javascript can be written in a
functional style quite easily (map, filter, and reduce
could be used as an example) and functional programming
prefers to use expressions instead of statements. The
`if then else` expression in ML is in fact a ternary
operator expression because it guarantees a return value.
If you want to read more about the difference between
statements and expressions, [here's a cool article.](https://fsharpforfunandprofit.com/posts/expressions-vs-statements/)

### JSDoc

The documentation tags in JS are in the JSDoc style. There
are 3 main parts: `description, params, returns`. Here's
and example snippet.

    /**
     * Multiplies a given number by two.
     * @param {number} x The number to multiply.
     * @returns {number} The number multiplied by two.
     */
    function multByTwo(x: number): number {
        return x*2
    }
    
If you define the types in the function, JSDoc will fill in
the types in the documentation as well. There are a [whole
load](http://usejsdoc.org/) of documentation tags and you
can then extract the docs out for easy reference later.

### Some cool JS language features:

#### Promises and `async/await`

`async/await` allows for really easy asynchronous processing.
Async functions are denoted with the `async` keyword:

    const inc = async x => x+1
    async function inc(x) {
        return x+1
    }
    
These calculations are done in parallel with the main program,
and the function returns a Promise\<number\> which can be
awaited to resolve to the number. 

    let five = await inc(4)
    // alternatively..
    let request = longAsyncFunction(my_url)
    ...
    // other stuff
    ...
    let result = await request
    
You can await things immediately or save the promise to a
variable and await it when you need it.

Async await is syntactic sugar on top of the Promise api.
Why not use promises directly? The short answer is looks:

    longAsyncFunction(my_url)
        .then(result => {
            do_stuff(result)
        }
    // vs
    do_stuff(await lonyAsyncFunction(my_url))
    
Sometimes, its useful to use the promise API:

    let crimes = await Promise.all(crime_urls.map(url => getCrimeFromUrl(url))
    
In this case, `getCrimeFromUrl` is an asynchronous function
that gets a crime from a URL. We have a list of `crime_urls`, 
and want to call this function for each url in the list.
`Promise.all` lets us resolve all the promises in the list
before returning the list of crimes.

#### Fetch API

The old way of doing AJAX requests looked a little like this:
    
    function reqListener() {
      var data = JSON.parse(this.responseText);
      console.log(data);
    }
    
    function reqError(err) {
      console.log('Fetch Error :-S', err);
    }
    
    var oReq = new XMLHttpRequest();
    oReq.onload = reqListener;
    oReq.onerror = reqError;
    oReq.open('get', './api/some.json', true);
    oReq.send();
        
The fetch API is a relatively new feature that uses our new
best friend: promises, and has a vastly simplified syntax
and a much more familiar feel to it. No silly apis.
    
    try {
        const response = await fetch('./api/some.json')
        console.log(await response.json())
    } catch (e) {
        onsole.log('Fetch Error :-S', e);
    }

#### Spread syntax

You have a list values that you want to pass into a function.
    
    // instead of this
    myFunction(list[0], list[1], list[2])
    // do this
    myFunction(...list)
    
It unpacks the list and passes in all the arguments. You can
do that same with dictionaries in react.

    const props = {
        arg1: "test",
        arg2: "value"
    }

    // instead of this
    <MyComponent arg1={props.arg1} arg2={props.arg2} />
    // do this
    <MyComponent {...props} />
    
  