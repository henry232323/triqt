# triqt
Run the Qt event loop from within the [Trio](https://github.com/python-trio/trio) event loop. With inspiration and code borrowed from [Quamash](https://github.com/harvimt/quamash) 

**This is a simple single-file answer to a difficult problem. It doesn't have any tests and isn't anything close to professionally maintained. If you're looking for a well made and well documented library that runs Trio within the Qt loop, I recommend [qtrio](https://github.com/altendky/qtrio)

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
