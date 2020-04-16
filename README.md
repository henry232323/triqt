# triqt
Run the Qt event loop from within the [Trio](https://github.com/python-trio/trio) event loop.

A simple way to use trio with your Python Qt application.
To begin running the app
```py
>>> app = App()
>>> trio.run(task, instruments=[triqt.Instrument(app)])
```
To invoke an async function from Qt using a Signal
```py
>>> triqt.async_signal(func, args)
```
