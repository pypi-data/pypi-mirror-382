from omgui.spf import spf

spf(["This is a success", "hello, world"], status="success", pad=1)
spf.success(["This is a success", "hello, world"], pad=1)

spf(["This is a warning", "hello, world"], status="warning", pad=1)
spf.warning(["This is a warning", "hello, world"], pad=1)

spf(["This is an error", "hello, world"], status="error", pad=1)
spf.error(["This is an error", "hello, world"], pad=1)

x = spf.produce(["This is produced", "hello, world"], pad=1)
print(x)
y = spf.produce(["This is produced success", "hello, world"], status="success", pad=1)
print(y)
